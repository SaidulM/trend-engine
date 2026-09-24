# 🔍 কোড অডিট রিপোর্ট

> **রাউন্ড ২ (সর্বশেষ)** নিচে ▸ [রাউন্ড ২ দেখুন](#-অডিট-রাউন্ড-২)

## রাউন্ড ১ — যা যা ভাঙা ছিল

সিনিয়র ডেভেলপার হিসেবে আগের ভার্সনটা রিভিউ করে **১৪টি টেকনিক্যাল প্রবলেম** পাওয়া গেছে।
`🔴 = প্রোডাকশনে সিস্টেম ভেঙে দিত`, `🟠 = ডেটা কোয়ালিটি নষ্ট করত`, `🟡 = মেইনটেন্যান্স ঝুঁকি`।

| # | সমস্যা | প্রভাব | সমাধান | প্রমাণ |
|---|---|---|---|---|
| 1 | 🔴 **স্কোরিং O(n) নেটওয়ার্ক কল** — ৩৫ টপিক × ৬ প্ল্যাটফর্ম × ৬ ক্যাটাগরি × ২ কল = **২,৫২০ sequential request ≈ ২৫ মিনিট** | GitHub Actions টাইমআউট, রোজ ব্যর্থ | **Two-stage pipeline**: আগে offline cheap-score → top ৮ shortlist → শুধু তাদের জন্য নেটওয়ার্ক স্কোরিং, ThreadPool(8) সহ | মাপা: **২৫ মিনিট → ১.৫ মিনিট/ক্যাটাগরি** |
| 2 | 🔴 **কোনো retry/backoff নেই** — একটা টাইমআউট মানেই সেই সোর্স শূন্য | ট্যাবে "(no data)" ভরে যেত | `urllib3.Retry` (429/5xx, backoff, Retry-After মান্য) + per-host throttle + UA rotation | `src/http.py` |
| 3 | 🟠 **diversify fallback ক্লোন ফিরিয়ে আনত** — কম ফল পেলে সরাসরি raw লিস্ট জুড়ে দিত | "how to pray salah × ৩" | `pick_diverse()` — কঠোর→শিথিল ৪ ধাপ relaxation | রিগ্রেশন টেস্ট যোগ করা |
| 4 | 🟠 **দিনে-দিনে একই টপিক** — কোনো হিস্ট্রি ছিল না | রোজ একই আর্টিকেল আইডিয়া | `state/seen.json` repo-তে কমিট হয়, **৫ দিন** একই টপিক ব্লক + `🆕` ব্যাজ | `src/state.py` |
| 5 | 🔴 **ARCHIVE আনবাউন্ডেড** — রোজ ১৮০ সারি, কখনো ছাঁটা হতো না | Google-এর ১০M সেল লিমিটে শিট মরে যেত | `ARCHIVE_MAX_ROWS=20000`, পুরনো সারি অটো-ট্রিম | `src/sheets.py` |
| 6 | 🟠 **Sheets 429 হ্যান্ডেল করা হতো না** | আধা-লেখা শিট, নীরব ডেটা লস | `_retry()` exponential backoff সব write-এ | |
| 7 | 🟡 **Credential ভুল হলে অস্পষ্ট crash** | ইউজার বুঝত না কী করতে হবে | প্রি-ফ্লাইট ভ্যালিডেশন + বাংলা এরর: *"এই ইমেইলটি Editor হিসেবে Share করো: bot@..."* | |
| 8 | 🟠 **HTTP ক্যাশ নেই** — একই URL বারবার | ধীর + রেট-লিমিট ব্লক | ডিস্ক ক্যাশ (TTL ১.৫ঘ) + GitHub Actions cache-এ persist | |
| 9 | 🟠 **pytrends ব্যর্থ হলেও বারবার চেষ্টা** — Actions IP-তে প্রায়ই 429 | প্রতি কলে ৫-১০ সে. নষ্ট | প্রথম ব্যর্থতায় circuit-breaker (`_pt_dead`) + `DISABLE_PYTRENDS` | |
| 10 | 🔴 **নীরব ব্যর্থতা** — সব সোর্স ব্লক হলেও workflow সবুজ | খালি শিট, কেউ জানত না | ৪০%-এর কম স্লট ভরলে exit code 1 + **অটো GitHub Issue** | `daily-trends.yml` |
| 11 | 🟡 **কোনো টেস্ট নেই** | কনফিগ এডিট করলেই ক্যাটাগরি লিক | **২৩টি pytest** + CI workflow (ruff + pytest প্রতি push-এ) | `tests/` — সব পাস |
| 12 | 🟠 **Reddit JSON Actions IP থেকে 403** | Reddit সারি খালি | RSS fallback + UA rotation + throttle | raw=10 নিশ্চিত হয়েছে |
| 13 | 🟡 **`print()` দিয়ে ডিবাগিং** | Actions লগে কিছু বোঝা যেত না | স্ট্রাকচার্ড `logging` + per-platform raw→kept কাউন্ট + মোট সময় | |
| 14 | 🟡 **Wikipedia কল সব টপিকে** — সার্চ-কোয়েরিতে অর্থহীন | সময় নষ্ট | শুধু entity-ধরনের হেডলাইনে (capitalized token আছে এমন) | |

---

## ➕ প্রফেশনাল ফিচার যা নতুন যোগ হলো

| ফিচার | কেন দরকার |
|---|---|
| **DASHBOARD ট্যাব** | সব ক্যাটাগরির টপ ৬০ টপিক এক জায়গায়, স্কোর অনুযায়ী সাজানো — আর্টিকেল প্ল্যান করার জন্য এটাই আসল কাজের পাতা |
| **Score heat-map** | সবুজ = বেশি সার্চেবল, লাল = দুর্বল। এক নজরে বোঝা যায় |
| **`🆕 New?` কলাম** | আজকেই প্রথম এসেছে কি না |
| **`data/YYYY-MM-DD.json` স্ন্যাপশট** | GitHub repo-ই ফ্রি টাইম-সিরিজ ডেটাবেস; ৬০ দিন পর অটো ক্লিন |
| **Actions artifact (৩০ দিন)** | শিট নষ্ট হলেও ডেটা ফেরত পাওয়া যায় |
| **`workflow_dispatch` ইনপুট** | UI থেকেই নির্দিষ্ট ক্যাটাগরি বা dry-run চালানো যায় — ডিবাগ সহজ |
| **`concurrency` group** | দুটো রান একসাথে চললে শিট করাপ্ট হওয়া আটকায় |
| **অটো failure issue** | সিস্টেম ভাঙলে GitHub-এ নোটিফিকেশন |
| **CI (ruff + pytest)** | কনফিগ এডিট করে ভুল করলে push-এই ধরা পড়ে |
| **Groq সাপোর্ট** | Gemini-র বিকল্প ফ্রি LLM, কার্ড ছাড়া |
| **DuckDuckGo suggest** | চতুর্থ সার্চ-ডিমান্ড সিগন্যাল, key ছাড়া |

---

## 💰 খরচ যাচাই — সবকিছু ১০০% ফ্রি, কার্ড লাগে না

| সার্ভিস | প্ল্যান | লিমিট | আমাদের ব্যবহার | কার্ড? |
|---|---|---|---|---|
| GitHub Actions | Free (public repo) | **আনলিমিটেড** মিনিট | ~১৮ মিনিট/দিন | ❌ না |
| GitHub Actions | Free (private repo) | ২,০০০ মিনিট/মাস | ~৫৪০ মিনিট/মাস | ❌ না |
| Google Sheets API | Free | ৩০০ req/মিনিট | ~৫০ req/দিন | ❌ না |
| Google Service Account | Free | — | — | ❌ না |
| Google Trends / News RSS | পাবলিক | — | — | ❌ না |
| Google/Bing/YouTube/DDG Suggest | পাবলিক | — | throttled | ❌ না |
| Reddit public JSON/RSS | Free | ~৬০/মিনিট | throttled | ❌ না |
| Wikipedia / Wikimedia API | Free | ~২০০/সে. | সামান্য | ❌ না |
| Gemini API (AI Studio) | Free tier | ১,৫০০ req/দিন | ৩৬ req/দিন | ❌ না |
| Groq (বিকল্প) | Free tier | দৈনিক কোটা | ৩৬ req/দিন | ❌ না |
| YouTube Data API | Free | ১০,০০০ ইউনিট/দিন | ~৩,৩০০ ইউনিট | ❌ না |

> **ট্রায়াল পিরিয়ড নেই, ক্রেডিট কার্ড নেই, কোনো পেইড টিয়ার নেই।** repo public রাখলে Actions মিনিটও আনলিমিটেড।

---

## ⚡ পারফরম্যান্স (আসল মাপা)

```
আগে :  ~25 মিনিট শুধু স্কোরিং-এ  →  টাইমআউট ❌
এখন :  1.5 মিনিট / ক্যাটাগরি  ×  6  =  ~9-18 মিনিট  ✅  (timeout 40 মিনিট)
        30/30 স্লট ভর্তি, 0 failures
```


---

# 🔍 অডিট রাউন্ড ২

দ্বিতীয় দফা রিভিউয়ে আরও **৪টি সমস্যা** পাওয়া গেছে, যার একটি **crash-level**।

| # | সমস্যা | প্রভাব | সমাধান |
|---|---|---|---|
| 15 | 🔴 **`write_dashboard()` ভুল index ধরে নিত** — `dash` সারি ছিল `[stamp, cat, platform, rank, title, score, ...]` কিন্তু কোড `r[4]` কে score ভাবত (আসলে title) আর `r[10]` পড়ত যেখানে সারিতে মাত্র ১০টি ঘর | `isinstance(r[4], float)` সবসময় False → **DASHBOARD চিরকাল খালি**; আর `r[10]` → **IndexError crash** | index-juggling সম্পূর্ণ বাদ, এখন **dict** (`r["score"]`, `r["topic"]`) ব্যবহার হয়। রিগ্রেশন টেস্ট যোগ করা হয়েছে |
| 16 | 🟠 **`detect_intent` regex-এ suffix মিসিং** — `unveil` লেখা ছিল, `unveils` মিলত না | "Apple unveils M5 chip" → News না হয়ে Informational | `unveil[sd]?`, `launch(es\|ed\|ing)?`, `announce[sd]?` ইত্যাদি |
| 17 | 🟠 **ARCHIVE trim ভুল কাউন্ট** — `ws.row_count` হলো গ্রিডের সাইজ, ব্যবহৃত সারি নয় | ট্রিম হয় খুব তাড়াতাড়ি নয়তো কখনোই না | `len(ws.col_values(1))` — আসল ব্যবহৃত সারি |
| 18 | 🟡 ফরম্যাটিং কোড ৩ জায়গায় ডুপ্লিকেট | মেইনটেন্যান্স ঝুঁকি | একটি `_fmt()` হেল্পারে একত্র |

**টেস্ট:** ২৩ → **২৭টি** (নতুন: intent detection, competition proxy, fallback brief completeness, dashboard-dict রিগ্রেশন)

---

# ✍️ নতুন: CONTENT KIT — টপিক থেকে সরাসরি কনটেন্ট

তুমি চেয়েছিলে *"যাচাই করা টপিক যার উপর কোয়ালিটি আর্টিকেল ও শর্ট ভিডিও বানাতে পারি"*। সেটার জন্য পুরো নতুন লেয়ার:

### 🎯 Opportunity Score — "কোনটা আগে লিখব?"
শুধু ডিমান্ড দেখলে ভুল হয় — বড় কীওয়ার্ডে ট্রাফিক বেশি কিন্তু র‍্যাঙ্ক করা অসম্ভব। তাই:

```
Opportunity = (Demand × 0.65) + ((100 − Competition) × 0.35)
```
- **Demand** = ৭টি ফ্রি সিগন্যালের স্কোর
- **Competition** = ফ্রি প্রক্সি (কীওয়ার্ড দৈর্ঘ্য + Wikipedia totalhits) — Ahrefs KD-র বিকল্প
- লং-টেইল টপিক (কম কম্পিটিশন) স্বাভাবিকভাবেই উপরে ওঠে — নতুন সাইটের জন্য এটাই সঠিক

### 📋 প্রতিটি টপিকের জন্য যা তৈরি হয়
| ফিল্ড | কীভাবে |
|---|---|
| **Search Intent** | How-to / Commercial / News / Explainer — regex রুল |
| **People Also Ask** | Google Suggest "alphabet soup" (১৩টি সাফিক্স দিয়ে সম্প্রসারণ) — আসল প্রশ্ন যা মানুষ লিখছে |
| **৩টি SEO Title** (55-65 chars) | Gemini/Groq ফ্রি LLM |
| **Meta description** | ≤155 chars |
| **৬টি target keyword** | primary প্রথমে |
| **Article outline** | ৫-৭টি H2 সেকশন |
| **FAQ** | ৪টি প্রশ্ন যার উত্তর আর্টিকেলে থাকতেই হবে |
| **🎬 Video Hook** | প্রথম ৩ সেকেন্ড — scroll থামানোর লাইন |
| **🎬 Script beats** | ৪-৫টি লাইন, <৪৫ সেকেন্ড (Shorts/Reels-এর মাপে) |
| **Caption + ৬টি Hashtag** | Facebook / YouTube Shorts-এর জন্য রেডি |

> LLM key না দিলেও **হিউরিস্টিক fallback** কাজ করে — outline, FAQ ও ভিডিও beats তৈরি হয়, শুধু কম পালিশড।

### 📄 আউটপুট ৩ জায়গায়
1. **CONTENT_PLAN ট্যাব** — ২০ কলাম, Opportunity-সর্টেড, `Status` ড্রপডাউন (To Do / Writing / Published / Video Done / Skip)
2. **REPORT.md** — repo-তে কমিট হয়, ফোন থেকেও পড়া যায়
3. **data/YYYY-MM-DD.json** — প্রোগ্রাম্যাটিক ব্যবহারের জন্য

---

# 📗 নতুন: Apps Script সাইড-টুল (`apps-script/Code.gs`)

শিটের ভিতরেই কাজ করার জন্য (ফ্রি, কোনো key লাগে না):
- **🔥 Trend Engine মেনু**
- **📋 ব্রিফ কপি করো** — সারি সিলেক্ট করে এক ক্লিকে পুরো আর্টিকেল ব্রিফ পপআপে
- **🎬 ভিডিও স্ক্রিপ্ট** — hook / beats / caption / hashtags আলাদা কার্ডে
- **✅ Published / 🎥 Video Done** — একসাথে অনেক সারি মার্ক করা
- **📧 রোজ দুপুর ২টায় ইমেইল ডাইজেস্ট** — টপ ১০ টপিক তোমার Gmail-এ (MailApp, ফ্রি)
- **📊 সারাংশ** — কোন ক্যাটাগরিতে কয়টা, কয়টা নতুন
