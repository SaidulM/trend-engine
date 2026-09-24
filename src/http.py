"""
প্রোডাকশন-গ্রেড HTTP লেয়ার।
ফিক্স করে: রিট্রাই নেই, রেট-লিমিট নেই, ক্যাশ নেই, টাইমআউট হ্যাং, UA ব্লক।
"""
import os, time, json, hashlib, logging, threading, random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger("http")

CACHE_DIR = os.getenv("HTTP_CACHE_DIR", ".httpcache")
CACHE_TTL = int(os.getenv("HTTP_CACHE_TTL", "5400"))      # ১.৫ ঘণ্টা
TIMEOUT = (8, 18)                                        # connect, read

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]


class Throttle:
    """প্রতি-হোস্ট মিনিমাম গ্যাপ — Google/Reddit ব্লক এড়াতে (thread-safe)।"""
    def __init__(self):
        self._last, self._lock = {}, threading.Lock()
        self.rules = {
            "suggestqueries.google.com": 0.30,
            "suggestqueries-clients6.youtube.com": 0.30,
            "www.reddit.com": 1.0,
            "trends.google.com": 2.0,
            "news.google.com": 0.4,
            "www.bing.com": 0.30,
            "en.wikipedia.org": 0.05,
            "wikimedia.org": 0.05,
        }

    def wait(self, host):
        gap = self.rules.get(host, 0.25)
        with self._lock:
            prev = self._last.get(host, 0)
            delay = gap - (time.time() - prev)
            if delay > 0:
                time.sleep(delay + random.uniform(0, 0.15))
            self._last[host] = time.time()


THROTTLE = Throttle()


def _session():
    s = requests.Session()
    retry = Retry(total=2, connect=2, read=1, backoff_factor=0.8,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=frozenset(["GET"]), respect_retry_after_header=True)
    ad = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    s.mount("https://", ad)
    s.mount("http://", ad)
    return s


_local = threading.local()


def session():
    if not hasattr(_local, "s"):
        _local.s = _session()
    return _local.s


def _cache_path(url):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, hashlib.sha256(url.encode()).hexdigest()[:24] + ".json")


def get(url, use_cache=True, ttl=None):
    """টেক্সট ফেরত দেয়, ব্যর্থ হলে '' — কখনো exception raise করে না।"""
    p = _cache_path(url)
    ttl = CACHE_TTL if ttl is None else ttl
    if use_cache and os.path.exists(p):
        try:
            with open(p) as f:
                c = json.load(f)
            if time.time() - c["t"] < ttl:
                return c["b"]
        except Exception:
            pass

    from urllib.parse import urlparse
    THROTTLE.wait(urlparse(url).netloc)
    try:
        r = session().get(url, timeout=TIMEOUT, headers={
            "User-Agent": random.choice(UA_POOL),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8",
        })
        if r.status_code == 200:
            body = r.text
            if use_cache:
                try:
                    with open(p, "w") as f:
                        json.dump({"t": time.time(), "b": body}, f)
                except Exception:
                    pass
            return body
        log.warning("HTTP %s  %s", r.status_code, url[:90])
    except Exception as e:
        log.warning("FAIL %s  %s", type(e).__name__, url[:90])
    return ""


def get_json(url, **kw):
    t = get(url, **kw)
    if not t:
        return None
    try:
        return json.loads(t)
    except Exception:
        return None
