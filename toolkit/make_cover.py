#!/usr/bin/env python3
"""
make_cover.py — 为《戴文旭行业笔记》生成公众号封面图
风格参考：十五五 demo 的信息图 —— 简洁、几何、蓝/绿/橙为主色
尺寸：900 × 500 (适配微信封面 2.35:1 与 16:9 通吃)

用法:
    python3 make_cover.py \
        --output images/01.png \
        --series "戴文旭行业笔记 · 01" \
        --title "打螺丝到设计院老板" \
        --subtitle "一个大专生的十年笨功夫" \
        --accent blue

    accent 可选：blue / green / orange / dark
"""
import argparse
import os
from PIL import Image, ImageDraw, ImageFont

# ========== 色板（参考十五五 demo 的蓝绿橙） ==========
PALETTES = {
    "blue": {
        "bg_top": "#0b1e3d",     # 深蓝
        "bg_bot": "#1f4a8a",     # 中蓝
        "accent": "#4ea3ff",     # 亮蓝
        "text": "#ffffff",
        "sub": "#bfd4f0",
        "deco": "#2c6bb5",
    },
    "green": {
        "bg_top": "#0b2e22",
        "bg_bot": "#155e4a",
        "accent": "#3cd39a",
        "text": "#ffffff",
        "sub": "#b9ebd6",
        "deco": "#1e7a5d",
    },
    "orange": {
        "bg_top": "#3a1f05",
        "bg_bot": "#7d4510",
        "accent": "#ffb33d",
        "text": "#ffffff",
        "sub": "#f5d9b0",
        "deco": "#a55a18",
    },
    "dark": {
        "bg_top": "#0a0a0a",
        "bg_bot": "#1a1a1a",
        "accent": "#00a67d",
        "text": "#ffffff",
        "sub": "#a0a0a0",
        "deco": "#2a2a2a",
    },
}

FONT_REG = "/System/Library/Fonts/Hiragino Sans GB.ttc"   # 正常粗细
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"    # 加粗
WIDTH, HEIGHT = 1080, 600


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def gradient_background(img, top_color, bot_color):
    """垂直渐变背景"""
    top = hex_to_rgb(top_color)
    bot = hex_to_rgb(bot_color)
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top[0] * (1 - ratio) + bot[0] * ratio)
        g = int(top[1] * (1 - ratio) + bot[1] * ratio)
        b = int(top[2] * (1 - ratio) + bot[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_decorations(draw, palette):
    """几何装饰：圆环 + 细线"""
    accent = hex_to_rgb(palette["accent"])
    deco = hex_to_rgb(palette["deco"])

    # 右下角大圆环（1/4 可见）
    draw.ellipse(
        [(WIDTH - 280, HEIGHT - 280), (WIDTH + 140, HEIGHT + 140)],
        outline=deco + (180,),
        width=3,
    )
    draw.ellipse(
        [(WIDTH - 200, HEIGHT - 200), (WIDTH + 60, HEIGHT + 60)],
        outline=deco + (120,),
        width=2,
    )

    # 左下角小方块装饰（7x7 网格小点）
    for row in range(4):
        for col in range(6):
            x = 48 + col * 14
            y = HEIGHT - 100 + row * 14
            draw.ellipse([(x - 2, y - 2), (x + 2, y + 2)], fill=deco + (200,))

    # 顶部细线
    draw.line(
        [(60, 48), (200, 48)],
        fill=accent,
        width=3,
    )


def draw_text_block(draw, series, title, subtitle, tagline, palette):
    """文字布局：series 在上，大标题在中，副标题和 tagline 在下"""
    text_color = hex_to_rgb(palette["text"])
    sub_color = hex_to_rgb(palette["sub"])
    accent_color = hex_to_rgb(palette["accent"])

    # 系列标签（顶部小字）
    font_series = ImageFont.truetype(FONT_REG, 22)
    draw.text((60, 70), series, fill=accent_color, font=font_series)

    # 主标题（加粗 Heiti Medium）
    title_font_size = 68 if len(title) <= 12 else (58 if len(title) <= 16 else 48)
    font_title = ImageFont.truetype(FONT_BOLD, title_font_size)

    # 按字符数换行
    max_chars = 11 if title_font_size == 68 else (13 if title_font_size == 58 else 15)
    title_lines = [title[i : i + max_chars] for i in range(0, len(title), max_chars)]

    y_cursor = 140
    for line in title_lines:
        draw.text((60, y_cursor), line, fill=text_color, font=font_title)
        y_cursor += title_font_size + 10

    # 装饰短线
    line_y = y_cursor + 14
    draw.line([(60, line_y), (180, line_y)], fill=accent_color, width=4)
    y_cursor = line_y + 30

    # 副标题
    if subtitle:
        font_sub = ImageFont.truetype(FONT_REG, 30)
        sub_max = 24
        sub_lines = [subtitle[i : i + sub_max] for i in range(0, len(subtitle), sub_max)]
        for line in sub_lines:
            draw.text((60, y_cursor), line, fill=sub_color, font=font_sub)
            y_cursor += 42

    # 底部署名
    font_tag = ImageFont.truetype(FONT_REG, 20)
    draw.text((60, HEIGHT - 60), tagline, fill=sub_color, font=font_tag)


def make_cover(output, series, title, subtitle, tagline, accent):
    palette = PALETTES.get(accent, PALETTES["blue"])
    img = Image.new("RGB", (WIDTH, HEIGHT), "#000000")
    gradient_background(img, palette["bg_top"], palette["bg_bot"])

    # 加一个半透明叠加层让装饰更柔和
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    draw_decorations(overlay_draw, palette)
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    # 正式文字
    draw = ImageDraw.Draw(img)
    draw_text_block(draw, series, title, subtitle, tagline, palette)

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    img.convert("RGB").save(output, "PNG", quality=95)
    print(f"✓ {output}  ({WIDTH}×{HEIGHT}, {accent})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--series", default="戴文旭行业笔记")
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    parser.add_argument(
        "--tagline", default="零碳电力圈 · 戴文旭主笔 · 长期主义者同行"
    )
    parser.add_argument("--accent", default="blue", choices=list(PALETTES.keys()))
    args = parser.parse_args()

    make_cover(
        args.output,
        args.series,
        args.title,
        args.subtitle,
        args.tagline,
        args.accent,
    )


if __name__ == "__main__":
    main()
