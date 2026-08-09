"""一次性重建所有 .md 文件（从 index.html 提取文章）"""
import re, os

BASE = r"c:\Users\林正澔\Desktop\myweb\deploy"
ARTICLES = os.path.join(BASE, "content", "articles")
os.makedirs(ARTICLES, exist_ok=True)

with open(os.path.join(BASE, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# 元数据（从 index.html 中的 articles 数组直接提取）
articles = [
    {"id":1, "title":"止战之殇", "category":"原创", "author":"", "date":"2026-08-04", "time":"16:08", "sortDate":"2026-08-04", "excerpt":"帝国·圣洛基市的枪声打破了下午茶的宁静。我作为前线报道员，踏上了前往加瑟的征途……"},
    {"id":2, "title":"后战争时代·第一章", "category":"原创", "author":"", "date":"时间不可考", "time":"", "sortDate":"2024-01-01", "excerpt":"2077年，地联集团发布了一款名为「联梦」的VR眼镜，全球为之疯狂。"},
    {"id":4, "title":"定语从句：whose与whom的用法笔记", "category":"原创", "author":"", "date":"2025-01-16", "time":"00:26", "sortDate":"2025-01-16", "excerpt":"NCE2教了定语从句，但几乎完全没提到过whose和whom主导的定语从句。"},
    {"id":5, "title":"论损友与益友", "category":"原创", "author":"", "date":"2025-04-12", "time":"21:17", "sortDate":"2025-04-12", "excerpt":"回家途中无事可做，念此前在语文卷子上看到一篇议论文，对其观点略有不满……"},
    {"id":7, "title":"关于泛情问题的讨论", "category":"原创", "author":"", "date":"2025-07-18", "time":"02:51", "sortDate":"2025-07-18", "excerpt":"泛情是一种决策，这是无意识的，决策的回报是更多生子机会，决策代价是更低的信任……"},
    {"id":8, "title":"一个时代的缩影——我的背景", "category":"原创", "author":"", "date":"2026-02-10", "time":"22:57", "sortDate":"2026-02-10", "excerpt":"我是一个混合了很多地方文化的人。1949年，随着红旗插遍长江以南……"},
    {"id":9, "title":"furry的污名化与朋友圈风波", "category":"原创", "author":"", "date":"2026-05-10", "time":"19:24", "sortDate":"2026-05-10", "excerpt":"在今天下午两点我发了一条朋友圈，内容是在分享一个B站视频的同时评论……"},
    {"id":10, "title":"青少年男生的抵抗心理", "category":"原创", "author":"", "date":"2026-05-10", "time":"22:02", "sortDate":"2026-05-10", "excerpt":"我发现了一种比较特殊的个性。在我的观察中，这个个性的特征在青少年男生中比较明显……"},
    {"id":11, "title":"数学表达的一点想法", "category":"原创", "author":"", "date":"2026-05-16", "time":"21:44", "sortDate":"2026-05-16", "excerpt":"我认为在写数学表达的时候，表达者所写的所有对象应当被默认同时表达了表达符号内隐含的信息……"},
    {"id":12, "title":"后虚无主义时代的象征——奶蛙的崛起", "category":"原创", "author":"", "date":"2026-06-17", "time":"21:44", "sortDate":"2026-06-17", "excerpt":"奶蛙，一种人为创造的虚拟概念。奶蛙的出现离不开其形象来源——奶龙……"},
    {"id":13, "title":"男青少年人格分类", "category":"原创", "author":"", "date":"2026-06-23", "time":"", "sortDate":"2026-06-23", "excerpt":"我发现了一种比较特殊的个性。在我的观察中，这个个性的特征在青少年男生中比较明显……"},
    {"id":14, "title":"自哈基贝的半个失恋感想——大好人的自述", "category":"原创", "author":"", "date":"2025-11-09", "time":"15:04", "sortDate":"2025-11-09", "excerpt":"'这不可能啊，你性格很好的呀'——多。我叫哈基贝……"},
    {"id":15, "title":"亡妻回忆录", "category":"原创", "author":"", "date":"2025-11-16", "time":"14:49", "sortDate":"2025-11-16", "excerpt":"本篇一切内容均为虚构。大家可曾听过所谓'直男技术宅'这般的群体呢？"},
    {"id":16, "title":"The Fading Elderly in Silence", "category":"原创", "author":"", "date":"2025-11-17", "time":"01:33", "sortDate":"2025-11-17", "excerpt":"My name is Jiahao, a student from a junior high school in my community."},
    {"id":17, "title":"我和琳琳认识的第一百天", "category":"原创", "author":"", "date":"2026-05-08", "time":"", "sortDate":"2026-05-08", "excerpt":"今天是，我和琳琳认识的第一百天～感谢我们的吴启凡、林宇聪、雷耀祖……"},
    {"id":18, "title":"止战之殇（续写）", "category":"优秀二创", "author":"闻人木", "date":"2026-08-01", "time":"21:02", "sortDate":"2026-08-01", "excerpt":"空气里残存的硝烟并非火药独有的刺鼻，还裹挟着一丝淡若鸢尾、令人心神恍惚的甜香……"},
    {"id":19, "title":"100天——致我重要的人", "category":"优秀二创", "author":"琳琳", "date":"2026-05-08", "time":"", "sortDate":"2026-05-08", "excerpt":"好开心，时间好快，今天居然已经是我们认识的100天啦。"}
]

for a in articles:
    aid = a['id']
    # 从 HTML 提取正文
    pattern = rf'<div id="ab-{aid}">(.*?)</div>'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        print(f'警告: ab-{aid} 未找到')
        continue

    body_html = match.group(1).strip()
    # HTML → Markdown
    body_html = re.sub(r'<p>\s*(.*?)\s*</p>', r'\1\n\n', body_html, flags=re.DOTALL)
    body_html = re.sub(r'<strong>(.*?)</strong>', r'**\1**', body_html)
    body_html = re.sub(r'<em>(.*?)</em>', r'*\1*', body_html)
    body_html = body_html.replace('<br>', '\n')
    body_html = re.sub(r'<[^>]+>', '', body_html)
    body_html = re.sub(r'\n{3,}', '\n\n', body_html).strip()

    md_content = f'''---
id: {aid}
title: "{a['title']}"
category: {a['category']}
author: "{a['author']}"
date: {a['date']}
time: "{a['time']}"
sortDate: {a['sortDate']}
excerpt: "{a['excerpt']}"
---

# {a['title']}

{body_html}'''

    fpath = os.path.join(ARTICLES, f'{aid}.md')
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f'已创建 {aid}.md')

print('\n全部 .md 文件已重建，运行 python build.py 即可')