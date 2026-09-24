#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════
#  এক কমান্ডে তোমার GitHub-এ সব ফাইল আপলোড
#  ব্যবহার:  bash push-to-github.sh https://github.com/USERNAME/REPO.git
# ════════════════════════════════════════════════════════════
set -e
REMOTE="${1:-}"
if [ -z "$REMOTE" ]; then
  echo "❌ repo URL দাও:"
  echo "   bash push-to-github.sh https://github.com/USERNAME/REPO.git"
  exit 1
fi
command -v git >/dev/null || { echo "❌ git ইনস্টল করা নেই"; exit 1; }

git init -q 2>/dev/null || true
git config user.name  "$(git config user.name  || echo trend-bot)"
git config user.email "$(git config user.email || echo bot@example.com)"
git add -A
git commit -q -m "feat: daily trend engine — collectors, scoring, AI verify, content kit" || echo "ℹ️  কমিট করার নতুন কিছু নেই"
git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"

echo ""
echo "🚀 push করা হচ্ছে → $REMOTE"
echo "   Username = তোমার GitHub ইউজারনেম"
echo "   Password = Personal Access Token (পাসওয়ার্ড নয়!)"
echo "   টোকেন বানাও: github.com/settings/tokens  → scope: repo, workflow"
echo ""
git push -u origin main

cat <<'DONE'

✅ আপলোড সম্পূর্ণ! এখন বাকি ৩টি কাজ:

  1️⃣  Settings → Secrets and variables → Actions → New repository secret
        GOOGLE_SERVICE_ACCOUNT_JSON   (JSON ফাইলের পুরো কনটেন্ট)
        SHEET_ID                      (শিটের URL থেকে)
        GEMINI_API_KEY                (aistudio.google.com/apikey — ফ্রি)
        YOUTUBE_API_KEY               (ঐচ্ছিক)

  2️⃣  Settings → Actions → General → Workflow permissions
        ✅ Read and write permissions

  3️⃣  Actions → Daily Trend Tracker → Run workflow  (প্রথম টেস্ট)

  📄 শিটের ভিতরের অংশ: apps-script/Code.gs → Extensions → Apps Script-এ paste করে setupAll চালাও
DONE
