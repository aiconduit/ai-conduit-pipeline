"""
ffmpeg zoompan/Ken Burns エフェクトパターン集
参考: NapoleonWilson/cerberus, bannerbear.com, openshorts
"""

# === 基本zoompanパターン ===

# ゆっくりズームイン（中央）
ZOOM_IN_CENTER = "zoompan=z='min(zoom+0.0015,1.5)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"

# ゆっくりズームアウト（中央）
ZOOM_OUT_CENTER = "zoompan=z='if(lte(on,1),1.5,max(1.5-0.003*on,1.0))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"

# 左上からズームイン
ZOOM_IN_TOP_LEFT = "zoompan=z='zoom+0.001':x=0:y=0:d=125"

# 右下からズームイン
ZOOM_IN_BOTTOM_RIGHT = "zoompan=z='zoom+0.001':x='iw-iw/zoom':y='ih-ih/zoom':d=125"

# 左→右パン（ズームなし）
PAN_LEFT_RIGHT = "zoompan=z=1.2:x='iw*on/500':y='ih/2-(ih/zoom/2)'"

# 右→左パン
PAN_RIGHT_LEFT = "zoompan=z=1.2:x='max(0,iw-iw*on/500)':y='ih/2-(ih/zoom/2)'"

# 上→下パン
PAN_TOP_BOTTOM = "zoompan=z=1.2:x='iw/2-(iw/zoom/2)':y='ih*on/500'"

# === 高品質スムーズzoompan（jerky防止・scale=8000必須）===
SMOOTH_ZOOM_IN = [
    "scale=8000:-1",
    "zoompan=z='zoom+0.001':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=960x960:fps=30"
]

# === ランダム選択用パターン ==
CAMERA_MOVES_9_16 = {
    "zoom_in_center": ZOOM_IN_CENTER,
    "zoom_out_center": ZOOM_OUT_CENTER,
    "zoom_in_top_left": ZOOM_IN_TOP_LEFT,
    "zoom_in_bottom_right": ZOOM_IN_BOTTOM_RIGHT,
    "pan_left_right": PAN_LEFT_RIGHT,
    "pan_right_left": PAN_RIGHT_LEFT,
    "pan_top_bottom": PAN_TOP_BOTTOM,
}

# === moodごとのカメラ動き推奨 ===
MOOD_CAMERA_MAP = {
    "hook": "zoom_in_center",        # 引き込む
    "interrupt": "pan_left_right",   # 動きで注目
    "value": "zoom_out_center",      # 広がりを見せる
    "secondary_hook": "zoom_in_top_left",
    "cta": "zoom_in_center",         # 最後は引き込む
}

if __name__ == "__main__":
    import random
    mood = "hook"
    cam = CAMERA_MOVES_9_16.get(MOOD_CAMERA_MAP.get(mood, "zoom_in_center"))
    print(f"Mood: {mood}")
    print(f"Camera: {cam}")
