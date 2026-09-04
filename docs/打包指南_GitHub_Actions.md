# 打包指南（GitHub Actions 版）

> 适合不愿意在本地装 Android Studio 的用户。
> 全程在 GitHub 云端跑编译，5-10 分钟得到 APK。

---

## 一、前提

- 一个 GitHub 账号（免费注册即可）
- 浏览器（全程不需要安装任何软件）

---

## 二、操作步骤（约 10 分钟）

### 第 1 步：把这个目录上传成你自己的 GitHub 仓库

任选一种方式：

#### A. GitHub 网页直传（最简单）

1. 打开 https://github.com/new
2. **Repository name** 填 `jmgo-n3-channels`（自己定）
3. **Private** 或 **Public** 随便
4. **不要勾** "Add a README" / "Add .gitignore"
5. 点 **Create repository**
6. 在新页面点 **uploading an existing file**
7. 把本目录里**所有文件**（`assets/`、`.github/`、`docs/`、`tools/`、`README.md`）一次性拖进去
8. 滚到底部点 **Commit changes**

#### B. 命令行（如果已装 git）

```bash
cd <本项目根目录>
git init
git add .
git commit -m "init: 276 channels for JMGO N3"
git branch -M main
git remote add origin https://github.com/<你的用户名>/jmgo-n3-channels.git
git push -u origin main
```

---

### 第 2 步：触发打包

1. 进入你的 GitHub 仓库页面
2. 顶部标签点 **Actions**
3. 左侧选 **Build FongMi APK**
4. 右侧点 **Run workflow** → 选 `leanback`（投影仪必选）→ 绿色 **Run workflow** 按钮
5. 等 5-10 分钟，第一次会下载依赖（看日志进度条）

---

### 第 3 步：下载 APK

1. 工作流跑完后，**同一页面**会自动刷新
2. 滚到最底 **Artifacts** 区域
3. 点 **app-leanback-release** 下载（一个 zip，含 1 个 .apk）
4. 解压得到 `app-leanback-release.apk`

---

### 第 4 步：装到坚果 N3

任选一种方式：

#### A. U 盘安装（推荐）

1. 把 `app-leanback-release.apk` 拷到 U 盘根目录（FAT32/exFAT 都行）
2. N3 插入 U 盘 → 投影文件管理器 → 双击 apk
3. 第一次会弹"未知来源"——设置里允许一下
4. 装完桌面出现 **电视** 图标（FongMi 默认名字，可改）

#### B. 局域网 ADB（极客）

```bash
# N3 开发者模式开 ADB 调试，记下 IP
adb connect 192.168.x.x:5555
adb install -r app-leanback-release.apk
```

---

## 三、常见问题

| 现象 | 原因 / 解决 |
| --- | --- |
| Actions 跑失败，`./gradlew` 报错 | 看日志详情；90% 是 `local.properties` 没找到。已用 `echo sdk.dir` 步骤自动写入 |
| 第一次跑要等 8 分钟（要下 Gradle/SDK/AGP） | 正常；二次跑只需 2-3 分钟 |
| 装到 N3 上打开闪退 | 90% 是 `assets/spider/*.py` 里某个爬虫启动即 crash。FongMi 的日志在 N3 的 `Android/data/com.fongmi.android.tv/files/log/` 用 adb 取 |
| 想关掉某些频道 | 进壳子 → 设置 → 数据 → 站点管理 → 取消勾选 |
| 想换包名 / 图标 / 应用名 | 改 `FongMi-TV/app/build.gradle` 的 `applicationId` 和 `app_name`，需要 fork 整个 FongMi 仓库到本地编辑（要 AS） |
| 想换 icon | 替换 `FongMi-TV/app/src/main/res/drawable/ic_launcher.png` 后重新跑 Actions |
| `apkanalyzer` 装到一半提示版本不对 | 把 APK 拷到电脑，用 [APK Installer](https://www.coolapk.com/apk/258082) 装，会自动降级到兼容签名 |

---

## 四、产物长这样

构建成功后 APK 路径（云端）：

```
FongMi-TV/app/build/outputs/apk/leanback/release/app-leanback-release.apk
```

文件名就叫 `app-leanback-release.apk`，约 30-50 MB。

装到 N3 后默认入口是 `电视`，可在 N3 **设置 → 应用 → 全部应用 → 电视 → 设为默认**。

---

## 五、升级 / 改频道后重新出包

1. 改 `assets/spider/` 或 `assets/config/config.json`
2. 提交（网页或 git push）
3. 再次 **Actions → Build FongMi APK → Run workflow**
4. 下载新 artifact

全程不需要任何本地工具。
