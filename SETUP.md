# 🚀 সেটআপ গাইড — ধাপে ধাপে (মোট ~২০ মিনিট)

> ⚠️ **আগে জেনে নাও:** আমার কাছে তোমার GitHub-এর অ্যাক্সেস নেই, তাই আমি নিজে push করতে পারিনি।
> সব ফাইল তৈরি ও **git-এ কমিট করা অবস্থায়** রেডি — তুমি শুধু একটা কমান্ড চালাবে (ধাপ ৩)।

---

## ধাপ ১ — Google Sheet + Service Account (৮ মিনিট)

1. নতুন Google Sheet খোলো → নাম দাও *Trend Engine*
2. URL থেকে **SHEET_ID** কপি করো:
   `docs.google.com/spreadsheets/d/`**`↞ এই লম্বা অংশটা ↠`**`/edit`
3. [console.cloud.google.com](https://console.cloud.google.com) → **নতুন প্রজেক্ট** (ফ্রি, কার্ড লাগে না)
4. **APIs & Services → Library** → `Google Sheets API` খুঁজে **Enable**
5. **Credentials → Create Credentials → Service Account** → নাম দাও → **Create and Continue → Done**
6. তালিকা থেকে সেই account-এ ক্লিক → **Keys → Add Key → Create new key → JSON → Create**
   → একটা `.json` ফাইল ডাউনলোড হবে। এটা হারিও না।
7. 🔴 **সবচেয়ে গুরুত্বপূর্ণ ধাপ:** JSON ফাইলটা খুলে `client_email` এর মানটা কপি করো
   (দেখতে এমন: `trend-bot@my-project.iam.gserviceaccount.com`)
   → তোমার **Google Sheet → Share → এই ইমেইল paste করো → Editor → Send**

   > এই ধাপ বাদ গেলে স্ক্রিপ্ট চলবে কিন্তু শিটে লিখতে পারবে না।
   > ভুল হলে এখন পরিষ্কার বাংলা এরর দেখাবে।

---

## ধাপ ২ — ফ্রি API key (৪ মিনিট)

| Key | কোথা থেকে | লাগবে? |
|---|---|---|
| **GEMINI_API_KEY** | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) → *Create API key* | ⭐ দরকারি — AI ভেরিফিকেশন ও কনটেন্ট ব্রিফ এটা দিয়েই হয় |
| **YOUTUBE_API_KEY** | একই Cloud প্রজেক্টে `YouTube Data API v3` **Enable** → Credentials → API key | সুপারিশ |
| **GROQ_API_KEY** | [console.groq.com](https://console.groq.com) | ঐচ্ছিক (Gemini-র ব্যাকআপ) |

সবগুলোই ফ্রি টিয়ার, **ক্রেডিট কার্ড চায় না**।

---

## ধাপ ৩ — GitHub-এ আপলোড (৩ মিনিট)

**৩ক.** [github.com/new](https://github.com/new) → repo নাম দাও (যেমন `trend-engine`)
→ **Public** রাখলে Actions মিনিট আনলিমিটেড ফ্রি → **Create repository**
→ ⚠️ README/gitignore কিছু **অ্যাড করো না** (খালি repo চাই)

**৩খ.** [github.com/settings/tokens](https://github.com/settings/tokens) → *Generate new token (classic)*
→ scope টিক দাও: **`repo`** এবং **`workflow`** → Generate → টোকেন কপি করো

**৩গ.** টার্মিনালে (ফোল্ডারটা ডাউনলোড করে নিয়ে):
```bash
bash push-to-github.sh https://github.com/তোমার-ইউজারনেম/trend-engine.git
```
Username = তোমার GitHub ইউজারনেম · **Password = উপরের টোকেন** (আসল পাসওয়ার্ড নয়)

---

## ধাপ ৪ — Secrets বসাও (৩ মিনিট)

Repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret নাম | মান |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | ধাপ ১.৬-এর JSON ফাইলের **পুরো কনটেন্ট** (`{` থেকে `}` পর্যন্ত সব) |
| `SHEET_ID` | ধাপ ১.২-এর ID |
| `GEMINI_API_KEY` | ধাপ ২ |
| `YOUTUBE_API_KEY` | ধাপ ২ (ঐচ্ছিক) |

তারপর **Settings → Actions → General → Workflow permissions**
→ ✅ **Read and write permissions** সিলেক্ট করে **Save**

---

## ধাপ ৫ — Apps Script বসাও (২ মিনিট)

1. Google Sheet → **Extensions → Apps Script**
2. ডিফল্ট কোড মুছে `apps-script/Code.gs` ফাইলের পুরো কোড paste করো → **Save 💾**
3. উপরের ড্রপডাউনে **`setupAll`** সিলেক্ট করে **▶ Run**
   → permission চাইবে → *Advanced → Go to project (unsafe) → Allow*
4. Sheet রিলোড করো → উপরে **🔥 Trend Engine** মেনু দেখা যাবে

---

## ধাপ ৬ — প্রথম রান ✅

Repo → **Actions → Daily Trend Tracker → Run workflow → Run workflow**

~১৫-২০ মিনিট পর তোমার শিটে থাকবে:

```
DASHBOARD      টপ ৬০ ট্রেন্ডিং টপিক, স্কোর-সর্টেড, heat-map সহ
CONTENT_PLAN   ১৫টি সম্পূর্ণ ব্রিফ — title, outline, FAQ, ভিডিও স্ক্রিপ্ট, hashtags
Tech           ৬ প্ল্যাটফর্ম × ৫ টপিক
Health         ৬ প্ল্যাটফর্ম × ৫ টপিক
News           ৬ প্ল্যাটফর্ম × ৫ টপিক
Islamic        ৬ প্ল্যাটফর্ম × ৫ টপিক
Image_Emoji    ৬ প্ল্যাটফর্ম × ৫ টপিক
Business       ৬ প্ল্যাটফর্ম × ৫ টপিক
ARCHIVE        সব ইতিহাস
```

এরপর থেকে **রোজ দুপুর ১টা (IST)** অটো চলবে, আর **দুপুর ২টায়** টপ ১০ টপিক তোমার Gmail-এ ইমেইল আসবে।

---

## 📅 তোমার দৈনন্দিন রুটিন

1. দুপুর ২টায় ইমেইল খুলে টপ ১০ দেখো
2. শিটের **CONTENT_PLAN** ট্যাবে যাও (Opportunity অনুযায়ী সাজানো — উপরেরটাই সবচেয়ে সহজে র‍্যাঙ্ক করবে)
3. একটা সারি সিলেক্ট করে **🔥 Trend Engine → 📋 ব্রিফ কপি করো** → আর্টিকেল লেখো
4. **🎬 ভিডিও স্ক্রিপ্ট** → hook + beats + caption + hashtags নিয়ে Shorts/Reels বানাও
5. হয়ে গেলে **✅ Published** / **🎥 Video Done** মার্ক করো

---

## 🆘 সমস্যা হলে

| লক্ষণ | সমাধান |
|---|---|
| `❌ শিটে অ্যাক্সেস নেই` | ধাপ ১.৭ করোনি — service account email-কে Editor করো |
| `Permission denied (push)` | পাসওয়ার্ডের জায়গায় **টোকেন** দাও, `repo`+`workflow` scope সহ |
| Actions-এ `nothing to push` | স্বাভাবিক — state বদলায়নি |
| AI Check কলামে `scored` | `GEMINI_API_KEY` দাওনি — স্কোরিং তবু চলছে |
| অনেক `(no qualifying topic)` | সোর্স রেট-লিমিটেড, পরের রানে ঠিক হয়; বা `MIN_SCORE` কমাও |
| ব্রিফগুলো generic লাগছে | LLM key নেই — Gemini key দিলে অনেক ভালো হবে |
| `pytrends disabled` লগে | Google Actions IP ব্লক করেছে; বাকি ৬টা সিগন্যাল চালু |
