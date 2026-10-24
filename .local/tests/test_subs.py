import base64
import hashlib

import py7zr
import pytest


def napi_response(tmp_path, payload):
    archive = tmp_path / "subs.7z"
    with py7zr.SevenZipFile(archive, "w", password="iBlm8NTigvru0Jr0") as z:
        z.writestr(payload, "subs.txt")
    content = base64.b64encode(archive.read_bytes()).decode()
    return (
        "<result><status>success</status><subtitles>"
        f"<content><![CDATA[{content}]]></content>"
        "</subtitles></result>"
    )


def test_unpack_reads_the_password_protected_archive(subs, tmp_path):
    assert subs.unpack(napi_response(tmp_path, b"{1}{25}Hej")) == b"{1}{25}Hej"


def test_unpack_returns_none_when_napiprojekt_has_no_subtitles(subs):
    assert subs.unpack("<result><response_time>0.007 s.</response_time></result>") is None


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig", "cp1250", "iso-8859-2"])
def test_decode_recovers_polish_letters(subs, encoding):
    text = "Zażółć gęślą jaźń. Śćiąść ŹŻĄ"
    assert subs.decode(text.encode(encoding)) == text


def test_microdvd_becomes_srt_at_the_video_frame_rate(subs):
    srt = subs.to_srt("{25}{50}Zażółć|gęślą", fps=25)
    assert srt == "1\n00:00:01,000 --> 00:00:02,000\nZażółć\ngęślą\n\n"


def test_movie_hash_covers_the_first_ten_megabytes(subs, tmp_path):
    video = tmp_path / "movie.mkv"
    video.write_bytes(b"a" * subs.HASHED_BYTES + b"ignored")
    other = tmp_path / "other.mkv"
    other.write_bytes(b"a" * subs.HASHED_BYTES)
    assert subs.movie_hash(video) == subs.movie_hash(other)


@pytest.mark.parametrize(
    ("tracks", "expected"),
    [
        ([{"codec_name": "ac3", "channels": 6}], True),
        ([{"codec_name": "dts", "channels": 2}], True),
        ([{"codec_name": "ac3", "channels": 6}, {"codec_name": "aac", "channels": 2}], False),
        ([], False),
    ],
)
def test_needs_stereo(subs, tracks, expected):
    assert subs.needs_stereo(tracks) is expected


def test_downmix_favors_the_center_channel(subs):
    assert subs.downmix({"channel_layout": "5.1(side)"}) == [
        "-filter:a:0",
        "pan=stereo|FL<FC+0.3*FL+0.3*SL|FR<FC+0.3*FR+0.3*SR",
    ]
    assert subs.downmix({"channel_layout": "quad"}) == ["-ac:a:0", "2"]


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv", "The Matrix (1999).mkv"),
        ("Severance.S02E03.1080p.WEB.h264-GROUP.mkv", "Severance - S02E03.mkv"),
        ("Some.Home.Video.mp4", "Some Home Video.mp4"),
    ],
)
def test_plex_name(subs, filename, expected):
    assert subs.plex_name(filename) == expected


def test_rename_moves_subtitles_along(subs, tmp_path):
    video = tmp_path / "The.Matrix.1999.1080p.mkv"
    video.touch()
    (tmp_path / "The.Matrix.1999.1080p.pl.srt").touch()
    renamed = subs.rename(video)
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "The Matrix (1999).mkv",
        "The Matrix (1999).pl.srt",
    ]
    assert renamed == tmp_path / "The Matrix (1999).mkv"


def test_movie_hash_matches_md5_of_the_prefix(subs, tmp_path):
    data = bytes(range(256)) * (subs.HASHED_BYTES // 128)
    video = tmp_path / "movie.mkv"
    video.write_bytes(data)
    read = []
    assert subs.movie_hash(video, read.append) == hashlib.md5(data[: subs.HASHED_BYTES]).hexdigest()
    assert sum(read) == subs.HASHED_BYTES
