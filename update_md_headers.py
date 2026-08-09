"""批量给所有 .md 文件添加 YAML front matter（从 content/metadata.json 读取元数据）"""
import os
import json

BASE_DIR = r"c:\Users\林正澔\Desktop\myweb\deploy"
ARTICLES_DIR = os.path.join(BASE_DIR, "content", "articles")
META_PATH = os.path.join(BASE_DIR, "content", "metadata.json")

with open(META_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

articles_lookup = {str(a['id']): a for a in metadata.get('articles', [])}

for fname in os.listdir(ARTICLES_DIR):
    if not fname.endswith('.md'):
        continue
    fpath = os.path.join(ARTICLES_DIR, fname)
    aid = fname.replace('.md', '')

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    if content.startswith('---'):
        # 已有 front matter，跳过
        print(f'跳过 {fname}（已有 front matter）')
        continue

    meta = articles_lookup.get(aid, {})

    front = f'''---
id: {aid}
title: "{meta.get("title", "")}"
category: {meta.get("category", "原创")}
author: "{meta.get("author", "")}"
date: {meta.get("date", "")}
time: "{meta.get("time", "")}"
sortDate: {meta.get("sortDate", "")}
excerpt: "{meta.get("excerpt", "")}"
---

{content}'''
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(front)
    print(f'已更新 {fname}')

print('\n所有 .md 文件已添加 front matter')