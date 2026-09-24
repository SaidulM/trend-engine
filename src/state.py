"""
Repo-persisted state — GitHub repo-কেই ফ্রি ডেটাবেস হিসেবে ব্যবহার।
কাজ: (১) গত N দিনে দেখানো টপিক আবার না দেখানো, (২) 🆕 NEW ব্যাজ,
     (৩) দিনের JSON স্ন্যাপশট আর্কাইভ (ফ্রি হিস্ট্রি)।
"""
import os, json, datetime as dt, logging

log = logging.getLogger("state")
STATE_DIR = "state"
SEEN_FILE = os.path.join(STATE_DIR, "seen.json")
DATA_DIR = "data"
REPEAT_BLOCK_DAYS = int(os.getenv("REPEAT_BLOCK_DAYS", "5"))


def _today():
    return dt.date.today().isoformat()


def load_seen():
    """{normalized_title: 'YYYY-MM-DD'} — পুরনো এন্ট্রি অটো-পরিষ্কার।"""
    try:
        with open(SEEN_FILE) as f:
            raw = json.load(f)
    except Exception:
        return {}
    cutoff = (dt.date.today() - dt.timedelta(days=REPEAT_BLOCK_DAYS * 3)).isoformat()
    return {k: v for k, v in raw.items() if v >= cutoff}


def is_stale(seen, key):
    """True = সম্প্রতি দেখানো হয়েছে, আজ আবার দেখিও না।"""
    d = seen.get(key)
    if not d:
        return False
    cutoff = (dt.date.today() - dt.timedelta(days=REPEAT_BLOCK_DAYS)).isoformat()
    return d >= cutoff


def mark(seen, key):
    seen[key] = _today()


def save_seen(seen):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f, indent=0, sort_keys=True)
    log.info("state/seen.json saved (%d keys)", len(seen))


def save_snapshot(payload):
    os.makedirs(DATA_DIR, exist_ok=True)
    p = os.path.join(DATA_DIR, f"{_today()}.json")
    with open(p, "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    log.info("snapshot -> %s", p)
    # ৬০ দিনের বেশি পুরনো স্ন্যাপশট মুছে ফেলা (repo হালকা রাখতে)
    cutoff = (dt.date.today() - dt.timedelta(days=60)).isoformat()
    for fn in os.listdir(DATA_DIR):
        if fn.endswith(".json") and fn[:-5] < cutoff:
            os.remove(os.path.join(DATA_DIR, fn))
    return p
