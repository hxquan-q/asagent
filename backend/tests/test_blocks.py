from __future__ import annotations

from app.content.blocks import (
    ChartBlock,
    HtmlBlock,
    SvgBlock,
    TableBlock,
    TextBlock,
    block_to_dict,
    dict_to_block,
)
from app.content.sink import drain_sink, emit_block, new_sink


def test_html_sanitised():
    b = HtmlBlock(content="<b>ok</b><script>x</script><img src=x onerror=alert(1)>")
    assert "<script" not in b.content
    assert "onerror" not in b.content
    assert "<b>ok</b>" in b.content


def test_svg_sanitised():
    b = SvgBlock(content='<svg onload="a()"><rect width="5"/></svg>')
    assert "onload" not in b.content
    assert "<rect" in b.content


def test_javascript_href_stripped():
    b = SvgBlock(content='<svg><a xlink:href="javascript:alert(1)"><rect/></a></svg>')
    assert "javascript" not in b.content


def test_round_trip():
    for b in [
        TextBlock(content="hi"),
        TableBlock(title="t", columns=[{"name": "a", "type": "int"}], rows=[{"a": 1}]),
        ChartBlock(chart_type="pie", spec={"series": [1, 2]}),
        HtmlBlock(content="<i>x</i>"),
        SvgBlock(content="<svg/>"),
    ]:
        assert dict_to_block(block_to_dict(b)).type == b.type


def test_sink_emit_drain():
    new_sink()
    emit_block(TextBlock(content="x"))
    emit_block(TableBlock(rows=[{"a": 1}]))
    got = drain_sink()
    assert [b.type for b in got] == ["text", "table"]
    assert drain_sink() == []  # drained
