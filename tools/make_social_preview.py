# -*- coding: utf-8 -*-
"""生成 GitHub social preview（1280x640）。

仅用于生成本地图片，需要 Pillow；不属于仓库运行时依赖，也不参与质量门的模块白名单。
改技能数量或定位文案后重跑本脚本即可：
    python tools/make_social_preview.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 640
MARGIN = 88

BG_TOP = (10, 15, 22)
BG_BOTTOM = (16, 24, 34)
ACCENT = (56, 214, 169)
TEXT_MAIN = (238, 243, 248)
TEXT_SUB = (152, 166, 184)
PANEL_BG = (17, 26, 36)
PANEL_BORDER = (34, 48, 63)
CODE_CMD = (200, 212, 224)
CODE_OUT = (143, 160, 178)
CODE_KEY = ACCENT

FONT_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")


def font(name, size, index=0):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size, index=index)
    except OSError:
        return ImageFont.truetype(path, size)


def vertical_gradient(w, h, top, bottom):
    img = Image.new("RGB", (1, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.point((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img.resize((w, h), Image.BILINEAR)


def add_glow(base):
    """右上角一团极弱的青色光，避免大色块死平。"""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((W - 520, -300, W + 200, 340), fill=ACCENT + (40,))
    layer = layer.filter(ImageFilter.GaussianBlur(120))
    return Image.alpha_composite(base.convert("RGBA"), layer)


def add_grid(base):
    """40px 细网格，透明度极低，只在暗底上做纹理。"""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(MARGIN, W, 40):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 4))
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 4))
    return Image.alpha_composite(base, layer)


def draw_terminal(img, box, lines):
    """lines: [(kind, text), ...]，kind in {cmd, out, key}

    key 行是中文结论，Consolas 没有汉字会渲染成方块，必须用中文字体分段绘制。
    """
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=12, fill=PANEL_BG, outline=PANEL_BORDER, width=1)

    # 标题栏：三个点 + bash
    cy = y0 + 26
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((x0 + 24 + i * 20, cy - 5, x0 + 34 + i * 20, cy + 5), fill=c)
    d.text((x0 + 92, cy), "bash", font=font("consola.ttf", 15), fill=TEXT_SUB, anchor="lm")
    d.line([(x0, y0 + 48), (x1, y0 + 48)], fill=PANEL_BORDER, width=1)

    mono = font("consola.ttf", 19)
    mono_b = font("consolab.ttf", 19)
    y = y0 + 78
    for kind, text in lines:
        if kind == "cmd":
            d.text((x0 + 28, y), "$", font=mono_b, fill=ACCENT, anchor="lm")
            d.text((x0 + 52, y), text, font=mono_b, fill=CODE_CMD, anchor="lm")
        elif kind == "key":
            head, tail = text
            head_f = font("msyhbd.ttc", 19)
            tail_f = font("msyh.ttc", 19)
            # 对勾手绘：微软雅黑不含 U+2713，直接打字会是方块
            cx, cy_ = x0 + 56, y
            d.line([(cx, cy_), (cx + 6, cy_ + 6), (cx + 16, cy_ - 7)],
                   fill=CODE_KEY, width=3, joint="curve")
            d.text((cx + 28, y), head, font=head_f, fill=CODE_KEY, anchor="lm")
            d.text((cx + 28 + d.textlength(head, font=head_f) + 10, y), tail,
                   font=tail_f, fill=CODE_OUT, anchor="lm")
        else:
            d.text((x0 + 52, y), text, font=mono, fill=CODE_OUT, anchor="lm")
        y += 34


def build():
    base = vertical_gradient(W, H, BG_TOP, BG_BOTTOM)
    base = add_glow(base)
    base = add_grid(base)
    d = ImageDraw.Draw(base)

    # 顶部标签
    label = "AGENT SKILLS  ·  EMBEDDED  ·  OFFLINE"
    lf = font("consolab.ttf", 15)
    tw = d.textlength(label, font=lf)
    d.rounded_rectangle((MARGIN, 54, MARGIN + tw + 34, 88), radius=17,
                        fill=(22, 44, 48), outline=(38, 78, 74), width=1)
    d.text((MARGIN + 17, 71), label, font=lf, fill=ACCENT, anchor="lm")

    # 主标题
    d.text((MARGIN, 196), "嵌入式开发工具箱", font=font("msyhbd.ttc", 94),
           fill=TEXT_MAIN, anchor="ls")

    # 强调短横线
    d.rounded_rectangle((MARGIN, 238, MARGIN + 56, 242), radius=2, fill=ACCENT)

    # 副标题
    d.text((MARGIN, 286),
           "给 AI 编程助手的 15 个技能 —— 查寄存器、验写入、排故障、审代码、调 PID",
           font=font("msyh.ttc", 23), fill=TEXT_SUB, anchor="ls")

    draw_terminal(base, (MARGIN, 330, MARGIN + 848, 542), [
        ("cmd", "lookup.py lookup USART1.CR1 --demo"),
        ("out", "USART1.CR1   offset 0x00   reset 0x00000000   (demo.svd)"),
        ("out", "bit 0 UE    bit 1 RE    bit 2 TE    bit 5 RXNEIE"),
        ("key", ("已核验", "来源 demo.svd · 设备 ETK-DEMO · 版本 1.0")),
    ])

    # 底部能力行
    d.text((MARGIN, 590),
           "15 skills   ·   offline   ·   zero third-party deps   ·   python 3.10+",
           font=font("consola.ttf", 16), fill=(124, 138, 154), anchor="ls")

    return base.convert("RGB")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       ".github", "social-preview.png")
    img = build()
    img.save(out, "PNG", optimize=True)
    print("已生成 %s  %.1f KB  %dx%d" % (out, os.path.getsize(out) / 1024, img.width, img.height))
