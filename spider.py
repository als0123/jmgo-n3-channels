# -*- coding: utf-8 -*-
"""
CatVod / FongMi Spider 抽象基类（PC 端兼容实现）

打包到 APK 时，Chaquopy 实际会调用壳子自带的 base/spider.py；
此文件存在的目的：
1. 在 Windows / Linux 电脑上用普通 Python 即可 import 调试。
2. 为缺失部分接口的爬虫补全默认实现（直接返回空 / 抛 NotImplementedError）。
"""
import json
import re
import time
from urllib.parse import urljoin, urlencode, quote

try:
    import requests
except Exception:
    requests = None  # 让本地纯静态检查也能通过


class Spider(object):
    """所有 20 个 .py 都应继承这个类。"""

    # ----- 基础元信息 -----
    host = ""          # 站点 host，由 init() 覆盖
    ext = ""           # 由 init(extend) 注入
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    # ----- 框架会主动调用的接口（可被子类覆盖） -----
    def getName(self):         return self.__class__.__name__
    def getDependence(self):   return []
    def init(self, extend=""): self.ext = extend or ""
    def destroy(self):         pass
    def isVideoFormat(self, url): return bool(url and re.search(r"\.(m3u8|mp4|flv|mkv|avi|mov)(\?|$)", url, re.I))
    def manualVideoCheck(self):   return False
    def localProxy(self, param):  return None

    def homeContent(self, filterEnabled=False):
        return {"class": [], "list": []}

    def homeVideoContent(self):
        return {"list": []}

    def categoryContent(self, tid, pg, filter, extend):
        return {"list": [], "page": 1, "pagecount": 1, "limit": 30, "total": 0}

    def detailContent(self, ids):
        return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        return {"list": []}

    def playerContent(self, flag, id, vipFlags):
        return {"parse": 0, "url": "", "header": ""}

    def liveContent(self, url):
        return ""

    # ----- 通用网络工具 -----
    def fetch(self, url, headers=None, **kw):
        """统一的 GET 入口，自动加 UA。"""
        if requests is None:
            raise RuntimeError("需要 requests 库；请 pip install requests")
        kw.setdefault("timeout", 15)
        kw.setdefault("verify", False)
        h = dict(self.headers)
        if headers:
            h.update(headers)
        r = requests.get(url, headers=h, **kw)
        try:
            r.encoding = r.apparent_encoding or "utf-8"
        except Exception:
            r.encoding = "utf-8"
        return r

    def post(self, url, data=None, headers=None, **kw):
        if requests is None:
            raise RuntimeError("需要 requests 库；请 pip install requests")
        kw.setdefault("timeout", 15)
        kw.setdefault("verify", False)
        h = dict(self.headers)
        if headers:
            h.update(headers)
        r = requests.post(url, data=data, headers=h, **kw)
        try:
            r.encoding = r.apparent_encoding or "utf-8"
        except Exception:
            r.encoding = "utf-8"
        return r

    @staticmethod
    def url(path, base=None):
        if not path:
            return ""
        if path.startswith("http"):
            return path
        if path.startswith("//"):
            return "https:" + path
        return urljoin((base or "") + "/", path)
