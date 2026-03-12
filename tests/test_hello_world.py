"""Sample tests for hello_world module."""

from __future__ import annotations

from python_package_template.hello_world import goodbye_world, hello_goodbye, hello_world, say_goodbye, say_hello


def test_goodbye_world(capsys):
    """Test goodbye_world function.

    Args:
        capsys: Pytest fixture to capture stdout and stderr.

    """
    goodbye_world()
    captured = capsys.readouterr()
    assert captured.out == "Goodbye, world!\n"


def test_hello_goodbye(capsys):
    """Test hello_goodbye function.

    Args:
        capsys: Pytest fixture to capture stdout and stderr.

    """
    hello_goodbye()
    captured = capsys.readouterr()
    assert captured.out == "Hello, world!\nGoodbye, world!\n"


def test_hello_world(capsys):
    """Test hello_world function.

    It uses the some_integer fixture defined in conftest.py.

    Args:
        capsys: Pytest fixture to capture stdout and stderr.

    """
    hello_world()
    captured = capsys.readouterr()
    assert captured.out == "Hello, world!\n"


def test_say_goodbye(capsys, some_name):
    """Test say_goodbye function.

    It uses the some_name fixture defined in conftest.py.

    Args:
        capsys: Pytest fixture to capture stdout and stderr.
        some_name: A string input from fixture.

    """
    say_goodbye(some_name)
    captured = capsys.readouterr()
    assert captured.out == f"Goodbye, {some_name}!\n"


def test_say_hello(capsys, some_name):
    """Test say_hello function.

    It uses the some_name fixture defined in conftest.py.

    Args:
        capsys: Pytest fixture to capture stdout and stderr.
        some_name: A string input from fixture.

    """
    say_hello(some_name)
    captured = capsys.readouterr()
    assert captured.out == f"Hello, {some_name}!\n"
