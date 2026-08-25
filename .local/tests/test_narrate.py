from types import SimpleNamespace

import pytest


def speaks(events, narrate):
    return [(e.text, e.style) for e in events if isinstance(e, narrate.Speak)]


def test_chunks_keeps_short_text_whole(narrate):
    assert narrate.chunks("One. Two. Three.") == ["One. Two. Three."]


def test_chunks_splits_on_sentence_boundaries(narrate):
    text = "First sentence here. Second sentence here! Third one? Fourth… fifth."
    assert narrate.chunks(text, limit=45) == [
        "First sentence here. Second sentence here!",
        "Third one? Fourth… fifth.",
    ]


def test_chunks_never_splits_inside_a_sentence(narrate):
    long = "word " * 100
    assert narrate.chunks(long.strip(), limit=50) == [long.strip()]


def test_chunks_of_empty_text(narrate):
    assert narrate.chunks("") == []


def test_title_of(narrate):
    assert narrate.title_of("intro\n\n#  Hello World \n\ntext") == "Hello World"
    assert narrate.title_of("## only subheading\n") is None
    assert narrate.title_of("#hashtag") is None


@pytest.mark.parametrize(
    "text, expected",
    [
        ("example.com", True),
        ("blog.example.co.uk/post", True),
        ("notes.md", False),
        ("README.txt", False),
        ("plain words", False),
    ],
)
def test_looks_like_url(narrate, text, expected):
    assert bool(narrate.looks_like_url(text)) is expected


def test_load_markdown_reads_file_stdin_and_url(narrate, tmp_path, monkeypatch):
    path = tmp_path / "a.md"
    path.write_text("# hi")
    assert narrate.load_markdown(str(path)) == "# hi"

    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("piped"))
    assert narrate.load_markdown("-") == "piped"

    monkeypatch.setattr(narrate, "fetch_article", lambda url: url)
    assert narrate.load_markdown("https://x.org/a") == "https://x.org/a"
    assert narrate.load_markdown("x.org/a") == "https://x.org/a"

    with pytest.raises(SystemExit):
        narrate.load_markdown(str(tmp_path / "missing.md"))


def test_to_events_styles_and_pauses(narrate):
    events = narrate.to_events("# Title\n\nBody text.\n\n> Quoted.\n")
    assert speaks(events, narrate) == [
        ("Title", "header"),
        ("Body text.", "body"),
        ("Quoted.", "quote"),
    ]
    pauses = [e.seconds for e in events if isinstance(e, narrate.Pause)]
    assert pauses[0] == narrate.PAUSE_BEFORE_HEADER
    assert pauses[1] == narrate.PAUSE_AFTER_HEADER


def test_to_events_skips_tables_and_code(narrate):
    markdown = "| a | b |\n|---|---|\n| 1 | 2 |\n\n```\nprint()\n```\n\nAfter.\n"
    assert speaks(narrate.to_events(markdown), narrate) == [
        ("Table skipped.", "body"),
        ("Code sample skipped.", "body"),
        ("After.", "body"),
    ]


def test_to_events_list_pauses(narrate):
    events = narrate.to_events("- one\n- two\n\nPara.\n")
    pauses = [e.seconds for e in events if isinstance(e, narrate.Pause)]
    assert pauses == [
        narrate.PAUSE_AFTER_LIST_ITEM,
        narrate.PAUSE_AFTER_LIST_ITEM,
        narrate.PAUSE_AFTER_LIST,
        narrate.PAUSE_AFTER_PARAGRAPH,
    ]


def test_inline_text_drops_markup_keeps_code(narrate):
    events = narrate.to_events("Some *emphasis*, `code` and a\nsoft break.")
    assert speaks(events, narrate) == [("Some emphasis, code and a soft break.", "body")]


def test_duration(narrate):
    assert narrate.duration(SimpleNamespace(size=narrate.RATE * 61)) == "1:01"
    assert narrate.duration(SimpleNamespace(size=0)) == "0:00"
