"""WeChat Official Account half-automation helpers.

This module does NOT call the WeChat OpenAPI — that requires an authenticated
公众号 (微信认证) which the user does not have. Instead it produces a copy-paste
ready HTML payload from the daily wxfile markdown and (optionally) sends a
WeCom group-bot ping pointing at the file.

Workflow per day:
    1. Daily scheduler writes data/wxfile/<date>_<section>.md (already implemented).
    2. push_section_to_wechat() converts that md → wechat-flavored HTML, saves
       it next to the markdown as <date>_<section>.html.
    3. If a WECOM_BOT_WEBHOOK is configured, sends a markdown ping with the
       title + key numbers + a hint to "open mp.weixin.qq.com and paste".
    4. User opens the HTML file (or copies its body), pastes into the WeChat
       Official Account editor, clicks "发布".
"""

from __future__ import annotations

import json
import logging
import os
import pathlib
import re
from urllib import request as urlrequest
from urllib.error import URLError

# Title of the editor's "粘贴此处" section. Kept in English so users can ctrl-F.
PASTE_MARKER = "Paste below into mp.weixin.qq.com"


# ── Markdown → WeChat HTML ───────────────────────────────────────────────────


def _esc(text: str) -> str:
    """Minimal HTML escaping. Order matters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _wrap_inline(text: str) -> str:
    """Convert markdown inline tokens (bold + italic) to HTML.

    Applied AFTER escaping, so we have to operate on already-escaped text.
    Order: bold (**…**) before italic (*…*) to avoid greedy mismatches.
    """
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_LINK_RE = re.compile(r"(?<!\!)\[([^\]]+)\]\(([^)]+)\)")


def markdown_to_wechat_html(md: str, image_resolver=None) -> str:
    """Convert a wxfile-style markdown block to WeChat editor HTML.

    image_resolver: optional callable(rel_path) -> str. Called for each
    `![alt](rel)` markdown image to produce the final src URL/path. If None,
    the original rel path is preserved.

    Output is intentionally small and uses inline styles, since the WeChat
    editor strips <style>/<link> on paste.
    """
    lines = md.splitlines()
    out: list[str] = []
    in_list = False
    in_quote = False
    in_para: list[str] = []

    def _flush_para():
        if in_para:
            joined = " ".join(in_para)
            out.append(
                f'<p style="margin:0 0 12px 0;line-height:1.75;">{joined}</p>'
            )
            in_para.clear()

    def _close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def _close_quote():
        nonlocal in_quote
        if in_quote:
            out.append("</blockquote>")
            in_quote = False

    for raw in lines:
        line = raw.rstrip()

        # Image (own paragraph)
        m_img = _IMG_RE.match(line)
        if m_img:
            _flush_para()
            _close_list()
            _close_quote()
            alt, rel = m_img.group(1), m_img.group(2)
            src = image_resolver(rel) if image_resolver else rel
            out.append(
                f'<p style="text-align:center;margin:16px 0;">'
                f'<img src="{_esc(src)}" alt="{_esc(alt)}" '
                f'style="max-width:100%;height:auto;" />'
                f"</p>"
            )
            continue

        # Heading
        m_h = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m_h:
            _flush_para()
            _close_list()
            _close_quote()
            level = len(m_h.group(1))
            inner = _wrap_inline(_esc(m_h.group(2)))
            size_map = {1: "22px", 2: "19px", 3: "17px"}
            font_size = size_map.get(level, "16px")
            out.append(
                f'<h{level} style="font-size:{font_size};font-weight:bold;'
                f'margin:18px 0 10px 0;border-left:4px solid #07c160;'
                f'padding-left:10px;">{inner}</h{level}>'
            )
            continue

        # Blockquote (multi-line)
        if line.startswith(">"):
            _flush_para()
            _close_list()
            inner = _wrap_inline(_esc(line[1:].lstrip()))
            inner = _LINK_RE.sub(
                lambda m: f'<a href="{_esc(m.group(2))}">{_esc(m.group(1))}</a>',
                inner,
            )
            if not in_quote:
                out.append(
                    '<blockquote style="margin:0 0 12px 0;padding:8px 14px;'
                    'background:#f7f7f7;border-left:3px solid #07c160;'
                    'color:#555;line-height:1.7;">'
                )
                in_quote = True
            out.append(f"<p style=\"margin:4px 0;\">{inner}</p>")
            continue
        _close_quote()

        # Bullet list
        m_li = re.match(r"^[-*]\s+(.*)$", line)
        if m_li:
            _flush_para()
            inner = _wrap_inline(_esc(m_li.group(1)))
            inner = _LINK_RE.sub(
                lambda m: f'<a href="{_esc(m.group(2))}">{_esc(m.group(1))}</a>',
                inner,
            )
            if not in_list:
                out.append('<ul style="padding-left:24px;margin:0 0 12px 0;">')
                in_list = True
            out.append(
                f'<li style="margin:4px 0;line-height:1.7;">{inner}</li>'
            )
            continue
        _close_list()

        # Blank line ends the current paragraph
        if not line.strip():
            _flush_para()
            continue

        # Plain text accumulates into the current paragraph
        inline = _wrap_inline(_esc(line))
        inline = _LINK_RE.sub(
            lambda m: f'<a href="{_esc(m.group(2))}">{_esc(m.group(1))}</a>',
            inline,
        )
        in_para.append(inline)

    _flush_para()
    _close_list()
    _close_quote()
    return "\n".join(out)


# ── HTML envelope ────────────────────────────────────────────────────────────


_HTML_ENVELOPE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
          max-width: 720px; margin: 0 auto; padding: 24px; color:#222; }}
  .meta {{ color:#999; font-size:13px; margin-bottom:16px; }}
  .copy-hint {{ background:#fff8e1; border:1px solid #ffd54f; padding:10px 14px;
                 border-radius:6px; margin-bottom:18px; font-size:14px; color:#5d4037; }}
  .article {{ font-size:16px; }}
</style>
</head>
<body>
  <div class="copy-hint">
    📋 <strong>{paste_marker}</strong>: open
    <a href="https://mp.weixin.qq.com/" target="_blank">mp.weixin.qq.com</a> →
    新建图文 → click into the body → Ctrl+A on this page's article block → Ctrl+C → Ctrl+V into editor.
    Title and cover image still need a manual click.
  </div>
  <h1 style="font-size:24px;margin-bottom:6px;">{title}</h1>
  <div class="meta">{date} · {section}</div>
  <article class="article">
{body}
  </article>
</body>
</html>
"""


def build_wechat_html(title: str, body_html: str, date: str, section: str) -> str:
    return _HTML_ENVELOPE.format(
        title=_esc(title),
        body=body_html,
        date=_esc(date),
        section=_esc(section),
        paste_marker=PASTE_MARKER,
    )


# ── WeCom group-bot ping ─────────────────────────────────────────────────────


def send_wecom_bot(webhook: str, title: str, html_path: pathlib.Path,
                   summary_lines: list[str] | None = None,
                   timeout: int = 8) -> dict:
    """Send a markdown message to a WeCom (企业微信) group bot webhook.

    Returns the parsed response dict. Returns {"ok": False, "skipped": True}
    if the webhook is missing/empty.
    """
    if not webhook:
        return {"ok": False, "skipped": True, "reason": "no webhook configured"}
    summary_lines = summary_lines or []
    md = (
        f"📰 **{title}**\n\n"
        f"> 文件：`{html_path.name}`\n"
        + "".join(f"> {ln}\n" for ln in summary_lines)
        + "\n下一步：打开 mp.weixin.qq.com → 新建图文 → 粘贴本地 HTML 内容。"
    )
    payload = json.dumps({"msgtype": "markdown", "markdown": {"content": md}}).encode("utf-8")
    req = urlrequest.Request(
        webhook,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {"ok": data.get("errcode", -1) == 0, "raw": data}
    except (URLError, TimeoutError) as e:
        logging.warning("wecom bot ping failed: %s", e)
        return {"ok": False, "error": str(e)}


# ── Top-level orchestrator ──────────────────────────────────────────────────


def push_section_to_wechat(
    wxfile_dir: pathlib.Path,
    trade_date: str,
    section: str,
    *,
    title: str | None = None,
    summary_lines: list[str] | None = None,
    wecom_webhook: str | None = None,
) -> dict:
    """Render a wxfile section's .md to .html next to it; optionally ping WeCom.

    Returns: {ok, html_path, html_size, ping}
    """
    md_path = wxfile_dir / f"{trade_date}_{section}.md"
    if not md_path.exists():
        return {"ok": False, "error": f"missing {md_path}"}
    md = md_path.read_text(encoding="utf-8")

    # Resolve relative image refs to absolute file URIs so the local preview
    # in a browser still shows the embedded chart / wuyun / swan images.
    img_root = (wxfile_dir).resolve()

    def _resolver(rel: str) -> str:
        if rel.startswith(("http://", "https://", "file://")):
            return rel
        abs_path = (img_root / rel).resolve()
        return abs_path.as_uri() if abs_path.exists() else rel

    body = markdown_to_wechat_html(md, image_resolver=_resolver)
    article_title = title or _extract_title(md) or f"{trade_date} {section}"
    html = build_wechat_html(article_title, body, trade_date, section)

    html_path = wxfile_dir / f"{trade_date}_{section}.html"
    html_path.write_text(html, encoding="utf-8")

    ping = {"skipped": True}
    if wecom_webhook:
        ping = send_wecom_bot(
            wecom_webhook,
            article_title,
            html_path,
            summary_lines=summary_lines,
        )

    return {
        "ok": True,
        "html_path": str(html_path),
        "html_size": html_path.stat().st_size,
        "ping": ping,
    }


def _extract_title(md: str) -> str:
    for line in md.splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            return m.group(1)
    return ""


def get_wecom_webhook() -> str:
    """Read the WeCom bot webhook from the environment."""
    return os.environ.get("WECOM_BOT_WEBHOOK", "").strip()
