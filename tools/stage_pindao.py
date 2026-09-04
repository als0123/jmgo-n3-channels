#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 tools/_pindao_unzipped/pindao/*.py 全部去重 + 落盘到 assets/spider/ch_<n>.py
然后基于 _pindao_meta.csv 生成 config.sites 的 JSON 片段。
"""
import os, re, csv, json, hashlib, shutil, sys

ROOT = r"C:\Users\dy\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a9ae223fcb8c61289c2f4f5"
SRC  = os.path.join(ROOT, r"tools\_pindao_unzipped\pindao")
META = os.path.join(ROOT, r"tools\_pindao_meta.csv")
DST  = os.path.join(ROOT, r"assets\spider")
CHLIST = os.path.join(ROOT, r"tools\_chlist.json")
CFG    = os.path.join(ROOT, r"assets\config\config.json")

# ---- 工具 ----
def safe_name(name, fallback):
    s = (name or "").strip()
    s = re.sub(r"[\u0000-\u001f\u007f]", "", s)
    s = re.sub(r"[\s/\\:*?\"<>|]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("._")
    if not s:
        s = fallback
    return s[:48]

# ---- 读 meta ----
rows = []
with open(META, "r", encoding="utf-8-sig") as f:
    r = csv.DictReader(f)
    for row in r:
        rows.append(row)
print("meta 行数:", len(rows))

# ---- 去重（保留编号最小）----
seen = {}
unique = []
for row in sorted(rows, key=lambda x: int(re.findall(r"\d+", x["src"])[0])):
    h = row["sha1"]
    if h in seen:
        continue
    seen[h] = True
    unique.append(row)
print("唯一频道:", len(unique))

# ---- 拷贝并改名为 ch_<src>.py ----
new_files = []
for row in unique:
    n = int(re.findall(r"\d+", row["src"])[0])
    src = os.path.join(SRC, row["src"])
    dst = os.path.join(DST, f"ch_{n:03d}.py")
    shutil.copyfile(src, dst)
    new_files.append({"src": row["src"], "n": n, "name": row["name"], "host": row["host"], "path": f"ch_{n:03d}.py"})

# ---- 写频道清单 JSON 供 config 注入 ----
chlist = {
    "count": len(new_files),
    "duplicates_removed": len(rows) - len(unique),
    "files": new_files,
}
with open(CHLIST, "w", encoding="utf-8") as f:
    json.dump(chlist, f, ensure_ascii=False, indent=2)
print("已落盘到 chlist:", CHLIST)

# ---- 重新生成 config.json ----
# 保留"用户 20 个原频道"先入数组，再追加 pindao 频道
with open(CHLIST, "r", encoding="utf-8") as f:
    ch = json.load(f)

# 用户原 20 个频道（已手动登记）
user_20 = [
    ("zhenlang",   "真狼影视",   "spider_zhenlang.py",   "https://zlys9.top"),
    ("guazi",      "瓜子",        "spider_guazi.py",       ""),
    ("wukong",     "悟空影视",   "spider_wukong.py",      "https://www.yikucun.com"),
    ("kenan",      "柯南影视",   "spider_kenan.py",       "https://www.knvod.com"),
    ("uvod",       "UVOD",       "spider_uvod.py",        "https://www.uvod.tv"),
    ("ys2046",     "YS2046",     "spider_ys2046.py",      "https://ys2046.lat"),
    ("chu8",       "初8影视",    "spider_chu8.py",        "https://cjysw.cc"),
    ("qidian",     "奇点影视",   "spider_qidian.py",      "https://www.qdys2.cc"),
    ("xinghe",     "星河影视",   "spider_xinghe.py",      "https://xhkan.top"),
    ("xingchen",   "星辰影院",   "spider_xingchen.py",    "http://www.dgpengcheng.com"),
    ("zhizhi",     "枝枝影视",   "spider_zhizhi.py",      "https://zzoc.cc"),
    ("ni",         "泥视频",     "spider_ni.py",          "https://www.nivod.cc"),
    ("smys",       "smys",       "spider_smys.py",        "https://www.china-eae.com"),
    ("baokuan",    "爆款片库",   "spider_baokuan.py",     "https://bkpk82.baokuanpk.cc"),
    ("meiju",      "美剧天堂",   "spider_meiju.py",       "https://www.meijutt.cc"),
    ("aiyifan",    "爱壹帆",     "spider_aiyifan.py",     "https://www.iyf.lv"),
    ("rbotv",      "RBOTV",      "spider_rbotv.py",       "http://v.rbotv.cn"),
    ("yingxiang",  "映像星球",   "spider_yingxiang.py",   "https://www.yxxq41.cc"),
    ("tencent",    "腾讯视频",   "spider_tencent.py",     "https://v.qq.com"),
    ("maomi",      "猫咪AV",     "spider_maomi.py",       "https://maomi66.cc"),
]

def site(key, name, api, ext=""):
    return {
        "key": key, "name": name, "type": 3, "api": api, "ext": ext,
        "searchable": 1, "quickSearch": 1, "filterable": 1
    }

sites = []
for k, n, a, e in user_20:
    sites.append(site(k, n, a, e))

# 追加 pindao 频道
for f in ch["files"]:
    nm = f["name"] or f"频道{f['n']}"
    safe = re.sub(r"[^A-Za-z0-9_]", "_", (nm or f"ch{f['n']}"))[:30] or f"ch{f['n']}"
    key = f"ch_{f['n']:03d}_{safe}"
    sites.append(site(key, nm, f["path"], f["host"]))

# 读已有 config.json 顶层结构，注入新 sites
with open(CFG, "r", encoding="utf-8") as f:
    cfg = json.load(f)
cfg["sites"] = sites
cfg["__note__"] = (
    f"总计 {len(sites)} 个频道。其中前 20 个是用户原始影视源；"
    f"其余 {len(sites) - 20} 个来自 pindao 聚合包（已按内容去重），"
    "如需只保留影视，可编辑 sites 数组删除非影视项；详见 docs/加频道指南.md。"
)
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)

print(f"config.json 已重写: sites 数量 = {len(sites)}")
print(f"  - 用户原 20 个")
print(f"  - pindao 追加 {len(sites)-20} 个")
