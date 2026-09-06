import json
import os


def _sales_directory():
    return json.loads(os.environ.get("SALES_USERS", "{}"))


def _manager_ids():
    raw = os.environ.get("MANAGER_USER_IDS", "")
    return {uid.strip() for uid in raw.split(",") if uid.strip()}


def is_manager(user_id):
    return user_id in _manager_ids()


def is_registered_sales(user_id):
    return user_id in _sales_directory()


def sales_display_name(user_id):
    return _sales_directory().get(user_id, "未登記業務")
