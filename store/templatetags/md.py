import re, html
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def md(text):
    """Tiny, dependency-free markdown: **bold**, *italic*, paragraphs, '- ' lists."""
    if not text:
        return ""
    t = html.escape(str(text)).replace("\r\n", "\n")
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)", r"<em>\1</em>", t)
    blocks = re.split(r"\n\s*\n", t.strip())
    out = []
    for b in blocks:
        lines = [l for l in b.split("\n")]
        stripped = [l.strip() for l in lines if l.strip()]
        if stripped and all(l.startswith("- ") for l in stripped):
            items = "".join(f"<li>{l[2:].strip()}</li>" for l in stripped)
            out.append(f"<ul style='margin:0 0 1em 1.1em;list-style:disc'>{items}</ul>")
        else:
            out.append("<p style='margin:0 0 1em'>" + "<br>".join(lines) + "</p>")
    return mark_safe("".join(out))
