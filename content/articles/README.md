# 如何添加新文章

在 `content/articles/` 目录新建一个 `.md` 文件，格式如下：

```markdown
---
category: 原创
date: 2026-09-01
excerpt: 这是文章摘要，显示在首页列表里
---

# 文章标题

正文内容……
```

**最小格式（只写正文也可以）：**
```markdown
# 我的新文章

正文内容……
```
`build.py` 会自动填充默认值。

# 如何添加活动

在对应文章的 `.md` 文件 front matter 加上：
```yaml
activity: 200day
activity_title: 认识琳琳200天活动
activity_status: active
activity_link: preview-200days.html
activity_desc: 倒计时中
```

然后运行：
```bash
python build.py
```

上传 `deploy/` 下所有文件到 GitHub 即可。