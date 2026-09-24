"""
Google Sheets রাইটার।
ফিক্স: API quota burst, ARCHIVE আনবাউন্ডেড গ্রোথ (10M cell limit), ফরম্যাটিং কল-স্পাম,
      হেডার মিসিং, credential ভুল হলে অস্পষ্ট এরর।
যোগ: DASHBOARD ট্যাব, score heat-map, hyperlink, retry-on-429।
"""
import os, json, time, logging, datetime as dt
import gspread
from google.oauth2.service_account import Credentials

log = logging.getLogger("sheets")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER = ["Date/Time", "Platform", "#", "Trending Topic", "Score", "AI Check",
          "New?", "Source Info", "Link"]
ARCHIVE_MAX_ROWS = 20000


def _creds():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        raise SystemExit("❌ GOOGLE_SERVICE_ACCOUNT_JSON secret সেট করা নেই।")
    try:
        info = json.loads(raw)
    except json.JSONDecodeError:
        raise SystemExit("❌ GOOGLE_SERVICE_ACCOUNT_JSON বৈধ JSON নয় — পুরো ফাইলের কনটেন্ট paste করো।")
    for k in ("client_email", "private_key", "token_uri"):
        if k not in info:
            raise SystemExit(f"❌ service-account JSON-এ '{k}' নেই।")
    return Credentials.from_service_account_info(info, scopes=SCOPES), info["client_email"]


def open_sheet():
    creds, email = _creds()
    sid = os.getenv("SHEET_ID", "").strip()
    if not sid:
        raise SystemExit("❌ SHEET_ID secret সেট করা নেই।")
    try:
        ss = gspread.authorize(creds).open_by_key(sid)
    except gspread.exceptions.APIError as e:
        if "PERMISSION_DENIED" in str(e) or "403" in str(e):
            raise SystemExit(f"❌ শিটে অ্যাক্সেস নেই। Google Sheet-এ এই ইমেইলটি "
                             f"Editor হিসেবে Share করো:\n   {email}")
        raise
    log.info("sheet opened: %s", ss.title)
    return ss


def _retry(fn, *a, **kw):
    """429 / 5xx হলে exponential backoff।"""
    for i in range(5):
        try:
            return fn(*a, **kw)
        except gspread.exceptions.APIError as e:
            code = getattr(e, "response", None)
            s = str(e)
            if "429" in s or "RESOURCE_EXHAUSTED" in s or "503" in s or "500" in s:
                w = 2 ** i * 3
                log.warning("Sheets throttled, retry in %ss", w)
                time.sleep(w)
                continue
            raise
    raise RuntimeError("Sheets API বারবার ব্যর্থ হয়েছে")


def _ws(ss, title, rows=200, cols=12):
    try:
        return ss.worksheet(title)
    except gspread.WorksheetNotFound:
        return _retry(ss.add_worksheet, title=title, rows=rows, cols=cols)


def write_category(ss, cat, rows):
    ws = _ws(ss, cat, rows=len(rows) + 10, cols=len(HEADER))
    _retry(ws.clear)
    _retry(ws.update, range_name="A1", values=[HEADER] + rows,
           value_input_option="USER_ENTERED")
    n = len(rows) + 1
    reqs = [
        {"repeatCell": {
            "range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {
                "backgroundColor": {"red": .10, "green": .45, "blue": .91},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                "verticalAlignment": "MIDDLE"}},
            "fields": "userEnteredFormat"}},
        {"updateSheetProperties": {
            "properties": {"sheetId": ws.id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount"}},
        # Score কলামে heat-map (সবুজ = বেশি সার্চেবল)
        {"addConditionalFormatRule": {"rule": {
            "ranges": [{"sheetId": ws.id, "startRowIndex": 1, "endRowIndex": n,
                        "startColumnIndex": 4, "endColumnIndex": 5}],
            "gradientRule": {
                "minpoint": {"color": {"red": 1, "green": .85, "blue": .85}, "type": "NUMBER", "value": "20"},
                "midpoint": {"color": {"red": 1, "green": .97, "blue": .70}, "type": "NUMBER", "value": "50"},
                "maxpoint": {"color": {"red": .72, "green": .93, "blue": .74}, "type": "NUMBER", "value": "80"}}},
            "index": 0}},
        {"updateDimensionProperties": {
            "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4},
            "properties": {"pixelSize": 430}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {
            "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 7, "endIndex": 9},
            "properties": {"pixelSize": 230}, "fields": "pixelSize"}},
    ]
    try:
        _retry(ss.batch_update, {"requests": reqs})
    except Exception as e:
        log.warning("formatting skipped: %s", str(e)[:90])
    log.info("✔ %-12s %d rows", cat, len(rows))


def write_dashboard(ss, records, stamp):
    """সব ক্যাটাগরির সেরা টপিক এক জায়গায়।
    FIX: আগে list-index ধরে নিত (r[4]=score), আসলে r[4]=title ছিল →
         DASHBOARD সবসময় খালি থাকত এবং r[10]-এ IndexError crash হতো।
         এখন dict ব্যবহার করা হয়, index-juggling সম্পূর্ণ বাদ।"""
    top = sorted([r for r in records if isinstance(r.get("score"), (int, float))],
                 key=lambda r: -r["score"])[:60]
    head = ["Rank", "Score", "Category", "Platform", "Trending Topic", "New?", "AI Check", "Link"]
    body = [[i + 1, r["score"], r["category"], r["platform"], r["topic"],
             "🆕" if r.get("new") else "", r.get("ai", ""), r.get("link", "")]
            for i, r in enumerate(top)]
    ws = _ws(ss, "DASHBOARD", rows=len(body) + 12, cols=len(head))
    _retry(ws.clear)
    _retry(ws.update, range_name="A1",
           values=[[f"🔥 TOP TRENDING TOPICS — {stamp} (US)"], [], head] + body,
           value_input_option="USER_ENTERED")
    _fmt(ss, ws, header_row=2, n=len(body) + 3, score_col=1, wide={4: 460})
    log.info("✔ DASHBOARD  %d rows", len(body))


CP_HEAD = ["Priority", "Opportunity", "Demand", "Competition", "Category", "Intent",
           "Topic", "Best Title", "Alt Titles", "Meta Description", "Target Keywords",
           "Article Outline", "FAQ / People Also Ask", "🎬 Video Hook", "🎬 Video Script",
           "🎬 CTA", "Caption", "Hashtags", "Status", "Source"]


def write_content_plan(ss, plan, stamp):
    """আসল কাজের পাতা — এখান থেকে সরাসরি আর্টিকেল ও শর্ট ভিডিও বানানো যায়।"""
    rows = []
    for i, p in enumerate(plan):
        titles = p.get("titles") or [p["topic"]]
        rows.append([
            i + 1, p.get("opportunity"), p.get("demand"), p.get("competition"),
            p.get("category", ""), p.get("intent", ""), p["topic"],
            titles[0],
            "\n".join(titles[1:]),
            p.get("meta", ""),
            ", ".join(p.get("keywords", [])),
            "\n".join(f"{n+1}. {h}" for n, h in enumerate(p.get("outline", []))),
            "\n".join("• " + q for q in p.get("faq", [])),
            p.get("hook", ""),
            "\n".join(f"{n+1}. {b}" for n, b in enumerate(p.get("beats", []))),
            p.get("cta", ""), p.get("caption", ""),
            " ".join(p.get("hashtags", [])),
            "To Do", p.get("link", ""),
        ])
    ws = _ws(ss, "CONTENT_PLAN", rows=len(rows) + 12, cols=len(CP_HEAD))
    _retry(ws.clear)
    _retry(ws.update, range_name="A1",
           values=[[f"✍️ CONTENT PLAN — {stamp} · Opportunity অনুযায়ী সাজানো"], [], CP_HEAD] + rows,
           value_input_option="USER_ENTERED")
    _fmt(ss, ws, header_row=2, n=len(rows) + 3, score_col=1,
         wide={6: 320, 7: 330, 11: 420, 12: 380, 14: 420})
    try:
        _retry(ss.batch_update, {"requests": [
            # Status ড্রপডাউন — কোনটা লেখা হয়ে গেছে ট্র্যাক করতে
            {"setDataValidation": {
                "range": {"sheetId": ws.id, "startRowIndex": 3,
                          "endRowIndex": len(rows) + 3,
                          "startColumnIndex": 18, "endColumnIndex": 19},
                "rule": {"condition": {"type": "ONE_OF_LIST", "values": [
                    {"userEnteredValue": v} for v in
                    ("To Do", "Writing", "Published", "Video Done", "Skip")]},
                    "showCustomUi": True, "strict": False}}},
            {"repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 3,
                          "endRowIndex": len(rows) + 3},
                "cell": {"userEnteredFormat": {"wrapStrategy": "CLIP",
                                               "verticalAlignment": "TOP"}},
                "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)"}},
        ]})
    except Exception as e:
        log.warning("content-plan extras skipped: %s", str(e)[:90])
    log.info("✔ CONTENT_PLAN %d briefs", len(rows))


def _fmt(ss, ws, header_row, n, score_col, wide=None):
    reqs = [
        {"repeatCell": {"range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 1},
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "fontSize": 13}}},
                        "fields": "userEnteredFormat.textFormat"}},
        {"repeatCell": {"range": {"sheetId": ws.id, "startRowIndex": header_row,
                                  "endRowIndex": header_row + 1},
                        "cell": {"userEnteredFormat": {
                            "backgroundColor": {"red": .12, "green": .12, "blue": .14},
                            "textFormat": {"bold": True, "foregroundColor":
                                           {"red": 1, "green": 1, "blue": 1}}}},
                        "fields": "userEnteredFormat"}},
        {"updateSheetProperties": {
            "properties": {"sheetId": ws.id,
                           "gridProperties": {"frozenRowCount": header_row + 1}},
            "fields": "gridProperties.frozenRowCount"}},
        {"addConditionalFormatRule": {"rule": {
            "ranges": [{"sheetId": ws.id, "startRowIndex": header_row + 1, "endRowIndex": n,
                        "startColumnIndex": score_col, "endColumnIndex": score_col + 1}],
            "gradientRule": {
                "minpoint": {"color": {"red": 1, "green": .85, "blue": .85}, "type": "NUMBER", "value": "20"},
                "midpoint": {"color": {"red": 1, "green": .97, "blue": .70}, "type": "NUMBER", "value": "50"},
                "maxpoint": {"color": {"red": .72, "green": .93, "blue": .74}, "type": "NUMBER", "value": "80"}}},
            "index": 0}},
    ]
    for col, px in (wide or {}).items():
        reqs.append({"updateDimensionProperties": {
            "range": {"sheetId": ws.id, "dimension": "COLUMNS",
                      "startIndex": col, "endIndex": col + 1},
            "properties": {"pixelSize": px}, "fields": "pixelSize"}})
    try:
        _retry(ss.batch_update, {"requests": reqs})
    except Exception as e:
        log.warning("formatting skipped: %s", str(e)[:90])


def append_archive(ss, rows):
    ws = _ws(ss, "ARCHIVE", rows=2000, cols=11)
    if not ws.acell("A1").value:
        _retry(ws.update, range_name="A1", values=[["Date/Time", "Category"] + HEADER[1:]])
    if rows:
        _retry(ws.append_rows, rows, value_input_option="USER_ENTERED")
    # গ্রোথ ক্যাপ — Google-এর 10M cell limit-এ পৌঁছানো আটকায়
    try:
        total = len(ws.col_values(1))          # FIX: row_count = গ্রিড সাইজ, ব্যবহৃত সারি নয়
        if total > ARCHIVE_MAX_ROWS:
            ws.delete_rows(2, total - ARCHIVE_MAX_ROWS + 1)
            log.info("archive trimmed to %d rows", ARCHIVE_MAX_ROWS)
    except Exception:
        pass
    log.info("✔ ARCHIVE   +%d rows", len(rows))
