import pytest

RESYNC = "ERROR : \x1b[31mBisync aborted. Must run --resync to recover.\x1b[0m"
RETRYABLE = "ERROR : Bisync aborted. Error is retryable without --resync due to --resilient mode."


@pytest.mark.parametrize(
    "output, kind",
    [
        ("ERROR : trust token expired, please reauth\n" + RETRYABLE, "login"),
        ("requestPCS(iclouddrive): timed out waiting for device approval", "login"),
        (RESYNC, "resync"),
        ("cannot find prior Path1 or Path2 listings, likely due to ...\n" + RETRYABLE, "resync"),
        ("dial tcp: lookup p123-ckdatabasews.icloud.com: no such host\n" + RETRYABLE, "error"),
    ],
)
def test_classify(icloud, output, kind):
    assert icloud.classify(output) == kind


def test_login_failure_notifies_once_per_streak(icloud):
    failures, alerts = {}, []
    for _ in range(5):
        failures, alert = icloud.record(failures, "login")
        alerts.append(alert)
    assert alerts == [True, False, False, False, False]


def test_transient_errors_notify_only_when_they_persist(icloud):
    failures, alerts = {}, []
    for _ in range(6):
        failures, alert = icloud.record(failures, "error")
        alerts.append(alert)
    assert alerts == [False, False, False, True, False, False]


def test_new_kind_of_failure_starts_a_new_streak(icloud):
    failures, _ = icloud.record({"kind": "error", "count": 9}, "login")
    assert failures == {"kind": "login", "count": 1}


def test_sync_is_silent_before_first_resync(icloud, monkeypatch, tmp_path):
    monkeypatch.setattr(icloud, "signed_in", lambda: True)
    monkeypatch.setattr(icloud, "WORKDIR", tmp_path)
    monkeypatch.setattr(icloud, "bisync", lambda *a, **kw: pytest.fail("bisync ran"))
    icloud.sync()


@pytest.mark.parametrize(
    "size, text", [(999, "999 B"), (300_000_000, "300 MB"), (2.1e12, "2.1 TB")]
)
def test_human(icloud, size, text):
    assert icloud.human(size) == text
