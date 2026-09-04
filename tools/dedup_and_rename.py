#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描 tools/_pindao_unzipped/pindao/*.py
- 抽 getName()、self.host、self.headers
- 抽 init(extend="") 的默认 host
- 抓 SHA1 用于去重
- 输出一份 CSV
"""
import os, re, csv, hashlib, json, sys, glob

ROOT = r"C:\Users\dy\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a9ae223fcb8c61289c2f4f5"
SRC  = os.path.join(ROOT, r"tools\_pindao_unzipped\pindao")
OUT  = os.path.join(ROOT, r"tools\_pindao_meta.csv")

def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def parse_py(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()

    # getName()
    name = ""
    m = re.search(r"def\s+getName\s*\(\s*self[^)]*\)\s*:[\s\S]{0,800}?return\s+['\"\u201c\u2018]([^'\"\u201c\u2018\r\n]+)", txt)
    if m: name = m.group(1).strip()

    # self.host = '...'
    host = ""
    m = re.search(r"self\.host\s*=\s*['\"]([^'\"]+)", txt)
    if m: host = m.group(1).strip()

    # 类级 host = '...'
    if not host:
        m = re.search(r"^\s*host\s*=\s*['\"]([^'\"]+)", txt, re.M)
        if m: host = m.group(1).strip()

    # init(extend) 内 fallback host
    init_default = ""
    m = re.search(r"def\s+init\s*\(\s*self[^)]*extend[^)]*\)\s*:[\s\S]{0,400}?self\.host\s*=\s*\(?extend.*?or\s*['\"]([^'\"]+)", txt)
    if m: init_default = m.group(1).strip()

    return name, host, init_default

def slugify(name, fallback):
    s = (name or "").strip()
    if not s:
        s = fallback
    # 去掉 emoji 和非法字符
    s = re.sub(r"[\u0000-\u001f\u007f]", "", s)
    s = re.sub(r"[\s/\\:*?\"<>|]+", "_", s)
    return s[:48] or fallback

files = sorted(glob.glob(os.path.join(SRC, "*.py")),
               key=lambda p: int(re.findall(r"\d+", os.path.basename(p))[0]))

rows = []
for p in files:
    name, host, init_default = parse_py(p)
    rows.append({
        "src": os.path.basename(p),
        "sha1": sha1(p),
        "name": name,
        "host": host,
        "init_default": init_default,
        "size": os.path.getsize(p),
    })

# 1) 先按 sha1 去重，保留编号最小
seen = {}
unique = []
for r in sorted(rows, key=lambda x: int(re.findall(r"\d+", x["src"])[0])):
    if r["sha1"] in seen:
        seen[r["sha1"]].append(r["src"])
        continue
    seen[r["sha1"]] = [r["src"]]
    unique.append(r)

# 2) 写出 CSV
with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["src","sha1","name","host","init_default","size"])
    w.writeheader()
    for r in unique:
        w.writerow(r)

# 3) 写出名字冲突报告
print("源文件总数:", len(files))
print("去重后 (按 sha1):", len(unique))
print("被去重掉的副本:")
for k, v in seen.items():
    if len(v) > 1:
        print("  ", v)

# 4) 写出建议的 new_name 序列
print("\n--- unique 频道一览 ---")
for r in unique:
    nm = slugify(r["name"], r["src"].split(".")[0])
    print(f"  {r['src']:>8}  size={r['size']:>6}  {nm}  host={r['host'] or r['init_default']}")
