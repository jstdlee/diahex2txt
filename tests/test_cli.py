from typer.testing import CliRunner

from diahex2txt.main import app

runner = CliRunner()
H = "0100001480000110000000040000000000000000"


def test_argument():
    r = runner.invoke(app, [H])
    assert r.exit_code == 0 and "CCR" in r.stdout


def test_stdin():
    r = runner.invoke(app, ["-"], input=H + "\n")
    assert r.exit_code == 0 and "CCR" in r.stdout


def test_error_exit_code():
    r = runner.invoke(app, ["zz"])
    assert r.exit_code == 1 and "Error" in r.stdout


def test_error_after_good_message_exit_code():
    r = runner.invoke(app, [H + "aabbcc"])
    assert "=== Message 2 ===" in r.stdout and "truncated header" in r.stdout
    assert r.exit_code == 1


def test_file_via_stdin_redirect_style():
    r = runner.invoke(app, [], input="0x" + H + "\r\n")
    assert r.exit_code == 0 and "CCR" in r.stdout
