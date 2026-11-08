#!/usr/bin/env python3
"""
Generate high-fidelity animated demo GIF for OpenYantra README & community showcase:
Demonstrates:
1. Capture architectural decision in Cursor via Cmd+Shift+Y HUD
2. Git commit auto-ingestion
3. Instant recall in a fresh Claude Desktop session via MCP
4. Strict workspace / project isolation
"""

import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path("scratch_frames")
if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Colors
BG = (13, 16, 23)
PANEL_BG = (22, 27, 34)
CARD_BG = (16, 20, 27)
BORDER = (48, 54, 61)
TEXT_WHITE = (240, 246, 252)
TEXT_MUTED = (139, 148, 158)
TEXT_DIM = (80, 90, 105)
AMBER = (245, 160, 0)
CYAN = (0, 210, 255)
GREEN = (46, 160, 67)
PURPLE = (163, 113, 247)
RED = (248, 81, 73)

WIDTH, HEIGHT = 960, 540

# Fonts
font_code = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13)
font_code_bold = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
font_code_small = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11)
font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
font_hud = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13)


def draw_window_frame(draw, x, y, w, h, title, active=True):
    # Window container
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=PANEL_BG, outline=CYAN if active else BORDER, width=1)
    # Title bar
    draw.rounded_rectangle([x, y, x + w, y + 36], radius=10, fill=(30, 36, 46))
    draw.rectangle([x, y + 26, x + w, y + 36], fill=(30, 36, 46))
    draw.line([x, y + 36, x + w, y + 36], fill=BORDER, width=1)
    
    # Mac window control dots
    draw.ellipse([x + 14, y + 13, x + 24, y + 23], fill=(255, 95, 87))
    draw.ellipse([x + 30, y + 13, x + 40, y + 23], fill=(254, 188, 46))
    draw.ellipse([x + 46, y + 13, x + 56, y + 23], fill=(40, 200, 64))
    
    # Title
    draw.text((x + 70, y + 10), title, font=font_title, fill=TEXT_WHITE if active else TEXT_MUTED)


def create_frame(frame_num: int, stage: str, subprogress: float = 1.0):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Top Header banner
    draw.rectangle([0, 0, WIDTH, 42], fill=(18, 22, 30))
    draw.line([0, 42, WIDTH, 42], fill=BORDER, width=1)
    
    # Brand title
    draw.text((20, 12), "⚡ OPENYANTRA", font=font_code_bold, fill=AMBER)
    draw.text((150, 13), "Cross-App Persistent Memory & Context Mesh", font=font_code, fill=TEXT_MUTED)
    
    # Pill badges
    badge_x = WIDTH - 290
    draw.rounded_rectangle([badge_x, 10, badge_x + 130, 32], radius=11, fill=(28, 38, 50), outline=CYAN, width=1)
    draw.text((badge_x + 12, 14), "MCP PROTOCOL", font=font_code_small, fill=CYAN)
    
    badge2_x = WIDTH - 150
    draw.rounded_rectangle([badge2_x, 10, badge2_x + 135, 32], radius=11, fill=(24, 40, 32), outline=GREEN, width=1)
    draw.text((badge2_x + 14, 14), "LOCAL-FIRST ODS", font=font_code_small, fill=GREEN)

    # Main split layout
    # Left pane: Cursor (x: 20, y: 56, w: 450, h: 420)
    # Right pane: Claude Desktop (x: 490, y: 56, w: 450, h: 420)
    
    # --- LEFT WINDOW: Cursor IDE ---
    cursor_active = stage in ("cursor_typing", "cursor_hud", "git_commit")
    draw_window_frame(draw, 20, 56, 450, 420, "Cursor  —  web-gateway/server.py", active=cursor_active)
    
    # Code editor content
    code_lines = [
        ("import os, asyncio", TEXT_MUTED),
        ("from fastapi import FastAPI, Depends", TEXT_MUTED),
        ("", TEXT_MUTED),
        ("app = FastAPI(title='Web Gateway')", TEXT_WHITE),
        ("", TEXT_MUTED),
        ("# TODO: migrate session store from Mongo", AMBER),
        ("async def get_session(token: str):", PURPLE),
        ("    # Architecture decision needed...", TEXT_MUTED),
        ("    return await db.lookup(token)", TEXT_WHITE),
    ]
    cy = 105
    for line, col in code_lines:
        draw.text((40, cy), line, font=font_code, fill=col)
        cy += 20

    # If stage == "cursor_hud": render floating HUD over Cursor!
    if stage in ("cursor_hud", "git_commit"):
        # Dark overlay over code
        hud_box = [50, 160, 440, 340]
        draw.rounded_rectangle(hud_box, radius=8, fill=(12, 15, 20), outline=AMBER, width=2)
        # HUD Header
        draw.rectangle([50, 160, 440, 192], fill=(28, 24, 16))
        draw.line([50, 192, 440, 192], fill=AMBER, width=1)
        draw.text((64, 168), "⌘+Shift+Y  OPENYANTRA HUD", font=font_code_bold, fill=AMBER)
        
        # Captured text
        decision_text = "Migrate session store to Redis JSON"
        displayed_text = decision_text[:int(len(decision_text) * subprogress)] if stage == "cursor_hud" else decision_text
        draw.text((64, 206), "!decision " + displayed_text + ("_" if stage == "cursor_hud" and subprogress < 1.0 else ""), font=font_code, fill=TEXT_WHITE)
        draw.text((64, 234), "Scope: #web-gateway  |  Priority: High", font=font_code_small, fill=TEXT_MUTED)
        
        # Confirmation status
        if subprogress >= 0.8 or stage == "git_commit":
            draw.rounded_rectangle([64, 260, 426, 315], radius=6, fill=(18, 32, 24), outline=GREEN, width=1)
            draw.text((76, 272), "✓ Committed to Agrasandhanī Ledger", font=font_code_small, fill=GREEN)
            draw.text((76, 292), "• Written to Dhāraṇā (Beliefs Sheet)", font=font_code_small, fill=TEXT_MUTED)

    # If stage == "git_commit": draw terminal post-commit output at bottom of Cursor
    if stage == "git_commit":
        draw.rounded_rectangle([32, 360, 458, 464], radius=6, fill=(10, 12, 16), outline=BORDER, width=1)
        draw.text((44, 372), "$ git commit -m 'arch: use redis json'", font=font_code, fill=CYAN)
        draw.text((44, 396), "[OpenYantra Git Hook] Auto-ingested commit", font=font_code_small, fill=AMBER)
        draw.text((44, 414), "✓ Hash: 9b2d8f1  Repo: web-gateway", font=font_code_small, fill=TEXT_MUTED)
        draw.text((44, 432), "✓ Session Log updated atomically", font=font_code_small, fill=GREEN)

    # --- RIGHT WINDOW: Claude Desktop ---
    claude_active = stage in ("claude_start", "claude_recall", "claude_isolation")
    draw_window_frame(draw, 490, 56, 450, 420, "Claude Desktop  —  Fresh Session", active=claude_active)
    
    if stage == "cursor_hud":
        # Empty waiting screen
        draw.text((540, 240), "Waiting for session start...", font=font_code, fill=TEXT_DIM)
    
    elif stage in ("git_commit", "claude_start"):
        # Claude boots up and calls MCP
        draw.rounded_rectangle([510, 105, 920, 175], radius=6, fill=CARD_BG, outline=BORDER, width=1)
        draw.text((524, 118), "⚙️ OpenYantra MCP Client Connected", font=font_code_bold, fill=CYAN)
        draw.text((524, 142), "⚡ Auto-detected local socket via stdio", font=font_code_small, fill=TEXT_MUTED)
        
        # Tool call
        draw.rounded_rectangle([510, 195, 920, 275], radius=6, fill=(16, 24, 34), outline=CYAN, width=1)
        draw.text((524, 208), "Tool Call: load_session_context()", font=font_code, fill=CYAN)
        draw.text((524, 230), "args: { 'workspace': 'web-gateway' }", font=font_code_small, fill=TEXT_MUTED)
        draw.text((524, 250), "Status: 200 OK — Reading chitrapat.ods", font=font_code_small, fill=GREEN)

    elif stage in ("claude_recall", "claude_isolation"):
        # Claude context payload
        draw.rounded_rectangle([510, 100, 920, 230], radius=6, fill=(14, 22, 30), outline=GREEN, width=1)
        draw.text((524, 112), "📥 RECALLED CONTEXT FROM OPENYANTRA", font=font_code_bold, fill=GREEN)
        draw.text((524, 136), "• Project: web-gateway (Active)", font=font_code_small, fill=TEXT_WHITE)
        draw.text((524, 156), "• Core Belief: Migrate session store to Redis JSON", font=font_code_small, fill=AMBER)
        draw.text((524, 176), "• Recent Commit: 9b2d8f1 (arch: use redis json)", font=font_code_small, fill=CYAN)
        draw.text((524, 196), "• Superseded: MongoDB session storage [Archived]", font=font_code_small, fill=TEXT_MUTED)

        # Claude's response speech bubble
        draw.rounded_rectangle([510, 245, 920, 355], radius=8, fill=(28, 34, 44), outline=PURPLE, width=1)
        draw.text((524, 258), "Claude Desktop:", font=font_code_bold, fill=PURPLE)
        resp1 = "Welcome back! In your Cursor session, you decided"
        resp2 = "to migrate the session store to Redis JSON (9b2d8f1)."
        resp3 = "Would you like me to write the Redis connection"
        resp4 = "pooling logic for web-gateway?"
        draw.text((524, 280), resp1, font=font_code_small, fill=TEXT_WHITE)
        draw.text((524, 296), resp2, font=font_code_small, fill=TEXT_WHITE)
        draw.text((524, 312), resp3, font=font_code_small, fill=TEXT_MUTED)
        draw.text((524, 328), resp4, font=font_code_small, fill=TEXT_MUTED)

        if stage == "claude_isolation":
            # Project isolation verification call at bottom
            draw.rounded_rectangle([510, 370, 920, 460], radius=6, fill=(22, 18, 28), outline=BORDER, width=1)
            draw.text((524, 382), "🔒 Project Isolation Check: mobile-app", font=font_code_bold, fill=TEXT_WHITE)
            draw.text((524, 404), "• Context for 'mobile-app': 0 leaking records", font=font_code_small, fill=GREEN)
            draw.text((524, 424), "• Redis decision strictly scoped to web-gateway", font=font_code_small, fill=TEXT_MUTED)

    # Bottom status bar
    draw.rectangle([0, HEIGHT - 32, WIDTH, HEIGHT], fill=(14, 18, 24))
    draw.line([0, HEIGHT - 32, WIDTH, HEIGHT - 32], fill=BORDER, width=1)
    
    stage_text_map = {
        "cursor_hud": "STEP 1: Capture in Cursor IDE via Cmd+Shift+Y HUD",
        "git_commit": "STEP 2: Auto-ingest git commit into session ledger",
        "claude_start": "STEP 3: Launch fresh Claude Desktop — 1-click MCP handshake",
        "claude_recall": "STEP 4: Seamless memory recall across tools with zero cloud",
        "claude_isolation": "STEP 5: Strict workspace isolation guarantees no context bleeding"
    }
    draw.text((24, HEIGHT - 22), stage_text_map.get(stage, ""), font=font_code_bold, fill=AMBER)
    draw.text((WIDTH - 280, HEIGHT - 22), "github.com/revanthlevaka/OpenYantra", font=font_code_small, fill=TEXT_MUTED)

    # Save frame
    frame_path = OUTPUT_DIR / f"frame_{frame_num:04d}.png"
    img.save(str(frame_path))


print("Rendering animation frames...")

frame_idx = 0

# Scene 1: Cursor HUD typing (12 frames)
for i in range(12):
    sub = (i + 1) / 12.0
    create_frame(frame_idx, "cursor_hud", subprogress=sub)
    frame_idx += 1

# Scene 2: Git commit & hook (8 frames)
for i in range(8):
    create_frame(frame_idx, "git_commit")
    frame_idx += 1

# Scene 3: Claude Desktop start & tool call (8 frames)
for i in range(8):
    create_frame(frame_idx, "claude_start")
    frame_idx += 1

# Scene 4: Claude Desktop recall response (12 frames)
for i in range(12):
    create_frame(frame_idx, "claude_recall")
    frame_idx += 1

# Scene 5: Project isolation proof (14 frames)
for i in range(14):
    create_frame(frame_idx, "claude_isolation")
    frame_idx += 1

print(f"Total frames rendered: {frame_idx}")

# Compile into GIF and MP4 using ffmpeg
gif_path = Path("assets/demo_cross_app_memory.gif")
mp4_path = Path("assets/demo_cross_app_memory.mp4")

print("Compiling GIF with ffmpeg...")
cmd_gif = [
    "/opt/homebrew/bin/ffmpeg", "-y",
    "-framerate", "5",
    "-i", str(OUTPUT_DIR / "frame_%04d.png"),
    "-vf", "split[s0][s1];[s0]palettegen=max_colors=128:reserve_transparent=0[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
    str(gif_path)
]
subprocess.run(cmd_gif, check=True)

print("Compiling MP4 with ffmpeg...")
cmd_mp4 = [
    "/opt/homebrew/bin/ffmpeg", "-y",
    "-framerate", "5",
    "-i", str(OUTPUT_DIR / "frame_%04d.png"),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-crf", "22",
    str(mp4_path)
]
subprocess.run(cmd_mp4, check=True)

# Clean up scratch frames
shutil.rmtree(OUTPUT_DIR)

print(f"Done! Created:\n - {gif_path} ({os.path.getsize(gif_path) / 1024:.1f} KB)\n - {mp4_path} ({os.path.getsize(mp4_path) / 1024:.1f} KB)")
