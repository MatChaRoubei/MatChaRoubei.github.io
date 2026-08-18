"""
构建脚本 — 扫描 content/articles/*.md，生成 articles.js + article_*.html
用法：python build.py

【傻瓜式操作】
  在 content/articles/ 新建 .md 文件 → python build.py → 上传
  最小格式只需 # 标题 + 正文，其余自动填充
"""
import os, json, re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(BASE_DIR, 'content', 'articles')
OUT_JS = os.path.join(BASE_DIR, 'articles.js')

def parse_front_matter(text):
    meta, body = {}, text.strip()
    if body.startswith('---'):
        end = body.find('---', 3)
        if end > 0:
            for line in body[3:end].strip().split('\n'):
                if ':' in line:
                    k, _, v = line.partition(':')
                    meta[k.strip()] = v.strip().strip('"\'').strip()
            body = body[end+3:].strip()
    return meta, body

def next_free_id(d):
    ids = {int(f.replace('.md','')) for f in os.listdir(d) if f[:-3].isdigit()}
    n = 1
    while n in ids:
        n += 1
    return n

def build():
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    files = sorted(
        [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.md') and f != 'README.md'],
        key=lambda x: int(x[:-3]) if x[:-3].isdigit() else 9999
    )

    articles, acts, seen_ids = [], [], set()

    for fname in files:
        fpath = os.path.join(ARTICLES_DIR, fname)
        raw = open(fpath, 'r', encoding='utf-8').read()
        meta, body = parse_front_matter(raw)

        # 决定 ID
        base = fname[:-3]
        pid = int(base) if base.isdigit() else None
        if pid is not None and pid in seen_ids:
            pid = None
        if pid is None:
            pid = next_free_id(ARTICLES_DIR)
        seen_ids.add(pid)
        if str(pid) != base:
            os.rename(fpath, os.path.join(ARTICLES_DIR, f'{pid}.md'))
            print(f'  → 重命名 {fname} → {pid}.md')

        # 标题
        lines = body.split('\n')
        title = meta.get('title','')
        if not title:
            for l in lines:
                if l.strip().startswith('# '):
                    title = l.strip()[2:]; break

        # 正文（去除标题行）
        body_text = '\n'.join(lines[1:]).strip() if lines and lines[0].startswith('# ') else body.strip()
        if not body_text.strip():
            body_text = lines[0].replace('# ','').strip() if lines else ''

        art = {
            'id': pid,
            'title': title,
            'category': meta.get('category','原创'),
            'author': meta.get('author',''),
            'date': meta.get('date',''),
            'time': meta.get('time',''),
            'sortDate': meta.get('sortDate') or meta.get('date',''),
            'excerpt': meta.get('excerpt','') or body_text[:100].replace('\n',' ').strip(),
            'body': md_to_html(body_text) if body_text else '',
            'chapters': meta.get('chapters','')
        }
        articles.append(art)
        gen_article_page(art)

        # 活动
        if meta.get('activity'):
            acts.append({
                'id': meta['activity'],
                'title': meta.get('activity_title', title),
                'date': meta.get('date',''),
                'status': meta.get('activity_status','active'),
                'link': meta.get('activity_link',''),
                'desc': meta.get('activity_desc', meta.get('excerpt',''))
            })

    out = {'articles': articles, 'activities': acts[::-1]}
    js = 'var SITE_ARTICLES_DATA = ' + json.dumps(out, ensure_ascii=False) + ';\n'
    with open(OUT_JS, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f'✅ articles.js 已生成 ({len(articles)} 文章, {len(acts)} 活动)')

    # 清理旧的 articles.json（不再需要）
    old_json = os.path.join(BASE_DIR, 'articles.json')
    if os.path.exists(old_json):
        os.remove(old_json)
        print('  → 已删除旧的 articles.json')

    # 清理不再使用的 article 页面
    valid_ids = {a['id'] for a in articles}
    for fname in os.listdir(BASE_DIR):
        m = re.match(r'^article_(\d+)\.html$', fname)
        if m and int(m.group(1)) not in valid_ids:
            os.remove(os.path.join(BASE_DIR, fname))
            print(f'  → 已删除多余 {fname}')

def md_to_html(t):
    out, in_p = [], False
    def flush():
        nonlocal in_p
        if in_p: out.append('</p>'); in_p = False
    for l in t.split('\n'):
        s = l.strip()
        if not s: flush(); continue
        if s.startswith('# '): flush(); out.append(f'<h2 class="md-h2">{s[2:]}</h2>')
        elif s.startswith('## '): flush(); out.append(f'<h3 class="md-h3">{s[3:]}</h3>')
        elif s.startswith('### '): flush(); out.append(f'<h4 class="md-h4">{s[4:]}</h4>')
        else:
            if not in_p: out.append('<p>'); in_p = True
            else: out.append('<br>')
            s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
            s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
            out.append(s)
    flush()
    return '\n'.join(out)

def gen_article_page(a):
    chapter_nav = ''
    chapters = (a.get('chapters') or '').strip()
    if chapters:
        links = []
        for part in chapters.split(','):
            part = part.strip()
            if not part or ':' not in part:
                continue
            label, _, href = part.partition(':')
            label, href = label.strip(), href.strip()
            active = ' active' if href == f'article_{a["id"]}.html' else ''
            links.append(f'<a href="{href}" class="chapter-link{active}">{label}</a>')
        if links:
            chapter_nav = '<div class="chapter-nav">' + ''.join(links) + '</div>'
    desc = (a.get('excerpt') or '').replace('&','&amp;').replace('"','&quot;').replace('<','&lt;').replace('>','&gt;')
    html = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><link rel="icon" type="image/jpeg" href="favicon.jpg"><title>{a['title']} — MatChaの神秘小屋</title><meta name="description" content="{desc}"><meta property="og:title" content="{a['title']}"><meta property="og:description" content="{desc}"><meta property="og:type" content="article"><meta property="og:image" content="favicon.jpg"><link rel="canonical" href="https://www.matchamilk.site/article_{a['id']}.html"><meta property="og:url" content="https://www.matchamilk.site/article_{a['id']}.html"><link rel="stylesheet" href="styles.css"><style>
:root{{--black:#111;--white:#f5f5f5;--gray-mid:#999;--gray-dark:#444;--green:#4a7c59;--spacing-xs:8px;--spacing-sm:16px;--spacing-md:32px;--spacing-lg:64px;--spacing-xl:96px;--border-thin:1px;--border-thick:4px;--font-mono:'Courier New',Courier,monospace;--font-sans:'Helvetica Neue',Helvetica,Arial,'PingFang SC','Noto Sans SC','Microsoft YaHei',sans-serif}}
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}html{{font-size:16px;-webkit-font-smoothing:antialiased}}body{{font-family:var(--font-sans);background:var(--white);color:var(--black);line-height:1.6;letter-spacing:.02em;min-height:100vh;position:relative}}
.grid-overlay{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;opacity:.06;background-image:linear-gradient(to right,var(--black)1px,transparent 1px),linear-gradient(to bottom,var(--black)1px,transparent 1px);background-size:48px 48px}}
.header-bar{{position:relative;z-index:10;display:flex;justify-content:space-between;align-items:center;padding:var(--spacing-md) var(--spacing-lg);border-bottom:var(--border-thin) solid var(--black);background:var(--white)}}.header-label{{font-family:var(--font-mono);font-size:.75rem;letter-spacing:.15em;text-transform:uppercase;color:var(--gray-dark)}}.header-dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:12px;vertical-align:middle}}.green-dot{{background:var(--green)}}.black-dot{{background:var(--black)}}.header-left,.header-right{{display:flex;align-items:center;gap:12px}}.header-right .header-dot{{margin-right:0;margin-left:12px}}
.article-page{{position:relative;z-index:1;max-width:760px;margin:0 auto;padding:var(--spacing-xl) var(--spacing-lg)}}.article-back{{display:inline-block;margin-bottom:var(--spacing-lg);font-family:var(--font-mono);font-size:.7rem;letter-spacing:.1em;color:var(--green);text-decoration:none;border-bottom:1px solid var(--green);padding-bottom:2px}}.article-back:hover{{color:var(--black);border-color:var(--black)}}.article-meta{{display:flex;gap:var(--spacing-sm);flex-wrap:wrap;margin-bottom:var(--spacing-sm)}}.article-cat{{font-family:var(--font-mono);font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;padding:2px 8px;border:1px solid var(--green);color:var(--green)}}.article-date{{font-family:var(--font-mono);font-size:.7rem;color:var(--gray-mid)}}.article-author{{font-family:var(--font-mono);font-size:.7rem;color:var(--green);font-weight:600}}.article-title{{font-size:2rem;font-weight:700;letter-spacing:.08em;color:var(--black);margin-bottom:var(--spacing-md);line-height:1.3}}.article-body{{font-size:.95rem;line-height:2;color:var(--gray-dark);letter-spacing:.03em}}.article-body p{{margin-bottom:var(--spacing-sm)}}.article-body strong{{color:var(--black)}}.footer-bar{{position:relative;z-index:10;display:flex;justify-content:space-between;align-items:center;padding:var(--spacing-md) var(--spacing-lg);border-top:var(--border-thin) solid var(--black);background:var(--white);font-family:var(--font-mono);font-size:.7rem;letter-spacing:.1em;color:var(--gray-mid)}}.footer-center .footer-dot{{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green)}}.disclaimer{{position:relative;z-index:10;text-align:center;padding:var(--spacing-sm) var(--spacing-md);background:var(--white);border-top:var(--border-thin) solid var(--black)}}.disclaimer p{{font-size:.7rem;letter-spacing:.05em;color:var(--gray-mid);font-style:italic}}
.chapter-nav{{display:flex;gap:var(--spacing-sm);flex-wrap:wrap;margin:var(--spacing-md) 0 var(--spacing-sm)}}.chapter-link{{display:inline-block;padding:8px 18px;border:var(--border-thick) solid var(--black);font-family:var(--font-mono);font-size:.7rem;letter-spacing:.1em;text-decoration:none;color:var(--black);transition:all .2s}}.chapter-link:hover,.chapter-link.active{{border-color:var(--green);background:var(--green);color:var(--white)}}
@media(max-width:768px){{.article-page{{padding:var(--spacing-lg) var(--spacing-md)}}.article-title{{font-size:1.5rem}}.header-bar{{padding:var(--spacing-sm) var(--spacing-md);flex-wrap:wrap;gap:4px;justify-content:center;text-align:center}}}}</style></head><body>
<div class="grid-overlay"></div><header class="header-bar"><div class="header-left"><span class="header-dot green-dot"></span><span class="header-label">MatChaの神秘小屋</span></div><div class="header-right"><span class="header-label">✨ おかえり ✨</span><span class="header-dot black-dot"></span></div></header>
<main class="article-page"><a href="index.html" class="article-back">← 返回首页</a>
<div class="article-meta"><span class="article-cat">{a['category']}</span><span class="article-date">{a['date']}{' ' + a['time'] if a.get('time') else ''}</span>{'<span class="article-author">作者：' + a['author'] + '</span>' if a.get('author') else ''}</div>
<h1 class="article-title">{a['title']}</h1>{chapter_nav}<div class="article-body">{a['body']}</div></main>
<footer class="footer-bar"><div class="footer-left"><span>© 2026 LIN ZHENGHAO</span></div><div class="footer-center"><span class="footer-dot green-dot"></span></div><div class="footer-right"><span>MatCha / 木茶</span></div></footer>
<div class="disclaimer"><p>这都是我用 DeepSeek 做的，我一眼网站源码都没有看，我也是小白来着 :P</p></div></body></html>'''
    open(os.path.join(BASE_DIR, f'article_{a["id"]}.html'), 'w', encoding='utf-8').write(html)

if __name__ == '__main__':
    build()