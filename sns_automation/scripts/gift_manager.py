import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

GIFT_LOG = Path("sns_automation/output/gift_log.json")
JST = timezone(timedelta(hours=9))
GIFTS = {
    "starter_kit": {"label": "AIスタートアップスターターキット", "limit": 50},
    "trend_report": {"label": "今週のトレンドレポート", "limit": 30},
    "template_pack": {"label": "AI活用テンプレートパック", "limit": 100},
}


def load_log():
    if GIFT_LOG.exists():
        with open(GIFT_LOG) as f:
            return json.load(f)
    return {"distributed": [], "daily_count": {}}


def save_log(log):
    GIFT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(GIFT_LOG, "w") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def is_duplicate(user_id, gift_type):
    log = load_log()
    for entry in log["distributed"]:
        if entry["user_id"] == user_id and entry["gift_type"] == gift_type:
            return True
    return False


def today_count(gift_type):
    log = load_log()
    today = datetime.now(JST).strftime("%Y-%m-%d")
    key = f"{today}_{gift_type}"
    return log["daily_count"].get(key, 0)


def distribute(user_id: str, gift_type: str) -> dict:
    if gift_type not in GIFTS:
        return {"success": False, "reason": "不明なギフト種類です"}

    if is_duplicate(user_id, gift_type):
        return {"success": False, "reason": "重複配布はできません"}

    if today_count(gift_type) >= GIFTS[gift_type]["limit"]:
        return {"success": False, "reason": "本日の配布上限に達しました"}

    gift_link = os.environ.get("GIFT_LINK", "")
    if not gift_link:
        return {"success": False, "reason": "GIFT_LINKが設定されていません"}

    log = load_log()
    today = datetime.now(JST).strftime("%Y-%m-%d")
    key = f"{today}_{gift_type}"

    log["distributed"].append({
        "user_id": user_id,
        "gift_type": gift_type,
        "label": GIFTS[gift_type]["label"],
        "timestamp": datetime.now(JST).isoformat(),
    })
    log["daily_count"][key] = log["daily_count"].get(key, 0) + 1
    save_log(log)

    return {"success": True, "gift_url": gift_link, "label": GIFTS[gift_type]["label"]}


def stats() -> dict:
    log = load_log()
    return {
        "total_distributed": len(log["distributed"]),
        "daily_count": log["daily_count"],
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        result = distribute(sys.argv[1], sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(stats(), ensure_ascii=False, indent=2))
