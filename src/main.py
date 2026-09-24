"""Entry point. GitHub Actions থেকে রোজ চলে।  লোকাল টেস্ট: DRY_RUN=1 python -m src.main"""
import os, sys, json, time, logging, traceback, datetime as dt
from zoneinfo import ZoneInfo

from .config import CATEGORIES, PLATFORMS, TOPICS_PER_PLATFORM
from .sources import COLLECTORS
from .verifier import verify, norm
from . import state

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)-7s %(name)-8s %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("main")

TZ = os.getenv("TZ_NAME", "Asia/Kolkata")
DRY = os.getenv("DRY_RUN", "").lower() in ("1", "true", "yes")
ONLY = [c.strip() for c in os.getenv("ONLY_CATEGORIES", "").split(",") if c.strip()]


def run():
    t0 = time.time()
    now = dt.datetime.now(ZoneInfo(TZ))
    stamp = now.strftime("%Y-%m-%d %H:%M")
    hist = state.load_seen()
    log.info("start %s  tz=%s  dry=%s  history=%d keys", stamp, TZ, DRY, len(hist))

    ss = None
    if not DRY:
        from .sheets import open_sheet
        ss = open_sheet()

    cats = {k: v for k, v in CATEGORIES.items() if not ONLY or k in ONLY}
    archive, records, snapshot = [], [], {"generated": stamp, "tz": TZ, "categories": {}}
    failures = []

    for cat, cfg in cats.items():
        log.info("── %s (%s)", cat, cfg["label"])
        rows, run_seen, cat_out = [], set(), []
        for plat in PLATFORMS:
            try:
                raw = COLLECTORS[plat](cat, cfg)
            except Exception:
                log.error("collector %s/%s crashed\n%s", cat, plat, traceback.format_exc())
                failures.append(f"{cat}/{plat}")
                raw = []
            try:
                picked = verify(cfg, raw, TOPICS_PER_PLATFORM, run_seen, hist, state.is_stale)
            except Exception:
                log.error("verify %s/%s crashed\n%s", cat, plat, traceback.format_exc())
                failures.append(f"verify:{cat}/{plat}")
                picked = []
            log.info("   %-14s raw=%-4d → %d", plat, len(raw), len(picked))

            for i in range(TOPICS_PER_PLATFORM):
                if i < len(picked):
                    it = picked[i]
                    link = it.get("link", "")
                    row = [stamp, plat, i + 1, it["title"], it.get("score", ""),
                           it.get("ai", "scored"), "🆕" if it.get("new") else "",
                           it.get("info", ""), link]
                    cat_out.append({"platform": plat, "rank": i + 1, "topic": it["title"],
                                    "score": it.get("score"), "link": link,
                                    "ai": it.get("ai", "scored"), "new": bool(it.get("new"))})
                    state.mark(hist, norm(it["title"]))
                    records.append({"topic": it["title"], "score": it.get("score"),
                                    "category": cat, "platform": plat, "link": link,
                                    "ai": it.get("ai", "scored"), "new": bool(it.get("new"))})
                else:
                    row = [stamp, plat, i + 1, "(no qualifying topic today)", "", "", "", "", ""]
                rows.append(row)
                archive.append([stamp, cat] + row[1:])

        snapshot["categories"][cat] = cat_out
        if DRY:
            for r in rows:
                print(f"  {r[1]:<14} {r[2]}  {str(r[4]):>5}  {r[6]:<2} {r[3][:88]}")
        else:
            from .sheets import write_category
            write_category(ss, cat, rows)

    # ── কনটেন্ট কিট: সেরা টপিকগুলোর আর্টিকেল ব্রিফ + শর্ট ভিডিও স্ক্রিপ্ট
    plan = []
    if os.getenv("SKIP_CONTENT", "").lower() not in ("1", "true", "yes"):
        try:
            from .contentkit import build_plan
            best = sorted([r for r in records if isinstance(r.get("score"), (int, float))],
                          key=lambda r: -r["score"])
            plan = build_plan(best)
            snapshot["content_plan"] = plan
        except Exception:
            log.error("content kit crashed\n%s", traceback.format_exc())

    if not DRY:
        from .sheets import write_dashboard, write_content_plan, append_archive
        write_dashboard(ss, records, stamp)
        if plan:
            write_content_plan(ss, plan, stamp)
        append_archive(ss, archive)
    elif plan:
        print("\n===== CONTENT PLAN (top 5) =====")
        for p in plan[:5]:
            print(f'\n  [{p["opportunity"]}] {p["category"]} · {p["intent"]}')
            print(f'   TOPIC : {p["topic"]}')
            print(f'   TITLE : {(p.get("titles") or [""])[0]}')
            print(f'   HOOK  : {p.get("hook","")}')
            for b in p.get("beats", [])[:3]:
                print(f'      → {b}')

    try:
        from .report import write_report
        write_report(stamp, records, plan)
    except Exception:
        log.warning("report skipped")

    state.save_seen(hist)
    state.save_snapshot(snapshot)

    kept = sum(1 for r in archive if not r[4].startswith("(no qualifying"))
    log.info("✅ done in %.1f min — %d/%d slots filled, %d failures",
             (time.time() - t0) / 60, kept, len(archive), len(failures))
    if failures:
        log.warning("degraded sources: %s", ", ".join(sorted(set(failures))[:12]))
    # অর্ধেকের বেশি খালি হলে workflow লাল করে দাও (নীরব ব্যর্থতা এড়াতে)
    if kept < len(archive) * 0.4:
        log.error("❌ too many empty slots — সোর্স ব্লক হতে পারে")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
