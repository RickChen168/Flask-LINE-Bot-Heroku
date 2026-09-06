import os

from flask import Flask, abort, jsonify, render_template, request

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    ButtonsTemplate,
    MessageEvent,
    TemplateSendMessage,
    TextMessage,
    TextSendMessage,
    URIAction,
)

import notify
import roles
import sheets
from line_liff import verify_id_token

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))

LIFF_ID = os.environ.get("LIFF_ID", "")
LIFF_UPLOAD_URL = f"https://liff.line.me/{LIFF_ID}" if LIFF_ID else ""


@app.route("/", methods=["GET", "POST"])
def callback():
    if request.method == "GET":
        return "Hello Heroku"

    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@app.route("/liff/upload", methods=["GET"])
def liff_upload_page():
    return render_template("liff_upload.html", liff_id=LIFF_ID)


@app.route("/api/records", methods=["POST"])
def api_create_record():
    if not sheets.is_configured():
        return jsonify({"error": "Google 試算表尚未設定完成，請聯繫管理者"}), 503

    data = request.get_json(force=True, silent=True) or {}

    verified = verify_id_token(data.get("id_token", ""))
    user_id = verified["user_id"] if verified else data.get("user_id", "")
    if not user_id:
        return jsonify({"error": "無法辨識使用者"}), 400

    customer_name = (data.get("customer_name") or "").strip()
    if not customer_name:
        return jsonify({"error": "客戶名稱為必填"}), 400

    sales_name = roles.sales_display_name(user_id)
    if not roles.is_registered_sales(user_id):
        sales_name = data.get("display_name") or sales_name

    status = (data.get("status") or "").strip()

    sheets.append_record(
        sales_name=sales_name,
        line_user_id=user_id,
        customer_name=customer_name,
        contact=(data.get("contact") or "").strip(),
        amount=data.get("amount") or "",
        status=status,
        note=(data.get("note") or "").strip(),
    )

    _notify_managers_by_email(
        subject=f"【新業務紀錄】{customer_name}",
        body=(
            f"業務：{sales_name}\n"
            f"客戶：{customer_name}\n"
            f"聯絡方式：{data.get('contact', '')}\n"
            f"商機金額：{data.get('amount', '')}\n"
            f"狀態：{status}\n"
            f"備註：{data.get('note', '')}"
        ),
    )

    return jsonify({"ok": True})


def _notify_managers_by_email(subject, body):
    if not notify.is_configured():
        return
    try:
        notify.send_manager_email(subject, body)
    except Exception:
        pass


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if roles.is_manager(user_id):
        reply = _handle_manager_command(text)
    else:
        reply = _handle_sales_message(user_id)

    line_bot_api.reply_message(event.reply_token, reply)


def _handle_manager_command(text):
    if text in ("help", "說明", "指令"):
        return TextSendMessage(
            text="可用指令：\n最新 - 查看最新5筆紀錄\n本週 - 查看本週業績彙總\n查詢 關鍵字 - 依客戶/業務名稱查詢"
        )

    if text in ("最新", "最新5筆", "本週", "本週業績") or text.startswith("查詢"):
        if not sheets.is_configured():
            return TextSendMessage(text="Google 試算表尚未設定完成，請先完成設定")

    if text in ("最新", "最新5筆"):
        return TextSendMessage(text=_format_records(sheets.fetch_recent(5)))

    if text in ("本週", "本週業績"):
        records = sheets.fetch_this_week()
        total = sum(_to_number(r.get("商機金額")) for r in records)
        return TextSendMessage(
            text=f"本週共 {len(records)} 筆紀錄，商機金額合計 {total}\n\n{_format_records(records)}"
        )

    if text.startswith("查詢"):
        keyword = text[len("查詢"):].strip()
        if not keyword:
            return TextSendMessage(text="請輸入「查詢 關鍵字」")
        return TextSendMessage(text=_format_records(sheets.search_records(keyword)))

    return TextSendMessage(text="輸入「說明」查看可用指令")


def _handle_sales_message(user_id):
    if not roles.is_registered_sales(user_id):
        return TextSendMessage(
            text=f"你好，你尚未被登記為業務人員。\n請將以下 LINE User ID 提供給管理者登記：\n{user_id}"
        )

    if not LIFF_UPLOAD_URL:
        return TextSendMessage(text="上傳功能尚未設定完成，請聯繫管理者")

    return TemplateSendMessage(
        alt_text="點此上傳業務資訊",
        template=ButtonsTemplate(
            title="業務資訊上傳",
            text="請點選下方按鈕填寫業務資訊",
            actions=[URIAction(label="開啟上傳表單", uri=LIFF_UPLOAD_URL)],
        ),
    )


def _format_records(records):
    if not records:
        return "查無紀錄"
    lines = [
        f"[{r.get('時間', '')}] {r.get('業務姓名', '')} - {r.get('客戶名稱', '')} "
        f"({r.get('狀態', '')}) 金額:{r.get('商機金額', '')}"
        for r in records
    ]
    return "\n".join(lines)


def _to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0
