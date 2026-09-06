import json
import os
from datetime import datetime, timedelta

import gspread
from google.oauth2.service_account import Credentials

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_SHEET_TAB = "業務紀錄"
_HEADERS = ["時間", "業務姓名", "LINE User ID", "客戶名稱", "聯絡方式", "商機金額", "狀態", "備註"]

_client = None


def is_configured():
    return bool(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") and os.environ.get("GOOGLE_SHEET_ID"))


def _get_client():
    global _client
    if _client is None:
        info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        creds = Credentials.from_service_account_info(info, scopes=_SCOPES)
        _client = gspread.authorize(creds)
    return _client


def _get_worksheet():
    sheet = _get_client().open_by_key(os.environ["GOOGLE_SHEET_ID"])
    try:
        worksheet = sheet.worksheet(_SHEET_TAB)
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=_SHEET_TAB, rows=1000, cols=len(_HEADERS))
        worksheet.append_row(_HEADERS)
    return worksheet


def append_record(sales_name, line_user_id, customer_name, contact, amount, status, note):
    worksheet = _get_worksheet()
    worksheet.append_row(
        [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            sales_name,
            line_user_id,
            customer_name,
            contact,
            amount,
            status,
            note,
        ]
    )


def fetch_records():
    return _get_worksheet().get_all_records()


def fetch_recent(limit=5):
    records = fetch_records()
    return records[-limit:]


def fetch_this_week():
    cutoff = datetime.now() - timedelta(days=7)
    result = []
    for row in fetch_records():
        try:
            row_time = datetime.strptime(row["時間"], "%Y-%m-%d %H:%M")
        except (KeyError, ValueError):
            continue
        if row_time >= cutoff:
            result.append(row)
    return result


def search_records(keyword):
    keyword = keyword.strip()
    return [
        row
        for row in fetch_records()
        if keyword in str(row.get("客戶名稱", "")) or keyword in str(row.get("業務姓名", ""))
    ]
