"""Tests for the WeChat Official Account half-automation module."""

from __future__ import annotations

import json
import pathlib
import sys
from unittest.mock import MagicMock, patch

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from integrations import wechat_oa as wx_oa
import server as stock_app


# ── markdown_to_wechat_html ──────────────────────────────────────────────────


class TestMarkdownToWechatHtml:
    """Markdown → WeChat-flavored inline-styled HTML conversion."""

    def test_h1_h2_render(self):
        html = wx_oa.markdown_to_wechat_html("# 标题\n## 子标题")
        assert "<h1" in html and "标题" in html
        assert "<h2" in html and "子标题" in html
        assert "border-left:4px solid" in html

    def test_paragraphs_separated_by_blank(self):
        html = wx_oa.markdown_to_wechat_html("p1\n\np2")
        assert html.count("<p ") == 2

    def test_bullet_list(self):
        html = wx_oa.markdown_to_wechat_html("- a\n- b\n- c")
        assert "<ul" in html
        assert html.count("<li") == 3
        assert "</ul>" in html

    def test_blockquote(self):
        html = wx_oa.markdown_to_wechat_html("> hello\n> world")
        assert "<blockquote" in html
        assert html.count("<p") == 2  # two quote lines as inner paragraphs
        assert "</blockquote>" in html

    def test_image_resolver_invoked(self):
        calls = []

        def _resolver(rel):
            calls.append(rel)
            return f"https://cdn/{rel}"

        html = wx_oa.markdown_to_wechat_html(
            "![alt](img/a.png)", image_resolver=_resolver
        )
        assert calls == ["img/a.png"]
        assert "https://cdn/img/a.png" in html
        assert "<img" in html
        assert 'alt="alt"' in html

    def test_image_passthrough_without_resolver(self):
        html = wx_oa.markdown_to_wechat_html("![](http://e.org/x.jpg)")
        assert "http://e.org/x.jpg" in html

    def test_bold_and_italic(self):
        html = wx_oa.markdown_to_wechat_html("plain **bold** and *em* text")
        assert "<strong>bold</strong>" in html
        assert "<em>em</em>" in html

    def test_html_escaping(self):
        html = wx_oa.markdown_to_wechat_html("a < b & c > d")
        assert "&lt;" in html
        assert "&amp;" in html
        assert "&gt;" in html

    def test_link_inline(self):
        html = wx_oa.markdown_to_wechat_html("see [docs](https://example.com)")
        assert '<a href="https://example.com">docs</a>' in html

    def test_link_inside_list(self):
        html = wx_oa.markdown_to_wechat_html("- check [link](https://x.io)")
        assert '<a href="https://x.io">link</a>' in html

    def test_complex_section(self):
        md = (
            "# 2026-06-03 收盘\n\n"
            "> **段落**：复盘\n\n"
            "## 三、盘后\n"
            "- 模式识别：过度交易\n"
            "- 决策日志累计 167 条\n\n"
            "![图](img/x.png)\n"
        )
        html = wx_oa.markdown_to_wechat_html(md)
        assert "<h1" in html and "<h2" in html
        assert "<blockquote" in html
        assert "<ul" in html and "<li" in html
        assert "<img" in html
        assert "<strong>段落</strong>" in html

    def test_empty_input(self):
        assert wx_oa.markdown_to_wechat_html("") == ""

    def test_trailing_blockquote_closes(self):
        html = wx_oa.markdown_to_wechat_html("> end")
        assert html.endswith("</blockquote>")

    def test_trailing_list_closes(self):
        html = wx_oa.markdown_to_wechat_html("- end")
        assert html.endswith("</ul>")


# ── build_wechat_html ────────────────────────────────────────────────────────


class TestBuildWechatHtml:
    def test_envelope_contains_paste_marker(self):
        html = wx_oa.build_wechat_html("T", "<p>x</p>", "2026-06-03", "closing")
        assert wx_oa.PASTE_MARKER in html
        assert "<title>T</title>" in html
        assert "2026-06-03" in html
        assert "closing" in html
        assert "<p>x</p>" in html

    def test_title_escaped(self):
        html = wx_oa.build_wechat_html("a<b>", "", "2026-01-01", "x")
        assert "<title>a&lt;b&gt;</title>" in html


# ── send_wecom_bot ───────────────────────────────────────────────────────────


class TestSendWecomBot:
    def test_no_webhook_skipped(self, tmp_path):
        out = wx_oa.send_wecom_bot("", "T", tmp_path / "x.html")
        assert out["ok"] is False
        assert out["skipped"] is True

    def test_success(self, tmp_path):
        sent = {}

        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return b'{"errcode":0,"errmsg":"ok"}'

        def _open(req, timeout=None):
            sent["url"] = req.full_url
            sent["body"] = req.data.decode("utf-8")
            sent["headers"] = dict(req.headers)
            return _Resp()

        with patch.object(wx_oa.urlrequest, "urlopen", _open):
            out = wx_oa.send_wecom_bot(
                "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xx",
                "今日复盘",
                tmp_path / "f.html",
                summary_lines=["S1", "S2"],
            )
        assert out["ok"] is True
        body = json.loads(sent["body"])
        assert body["msgtype"] == "markdown"
        assert "今日复盘" in body["markdown"]["content"]
        assert "S1" in body["markdown"]["content"]
        assert "f.html" in body["markdown"]["content"]

    def test_network_failure_returns_error(self, tmp_path):
        from urllib.error import URLError

        with patch.object(
            wx_oa.urlrequest,
            "urlopen",
            MagicMock(side_effect=URLError("boom")),
        ):
            out = wx_oa.send_wecom_bot(
                "https://wecom/h",
                "T",
                tmp_path / "x.html",
            )
        assert out["ok"] is False
        assert "error" in out

    def test_errcode_nonzero_marks_not_ok(self, tmp_path):
        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return b'{"errcode":40004,"errmsg":"bad"}'

        with patch.object(wx_oa.urlrequest, "urlopen", lambda *a, **kw: _Resp()):
            out = wx_oa.send_wecom_bot(
                "https://wecom/h",
                "T",
                tmp_path / "x.html",
            )
        assert out["ok"] is False
        assert out["raw"]["errcode"] == 40004


# ── push_section_to_wechat ───────────────────────────────────────────────────


class TestPushSection:
    def _write_md(self, dirpath: pathlib.Path, name: str, body: str):
        p = dirpath / name
        p.write_text(body, encoding="utf-8")
        return p

    def test_missing_md_returns_error(self, tmp_path):
        out = wx_oa.push_section_to_wechat(tmp_path, "2026-06-03", "closing")
        assert out["ok"] is False
        assert "missing" in out["error"]

    def test_writes_html_next_to_md(self, tmp_path):
        self._write_md(
            tmp_path, "2026-06-03_closing.md",
            "# T\n\n## 三\n- a\n- b\n",
        )
        out = wx_oa.push_section_to_wechat(tmp_path, "2026-06-03", "closing")
        assert out["ok"] is True
        html_path = tmp_path / "2026-06-03_closing.html"
        assert html_path.exists()
        assert out["html_path"] == str(html_path)
        text = html_path.read_text(encoding="utf-8")
        assert wx_oa.PASTE_MARKER in text
        assert "<h1" in text
        assert "<li" in text

    def test_image_resolver_uses_local_uri(self, tmp_path):
        img_dir = tmp_path / "img"
        img_dir.mkdir()
        (img_dir / "x.png").write_bytes(b"\x89PNG")
        self._write_md(
            tmp_path, "2026-06-03_closing.md",
            "# T\n\n![x](img/x.png)\n",
        )
        out = wx_oa.push_section_to_wechat(tmp_path, "2026-06-03", "closing")
        text = pathlib.Path(out["html_path"]).read_text(encoding="utf-8")
        # Local file URI for embedded images so the local preview works
        assert "file:" in text and "x.png" in text

    def test_skips_ping_without_webhook(self, tmp_path):
        self._write_md(tmp_path, "2026-06-03_closing.md", "# T\n")
        out = wx_oa.push_section_to_wechat(
            tmp_path, "2026-06-03", "closing", wecom_webhook=None
        )
        assert out["ping"]["skipped"] is True

    def test_calls_ping_when_webhook_set(self, tmp_path):
        self._write_md(tmp_path, "2026-06-03_closing.md", "# T\n- a\n")
        with patch.object(wx_oa, "send_wecom_bot",
                          return_value={"ok": True}) as mock_ping:
            out = wx_oa.push_section_to_wechat(
                tmp_path, "2026-06-03", "closing",
                wecom_webhook="https://wecom/hook",
                summary_lines=["sum"],
            )
        assert out["ping"] == {"ok": True}
        assert mock_ping.called
        kwargs = mock_ping.call_args.kwargs
        assert kwargs["summary_lines"] == ["sum"]

    def test_extracts_title_from_first_h1(self, tmp_path):
        self._write_md(
            tmp_path, "2026-06-03_closing.md",
            "## not h1\n# 真正的标题\nbody\n",
        )
        out = wx_oa.push_section_to_wechat(tmp_path, "2026-06-03", "closing")
        text = pathlib.Path(out["html_path"]).read_text(encoding="utf-8")
        assert "真正的标题" in text


# ── /api/content/wechat/push endpoint ────────────────────────────────────────


class TestWechatPushEndpoint:
    @pytest.fixture(autouse=True)
    def _client(self, tmp_path, monkeypatch):
        stock_app.app.config["TESTING"] = True
        self.client = stock_app.app.test_client()
        # Sandbox cfg.DATA_DIR
        monkeypatch.setattr(stock_app.cfg, "DATA_DIR", tmp_path)
        # Pre-populate a wxfile section
        wxdir = tmp_path / "wxfile"
        wxdir.mkdir()
        (wxdir / "2026-06-03_closing.md").write_text(
            "# 收盘\n- 决策日志 167\n- 涨停 84\n", encoding="utf-8",
        )
        self.tmp = tmp_path

    def test_invalid_section_returns_400(self):
        resp = self.client.post("/api/content/wechat/push/2026-06-03/bogus")
        assert resp.status_code == 400

    def test_renders_html(self):
        # Suppress any real WeCom call; webhook env unset → ping skipped
        with patch.dict("os.environ", {}, clear=False):
            stock_app.os.environ.pop("WECOM_BOT_WEBHOOK", None)
            resp = self.client.post("/api/content/wechat/push/2026-06-03/closing")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        html_path = pathlib.Path(data["html_path"])
        assert html_path.exists()
        text = html_path.read_text(encoding="utf-8")
        assert "收盘" in text
        assert "决策日志 167" in text
        assert wx_oa.PASTE_MARKER in text

    def test_summary_lines_from_first_three_bullets(self):
        captured = {}

        def _fake_push(*, wxfile_dir, trade_date, section,
                       summary_lines=None, wecom_webhook=None):
            captured["summary"] = summary_lines
            return {"ok": True, "html_path": str(wxfile_dir / "x.html"),
                    "html_size": 0, "ping": {"skipped": True}}

        with patch.object(stock_app.wx_oa, "push_section_to_wechat", _fake_push):
            self.client.post("/api/content/wechat/push/2026-06-03/closing")
        assert captured["summary"] == ["决策日志 167", "涨停 84"]

    def test_missing_md_returns_ok_false(self):
        resp = self.client.post("/api/content/wechat/push/2099-01-01/closing")
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is False
