/**
 * ═══════════════════════════════════════════════════════════════
 *  TREND ENGINE — Google Sheet সাইড স্ক্রিপ্ট
 *  এটা ডেটা আনে না (সেটা GitHub Actions করে)।
 *  এটা শিটটাকে ব্যবহারযোগ্য ওয়ার্কস্পেস বানায়।
 * ═══════════════════════════════════════════════════════════════
 *  বসানোর নিয়ম:
 *    1. Google Sheet → Extensions → Apps Script
 *    2. এই পুরো কোড paste করে Save (💾)
 *    3. Run ▸ setupAll  একবার চালাও → permission Allow করো
 *    4. Sheet রিলোড করো → উপরে "🔥 Trend Engine" মেনু আসবে
 *
 *  সবকিছু ফ্রি — কোনো API key বা পেইড সার্ভিস লাগে না।
 * ═══════════════════════════════════════════════════════════════
 */

var CATS = ['Tech', 'Health', 'News', 'Islamic', 'Image_Emoji', 'Business'];
var EMAIL_HOUR = 14;   // ডেইলি ইমেইল ডাইজেস্ট পাঠানোর সময় (২টা, ডেটা আসার ১ ঘণ্টা পর)

/* ─────────────────────────── MENU ─────────────────────────── */

function onOpen() {
  SpreadsheetApp.getUi().createMenu('🔥 Trend Engine')
    .addItem('📋 নির্বাচিত টপিকের ব্রিফ কপি করো', 'showBrief')
    .addItem('🎬 নির্বাচিত টপিকের ভিডিও স্ক্রিপ্ট', 'showScript')
    .addSeparator()
    .addItem('✅ Published হিসেবে মার্ক করো', 'markPublished')
    .addItem('🎥 Video Done হিসেবে মার্ক করো', 'markVideo')
    .addSeparator()
    .addItem('📊 আজকের সারাংশ দেখাও', 'showSummary')
    .addItem('📧 এখনই ইমেইল ডাইজেস্ট পাঠাও', 'sendDigest')
    .addSeparator()
    .addItem('⚙️ সব সেটআপ করো (একবার)', 'setupAll')
    .addToUi();
}

function setupAll() {
  applyLooks_();
  installTriggers_();
  SpreadsheetApp.getActive().toast('সেটআপ সম্পূর্ণ ✅  মেনু দেখতে পেজ রিলোড করো।', 'Trend Engine', 8);
}

/* ─────────────────── ব্রিফ / স্ক্রিপ্ট ভিউয়ার ─────────────────── */

function showBrief() {
  var r = planRow_();
  if (!r) return;
  var h = [
    card_('TOPIC', r['Topic']),
    card_('BEST TITLE', r['Best Title']),
    card_('ALT TITLES', r['Alt Titles']),
    card_('INTENT / OPPORTUNITY', r['Intent'] + '  •  Opportunity ' + r['Opportunity'] +
          '  (Demand ' + r['Demand'] + ' / Competition ' + r['Competition'] + ')'),
    card_('META DESCRIPTION', r['Meta Description']),
    card_('TARGET KEYWORDS', r['Target Keywords']),
    card_('ARTICLE OUTLINE', r['Article Outline']),
    card_('FAQ / PEOPLE ALSO ASK', r['FAQ / People Also Ask'])
  ].join('');
  show_(h, '📋 Article Brief');
}

function showScript() {
  var r = planRow_();
  if (!r) return;
  var h = [
    card_('TOPIC', r['Topic']),
    card_('🎬 HOOK (প্রথম ৩ সেকেন্ড)', r['🎬 Video Hook']),
    card_('🎬 SCRIPT', r['🎬 Video Script']),
    card_('🎬 CTA', r['🎬 CTA']),
    card_('CAPTION', r['Caption']),
    card_('HASHTAGS', r['Hashtags'])
  ].join('');
  show_(h, '🎬 Short Video Script');
}

function planRow_() {
  var sh = SpreadsheetApp.getActiveSheet();
  if (sh.getName() !== 'CONTENT_PLAN') {
    SpreadsheetApp.getUi().alert('CONTENT_PLAN ট্যাবে গিয়ে একটা সারি সিলেক্ট করো।');
    return null;
  }
  var row = sh.getActiveRange().getRow();
  if (row < 4) {
    SpreadsheetApp.getUi().alert('হেডারের নিচের কোনো টপিক সারি সিলেক্ট করো।');
    return null;
  }
  var head = sh.getRange(3, 1, 1, sh.getLastColumn()).getValues()[0];
  var vals = sh.getRange(row, 1, 1, sh.getLastColumn()).getValues()[0];
  var o = {};
  head.forEach(function (h, i) { o[h] = vals[i]; });
  return o;
}

function card_(label, val) {
  val = String(val == null ? '' : val).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  return '<div style="margin:0 0 16px"><div style="font:600 11px/1.4 system-ui;' +
    'letter-spacing:.08em;color:#5f6368;text-transform:uppercase">' + label + '</div>' +
    '<div style="font:14px/1.6 system-ui;color:#202124;white-space:pre-wrap;' +
    'background:#f8f9fa;border-left:3px solid #1a73e8;padding:10px 12px;' +
    'border-radius:0 6px 6px 0;margin-top:5px">' + (val || '—') + '</div></div>';
}

function show_(html, title) {
  var out = HtmlService.createHtmlOutput(
    '<div style="padding:18px;font-family:system-ui">' + html +
    '<div style="font:12px system-ui;color:#5f6368;padding-top:6px;border-top:1px solid #dadce0">' +
    'টেক্সট সিলেক্ট করে Ctrl+C দিয়ে কপি করো</div></div>').setWidth(560).setHeight(640);
  SpreadsheetApp.getUi().showModalDialog(out, title);
}

/* ─────────────────────── স্ট্যাটাস মার্কিং ─────────────────────── */

function markPublished() { setStatus_('Published'); }
function markVideo() { setStatus_('Video Done'); }

function setStatus_(v) {
  var sh = SpreadsheetApp.getActiveSheet();
  if (sh.getName() !== 'CONTENT_PLAN') return;
  var head = sh.getRange(3, 1, 1, sh.getLastColumn()).getValues()[0];
  var col = head.indexOf('Status') + 1;
  if (!col) return;
  var rows = sh.getActiveRangeList().getRanges();
  var n = 0;
  rows.forEach(function (rg) {
    for (var i = 0; i < rg.getNumRows(); i++) {
      var r = rg.getRow() + i;
      if (r >= 4) { sh.getRange(r, col).setValue(v); n++; }
    }
  });
  SpreadsheetApp.getActive().toast(n + ' টি সারি "' + v + '" করা হয়েছে', '', 4);
}

/* ────────────────────────── সারাংশ ────────────────────────── */

function summary_() {
  var ss = SpreadsheetApp.getActive();
  var out = { total: 0, fresh: 0, cats: [], top: [] };
  CATS.forEach(function (c) {
    var sh = ss.getSheetByName(c);
    if (!sh) return;
    var v = sh.getDataRange().getValues().slice(1);
    var filled = v.filter(function (r) { return r[3] && String(r[3]).indexOf('(no qualifying') < 0; });
    var nw = filled.filter(function (r) { return r[6] === '🆕'; }).length;
    out.total += filled.length; out.fresh += nw;
    out.cats.push({ name: c, n: filled.length, fresh: nw });
  });
  var d = ss.getSheetByName('DASHBOARD');
  if (d) {
    out.top = d.getDataRange().getValues().slice(3, 13)
      .filter(function (r) { return r[4]; })
      .map(function (r) { return { s: r[1], c: r[2], t: r[4], l: r[7] }; });
  }
  var p = ss.getSheetByName('CONTENT_PLAN');
  out.briefs = p ? Math.max(p.getLastRow() - 3, 0) : 0;
  return out;
}

function showSummary() {
  var s = summary_();
  var h = '<div style="font:14px/1.7 system-ui;padding:18px">' +
    '<h2 style="margin:0 0 4px">📊 আজকের সারাংশ</h2>' +
    '<p style="color:#5f6368;margin:0 0 14px">মোট <b>' + s.total + '</b> টপিক · <b>' +
    s.fresh + '</b> টি নতুন 🆕 · <b>' + s.briefs + '</b> টি কনটেন্ট ব্রিফ</p>';
  s.cats.forEach(function (c) {
    h += '<div style="display:flex;justify-content:space-between;padding:5px 0;' +
      'border-bottom:1px solid #eee"><span>' + c.name + '</span><span style="color:#5f6368">' +
      c.n + '/30 · ' + c.fresh + ' new</span></div>';
  });
  h += '<h3 style="margin:18px 0 8px">🔥 টপ ১০</h3>';
  s.top.forEach(function (t, i) {
    h += '<div style="padding:6px 0;border-bottom:1px solid #f1f3f4">' +
      '<b style="color:#1a73e8">' + t.s + '</b> · <span style="color:#5f6368;font-size:12px">' +
      t.c + '</span><br>' + (t.l ? '<a href="' + t.l + '" target="_blank">' + t.t + '</a>' : t.t) +
      '</div>';
  });
  SpreadsheetApp.getUi().showModalDialog(
    HtmlService.createHtmlOutput(h + '</div>').setWidth(560).setHeight(640), 'সারাংশ');
}

/* ───────────────────── ইমেইল ডাইজেস্ট (ফ্রি) ───────────────────── */

function sendDigest() {
  var s = summary_();
  var ss = SpreadsheetApp.getActive();
  if (!s.top.length) { ss.toast('এখনো ডেটা আসেনি।'); return; }

  var rows = s.top.map(function (t, i) {
    return '<tr><td style="padding:9px 10px;border-bottom:1px solid #eee;color:#1a73e8;' +
      'font-weight:700;width:46px">' + t.s + '</td>' +
      '<td style="padding:9px 10px;border-bottom:1px solid #eee">' +
      '<div style="font-size:11px;color:#5f6368;text-transform:uppercase">' + t.c + '</div>' +
      (t.l ? '<a href="' + t.l + '" style="color:#202124;text-decoration:none">' + t.t + '</a>' : t.t) +
      '</td></tr>';
  }).join('');

  var html =
    '<div style="font-family:system-ui;max-width:620px;margin:auto">' +
    '<h2 style="margin:0 0 2px">🔥 আজকের ট্রেন্ডিং টপিক</h2>' +
    '<p style="color:#5f6368;margin:0 0 16px">' + s.total + ' টপিক · ' + s.fresh +
    ' নতুন · ' + s.briefs + ' কনটেন্ট ব্রিফ রেডি</p>' +
    '<table style="width:100%;border-collapse:collapse;font-size:14px">' + rows + '</table>' +
    '<p style="margin:20px 0"><a href="' + ss.getUrl() +
    '" style="background:#1a73e8;color:#fff;padding:11px 20px;border-radius:6px;' +
    'text-decoration:none;display:inline-block">শিট খোলো →</a></p></div>';

  MailApp.sendEmail({
    to: Session.getActiveUser().getEmail(),
    subject: '🔥 ট্রেন্ডিং টপিক — ' + Utilities.formatDate(
      new Date(), ss.getSpreadsheetTimeZone(), 'd MMM yyyy'),
    htmlBody: html
  });
  ss.toast('ইমেইল পাঠানো হয়েছে ✅');
}

/* ─────────────────────── লুক অ্যান্ড ফিল ─────────────────────── */

function applyLooks_() {
  var ss = SpreadsheetApp.getActive();
  CATS.concat(['DASHBOARD', 'CONTENT_PLAN']).forEach(function (n) {
    var sh = ss.getSheetByName(n);
    if (!sh) return;
    sh.setHiddenGridlines(true);
    try { sh.getDataRange().setVerticalAlignment('top'); } catch (e) {}
  });
  // ট্যাব রঙ — এক নজরে চেনা যায়
  var colors = { DASHBOARD: '#e8710a', CONTENT_PLAN: '#188038', ARCHIVE: '#9aa0a6' };
  Object.keys(colors).forEach(function (n) {
    var sh = ss.getSheetByName(n);
    if (sh) sh.setTabColor(colors[n]);
  });
  CATS.forEach(function (n) {
    var sh = ss.getSheetByName(n);
    if (sh) sh.setTabColor('#1a73e8');
  });
}

function installTriggers_() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (['sendDigest', 'applyLooks_'].indexOf(t.getHandlerFunction()) >= 0)
      ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('sendDigest').timeBased()
    .atHour(EMAIL_HOUR).nearMinute(0).everyDays(1).create();
}
