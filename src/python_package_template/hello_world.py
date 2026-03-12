"""Hello World Module."""

from __future__ import annotations


def say_hello(name: str) -> None:
    """Say Hello Function.

    Args:
        name: Name to greet.

    """
    print(f"Hello, {name}!")


def hello_world() -> None:
    """Hello World Function."""
    say_hello("world")


def say_goodbye(name: str) -> None:
    """Good bye Function.

    Args:
        name: Name to bid farewell.

    """
    print(f"Goodbye, {name}!")


def goodbye_world() -> None:
    """Goodbye World Function."""
    say_goodbye("world")


def hello_goodbye() -> None:
    """Hello Goodbye Function."""
    hello_world()
    goodbye_world()
