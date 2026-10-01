# 🔑 Secrets — কী কী বসাতে হবে এবং কীভাবে

## মোট ৪টি (২টি বাধ্যতামূলক, ২টি ঐচ্ছিক)

| # | Secret নাম (হুবহু এই বানান) | বাধ্যতামূলক? | কী বসাবে |
|---|---|---|---|
| 1 | `GOOGLE_SERVICE_ACCOUNT_JSON` | ✅ **হ্যাঁ** | JSON ফাইলের পুরো কনটেন্ট |
| 2 | `SHEET_ID` | ✅ **হ্যাঁ** | Google Sheet-এর URL থেকে ID |
| 3 | `GEMINI_API_KEY` | ⭐ জোরালো সুপারিশ | AI Studio-র ফ্রি key |
| 4 | `YOUTUBE_API_KEY` | ঐচ্ছিক | YouTube Data API key |

> ⚠️ নামগুলো **ঠিক এভাবেই** লিখতে হবে — সব বড় হাতের অক্ষর, মাঝে আন্ডারস্কোর `_`।
> একটা অক্ষর এদিক-ওদিক হলে workflow খুঁজে পাবে না।

---

## 📍 কোথায় বসাবে

👉 **[github.com/SaidulM/trend-engine/settings/secrets/actions](https://github.com/SaidulM/trend-engine/settings/secrets/actions)**

অথবা হাতে: তোমার repo → **Settings** → বাঁ পাশে **Secrets and variables** → **Actions** → সবুজ বোতাম **New repository secret**

প্রতিবার: **Name** ঘরে নাম, **Secret** ঘরে মান → **Add secret** → আবার New repository secret

---

# ১️⃣ `GOOGLE_SERVICE_ACCOUNT_JSON`

### মান কোথায় পাবে
1. [console.cloud.google.com](https://console.cloud.google.com) → উপরে **নতুন প্রজেক্ট** বানাও (ফ্রি, কার্ড লাগে না)
2. **APIs & Services → Library** → `Google Sheets API` লিখে খোঁজো → **Enable**
3. **APIs & Services → Credentials** → **+ Create Credentials** → **Service account**
   - নাম: `trend-bot` → **Create and Continue** → **Done**
4. তালিকা থেকে `trend-bot`-এ ক্লিক → উপরে **KEYS** ট্যাব → **Add Key → Create new key**
   - টাইপ: **JSON** → **Create** → একটা `.json` ফাইল ডাউনলোড হবে
5. ফাইলটা **Notepad / TextEdit** দিয়ে খোলো

### কী বসাবে
ফাইলের **পুরো লেখাটা** — `{` থেকে শুরু করে শেষ `}` পর্যন্ত সবকিছু কপি করে paste করো।

দেখতে এরকম হবে:
```json
{
  "type": "service_account",
  "project_id": "my-project-123",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQ...\n-----END PRIVATE KEY-----\n",
  "client_email": "trend-bot@my-project-123.iam.gserviceaccount.com",
  "client_id": "1234567890",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

❌ **যা করবে না:** ফাইলের নাম লিখবে না, অংশবিশেষ দেবে না, `{` `}` বাদ দেবে না।

### 🔴 এরপরেই সবচেয়ে জরুরি কাজ
ওই JSON-এর ভিতরে `"client_email"` লাইনটা খুঁজে বের করো, যেমন:
```
trend-bot@my-project-123.iam.gserviceaccount.com
```
এই ইমেইলটা কপি করে → তোমার **Google Sheet খোলো → ডান পাশে Share বোতাম → ইমেইলটা paste করো → ড্রপডাউনে Editor বেছে নাও → Send**

> এই ধাপ না করলে সব secret ঠিক থাকলেও শিটে কিছু লেখা হবে না।
> (তখন এরর আসবে: *"❌ শিটে অ্যাক্সেস নেই"*)

---

# ২️⃣ `SHEET_ID`

তোমার Google Sheet-এর URL দেখো:

```
https://docs.google.com/spreadsheets/d/1a2B3cD4eFgHiJkLmNoPqRsTuVwXyZ_123456789/edit#gid=0
                                      └──────────── এই অংশটুকু ────────────┘
```

`/d/` আর `/edit`-এর **মাঝের লম্বা অংশটাই** `SHEET_ID`।

**উদাহরণ মান:** `1a2B3cD4eFgHiJkLmNoPqRsTuVwXyZ_123456789`

❌ পুরো URL দেবে না, শুধু ওই আইডিটুকু।

---

# ৩️⃣ `GEMINI_API_KEY` ⭐

এটা না দিলেও সিস্টেম চলবে, কিন্তু **কনটেন্ট ব্রিফ ও ভিডিও স্ক্রিপ্টগুলো সাদামাটা হবে**।
দিলে AI টপিক যাচাই করবে আর অনেক ভালো মানের ব্রিফ বানাবে। সম্পূর্ণ ফ্রি, কার্ড লাগে না।

1. [aistudio.google.com/apikey](https://aistudio.google.com/apikey) খোলো
2. **Create API key** → প্রজেক্ট বেছে নাও → key কপি করো

**মান দেখতে:** `AIzaSyB...` (৩৯ অক্ষরের মতো)

---

# ৪️⃣ `YOUTUBE_API_KEY` (ঐচ্ছিক)

দিলে YouTube-এর **আসল ভিউ-কাউন্ট সহ ট্রেন্ডিং ভিডিও** আসবে। না দিলে সার্চ-ডিমান্ড দিয়ে কাজ চলবে।

১ নম্বরে যে Cloud প্রজেক্ট বানিয়েছ, সেখানেই:
1. **APIs & Services → Library** → `YouTube Data API v3` → **Enable**
2. **Credentials → + Create Credentials → API key** → কপি করো

**মান দেখতে:** `AIzaSy...`

---

## ⚙️ শেষ ধাপ — পারমিশন চালু করো

👉 **[Settings → Actions → General](https://github.com/SaidulM/trend-engine/settings/actions)**

একদম নিচে **Workflow permissions** অংশে:
- ⦿ **Read and write permissions** সিলেক্ট করো
- **Save** চাপো

*(এটা দরকার কারণ বট রোজ `state/` ও `data/` ফোল্ডারে ডেটা সেভ করে।)*

---

## ▶️ এবার চালিয়ে দেখো

👉 **[Actions → Daily Trend Tracker](https://github.com/SaidulM/trend-engine/actions/workflows/daily-trends.yml)** → ডান পাশে **Run workflow** → আবার **Run workflow**

- ভুল থাকলে **১ সেকেন্ডেই** থেমে গিয়ে Summary-তে বাংলায় কী ভুল তা দেখাবে
- সব ঠিক থাকলে **১৫–২০ মিনিট** চলবে, তারপর শিটে ৯টি ট্যাব তৈরি হবে
- সফল হলে আগের ৫টি failure issue **নিজে থেকেই বন্ধ** হয়ে যাবে

---

## ✅ চেকলিস্ট

- [ ] `GOOGLE_SERVICE_ACCOUNT_JSON` বসানো (পুরো JSON)
- [ ] `SHEET_ID` বসানো (শুধু আইডি)
- [ ] `GEMINI_API_KEY` বসানো
- [ ] `YOUTUBE_API_KEY` বসানো (ঐচ্ছিক)
- [ ] 🔴 service account-এর `client_email` শিটে **Editor** হিসেবে Share করা
- [ ] Workflow permissions = **Read and write**
- [ ] `apps-script/Code.gs` → Google Sheet → Extensions → Apps Script-এ paste + `setupAll` রান
- [ ] GitHub টোকেনটা **revoke** করা ([লিংক](https://github.com/settings/personal-access-tokens))

---

## 🆘 এরর এলে

| এরর | মানে | সমাধান |
|---|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON secret সেট করা নেই` | নাম ভুল বা বসানো হয়নি | বানান মিলিয়ে দেখো |
| `বৈধ JSON নয়` | অংশবিশেষ paste হয়েছে | `{` থেকে `}` পুরোটা দাও |
| `শিটে অ্যাক্সেস নেই` | Share করোনি | `client_email`-কে Editor করো |
| `AI Check` কলামে `scored` | Gemini key নেই | `GEMINI_API_KEY` বসাও |
| Permission denied (push) in Actions | Workflow permission | Read and write করো |
