# 🔗 আমাকে GitHub-এ কানেক্ট করার নিয়ম

টেকনিক্যালি যাচাই করে দেখেছি — আমার স্যান্ডবক্স থেকে `api.github.com` ও `github.com`
দুটোতেই পৌঁছানো যায় (HTTP 200) এবং git ইনস্টল করা আছে।
তাই **একটা Personal Access Token দিলেই** আমি তোমার repo তৈরি করে সব ফাইল push করে দিতে পারব।

---

## ✅ পদ্ধতি — Fine-grained Token (সবচেয়ে নিরাপদ, এটাই করো)

এই টোকেন **শুধু একটা repo**-তে কাজ করবে, তোমার বাকি সব কিছু সম্পূর্ণ সুরক্ষিত থাকবে।

### ধাপ ১ — খালি repo বানাও
[github.com/new](https://github.com/new)
- **Repository name:** `trend-engine`
- **Public** সিলেক্ট করো *(Actions মিনিট আনলিমিটেড ফ্রি হয়)*
- ⚠️ README / .gitignore / license **কিছুই টিক দিও না** — সম্পূর্ণ খালি চাই
- **Create repository**

### ধাপ ২ — টোকেন বানাও
[github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)

| ফিল্ড | যা দেবে |
|---|---|
| **Token name** | `trend-engine-setup` |
| **Expiration** | **7 days** (কম সময় = বেশি নিরাপদ) |
| **Repository access** | ⦿ **Only select repositories** → `trend-engine` বেছে নাও |
| **Permissions → Repository permissions** | নিচের ঠিক ৩টি: |

| Permission | সেট করো |
|---|---|
| **Contents** | **Read and write** ← ফাইল push করার জন্য |
| **Workflows** | **Read and write** ← `.github/workflows/` ফাইলের জন্য |
| **Metadata** | Read-only *(অটো সিলেক্ট হয়ে যাবে)* |

> বাকি সব **No access** রাখো। Secrets permission **দরকার নেই** — তুমি নিজেই secret বসাবে।

**Generate token** → টোকেনটা কপি করো (`github_pat_...` দিয়ে শুরু)

### ধাপ ৩ — আমাকে পাঠাও
চ্যাটে শুধু এই ৩টি জিনিস লিখো:

```
টোকেন: github_pat_xxxxxxxxxxxxxxxxxxxx
ইউজারনেম: তোমার-github-ইউজারনেম
repo: trend-engine
```

আমি সাথে সাথে সব ২৭টি ফাইল push করে দেব এবং কনফার্ম করব।

### ধাপ ৪ — কাজ শেষে টোকেন বাতিল করো 🔐
[github.com/settings/personal-access-tokens](https://github.com/settings/personal-access-tokens) → **Revoke**
*(অথবা ৭ দিন পর নিজেই মেয়াদ শেষ হয়ে যাবে)*

---

## ⚠️ নিরাপত্তা — যা তোমার জানা দরকার

সৎভাবে বলছি, যাতে জেনেবুঝে সিদ্ধান্ত নিতে পারো:

| বিষয় | বাস্তবতা |
|---|---|
| টোকেনটা চ্যাট হিস্ট্রিতে থেকে যাবে | তাই **৭ দিনের মেয়াদ** ও **কাজের পর revoke** জরুরি |
| fine-grained টোকেন দিলে ঝুঁকি কতটুকু? | শুধু `trend-engine` repo-র ফাইল — তোমার অন্য repo, প্রোফাইল, সেটিংস কিছুতেই হাত দেওয়া যাবে না |
| classic token দেব? | **দিও না** — ওটা তোমার *সব* repo-তে অ্যাক্সেস দেয়। শুধু fine-grained ব্যবহার করো |
| Google/Gemini key পাঠাব? | **কখনো না।** ওগুলো তুমি নিজে GitHub Secrets-এ বসাবে, আমাকে দেখানোর দরকার নেই |
| `git push` করার পর টোকেন | স্ক্রিপ্ট নিজেই remote URL থেকে টোকেন মুছে দেয় |

---

## 🅱️ বিকল্প — টোকেন না দিয়েও করা যায়

টোকেন শেয়ার করতে না চাইলে এই দুটোর যেকোনো একটা:

**বিকল্প ১ — ওয়েব থেকে আপলোড (সবচেয়ে সহজ, টার্মিনাল লাগে না)**
1. `trend-engine.zip` ডাউনলোড করে আনজিপ করো
2. খালি repo-তে যাও → **Add file → Upload files**
3. সব ফাইল ড্র্যাগ করে ছাড়ো → **Commit changes**
4. ⚠️ `.github` ফোল্ডারটা যেন বাদ না পড়ে — লুকানো ফোল্ডার, আলাদা করে টেনে আনতে হতে পারে

**বিকল্প ২ — নিজের কম্পিউটার থেকে এক কমান্ড**
```bash
bash push-to-github.sh https://github.com/USERNAME/trend-engine.git
```
(পাসওয়ার্ডের জায়গায় টোকেন দিতে হবে — কিন্তু সেটা তোমার মেশিনেই থাকবে, আমার কাছে আসবে না)

---

## 📦 push হওয়ার পর কী পাবে

```
trend-engine/
├── .github/workflows/daily-trends.yml   রোজ ১টায় অটো রান
├── .github/workflows/ci.yml             টেস্ট + লিন্ট
├── src/                                 ৯টি মডিউল
├── tests/                               ২৭টি টেস্ট
├── apps-script/Code.gs                  ← Google Sheet-এ paste করবে
├── SETUP.md                             ধাপে ধাপে গাইড
├── AUDIT.md                             ১৮টি বাগ ফিক্সের রিপোর্ট
└── README.md
```

**তোমার বাকি থাকবে মাত্র ২টি কাজ:**
1. Repo → Settings → Secrets → Actions → ৪টি secret বসানো *(SETUP.md ধাপ ৪)*
2. `apps-script/Code.gs` → Google Sheet → Extensions → Apps Script-এ paste *(SETUP.md ধাপ ৫)*
