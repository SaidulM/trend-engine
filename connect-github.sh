#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════
#  GitHub-এ সব ফাইল আপলোড — টোকেন দিয়ে স্বয়ংক্রিয়ভাবে
#  ব্যবহার:  bash connect-github.sh <TOKEN> <USERNAME> <REPO_NAME>
# ══════════════════════════════════════════════════════════════════
set -euo pipefail

TOKEN="${1:?টোকেন দাও}"
USER="${2:?GitHub ইউজারনেম দাও}"
REPO="${3:-trend-engine}"

API="https://api.github.com"
hdr=(-H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json")

echo "▸ টোকেন যাচাই করা হচ্ছে..."
who=$(curl -s "${hdr[@]}" "$API/user" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("login","?"))')
[ "$who" = "?" ] && { echo "❌ টোকেন কাজ করছে না"; exit 1; }
echo "  ✓ লগইন: $who"

echo "▸ repo আছে কি না দেখা হচ্ছে: $USER/$REPO"
code=$(curl -s -o /dev/null -w '%{http_code}' "${hdr[@]}" "$API/repos/$USER/$REPO")
if [ "$code" = "404" ]; then
  echo "  repo নেই — তৈরি করা হচ্ছে..."
  curl -s "${hdr[@]}" -X POST "$API/user/repos" \
    -d "{\"name\":\"$REPO\",\"private\":false,\"description\":\"Daily multi-platform trend engine → Google Sheets\",\"auto_init\":false}" \
    -o /dev/null -w '  HTTP %{http_code}\n'
else
  echo "  ✓ repo পাওয়া গেছে (HTTP $code)"
fi

echo "▸ কমিট ও push..."
cd "$(dirname "$0")"
git init -q 2>/dev/null || true
git config user.name "$USER"
git config user.email "$USER@users.noreply.github.com"
git add -A
git commit -q -m "feat: daily trend engine — collectors, AI verification, content kit" 2>/dev/null || echo "  (নতুন পরিবর্তন নেই)"
git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "https://${USER}:${TOKEN}@github.com/${USER}/${REPO}.git"
git push -u origin main --force
git remote set-url origin "https://github.com/${USER}/${REPO}.git"   # টোকেন মুছে ফেলা

echo ""
echo "✅ আপলোড সম্পূর্ণ → https://github.com/$USER/$REPO"
echo ""
echo "এখন তোমার ২টি কাজ:"
echo "  1. Settings → Secrets → Actions-এ ৪টি secret বসাও"
echo "  2. apps-script/Code.gs → Google Sheet-এ paste করো"
echo ""
echo "🔐 কাজ শেষে টোকেনটা অবশ্যই revoke করো: github.com/settings/tokens"
