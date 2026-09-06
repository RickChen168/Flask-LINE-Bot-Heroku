import os

import requests


def verify_id_token(id_token):
    """Verify a LIFF idToken against LINE's endpoint.

    Returns None (skip verification) when LINE_CHANNEL_ID isn't configured,
    so local/dev setups can pass the userId/displayName straight from the
    client without wiring up channel verification first.
    """
    channel_id = os.environ.get("LINE_CHANNEL_ID")
    if not channel_id:
        return None
    resp = requests.post(
        "https://api.line.me/oauth2/v2.1/verify",
        data={"id_token": id_token, "client_id": channel_id},
        timeout=10,
    )
    resp.raise_for_status()
    payload = resp.json()
    return {"user_id": payload["sub"], "name": payload.get("name", "")}
