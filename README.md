# 坚果 N3 投影仪自用频道包

> 基于 [FongMi/TV](https://github.com/FongMi/TV) 开源壳子，把 276 个 Py Spider 频道打进 `assets/`，GitHub Actions 一键出 `app-leanback-release.apk`，装到坚果 N3 / N3 Pro / N3 Ultra 即可使用。

## 📦 这个仓库里有什么

```
.
├── assets/
│   ├── spider/         # 276 个 .py 频道源（20 个用户原 + 256 个 pindao 去重后）
│   │   ├── base/       # CatVod Spider 兼容基类（PC 端可 import 调试）
│   │   ├── spider_zhenlang.py, spider_wukong.py, ...   ← 你的 20 个正片影视
│   │   └── ch_001.py ~ ch_256.py                        ← pindao 聚合
│   └── config/
│       └── config.json # 登记 276 个频道 + DoH/代理/广告过滤
├── .github/workflows/
│   └── build.yml       # 一键打包 GitHub Actions
├── docs/
│   ├── 加频道指南.md
│   └── 打包指南_GitHub_Actions.md
└── tools/              # 去重 / 元数据提取脚本（不用管）
```

## 🚀 三步出 APK（详细见 [docs/打包指南_GitHub_Actions.md](docs/打包指南_GitHub_Actions.md)）

1. **Fork** 仓库到你的 GitHub
2. 打开 **Actions → Build FongMi APK → Run workflow**（默认 leanback，点 Run 即可）
3. 等 5-10 分钟，下载 Artifact：`app-leanback-release.apk`

把这个 APK 拷到 U 盘、装到 N3 即可（设置 → 安全 → 允许安装未知来源）。

## 🛠 加 / 减频道

详见 [docs/加频道指南.md](docs/加频道指南.md)。最简流程：

```bash
# 1. 把新 .py 拷到 assets/spider/
cp new_spider.py assets/spider/ch_999.py

# 2. 编辑 assets/config/config.json 的 sites 数组，加一条：
# { "key":"mynew","name":"新频道","type":3,"api":"ch_999.py","ext":"...","searchable":1 }

# 3. 提交 → 触发 Actions → 下载新 APK
```

## ⚙️ 关键参数

- **minSdk** 24（Android 7.0）—— 坚果 N3 是 Android 11/12，兼容
- **flavor** `leanback`（TV 模式，10 键遥控器友好）；如要装手机可改 `mobile`
- **依赖** Chaquopy 自带 requests / lxml / bs4 / pyquery / urllib3；唯一需手动 `pip install` 的是 `pycryptodome`

## ⚠️ 关于频道内容

pindao 聚合包中**混杂了**不同类型频道。安装后**默认全部启用**——请在壳子 `设置 → 数据 → 站点管理` 关闭不想要的频道。详见 [docs/加频道指南.md](docs/加频道指南.md) 第 6 节。
