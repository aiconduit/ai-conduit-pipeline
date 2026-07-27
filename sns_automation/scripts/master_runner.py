import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import LOG_FORMAT, LOG_DATE_FORMAT

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("master_runner")

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK", "")


def run_script(script_name: str, args: list[str] | None = None) -> dict[str, Any]:
    script_path = SCRIPTS_DIR / script_name
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    logger.info("Running: %s", " ".join(cmd))
    start = time.time()

    result = {
        "script": script_name,
        "success": False,
        "returncode": -1,
        "stdout": "",
        "stderr": "",
        "duration_seconds": 0,
    }

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            env=os.environ.copy(),
            cwd=str(PROJECT_ROOT),
        )
        result["returncode"] = proc.returncode
        result["stdout"] = proc.stdout[-2000:] if proc.stdout else ""
        result["stderr"] = proc.stderr[-2000:] if proc.stderr else ""

        if proc.returncode == 0:
            result["success"] = True
            logger.info("%s completed successfully", script_name)
        else:
            logger.error("%s failed (rc=%d): %s", script_name, proc.returncode, proc.stderr[:500])
    except subprocess.TimeoutExpired:
        logger.error("%s timed out after 600s", script_name)
        result["stderr"] = "Timeout expired (600s)"
    except FileNotFoundError:
        logger.error("%s not found at %s", script_name, script_path)
        result["stderr"] = f"Script not found: {script_path}"
    except Exception as e:
        logger.error("%s encountered error: %s", script_name, e)
        result["stderr"] = str(e)

    result["duration_seconds"] = round(time.time() - start, 2)
    return result


def send_slack_notification(message: str, is_error: bool = False) -> None:
    if not SLACK_WEBHOOK:
        return
    color = "danger" if is_error else "good"
    payload = {
        "attachments": [
            {
                "color": color,
                "text": message,
                "mrkdwn_in": ["text"],
            }
        ]
    }
    try:
        resp = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Slack notification sent")
    except requests.RequestException as e:
        logger.warning("Slack notification failed: %s", e)


def run_full_pipeline() -> dict[str, Any]:
    pipeline = [
        ("trending_collector.py", None, True),
        ("content_planner.py", None, True),
        ("x_auto_post.py", None, False),
        ("tiktok_uploader.py", None, False),
    ]

    results: list[dict[str, Any]] = []
    has_failure = False

    for script_name, args, critical in pipeline:
        result = run_script(script_name, args)
        results.append(result)

        if not result["success"]:
            if critical:
                logger.error("Critical step %s failed. Halting pipeline.", script_name)
                has_failure = True
                break
            else:
                logger.warning("Non-critical step %s failed. Continuing.", script_name)
                has_failure = True

    summary = {
        "pipeline_run": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_steps": len(results),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "has_failure": has_failure,
            "steps": results,
        }
    }

    return summary


def run_comment_monitor() -> dict[str, Any]:
    return run_script("instagram_dm_bot.py", ["--once"])


def save_report(summary: dict[str, Any]) -> None:
    output_dir = SCRIPTS_DIR.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Report saved to %s", report_path)


def format_slack_message(summary: dict[str, Any]) -> str:
    run = summary["pipeline_run"]
    lines = [
        f"*AI Conduit Pipeline Run*",
        f"Time: {run['timestamp']}",
        f"Steps: {run['successful']}/{run['total_steps']} successful",
        f"Status: {'⚠️ FAILURES' if run['has_failure'] else '✅ ALL OK'}",
        "",
    ]
    for step in run["steps"]:
        icon = "✅" if step["success"] else "❌"
        lines.append(f"{icon} `{step['script']}` ({step['duration_seconds']}s)")
        if not step["success"] and step["stderr"]:
            lines.append(f"   ```{step['stderr'][:200]}```")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="AI Conduit SNS Automation Master Runner")
    parser.add_argument("--mode", choices=["full", "content", "monitor", "post"],
                        default="full", help="Pipeline mode to run")
    parser.add_argument("--no-slack", action="store_true", help="Disable Slack notifications")

    args = parser.parse_args()
    summary: dict[str, Any] = {}

    logger.info("Master runner started (mode=%s)", args.mode)

    try:
        if args.mode == "full":
            summary = run_full_pipeline()
            summary["instagram_monitor"] = run_comment_monitor()

        elif args.mode == "content":
            for script in ["trending_collector.py", "content_planner.py"]:
                r = run_script(script)
                summary[script] = r

        elif args.mode == "monitor":
            summary["instagram_monitor"] = run_comment_monitor()

        elif args.mode == "post":
            for script in ["x_auto_post.py", "tiktok_uploader.py"]:
                r = run_script(script)
                summary[script] = r

        save_report(summary)

        if summary:
            has_failure = any(
                not r.get("success", True)
                for r in summary.values()
                if isinstance(r, dict) and "success" in r
            ) or any(
                step.get("success") is False
                for step in summary.get("pipeline_run", {}).get("steps", [])
            )

            if SLACK_WEBHOOK and not args.no_slack:
                if "pipeline_run" in summary:
                    msg = format_slack_message(summary)
                else:
                    msg = json.dumps(summary, ensure_ascii=False, indent=2)
                send_slack_notification(msg, is_error=has_failure)

            if has_failure:
                logger.warning("Pipeline completed with failures")
                sys.exit(1)
            else:
                logger.info("Pipeline completed successfully")
        else:
            logger.warning("No summary generated")

    except Exception as e:
        logger.critical("Master runner crashed: %s", e, exc_info=True)
        if SLACK_WEBHOOK and not args.no_slack:
            send_slack_notification(f"*Master Runner CRASHED*\n```{e}```", is_error=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
