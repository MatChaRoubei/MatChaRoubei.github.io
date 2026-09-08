# MatCha の神秘小屋

林正澔（MatCha）的个人网站 —— 一个瑞士国际主义风格的个人空间，包含「介绍 / 文章 / 活动 / 关于我 / 链接 / 广告」等板块。

## 技术栈
- 纯静态 **HTML + CSS + JavaScript**（无框架）
- **Python** 构建脚本：从 `content/articles/*.md` 生成文章数据与页面

## 目录结构
```
deploy/
├── index.html           # 首页（门户）
├── about.html           # 关于我
├── links.html           # 社交 + 项目 + 友情链接
├── ad.html              # MC 交流群广告
├── passage.html         # 文章列表页
├── article_*.html       # 文章详情页（由 build.py 生成）
├── styles.css           # 全站样式
├── articles.js          # 文章数据（由 build.py 生成）
├── content/articles/    # 文章源文件（Markdown）
├── build.py             # 构建脚本
├── sitemap.xml          # 站点地图
├── robots.txt           # 爬虫规则
└── ...
```

## 本地构建
```bash
python build.py
```
扫描 `content/articles/*.md`，生成 `articles.js` 和 `article_*.html`。

## 添加文章
在 `content/articles/` 新建一个 `.md` 文件（格式见该目录下的 `README.md`），然后运行 `python build.py`。

## 添加活动
在 `content/activities/` 新建一个带有 `id / title / date / status / link / desc` 元数据的 `.md` 文件。活动与文章分开维护，专题页面可独立设计；运行 `python build.py` 后，首页活动区会自动读取新活动。

## 部署
托管于 **Cloudflare Pages**（绑定本 GitHub 仓库，push 后自动部署）。

## 版本
- `v1.0.0` 首个正式版
