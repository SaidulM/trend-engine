"""
CONTENT KIT — ট্রেন্ডিং টপিককে সরাসরি "লেখার যোগ্য" কনটেন্টে রূপান্তর।

প্রতিটি সেরা টপিকের জন্য তৈরি করে:
  • Search intent (informational / commercial / news / how-to)
  • Opportunity score — ডিমান্ড বনাম কম্পিটিশন (ফ্রি প্রক্সি)
  • SEO title options + meta description
  • Article outline (H2/H3) + target keywords
  • People-Also-Ask ধরনের প্রশ্ন (Google autocomplete "alphabet soup")
  • YouTube/Facebook শর্ট ভিডিও স্ক্রিপ্ট (hook → beats → CTA) + hashtags

সব ফ্রি: Google Suggest + Gemini/Groq ফ্রি টিয়ার। LLM না থাকলে হিউরিস্টিক fallback।
"""
import os, re, json, string, logging
from concurrent.futures import ThreadPoolExecutor

from .http import get_json
from .sources import google_suggest
from .verifier import norm, _call_llm

log = logging.getLogger("content")

CONTENT_TOPICS = int(os.getenv("CONTENT_TOPICS", "15"))   # রোজ কয়টা full brief


# ------------------------------------------------------------------ intent
INTENT_RULES = [
    ("How-to / Tutorial", r"\b(how to|how do|guide|tutorial|step by step|diy|fix|setup|install)\b"),
    ("Commercial / Review", r"\b(best|top \d|vs|versus|review|cheapest|price|worth it|alternative|buy)\b"),
    ("News / Update", r"\b(launch(es|ed|ing)?|announce[sd]?|unveil[sd]?|reveal[sd]?|leak[sd]?|"
                      r"breaking|report[sd]?|releases?|released|update[sd]?|new|2026|2025)\b"),
    ("Question / Explainer", r"^(what|why|which|is|are|can|should|does|do|when|where)\b|\?$"),
]


def detect_intent(title):
    for name, pat in INTENT_RULES:
        if re.search(pat, title, re.I):
            return name
    return "Informational"


# ------------------------------------------------------------------ PAA
ALPHA = list(string.ascii_lowercase)[:8] + ["how", "why", "what", "best", "vs"]


def people_also_ask(topic, limit=8):
    """'Alphabet soup' — Google Suggest-কে বাড়িয়ে আসল প্রশ্নগুলো বের করা।"""
    seed = " ".join(norm(topic).split()[:4])
    if not seed:
        return []

    def one(sfx):
        return google_suggest(f"{seed} {sfx}")
    out = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for res in ex.map(one, ALPHA[:10]):
            out += res or []
    qs, seen = [], set()
    for s in out:
        s = s.strip()
        k = norm(s)
        if not k or k in seen or len(s.split()) < 3:
            continue
        seen.add(k)
        qs.append(s[0].upper() + s[1:] + ("" if s.endswith("?") else "?"))
    # প্রশ্নবাচক শব্দ দিয়ে শুরু হওয়াগুলো আগে
    qs.sort(key=lambda x: (not re.match(r"^(what|why|how|is|can|does|which|when|who)\b", x, re.I),
                           len(x)))
    return qs[:limit]


# ------------------------------------------------------------------ competition
def competition_proxy(topic):
    """
    ফ্রি কম্পিটিশন প্রক্সি (Ahrefs KD-র বিকল্প):
    Wikipedia সার্চে কত ফল + টপিকের দৈর্ঘ্য। লং-টেইল = কম কম্পিটিশন = ভালো সুযোগ।
    0 (সহজ) — 100 (কঠিন)
    """
    words = len(norm(topic).split())
    base = 85 if words <= 2 else 65 if words == 3 else 45 if words == 4 else 30 if words <= 6 else 20
    try:
        d = get_json("https://en.wikipedia.org/w/api.php?action=query&list=search&format=json"
                     "&srlimit=1&srsearch=" + re.sub(r"\s+", "%20", norm(topic)[:60]))
        hits = (d or {}).get("query", {}).get("searchinfo", {}).get("totalhits", 0)
        if hits > 50000:
            base += 10
        elif hits < 500:
            base -= 10
    except Exception:
        pass
    return max(5, min(base, 100))


def opportunity(demand_score, topic):
    """সুযোগ = ডিমান্ড বেশি + কম্পিটিশন কম। এটাই আসলে 'কোনটা আগে লিখব' বলে দেয়।"""
    comp = competition_proxy(topic)
    opp = (demand_score * 0.65) + ((100 - comp) * 0.35)
    return round(min(opp, 100), 1), comp


# ------------------------------------------------------------------ AI brief
BRIEF_PROMPT = """You are a senior content strategist for a US audience.

TOPIC: "{topic}"
CATEGORY: {category}
SEARCH INTENT: {intent}
RELATED QUESTIONS PEOPLE SEARCH:
{paa}

Produce a practical content brief. Be specific and useful — no filler, no fluff.
Return ONLY valid JSON with exactly these keys:
{{
 "angle": "one sentence — the unique angle that makes this worth reading TODAY",
 "titles": ["3 SEO headlines, 55-65 chars, include the main keyword"],
 "meta": "meta description, max 155 chars",
 "keywords": ["6 target keywords/phrases, primary first"],
 "outline": ["5-7 H2 section headings in logical reading order"],
 "faq": ["4 questions the article must answer"],
 "video": {{
   "hook": "first 3 seconds of a short video — must stop the scroll",
   "beats": ["4-5 short spoken lines, 1 line per scene, total under 45 seconds"],
   "cta": "closing call to action",
   "caption": "Facebook/YouTube Shorts caption under 150 chars",
   "hashtags": ["6 relevant hashtags with #"]
 }}
}}"""


def build_brief(topic, category, intent, paa):
    raw = _call_llm_json(BRIEF_PROMPT.format(
        topic=topic, category=category, intent=intent,
        paa="\n".join("- " + q for q in paa[:6]) or "- (none)"))
    if raw:
        return raw
    return _fallback_brief(topic, intent, paa)


def _call_llm_json(prompt):
    txt = _llm_text(prompt)
    if not txt:
        return None
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
        return d if isinstance(d, dict) and d.get("titles") else None
    except Exception:
        return None


def _llm_text(prompt):
    import requests
    gk = os.getenv("GEMINI_API_KEY", "").strip()
    grq = os.getenv("GROQ_API_KEY", "").strip()
    ok = os.getenv("OPENAI_API_KEY", "").strip()
    try:
        if gk:
            r = requests.post("https://generativelanguage.googleapis.com/v1beta/models/"
                              "gemini-2.0-flash:generateContent?key=" + gk,
                              json={"contents": [{"parts": [{"text": prompt}]}],
                                    "generationConfig": {"temperature": 0.6,
                                                         "responseMimeType": "application/json"}},
                              timeout=70)
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        if grq:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Authorization": "Bearer " + grq},
                              json={"model": "llama-3.3-70b-versatile",
                                    "messages": [{"role": "user", "content": prompt}],
                                    "temperature": 0.6,
                                    "response_format": {"type": "json_object"}}, timeout=70)
            return r.json()["choices"][0]["message"]["content"]
        if ok:
            r = requests.post("https://api.openai.com/v1/chat/completions",
                              headers={"Authorization": "Bearer " + ok},
                              json={"model": "gpt-4o-mini",
                                    "messages": [{"role": "user", "content": prompt}],
                                    "temperature": 0.6,
                                    "response_format": {"type": "json_object"}}, timeout=70)
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        log.info("brief LLM skip: %s", str(e)[:90])
    return None


def _fallback_brief(topic, intent, paa):
    """LLM key না থাকলেও যেন কাজে লাগার মতো কিছু পাওয়া যায়।"""
    kw = " ".join(norm(topic).split()[:4])
    return {
        "angle": f"{intent} — মানুষ এখন '{kw}' খুঁজছে; সরাসরি উত্তর দিয়ে শুরু করো।",
        "titles": [topic[:65],
                   f"{topic[:48]}: What You Need to Know",
                   f"{kw.title()} Explained (2026 Guide)"],
        "meta": f"Everything about {kw} — clear answers, latest updates and practical tips."[:155],
        "keywords": [kw] + [" ".join(norm(q).split()[:4]) for q in paa[:5]],
        "outline": ["Quick answer (TL;DR)", f"What is {kw}?", "Why it's trending right now",
                    "Key details / how it works", "Pros, cons and common mistakes",
                    "What to do next"],
        "faq": paa[:4] or [f"What is {kw}?", f"Why is {kw} trending?",
                           f"How does {kw} work?", f"Is {kw} worth it?"],
        "video": {
            "hook": f"Everyone's searching for {kw} right now — here's why.",
            "beats": [f"{kw} just blew up in the US.",
                      "Here's the part most people miss.",
                      "This is what actually matters for you.",
                      "Three things to remember."],
            "cta": "Follow for daily updates.",
            "caption": f"{topic[:120]}"[:150],
            "hashtags": ["#trending", "#shorts", "#viral", "#news", "#fyp",
                         "#" + (norm(topic).split() or ["topic"])[0]],
        },
    }


# ------------------------------------------------------------------ orchestrator
def build_plan(top_items, limit=None):
    """top_items = [{'topic','score','category','platform','link'}] → কনটেন্ট প্ল্যান সারি।"""
    limit = limit or CONTENT_TOPICS
    picks = top_items[:limit]
    log.info("content kit: %d টপিকের brief তৈরি হচ্ছে", len(picks))

    def one(it):
        topic = it["topic"]
        intent = detect_intent(topic)
        paa = people_also_ask(topic)
        opp, comp = opportunity(it.get("score") or 0, topic)
        b = build_brief(topic, it.get("category", ""), intent, paa)
        v = b.get("video", {}) or {}
        return {
            "topic": topic, "category": it.get("category", ""),
            "platform": it.get("platform", ""), "demand": it.get("score"),
            "competition": comp, "opportunity": opp, "intent": intent,
            "angle": b.get("angle", ""),
            "titles": b.get("titles", []), "meta": b.get("meta", ""),
            "keywords": b.get("keywords", []), "outline": b.get("outline", []),
            "faq": (b.get("faq") or paa)[:5], "paa": paa,
            "hook": v.get("hook", ""), "beats": v.get("beats", []),
            "cta": v.get("cta", ""), "caption": v.get("caption", ""),
            "hashtags": v.get("hashtags", []), "link": it.get("link", ""),
        }

    with ThreadPoolExecutor(max_workers=4) as ex:
        plan = list(ex.map(_safe(one), picks))
    plan = [p for p in plan if p]
    plan.sort(key=lambda p: -(p["opportunity"] or 0))
    return plan


def _safe(fn):
    def wrap(x):
        try:
            return fn(x)
        except Exception as e:
            log.warning("brief failed for %r: %s", str(x)[:60], str(e)[:90])
            return None
    return wrap
