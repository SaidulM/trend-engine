"""দৈনিক Markdown রিপোর্ট — repo-তে REPORT.md হিসেবে কমিট হয়, ফোন থেকেও পড়া যায়।"""
import os


def write_report(stamp, records, plan, path="REPORT.md"):
    top = sorted([r for r in records if isinstance(r.get("score"), (int, float))],
                 key=lambda r: -r["score"])[:20]
    L = [f"# 🔥 Trending Report — {stamp}", "",
         f"**{len(records)}** টপিক সংগ্রহ · **{len(plan)}** কনটেন্ট ব্রিফ তৈরি", "",
         "## 📊 টপ ২০ ট্রেন্ডিং টপিক", "",
         "| # | Score | Category | Platform | Topic |", "|--:|--:|---|---|---|"]
    for i, r in enumerate(top, 1):
        t = r["topic"].replace("|", "/")
        link = f'[{t}]({r["link"]})' if r.get("link") else t
        L.append(f'| {i} | {r["score"]} | {r["category"]} | {r["platform"]} | {link} |')

    L += ["", "## ✍️ আজকের কনটেন্ট প্ল্যান (Opportunity অনুযায়ী)", ""]
    for i, p in enumerate(plan[:10], 1):
        L += [f'### {i}. {p["topic"]}',
              f'`Opportunity {p["opportunity"]}` · `Demand {p["demand"]}` · '
              f'`Competition {p["competition"]}` · *{p["intent"]}* · **{p["category"]}**', ""]
        if p.get("angle"):
            L.append(f'> {p["angle"]}')
            L.append("")
        if p.get("titles"):
            L.append(f'**Title:** {p["titles"][0]}')
        if p.get("keywords"):
            L.append(f'**Keywords:** `{"` `".join(p["keywords"][:6])}`')
        if p.get("outline"):
            L += ["", "**Outline**"] + [f"- {h}" for h in p["outline"]]
        if p.get("hook"):
            L += ["", "**🎬 Short video**", f"- *Hook:* {p['hook']}"] + \
                 [f"- {b}" for b in p.get("beats", [])] + \
                 ([f'- *CTA:* {p["cta"]}'] if p.get("cta") else [])
        if p.get("hashtags"):
            L.append(f'- *Tags:* {" ".join(p["hashtags"])}')
        L.append("")
    with open(path, "w") as f:
        f.write("\n".join(L))
    return path
