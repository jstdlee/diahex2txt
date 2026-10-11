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
