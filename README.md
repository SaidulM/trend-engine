# 🔥 Daily Trend Engine

**US-এর মোস্ট ট্রেন্ডিং + মোস্ট সার্চেবল টপিক — ক্যাটাগরি ও প্ল্যাটফর্ম অনুযায়ী, রোজ দুপুর ১টায় তোমার Google Sheet-এ।**
১০০% ফ্রি · কোনো ক্রেডিট কার্ড নয় · কোনো ট্রায়াল নয় · সব ওপেন/পাবলিক API।

> 🔍 আগের ভার্সনের **১৪টি টেকনিক্যাল বাগ** খুঁজে ফিক্স করা হয়েছে — বিস্তারিত **[AUDIT.md](AUDIT.md)**-এ।

---

## 📊 আউটপুট

**৮টি ট্যাব:** `DASHBOARD` · Tech · Health · News · Islamic · Image_Emoji · Business · `ARCHIVE`

প্রতি ক্যাটাগরি ট্যাবে **৬ প্ল্যাটফর্ম × ৫ টপিক = ৩০ সারি**:

| Date/Time | Platform | # | Trending Topic | Score | AI Check | New? | Source Info | Link |
|---|---|---|---|---|---|---|---|---|
| 2026-09-24 13:00 | Bing Search | 1 | What is Eid al-Fitr? Ramadan is over... | **66.0** | AI-verified ✓ | 🆕 | Bing News • GT:42 | 🔗 |
| 2026-09-24 13:00 | Quora | 1 | Where can I find an English translation of the Quran... | **56.0** | AI-verified ✓ | 🆕 | Quora question demand | 🔗 |

**DASHBOARD** = সব ক্যাটাগরির টপ ৬০ টপিক, স্কোর অনুযায়ী সাজানো। আর্টিকেল লেখার জন্য এখান থেকেই শুরু করো।
Score কলামে **heat-map** — 🟩 সবুজ = বেশি সার্চেবল, 🟥 লাল = দুর্বল।

---

## 🧠 "মোস্ট সার্চেবল" কীভাবে মাপা হয় (Ahrefs ছাড়া)

Ahrefs/Semrush-এর ফ্রি API নেই (সব কার্ড চায়)। তাই **৭টি ফ্রি সিগন্যাল** মিলিয়ে ০–১০০ স্কোর:

| সিগন্যাল | সোর্স | ওজন | কী বোঝায় |
|---|---|---|---|
| Google Autocomplete depth | suggestqueries.google.com | ২৮ | মানুষ আসলে কী টাইপ করছে (real volume proxy) |
| Google Trends interest | pytrends (0–100, US, 7d) | ২৫ | গতি বাড়ছে কি না |
| Reddit upvotes + comments | Reddit public JSON | ২৫ | কমিউনিটি এনগেজমেন্ট |
| YouTube viewCount | YouTube Data API | ২৫ | ভিডিও ডিমান্ড |
| Wikipedia pageviews (7d) | Wikimedia REST | ১৮ | এন্টিটি কতটা আলোচিত |
| Keyword density + recency | offline | ২২ | ক্যাটাগরি ফিট + "2026/launch/leak" |
| Bing + DuckDuckGo suggest | osjson / ddg ac | — | দ্বিতীয়-তৃতীয় ইঞ্জিনের ডিমান্ড |

তারপর **AI (Gemini/Groq/OpenAI)** চূড়ান্ত বাছাই করে — "এটা কি সত্যিই আর্টিকেল লেখার যোগ্য ট্রেন্ডিং টপিক?"

### ৩-স্তরের ফিল্টার (ফালতু জিনিস আটকায়)
```
Stage A (offline)  relevance gate → quality gate → dedupe → diversify → top 8
Stage B (network)  autocomplete + wikipedia + google trends  [parallel]
Stage C (AI)       Gemini/Groq চূড়ান্ত র‍্যাঙ্কিং
```
- **Relevance gate** — ক্যাটাগরির ৪০–৬০টি must-have কীওয়ার্ডে ম্যাচ না করলে সরাসরি বাদ
- **Quality gate** — clickbait, megathread, `[deleted]`, ইমোজি-স্প্যাম, খুব ছোট/বড় বাদ
- **Dedupe** — ৭২% মিল থাকলে বাদ, প্ল্যাটফর্মের মধ্যেও ও মধ্যেও
- **History** — গত **৫ দিনে** দেখানো টপিক আবার আসবে না (`state/seen.json`)

---

## 🚀 সেটআপ (একবার, ~১৫ মিনিট)

### ধাপ ১ — Google Sheet + Service Account
1. নতুন Google Sheet খোলো। URL থেকে **SHEET_ID** কপি করো:
   `docs.google.com/spreadsheets/d/`**`এই লম্বা অংশ`**`/edit`
2. [console.cloud.google.com](https://console.cloud.google.com) → নতুন প্রজেক্ট (ফ্রি, কার্ড লাগে না)
3. **APIs & Services → Library** → `Google Sheets API` → **Enable**
4. **Credentials → Create Credentials → Service Account** → নাম দাও → Create
5. সেই account → **Keys → Add Key → Create new key → JSON** → ডাউনলোড
6. ⚠️ **সবচেয়ে গুরুত্বপূর্ণ:** JSON-এর ভেতরের `client_email` (যেমন `bot@xyz.iam.gserviceaccount.com`) কপি করে **তোমার Sheet-এ Share → Editor** দাও। এটা বাদ গেলে কিছুই কাজ করবে না।

### ধাপ ২ — GitHub repo
```bash
git init && git add -A && git commit -m "trend engine"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```
> 💡 repo **public** রাখলে GitHub Actions মিনিট **আনলিমিটেড ফ্রি**। private হলে ২,০০০ মিনিট/মাস (আমাদের লাগে ~৫৪০)।

### ধাপ ৩ — Secrets
**Settings → Secrets and variables → Actions → New repository secret**

| Secret | মান | দরকার? |
|---|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | ডাউনলোড করা JSON ফাইলের **পুরো কনটেন্ট** | ✅ বাধ্যতামূলক |
| `SHEET_ID` | শিটের ID | ✅ বাধ্যতামূলক |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/apikey) — ফ্রি, কার্ড লাগে না | ⭐ জোরালো সুপারিশ |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — Gemini-র ফ্রি বিকল্প | ঐচ্ছিক |
| `YOUTUBE_API_KEY` | YouTube Data API v3 (ফ্রি ১০k ইউনিট/দিন) | ঐচ্ছিক, সুপারিশ |
| `OPENAI_API_KEY` | চাইলে | ঐচ্ছিক |

### ধাপ ৪ — Settings → Actions → General
**Workflow permissions** → ✅ *Read and write permissions* (state কমিট করার জন্য)

### ধাপ ৫ — চালাও
**Actions → Daily Trend Tracker → Run workflow**
এরপর থেকে রোজ **দুপুর ১টা IST** অটো।

> সময় বদলাতে `daily-trends.yml`-এ `cron: "30 7 * * *"` (UTC)। US Eastern দুপুর ১টা = `"0 17 * * *"`।

---

## 🧪 লোকাল টেস্ট
```bash
make install
make test                 # ২৩টি টেস্ট
make one CAT=Tech         # শিটে না লিখে শুধু Tech দেখাও
make dry                  # সব ক্যাটাগরি, শিটে লেখা ছাড়া
```

## ⚙️ টিউনিং — `src/config.py`
| ভ্যারিয়েবল | ডিফল্ট | কাজ |
|---|---|---|
| `MIN_SCORE` | 25 | আরও কড়া চাইলে 35–40 |
| `TOPICS_PER_PLATFORM` | 5 | প্রতি প্ল্যাটফর্মে কয়টা |
| `REPEAT_BLOCK_DAYS` (env) | 5 | কত দিন একই টপিক ব্লক |
| `SHORTLIST` (env) | 8 | বেশি = ভালো কোয়ালিটি, ধীর |

প্রতি ক্যাটাগরিতে এডিট করতে পারো: `must_any` (থাকতেই হবে), `never` (থাকলে বাদ), `seeds`, `subreddits`, `news_queries`, `yt_queries`, `quora_queries`, `extra_rss`।
**নতুন ক্যাটাগরি** = `CATEGORIES`-এ একটা ব্লক কপি করে বসাও → ট্যাব আপনা-আপনি তৈরি হবে।

---

## 📁 স্ট্রাকচার
```
.github/workflows/daily-trends.yml   রোজ ১টায় রান + state কমিট + failure issue
.github/workflows/ci.yml             প্রতি push-এ ruff + pytest
src/config.py     ৬ ক্যাটাগরির সোর্স ও কীওয়ার্ড রুল
src/http.py       retry · throttle · cache · UA rotation
src/sources.py    ৬ প্ল্যাটফর্মের সমান্তরাল কালেক্টর
src/verifier.py   3-stage gate + scoring + AI rerank
src/state.py      repo-persisted history (ফ্রি ডেটাবেস)
src/sheets.py     Sheets রাইটার + DASHBOARD + heat-map
src/main.py       অর্কেস্ট্রেটর
tests/            ২৩টি রিগ্রেশন টেস্ট
state/seen.json   গত দিনগুলোর টপিক (অটো কমিট)
data/YYYY-MM-DD.json  দৈনিক স্ন্যাপশট (৬০ দিন)
```

## 🆘 সমস্যা হলে
| লক্ষণ | কারণ |
|---|---|
| `❌ শিটে অ্যাক্সেস নেই` | ধাপ ১.৬ — service account email-কে Editor করোনি |
| `nothing to push` | স্বাভাবিক, state বদলায়নি |
| অনেক `(no qualifying topic today)` | সোর্স রেট-লিমিটেড — পরের রানে ঠিক হয়ে যায়; `MIN_SCORE` কমাতে পারো |
| AI Check-এ `scored` | LLM key দাওনি — স্কোরিং তবু কাজ করছে |
| pytrends disabled লগে | Google Actions IP ব্লক করেছে; বাকি ৬টা সিগন্যাল চালু থাকে |
