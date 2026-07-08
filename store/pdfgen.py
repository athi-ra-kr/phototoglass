"""Render saved studio designs (the serialized JSON on OrderItem.design) into a PDF.

This is a best-effort raster reconstruction using Pillow: background fill (image /
colour / gradient), portrait/sticker/image layers (with optional mask + frame and
rotation) and text layers. Fancy web fonts fall back to a bundled sans-serif.
"""
import io
import os
import re
import base64
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def _font(size):
    for p in _FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, max(8, int(size)))
            except Exception:
                pass
    return ImageFont.load_default()


def _hexes(s):
    return re.findall(r"#[0-9a-fA-F]{3,8}", s or "")


def _to_rgb(h):
    h = (h or "#ffffff").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except Exception:
        return (255, 255, 255)


def _load_img(src):
    if not src:
        return None
    try:
        if src.startswith("data:"):
            b64 = src.split(",", 1)[1]
            return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
        path = src
        mu = settings.MEDIA_URL
        if path.startswith(mu):
            path = path[len(mu):]
        fp = os.path.join(settings.MEDIA_ROOT, path.lstrip("/"))
        if os.path.exists(fp):
            return Image.open(fp).convert("RGBA")
    except Exception:
        return None
    return None


def _gradient(size, c1, c2):
    small = Image.new("RGB", (64, 64))
    px = small.load()
    for y in range(64):
        for x in range(64):
            t = (x + y) / 126.0
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return small.resize(size)


def _cover(img, size):
    iw, ih = img.size
    tw, th = size
    scale = max(tw / iw, th / ih)
    img = img.resize((max(1, int(iw * scale)), max(1, int(ih * scale))))
    x = (img.size[0] - tw) // 2
    y = (img.size[1] - th) // 2
    return img.crop((x, y, x + tw, y + th))


def _contain(img, size):
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    im = img.copy()
    im.thumbnail(size)
    out.paste(im, ((size[0] - im.size[0]) // 2, (size[1] - im.size[1]) // 2), im)
    return out


def _draw_text(canvas, L, W, H, sx, sy, norm):
    txt = L.get("text") or ""
    if not txt:
        return
    if norm:
        size = max(8, int((L.get("size") or 0.06) * H))
        x = int((L.get("x") or 0) * W)
        y = int((L.get("y") or 0) * H)
    else:
        scale = (sx + sy) / 2.0
        size = max(8, int((L.get("size") or 30) * scale))
        x = int((L.get("x") or 0) * sx)
        y = int((L.get("y") or 0) * sy)
    f = _font(size)
    hs = _hexes(L.get("color") or "#ffffff")
    col = _to_rgb(hs[0]) if hs else (255, 255, 255)
    tmp = Image.new("RGBA", (max(8, size * (len(txt) + 1)), max(8, int(size * 1.6))), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.text((2, 2), txt, font=f, fill=col + (255,))
    bbox = tmp.getbbox()
    if bbox:
        tmp = tmp.crop(bbox)
    if L.get("rot"):
        tmp = tmp.rotate(-float(L["rot"]), expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(tmp, (x, y))


DPI = 150


def _render(design):
    pw = float(design.get("pw") or 520)
    ph = float(design.get("ph") or 380)
    dim_w = design.get("dim_w")
    dim_h = design.get("dim_h")
    if dim_w and dim_h:                      # exact physical size of the frame (cm -> px @ DPI)
        W = max(1, round(float(dim_w) / 2.54 * DPI))
        H = max(1, round(float(dim_h) / 2.54 * DPI))
    else:
        W, H = int(pw * 2), int(ph * 2)
    norm = bool(design.get("norm"))
    sx, sy = W / pw, H / ph
    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    fill = design.get("fill") or {}
    if fill.get("image"):
        im = _load_img(fill["image"])
        if im:
            canvas.paste(_cover(im, (W, H)), (0, 0))
    elif fill.get("color"):
        col = fill["color"]
        hs = _hexes(col)
        if "gradient" in col and len(hs) >= 2:
            canvas.paste(_gradient((W, H), _to_rgb(hs[0]), _to_rgb(hs[1])), (0, 0))
        elif hs:
            canvas.paste(Image.new("RGB", (W, H), _to_rgb(hs[0])), (0, 0))

    for L in design.get("layers", []):
        if L.get("type") == "text":
            _draw_text(canvas, L, W, H, sx, sy, norm)
            continue
        img = _load_img(L.get("src"))
        if not img:
            continue
        if norm:
            w = max(1, int((L.get("w") or 0) * W)); h = max(1, int((L.get("h") or 0) * H))
            x = int((L.get("x") or 0) * W); y = int((L.get("y") or 0) * H)
        else:
            w = max(1, int((L.get("w") or 100) * sx)); h = max(1, int((L.get("h") or 100) * sy))
            x = int((L.get("x") or 0) * sx); y = int((L.get("y") or 0) * sy)
        img = img.resize((w, h))
        if L.get("mask"):
            m = _load_img(L["mask"])
            if m:
                img.putalpha(m.resize((w, h)).convert("L"))
        if L.get("pframe"):
            fr = _load_img(L["pframe"])
            if fr:
                img.alpha_composite(_contain(fr, (w, h)))
        if L.get("rot"):
            img = img.rotate(-float(L["rot"]), expand=True, resample=Image.BICUBIC)
        canvas.alpha_composite(img, (x, y))

    if design.get("frame"):
        fim = _load_img(design["frame"])
        if fim:
            canvas.alpha_composite(fim.resize((W, H)))

    return canvas.convert("RGB")


def _size_to_dim(img, design):
    """Place the studio render on a page at the exact physical size (cm) of the chosen dimension."""
    d = design or {}
    dim_w = d.get("dim_w")
    dim_h = d.get("dim_h")
    img = img.convert("RGB")
    if dim_w and dim_h:
        W = max(1, round(float(dim_w) / 2.54 * DPI))
        H = max(1, round(float(dim_h) / 2.54 * DPI))
        img = img.resize((W, H))
    return img


def _item_image(item):
    """The exact studio render if present, else a best-effort server render of the design."""
    if getattr(item, "render", None):
        try:
            item.render.open("rb")
            return Image.open(item.render).convert("RGB")
        except Exception:
            pass
    if item.design:
        return _render(item.design)
    return None


def build_item_pdf(item):
    img = _item_image(item)
    if img is None:
        return None
    img = _size_to_dim(img, item.design)
    buf = io.BytesIO()
    img.save(buf, "PDF", resolution=float(DPI))
    return buf.getvalue()


def build_order_pdf(order):
    pages = []
    for it in order.items.all():
        img = _item_image(it)
        if img is not None:
            pages.append(_size_to_dim(img, it.design))
    if not pages:
        return None
    buf = io.BytesIO()
    pages[0].save(buf, format="PDF", save_all=True, append_images=pages[1:], resolution=float(DPI))
    return buf.getvalue()
