"""
ভেরিফিকেশন + স্কোরিং পাইপলাইন।

TWO-STAGE ডিজাইন (পারফরম্যান্স ফিক্স):
  Stage A (offline, 0 network) : relevance gate → quality gate → dedupe →
                                 cheap score → top 12 shortlist
  Stage B (network, parallel)  : শুধু shortlist-এর জন্য Google Autocomplete +
                                 Wikipedia pageviews + Google Trends
  Stage C (AI)                 : Gemini/OpenAI চূড়ান্ত বাছাই

আগে ছিল ~2520 sequential call (~25 মিনিট) → এখন ~430 parallel call (~3 মিনিট)।
"""
import os, re, json, math, time, difflib, logging, threading
import urllib.parse as up
from concurrent.futures import ThreadPoolExecutor

from .config import MIN_SCORE
from .http import get, get_json
from .sources import google_suggest

log = logging.getLogger("verify")

SHORTLIST = int(os.getenv("SHORTLIST", "8"))

STOP = {"the", "a", "an", "of", "for", "and", "to", "in", "on", "is", "are", "with", "how",
        "what", "why", "best", "new", "your", "you", "this", "that", "it", "at", "by", "from",
        "s", "vs", "will", "can", "be", "as", "its", "has", "have", "was", "were", "after"}

CLICKBAIT = re.compile(
    r"(you won'?t believe|shocking|gone wrong|\bomg\b|click here|this one trick|\bwtf\b|"
    r"\bnsfw\b|sponsored|advertisement|deal[s]? of the day|save \d+%|buy now|coupon|"
    r"giveaway|\bsubscribe\b|link in bio)", re.I)

JUNK = re.compile(
    r"^(re:|\[deleted\]|\[removed\]|daily thread|weekly thread|megathread|rant|vent|"
    r"discussion thread|what'?s everyone|moronic monday|daily discussion|"
    r"monthly|weekend|free talk|meta:|mod post|psa:|aita)", re.I)


# ============================================================ STAGE A : gates
def norm(t):
    t = re.sub(r"[^a-z0-9 ]+", " ", (t or "").lower())
    return " ".join(w for w in t.split() if w not in STOP)


def relevant(title, cfg):
    t = " " + re.sub(r"[^a-z0-9' ]+", " ", title.lower()) + " "
    t = re.sub(r"\s+", " ", t)
    for bad in cfg.get("never", []):
        if f" {bad} " in t:
            return False
    for kw in cfg["must_any"]:
        if f" {kw} " in t or f" {kw}s " in t:
            return True
    return False


def quality_ok(title):
    w = title.split()
    if not (3 <= len(w) <= 22):
        return False
    if not (14 <= len(title) <= 160):
        return False
    if CLICKBAIT.search(title) or JUNK.search(title):
        return False
    if sum(c.isalpha() for c in title) / max(len(title), 1) < 0.55:
        return False
    if title.isupper():
        return False
    if title.count("?") > 2 or title.count("!") > 1:
        return False
    return True


def dedupe(items, thresh=0.72):
    kept, keys = [], []
    for it in items:
        n = norm(it["title"])
        if not n or len(n) < 6:
            continue
        if any(difflib.SequenceMatcher(None, n, k).ratio() > thresh for k in keys):
            continue
        keys.append(n)
        kept.append(it)
    return kept


def diversify(items, max_per_prefix=2, max_per_source=2, prefix_words=2):
    pre, src, out = {}, {}, []
    for it in items:
        p = " ".join(norm(it["title"]).split()[:prefix_words])
        s = (it.get("info") or "")[:24]
        if pre.get(p, 0) >= max_per_prefix or (s and src.get(s, 0) >= max_per_source):
            continue
        pre[p] = pre.get(p, 0) + 1
        src[s] = src.get(s, 0) + 1
        out.append(it)
    return out


def pick_diverse(cand, want):
    """কঠোর থেকে শিথিল — যত দূর সম্ভব বৈচিত্র্য রেখে want-সংখ্যক টপিক দেয়।
    আগের বাগ: fallback সরাসরি raw লিস্ট জুড়ে দিত, তাই ক্লোন ফিরে আসত।"""
    last = []
    for pfx, src, words in ((1, 2, 2), (1, 3, 3), (2, 3, 3), (2, 4, 4)):
        last = diversify(cand, pfx, src, words)
        if len(last) >= want:
            return last
    return last + [i for i in cand if i not in last]


def cheap_score(it, cfg):
    """নেটওয়ার্ক ছাড়া প্রি-র‍্যাঙ্ক — shortlist বাছতে।"""
    s, title = 0.0, it["title"]
    if it.get("hot"):
        s += 18
    if it.get("score_raw"):
        s += min(math.log10(it["score_raw"] + 1) * 9, 25)
    if it.get("views"):
        s += min(math.log10(it["views"] + 1) * 5, 25)
    t = " " + norm(title) + " "
    s += min(sum(2.5 for kw in cfg["must_any"] if f" {kw} " in t), 15)
    if re.search(r"\b(2026|2025|today|new|launch|launches|announce[sd]?|unveil[sd]?|leak|"
                 r"update|breaking|first|record|report)\b", title, re.I):
        s += 7
    if re.match(r"^(how|why|what|which|best|top|is|can|should|where)\b", title, re.I):
        s += 5
    if 6 <= len(title.split()) <= 14:
        s += 3
    return s


# ============================================================ STAGE B : demand
_cache, _lock = {}, threading.Lock()


def _memo(key, fn):
    with _lock:
        if key in _cache:
            return _cache[key]
    v = fn()
    with _lock:
        _cache[key] = v
    return v


def autocomplete_demand(title):
    key = " ".join(norm(title).split()[:4])
    if not key:
        return 0

    def run():
        sug = google_suggest(key)
        if not sug:
            return 0
        head = norm(key).split()[0]
        hits = sum(1 for s in sug if head in norm(s))
        return min(len(sug) * 2.5 + hits * 2, 28)
    return _memo("ac:" + key, run)


def wiki_interest(title):
    key = " ".join(norm(title).split()[:4])
    if not key:
        return 0

    def run():
        try:
            d = get_json("https://en.wikipedia.org/w/api.php?action=query&list=search"
                         f"&format=json&srlimit=1&srsearch={up.quote(key)}")
            hits = (d or {}).get("query", {}).get("search", [])
            if not hits:
                return 0
            page = hits[0]["title"].replace(" ", "_")
            import datetime as dt
            end = dt.date.today() - dt.timedelta(days=1)
            start = end - dt.timedelta(days=7)
            v = get_json("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
                         f"en.wikipedia/all-access/user/{up.quote(page, safe='')}/daily/"
                         f"{start:%Y%m%d}/{end:%Y%m%d}")
            views = sum(i["views"] for i in (v or {}).get("items", []))
            return min(int(math.log10(views + 1) * 5), 18)
        except Exception:
            return 0
    return _memo("wk:" + key, run)


_pytrends, _pt_dead = None, False


def trends_scores(titles):
    """pytrends ব্যাচ (max 5) — GitHub IP-তে 429 হলে নিঃশব্দে বন্ধ হয়ে যায়।"""
    global _pytrends, _pt_dead
    out = {}
    if _pt_dead or os.getenv("DISABLE_PYTRENDS"):
        return out
    try:
        from pytrends.request import TrendReq
        if _pytrends is None:
            _pytrends = TrendReq(hl="en-US", tz=360, retries=2, backoff_factor=0.6,
                                 requests_args={"headers": {"Accept-Language": "en-US"}})
        kw = []
        for t in titles[:5]:
            k = " ".join(norm(t).split()[:3])
            if k and k not in kw:
                kw.append(k)
        if not kw:
            return out
        _pytrends.build_payload(kw, timeframe="now 7-d", geo="US")
        df = _pytrends.interest_over_time()
        for t in titles[:5]:
            k = " ".join(norm(t).split()[:3])
            if k in df:
                out[t["title"] if isinstance(t, dict) else t] = float(df[k].mean())
        time.sleep(1.5)
    except Exception as e:
        log.info("pytrends disabled: %s", str(e)[:80])
        _pt_dead = True
    return out


def enrich(items, cfg):
    """shortlist-এর জন্য সমান্তরাল নেটওয়ার্ক স্কোরিং।"""
    def work(it):
        s = cheap_score(it, cfg) + autocomplete_demand(it["title"])
        # Wikipedia শুধু entity-ধরনের হেডলাইনে — সার্চ-কোয়েরিতে অর্থহীন ও ধীর
        if any(w[:1].isupper() for w in it["title"].split()[1:]):
            s += wiki_interest(it["title"])
        it["score"] = round(min(s, 100), 1)
        return it
    with ThreadPoolExecutor(max_workers=8) as ex:
        items = list(ex.map(work, items))
    tr = trends_scores([i["title"] for i in items[:5]])
    for it in items:
        if it["title"] in tr:
            it["score"] = round(min(it["score"] + tr[it["title"]] * 0.25, 100), 1)
            it["info"] = (it.get("info", "") + f" • GT:{int(tr[it['title']])}").strip(" •")
    return items


# ============================================================ STAGE C : AI
def llm_rerank(cfg, items, want):
    if len(items) <= want:
        return items
    listing = "\n".join(f"{i}. {x['title']}" for i, x in enumerate(items[:30]))
    prompt = (
        f'You are a senior SEO content editor. Category: "{cfg["label"]}".\n'
        f"Pick the {want} BEST topics from the numbered list. Criteria:\n"
        f"(1) genuinely on-topic for this category, (2) currently trending / high US search "
        f"demand, (3) specific and substantial enough to write a full article about.\n"
        f"Reject: vague phrases, duplicates, pure clickbait, local-only trivia, off-topic.\n"
        f'Return ONLY JSON: {{"picks":[indexes best-first]}}\n\n{listing}')
    idx = _call_llm(prompt)
    if not idx:
        return items
    picked = [items[i] for i in idx if isinstance(i, int) and 0 <= i < len(items)]
    for p in picked:
        p["ai"] = "AI-verified ✓"
    seen, out = set(), []
    for p in picked + items:
        if p["title"] not in seen:
            seen.add(p["title"])
            out.append(p)
    return out


def _call_llm(prompt):
    gk = os.getenv("GEMINI_API_KEY", "").strip()
    ok = os.getenv("OPENAI_API_KEY", "").strip()
    grq = os.getenv("GROQ_API_KEY", "").strip()      # ফ্রি, কার্ড লাগে না
    import requests
    try:
        if gk:
            r = requests.post("https://generativelanguage.googleapis.com/v1beta/models/"
                              "gemini-2.0-flash:generateContent?key=" + gk,
                              json={"contents": [{"parts": [{"text": prompt}]}],
                                    "generationConfig": {"temperature": 0.2,
                                                         "responseMimeType": "application/json"}},
                              timeout=60)
            txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        elif grq:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Authorization": "Bearer " + grq},
                              json={"model": "llama-3.3-70b-versatile",
                                    "messages": [{"role": "user", "content": prompt}],
                                    "temperature": 0.2,
                                    "response_format": {"type": "json_object"}}, timeout=60)
            txt = r.json()["choices"][0]["message"]["content"]
        elif ok:
            r = requests.post("https://api.openai.com/v1/chat/completions",
                              headers={"Authorization": "Bearer " + ok},
                              json={"model": "gpt-4o-mini",
                                    "messages": [{"role": "user", "content": prompt}],
                                    "temperature": 0.2}, timeout=60)
            txt = r.json()["choices"][0]["message"]["content"]
        else:
            return None
        m = re.search(r'"picks"\s*:\s*(\[[^\]]*\])', txt) or re.search(r"(\[[^\]]*\])", txt, re.S)
        return json.loads(m.group(1)) if m else None
    except Exception as e:
        log.info("LLM skip: %s", str(e)[:100])
        return None


# ============================================================ PIPELINE
def verify(cfg, raw, want, run_seen, hist_seen, is_stale):
    # --- Stage A
    pool = []
    for it in raw:
        t = re.sub(r"\s+", " ", it.get("title", "")).strip()
        if not t or not quality_ok(t) or not relevant(t, cfg):
            continue
        it["title"] = t
        pool.append(it)

    pool = dedupe(pool)
    fresh = [i for i in pool if norm(i["title"]) not in run_seen]
    # গত কয়েকদিনে দেখানো টপিক বাদ — কিন্তু কিছুই না থাকলে ফিরিয়ে আনি
    novel = [i for i in fresh if not is_stale(hist_seen, norm(i["title"]))]
    for i in novel:
        i["new"] = True
    cand = novel if len(novel) >= want else (novel + [i for i in fresh if i not in novel])

    for it in cand:
        it["_cheap"] = cheap_score(it, cfg)
    cand.sort(key=lambda x: -x["_cheap"])
    cand = pick_diverse(cand, SHORTLIST)
    short = cand[:SHORTLIST]

    # --- Stage B
    short = enrich(short, cfg)
    strong = [i for i in short if i["score"] >= MIN_SCORE]
    short = strong if len(strong) >= want else short
    short.sort(key=lambda x: -x["score"])

    # --- Stage C
    final = pick_diverse(llm_rerank(cfg, short, want), want)[:want]
    for i in final:
        run_seen.add(norm(i["title"]))
    return final
