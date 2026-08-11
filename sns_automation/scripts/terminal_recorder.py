#!/usr/bin/env python3
"""
terminal_recorder.py
台本の各シーンから、asciinema-automationスクリプトを生成してMP4を作る

使い方:
  python3 terminal_recorder.py --scene step1 --narration "手順1: $ claude と入力します" --duration 5.0 --out /tmp/step1.mp4
"""
import subprocess, os, sys, json, re, argparse, tempfile, shutil
from pathlib import Path

def extract_commands(narration: str) -> list:
    """ナレーションからコマンド・コードを抽出"""
    commands = []
    patterns = [
        (r"\$\s+([a-z][^。、\n]+)", "shell"),
        (r"/([a-z][a-z0-9-]+[^。、\n]*)", "slash"),
        (r"\.claude/[\w/.-]+", "path"),
        (r"(disallowedTools:[^。、\n]+)", "yaml"),
        (r"(name:[^。、\n]+)", "yaml"),
        (r"(description:[^。、\n]+)", "yaml"),
        (r"(npx [^。、\n]+)", "shell"),
        (r"(git [^。、\n]+)", "shell"),
        (r"(cd [^。、\n]+)", "shell"),
    ]
    for pattern, kind in patterns:
        for m in re.findall(pattern, narration):
            m = m.strip()
            if len(m) > 2 and m not in [c["cmd"] for c in commands]:
                if kind == "shell" and not m.startswith("$"):
                    m = "$ " + m
                commands.append({"cmd": m, "kind": kind})
    
    # コマンドが見つからない場合はナレーションの要点
    if not commands:
        words = re.sub(r"[。、！？]", "", narration)[:40]
        commands.append({"cmd": f"# {words}", "kind": "comment"})
    
    return commands[:4]

def make_asciinema_script(commands: list, duration: float) -> str:
    """asciinema-automation用スクリプトを生成"""
    # 1文字あたりの遅延を計算（ナレーション時間に合わせる）
    total_chars = sum(len(c["cmd"]) for c in commands)
    if total_chars == 0:
        total_chars = 1
    
    # 全体のデュレーションに合わせてdelayを調整
    delay_ms = int((duration * 1000 * 0.7) / total_chars)
    delay_ms = max(30, min(200, delay_ms))  # 30ms〜200msの範囲
    
    lines = [f"#$ delay {delay_ms}"]
    
    for i, cmd_info in enumerate(commands):
        cmd = cmd_info["cmd"]
        kind = cmd_info["kind"]
        
        if kind == "comment":
            lines.append(f"echo '{cmd[2:].strip()}'")
        elif kind == "yaml":
            lines.append(f"echo '{cmd}'")
        elif kind == "path":
            lines.append(f"echo '{cmd}'")
        elif cmd.startswith("$ "):
            lines.append(cmd[2:])
        elif cmd.startswith("/"):
            lines.append(f"echo '{cmd}'")
        else:
            lines.append(cmd)
        
        lines.append("#$ expect \$")
        
        # コマンド間の待機
        if i < len(commands) - 1:
            lines.append("#$ wait 300")
    
    return "\n".join(lines)

def record_to_mp4(script_content: str, output_path: str, duration: float,
                  theme: str = "dracula", cols: int = 80, rows: int = 24) -> bool:
    """
    asciinema-automationでスクリプトを実行してMP4を生成
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        script_file = os.path.join(tmpdir, "script.sh")
        cast_file = os.path.join(tmpdir, "output.cast")
        gif_file = os.path.join(tmpdir, "output.gif")
        
        # スクリプトファイルを書き出す
        with open(script_file, "w") as f:
            f.write(script_content)
        
        # asciinema-automationで録画
        try:
            result = subprocess.run([
                "asciinema-automation",
                "--asciinema-arguments",
                f"--overwrite --cols {cols} --rows {rows}",
                script_file, cast_file
            ], timeout=60, capture_output=True, text=True,
               env={**os.environ, "PS1": "$ ", "TERM": "xterm-256color"})
            
            if not os.path.exists(cast_file):
                print(f"  ⚠️ cast生成失敗: {result.stderr[:200]}")
                return _fallback_drawtext(script_content, output_path, duration, theme)
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"  ⚠️ asciinema-automation失敗: {e}")
            return _fallback_drawtext(script_content, output_path, duration, theme)
        
        # aggでGIF→FFmpegでMP4
        try:
            # スピード調整（ナレーション時間に合わせる）
            cast_duration = _get_cast_duration(cast_file)
            speed = cast_duration / duration if cast_duration > 0 else 1.0
            speed = max(0.3, min(3.0, speed))
            
            subprocess.run([
                "agg",
                "--theme", theme,
                "--cols", str(cols),
                "--rows", str(rows),
                "--speed", str(speed),
                "--idle-time-limit", "0.5",
                "--font-size", "18",
                cast_file, gif_file
            ], timeout=60, capture_output=True, check=True)
            
            # GIF→MP4変換（縦型1080x1920にパディング）
            subprocess.run([
                "ffmpeg", "-y",
                "-i", gif_file,
                "-vf", f"scale=1080:-2:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-pix_fmt", "yuv420p",
                "-t", str(duration),
                output_path
            ], timeout=60, capture_output=True, check=True)
            
            size = Path(output_path).stat().st_size // 1024
            print(f"  ✅ asciinema MP4: {output_path} ({size}KB, {duration:.1f}s)")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"  ⚠️ agg/ffmpeg失敗: {e}")
            return _fallback_drawtext(script_content, output_path, duration, theme)

def _get_cast_duration(cast_file: str) -> float:
    """castファイルの実際の長さを取得"""
    last_time = 0.0
    try:
        with open(cast_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("["):
                    data = json.loads(line)
                    if isinstance(data, list) and len(data) > 0:
                        last_time = float(data[0])
    except:
        pass
    return last_time

def _fallback_drawtext(script_content: str, output_path: str, duration: float,
                       theme: str = "dracula") -> bool:
    """FFmpeg drawtextフォールバック（asciinemaなしでも動く）"""
    commands = [l for l in script_content.split("\n")
                if l.strip() and not l.startswith("#")]
    
    bg_color = "0x0F0F14"
    filters = [
        "drawbox=x=0:y=0:w=iw:h=80:color=0x232328:t=fill",
        "drawbox=x=20:y=25:w=30:h=30:color=0xFF5F56:t=fill",
        "drawbox=x=65:y=25:w=30:h=30:color=0xFFBD2E:t=fill",
        "drawbox=x=110:y=25:w=30:h=30:color=0x27C93F:t=fill",
        "drawtext=text=\'Claude Code Terminal\':x=(w-tw)/2:y=25:fontcolor=0xB4B4B4:fontsize=28",
    ]
    
    y_pos = 130
    for i, cmd in enumerate(commands[:5]):
        safe_cmd = cmd.replace("'", "\'").replace(":", "\:").replace("[", "\[").replace("]", "\]")[:50]
        color = "0x64FF64" if cmd.startswith(("$", "echo", "cd", "git", "npx")) else "0x64C8FF"
        filters.append(
            f"drawtext=text=\'{safe_cmd}\':x=40:y={y_pos}:fontcolor={color}:fontsize=34:enable=\'gte(t,{i*0.6})\'"
        )
        y_pos += 65
    
    filters.append("drawbox=x=0:y=ih-80:w=iw:h=80:color=0x0078D7:t=fill")
    filters.append("drawtext=text=\'AI Conduit | Claude Code Tips\':x=30:y=ih-58:fontcolor=white:fontsize=28")
    
    result = subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={bg_color}:s=1080x1920:r=30:d={duration}",
        "-vf", ",".join(filters),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        output_path
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and Path(output_path).exists():
        size = Path(output_path).stat().st_size // 1024
        print(f"  ✅ drawtext fallback: {output_path} ({size}KB)")
        return True
    print(f"  ❌ drawtext失敗: {result.stderr[-200:]}")
    return False

def generate_scene_video(scene_title: str, narration: str, duration: float, output_path: str) -> bool:
    """シーンタイプに応じてターミナル録画動画を生成"""
    
    # Step1/Step2/Solutionのみターミナル録画
    if scene_title.lower() not in ["step1", "step2", "solution"]:
        return False
    
    print(f"  🎬 ターミナル録画: {scene_title}")
    commands = extract_commands(narration)
    print(f"  コマンド: {[c['cmd'] for c in commands]}")
    
    script = make_asciinema_script(commands, duration)
    return record_to_mp4(script, output_path, duration)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", required=True)
    parser.add_argument("--narration", required=True)
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    result = generate_scene_video(args.scene, args.narration, args.duration, args.out)
    print("✅ 成功" if result else "❌ 失敗")
