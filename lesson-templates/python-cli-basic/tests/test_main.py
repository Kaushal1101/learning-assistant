import pytest

from src.app.main import greet, main


def test_greet_returns_hello():
    assert greet("World") == "Hello, World!"


def test_greet_handles_various_names():
    assert greet("Alice") == "Hello, Alice!"
    assert greet("Bob") == "Hello, Bob!"


def test_greet_empty_name_raises():
    with pytest.raises(ValueError):
        greet("")


def test_hello_command_prints_greeting(capsys):
    exit_code = main(["hello", "World"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.strip() == "Hello, World!"


def test_hello_loud_flag(capsys):
    main(["hello", "World", "--loud"])
    out = capsys.readouterr().out
    assert "HELLO, WORLD!" in out


def test_missing_command_exits():
    with pytest.raises(SystemExit):
        main([])
