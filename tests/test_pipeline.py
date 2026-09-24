"""রিগ্রেশন টেস্ট — ক্যাটাগরি লিক, জাঙ্ক, ডুপ্লিকেট আবার ফিরে আসা আটকায়।"""
import pytest
from src.config import CATEGORIES, PLATFORMS, TOPICS_PER_PLATFORM
from src.verifier import relevant, quality_ok, dedupe, diversify, norm, cheap_score


@pytest.mark.parametrize("title,cat,expect", [
    ("Apple unveils M5 MacBook Pro with new AI chip", "Tech", True),
    ("Best chili recipe for a cold winter night", "Tech", False),
    ("Ozempic linked to lower heart risk in new study", "Health", True),
    ("Nasdaq slips as Fed signals a rate pause", "Health", False),
    ("How to pray Salah step by step for beginners", "Islamic", True),
    ("Nvidia earnings beat Wall Street estimates", "Business", True),
    ("New emoji coming to iPhone in the 2026 update", "Image_Emoji", True),
    ("Senate passes new immigration bill after debate", "News", True),
])
def test_relevance_gate(title, cat, expect):
    assert relevant(title, CATEGORIES[cat]) is expect


@pytest.mark.parametrize("title,ok", [
    ("Google unveils Gemini 3.8 Flash TTS models", True),
    ("Daily Discussion Thread February 2026", False),
    ("[deleted]", False),
    ("YOU WON'T BELIEVE THIS ONE TRICK", False),
    ("AI", False),
    ("a" * 200, False),
    ("🔥🔥🔥🔥🔥🔥🔥🔥", False),
])
def test_quality_gate(title, ok):
    assert quality_ok(title) is ok


def test_dedupe_near_duplicates():
    items = [{"title": "Apple unveils M5 MacBook Pro"},
             {"title": "Apple unveils the new M5 MacBook Pro"},
             {"title": "Nvidia launches RTX 6090 GPU"}]
    assert len(dedupe(items)) == 2


def test_diversify_kills_autocomplete_clones():
    items = [{"title": f"best laptop 2026 for {x}", "info": "Google autocomplete"}
             for x in ("gaming", "college", "work", "design", "video")]
    assert len(diversify(items)) <= 2


def test_no_cross_category_keyword_overlap_explosion():
    """একই টপিক যেন ৩+ ক্যাটাগরিতে relevant না হয়।"""
    t = "Apple unveils M5 MacBook Pro with new AI chip"
    hits = [c for c, cfg in CATEGORIES.items() if relevant(t, cfg)]
    assert len(hits) <= 2, f"leaks into {hits}"


def test_cheap_score_prefers_hot_and_recent():
    cfg = CATEGORIES["Tech"]
    hot = cheap_score({"title": "OpenAI launches new GPT model today", "hot": True}, cfg)
    cold = cheap_score({"title": "some old software thing exists somewhere"}, cfg)
    assert hot > cold


def test_config_integrity():
    for cat, cfg in CATEGORIES.items():
        for k in ("label", "must_any", "seeds", "subreddits", "news_queries",
                  "yt_queries", "quora_queries"):
            assert cfg.get(k), f"{cat} missing {k}"
        assert len(cfg["must_any"]) >= 15
        assert not any(" " == s for s in cfg["seeds"])


def test_norm_strips_stopwords():
    assert norm("The Best of the New AI Tools") == "ai tools"


def test_grid_size():
    assert len(PLATFORMS) == 6 and TOPICS_PER_PLATFORM == 5


def test_pick_diverse_no_clone_leak():
    """রিগ্রেশন: fallback যেন ক্লোন ফিরিয়ে না আনে।"""
    from src.verifier import pick_diverse
    items = [{"title": f"how to pray salah {x}", "info": "Google autocomplete"}
             for x in ("step by step", "for kids", "sitting on floor", "correctly", "at home")]
    items += [{"title": "ramadan 2026 dates", "info": "Google autocomplete"},
              {"title": "hajj guide application", "info": "Bing search demand"},
              {"title": "zakat calculator online", "info": "Bing search demand"}]
    out = pick_diverse(items, 5)[:5]
    prefixes = [" ".join(norm(i["title"]).split()[:2]) for i in out]
    assert len(set(prefixes)) >= 3, prefixes


# ---------------------------------------------------------------- content kit
def test_detect_intent():
    from src.contentkit import detect_intent
    assert detect_intent("How to pray salah step by step") == "How-to / Tutorial"
    assert detect_intent("Best laptop 2026 vs MacBook") == "Commercial / Review"
    assert detect_intent("Apple unveils M5 chip") == "News / Update"


def test_opportunity_prefers_longtail():
    from src.contentkit import competition_proxy
    broad = competition_proxy("ai")
    longtail = competition_proxy("how to use ai tools for project management")
    assert longtail < broad


def test_fallback_brief_is_complete():
    """LLM key ছাড়াও ব্রিফ যেন ব্যবহারযোগ্য হয়।"""
    from src.contentkit import _fallback_brief
    b = _fallback_brief("Apple unveils M5 MacBook Pro", "News / Update", [])
    assert len(b["titles"]) == 3 and b["meta"] and len(b["outline"]) >= 5
    assert b["video"]["hook"] and len(b["video"]["beats"]) >= 4
    assert len(b["video"]["hashtags"]) == 6


def test_dashboard_uses_dicts_not_indexes():
    """রিগ্রেশন: আগের crash বাগ (r[4]=title ধরে নেওয়া, r[10] IndexError)।"""
    import inspect
    from src import sheets
    src = inspect.getsource(sheets.write_dashboard)
    body = src.split('"""')[-1]          # docstring বাদ দিয়ে শুধু আসল কোড
    assert "r[10]" not in body and "r[4]" not in body
    assert 'r.get("score")' in body and 'r["topic"]' in body
