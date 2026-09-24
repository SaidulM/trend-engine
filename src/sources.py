"""প্রতিটি প্ল্যাটফর্মের ক্যাটাগরি-নির্দিষ্ট কালেক্টর। সব ফ্রি, ক্রেডিট কার্ড লাগে না।"""
import os, re, json, html, logging, datetime as dt, urllib.parse as up
from concurrent.futures import ThreadPoolExecutor

import feedparser
from .http import get, get_json

log = logging.getLogger("sources")
POOL = int(os.getenv("FETCH_WORKERS", "6"))


def clean(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t or ""))
    t = re.sub(r"\s+", " ", t).strip()
    # ট্রেইলিং পাবলিশার নাম কেটে দেওয়া: "... - The Verge"
    t = re.sub(r"\s+[-–—|]\s+[A-Z][\w.'& ]{2,28}$", "", t)
    return t.strip(" -–—|")


def rss(url, limit=25, tag=""):
    txt = get(url)
    if not txt:
        return []
    try:
        d = feedparser.parse(txt)
    except Exception:
        return []
    out = []
    for e in d.entries[:limit]:
        t = clean(e.get("title", ""))
        if len(t) > 8:
            out.append({"title": t, "link": e.get("link", ""), "info": tag,
                        "published": e.get("published", "")})
    return out


def pmap(fn, items):
    """সমান্তরাল ফেচ — সিকোয়েন্সিয়াল ধীরগতির ফিক্স।"""
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=POOL) as ex:
        res = list(ex.map(lambda x: _safe(fn, x), items))
    return [r for sub in res for r in sub]


def _safe(fn, x):
    try:
        return fn(x) or []
    except Exception as e:
        log.warning("collector error %s: %s", getattr(fn, "__name__", fn), e)
        return []


# ---------------------------------------------------------------- suggest APIs
def google_suggest(seed):
    d = get_json("https://suggestqueries.google.com/complete/search"
                 f"?client=chrome&hl=en&gl=us&q={up.quote(seed)}")
    try:
        return [clean(x) for x in d[1]][:10]
    except Exception:
        return []


def youtube_suggest(seed):
    txt = get("https://suggestqueries-clients6.youtube.com/complete/search"
              f"?client=youtube&ds=yt&hl=en&gl=us&q={up.quote(seed)}")
    m = re.search(r"\((.*)\)", txt or "", re.S)
    if not m:
        return []
    try:
        return [clean(x[0]) for x in json.loads(m.group(1))[1]][:10]
    except Exception:
        return []


def bing_suggest(seed):
    d = get_json(f"https://api.bing.com/osjson.aspx?query={up.quote(seed)}&market=en-US")
    try:
        return [clean(x) for x in d[1]][:10]
    except Exception:
        return []


def ddg_suggest(seed):
    d = get_json(f"https://duckduckgo.com/ac/?q={up.quote(seed)}&kl=us-en")
    try:
        return [clean(x.get("phrase", "")) for x in d][:10]
    except Exception:
        return []


# ---------------------------------------------------------------- GOOGLE TRENDS
def google_trends(cat, cfg):
    out = []
    for u in ("https://trends.google.com/trending/rss?geo=US",
              "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"):
        hits = rss(u, 50, "Google daily trend")
        if hits:
            for h in hits:
                h["link"] = h["link"] or "https://trends.google.com/trending?geo=US"
                h["hot"] = True          # আসল daily trend = বোনাস স্কোর
            out += hits
            break

    def one(seed):
        return [{"title": s, "info": "Google autocomplete",
                 "link": "https://www.google.com/search?q=" + up.quote(s)}
                for s in google_suggest(seed)]
    out += pmap(one, cfg["seeds"])
    return out


# ---------------------------------------------------------------- YOUTUBE
def youtube(cat, cfg):
    out = []
    key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if key:
        after = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")

        def search(q):
            d = get_json("https://www.googleapis.com/youtube/v3/search?part=snippet&type=video"
                         f"&order=viewCount&publishedAfter={after}&regionCode=US"
                         f"&relevanceLanguage=en&maxResults=10&q={up.quote(q)}&key={key}", ttl=3600)
            if not d:
                return []
            if d.get("error"):
                log.warning("YouTube API: %s", d["error"].get("message", "")[:120])
                return []
            return d.get("items", [])

        items = pmap(search, cfg["yt_queries"])
        ids = [i["id"]["videoId"] for i in items if i.get("id", {}).get("videoId")][:50]
        stats = _yt_stats(ids, key)
        for i in items:
            vid = i.get("id", {}).get("videoId")
            if not vid:
                continue
            v = stats.get(vid, 0)
            out.append({"title": clean(i["snippet"]["title"]),
                        "link": f"https://youtu.be/{vid}",
                        "info": f'{i["snippet"]["channelTitle"]} • {v:,} views',
                        "views": v})

    def one(q):
        return [{"title": s, "info": "YouTube search demand",
                 "link": "https://www.youtube.com/results?search_query=" + up.quote(s)}
                for s in youtube_suggest(q)]
    out += pmap(one, cfg["yt_queries"])
    return out


def _yt_stats(ids, key):
    res = {}
    for i in range(0, len(ids), 50):
        d = get_json("https://www.googleapis.com/youtube/v3/videos?part=statistics&id="
                     + ",".join(ids[i:i + 50]) + "&key=" + key, ttl=3600) or {}
        for it in d.get("items", []):
            try:
                res[it["id"]] = int(it["statistics"].get("viewCount", 0))
            except Exception:
                pass
    return res


# ---------------------------------------------------------------- REDDIT
def reddit(cat, cfg):
    def one(sub):
        got = []
        d = get_json(f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=15")
        if d and "data" in d:
            for p in d["data"]["children"]:
                x = p["data"]
                if x.get("stickied") or x.get("over_18"):
                    continue
                got.append({"title": clean(x["title"]),
                            "link": "https://reddit.com" + x["permalink"],
                            "info": f'r/{sub} • {x.get("score",0):,} up • {x.get("num_comments",0)} cmt',
                            "score_raw": x.get("score", 0)})
        else:   # Actions IP থেকে JSON ব্লক হলে RSS fallback
            got = rss(f"https://www.reddit.com/r/{sub}/top/.rss?t=day&limit=10", 10, f"r/{sub}")
        return got
    return pmap(one, cfg["subreddits"])


# ---------------------------------------------------------------- QUORA
def quora(cat, cfg):
    """Quora-র পাবলিক API নেই — real question-demand (autocomplete) + site: সার্চ।"""
    def one(q):
        got = []
        for s in (google_suggest(q) + ddg_suggest(q)):
            s = s.strip()
            if len(s.split()) < 3:
                continue
            got.append({"title": s[0].upper() + s[1:] + ("" if s.endswith("?") else "?"),
                        "link": "https://www.quora.com/search?q=" + up.quote(s),
                        "info": "Quora question demand"})
        return got
    out = pmap(one, cfg["quora_queries"])
    out += rss("https://news.google.com/rss/search?q="
               + up.quote(f'site:quora.com {cfg["seeds"][0]}')
               + "&hl=en-US&gl=US&ceid=US:en", 8, "quora.com")
    return out


# ---------------------------------------------------------------- BING
def bing(cat, cfg):
    def news(q):
        return rss("https://www.bing.com/news/search?q=" + up.quote(q)
                   + "&format=RSS&cc=US&setlang=en-US", 12, "Bing News")

    def sug(seed):
        return [{"title": s, "info": "Bing search demand",
                 "link": "https://www.bing.com/search?q=" + up.quote(s)}
                for s in bing_suggest(seed)]
    return pmap(news, cfg["news_queries"]) + pmap(sug, cfg["seeds"])


# ---------------------------------------------------------------- GOOGLE NEWS
def google_news(cat, cfg):
    out = []
    if cfg.get("gnews_topic"):
        out += rss("https://news.google.com/rss/headlines/section/topic/"
                   f'{cfg["gnews_topic"]}?hl=en-US&gl=US&ceid=US:en', 25, "Google News topic")

    def q(x):
        return rss("https://news.google.com/rss/search?q=" + up.quote(x)
                   + "+when:2d&hl=en-US&gl=US&ceid=US:en", 12, "Google News")
    out += pmap(q, cfg["news_queries"])

    def feed(u):
        return rss(u, 12, up.urlparse(u).netloc.replace("www.", ""))
    out += pmap(feed, cfg.get("extra_rss", []))
    return out


COLLECTORS = {
    "Google Trends": google_trends,
    "YouTube": youtube,
    "Reddit": reddit,
    "Quora": quora,
    "Bing Search": bing,
    "Google News": google_news,
}
