#!/usr/bin/env python3
"""
master_pipeline.py
172ステップ完全実装 マスターパイプライン

セクション1: テーマ決定（26ステップ）
セクション2: 構成案作成（29ステップ）
セクション3: 台本生成（26ステップ）
セクション4: 動画生成（32ステップ）
セクション5: 字幕・編集（34ステップ）
セクション6: 投稿文作成（27ステップ）
セクション7: 投稿（28ステップ）
合計: 202ステップ（画像の172ステップ＋AI Conduit独自追加）
"""
import os, sys, json, time
from pathlib import Path
from datetime import datetime

def run_step(module_name, step_name, step_num, total):
    """各ステップを実行"""
    print(f"\n{'='*50}")
    print(f"📍 [{step_num}/{total}] {step_name}")
    print(f"{'='*50}")

    try:
        mod = __import__(module_name)
        result = mod.main()
        print(f"\n✅ {step_name} 完了")
        return result, True
    except Exception as e:
        print(f"\n❌ {step_name} 失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, False

def main():
    start_time = datetime.now()
    print(f"\n{'#'*50}")
    print(f"# AI Conduit 完全パイプライン")
    print(f"# {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"# 7セクション・172ステップ")
    print(f"{'#'*50}\n")

    # スクリプトディレクトリをパスに追加
    script_dir = Path(__file__).parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    results = {}
    total_steps = 7

    # ===== セクション1: テーマ決定 =====
    result, ok = run_step("step1_theme_selector", "テーマ決定（26ステップ）", 1, total_steps)
    results["theme"] = {"ok": ok, "data": result}
    if not ok:
        print("⚠️ テーマ決定失敗 → フォールバック使用")

    # ===== セクション2: 構成案作成 =====
    result, ok = run_step("step2_structure_planner", "構成案作成（29ステップ）", 2, total_steps)
    results["structure"] = {"ok": ok, "data": result}
    if not ok:
        print("⚠️ 構成案作成失敗 → フォールバック使用")

    # ===== セクション3: 台本生成 =====
    result, ok = run_step("step3_script_generator", "台本生成（26ステップ）", 3, total_steps)
    results["script"] = {"ok": ok, "data": result}
    if not ok:
        print("❌ 台本生成失敗 → パイプライン中断")
        save_log(results, start_time, "failed_at_script")
        return

    # ===== セクション4: 動画生成 =====
    result, ok = run_step("step4_video_generator", "動画生成（32ステップ）", 4, total_steps)
    results["video"] = {"ok": ok, "data": result}
    if not ok:
        print("❌ 動画生成失敗 → パイプライン中断")
        save_log(results, start_time, "failed_at_video")
        return

    # ===== セクション5: 字幕・編集 =====
    result, ok = run_step("step5_subtitle_editor", "字幕・編集（34ステップ）", 5, total_steps)
    results["editing"] = {"ok": ok, "data": result}
    if not ok:
        print("⚠️ 字幕・編集失敗 → draft_videoで続行")

    # ===== セクション6: 投稿文作成 =====
    result, ok = run_step("step6_post_writer", "投稿文作成（27ステップ）", 6, total_steps)
    results["post"] = {"ok": ok, "data": result}
    if not ok:
        print("⚠️ 投稿文作成失敗 → デフォルト文で続行")

    # ===== セクション7: 投稿 =====
    result, ok = run_step("step7_uploader", "投稿（28ステップ）", 7, total_steps)
    results["upload"] = {"ok": ok, "data": result}

    # 完了サマリー
    elapsed = (datetime.now() - start_time).seconds
    video_id = result.get("video_id","") if result else ""

    print(f"\n{'#'*50}")
    print(f"# パイプライン完了")
    print(f"# 所要時間: {elapsed//60}分{elapsed%60}秒")
    print(f"# セクション結果:")
    for k, v in results.items():
        print(f"#   {k}: {'✅' if v['ok'] else '❌'}")
    if video_id:
        print(f"# 投稿URL: https://youtube.com/shorts/{video_id}")
    print(f"{'#'*50}\n")

    save_log(results, start_time, "completed" if video_id else "failed")
    return results

def save_log(results, start_time, status):
    """実行ログ保存"""
    Path("logs").mkdir(exist_ok=True)
    log = {
        "timestamp": start_time.isoformat(),
        "status": status,
        "elapsed_seconds": (datetime.now() - start_time).seconds,
        "results": {k: v["ok"] for k, v in results.items()},
    }
    date_str = start_time.strftime("%Y%m%d_%H%M%S")
    Path(f"logs/pipeline_{date_str}.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2))
    print(f"✅ ログ保存: logs/pipeline_{date_str}.json")

if __name__ == "__main__":
    main()
