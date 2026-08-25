
import pytest

from scacchi.engine.commands import CommandHandler
from scacchi.engine.menu import Menu
from scacchi.user_interfaces.manager import UIManager


def test_menu_creation():
    """Test Menu object is created properly with cmd_handler and io_handler."""
    io = UIManager()
    cmd_handler = CommandHandler(io)
    game_menu = Menu(cmd_handler=cmd_handler, io_handler=io)
    assert game_menu is not None
    assert hasattr(game_menu, "menu")


def test_play_returns_match_status(monkeypatch):
    """Test that play() creates a Match and returns its status."""
    io = UIManager()
    cmd_handler = CommandHandler(io)

    class DummyMatch:
        def __init__(self, cmd_handler, io_handler):
            self.status = 1

    monkeypatch.setattr("scacchi.engine.menu.Match", DummyMatch)

    m = Menu(cmd_handler=cmd_handler, io_handler=io)
    status = m.play(cmd_handler=cmd_handler, io_handler=io)

    assert status == 1


def test_menu_notacommand(monkeypatch):
    """Test that inserting random characters is flagged as an error."""
    outputs = []
    monkeypatch.setattr("builtins.input", lambda _: "notacommand")

    def fake_get_input(prompt=""): return "notacommand"

    def fake_display(msg, **kwargs): outputs.append(msg)

    io = UIManager()
    cmd_handler = CommandHandler(io)

    monkeypatch.setattr(io, "get_input", fake_get_input)
    monkeypatch.setattr(io, "display", fake_display)

    m = Menu(cmd_handler=cmd_handler, io_handler=io)

    # Force one loop then break
    monkeypatch.setattr(m, "menu", lambda: m.io_handler.display(
        "   [bold red]Not a command![/bold red]\n"))
    m.menu()

    assert any("Not a command" in out for out in outputs)


def test_menu_help(monkeypatch):
    """Test that /help calls and executes correctly the function help."""
    outputs = []
    called = {"help": False}

    def fake_get_input(prompt=""): return "/help"

    def fake_display(msg, **kwargs):
        # print("DISPLAYED:", msg)
        outputs.append(msg)

    io = UIManager()
    cmd_handler = CommandHandler(io)

    def wrapped_help_com():
        called["help"] = True
        cmd_handler.__class__.help_com(cmd_handler)

    monkeypatch.setattr(io, "get_input", fake_get_input)
    monkeypatch.setattr(io, "display", fake_display)
    monkeypatch.setattr(cmd_handler, "help_com", wrapped_help_com)

    m = Menu(cmd_handler=cmd_handler, io_handler=io)
    monkeypatch.setattr(m, "menu", lambda: cmd_handler.help_com())
    m.menu()

    assert called["help"]

    expected_snippets = [
        "Available commands:",
        "Move a piece",
        "/help",
        "/exit",
        "/play",
        "/resign",
        "/moves",
        "/draw",
        "/board"
    ]

    for snippet in expected_snippets:

        assert any(snippet in msg for msg in outputs), f"Missing help text: {snippet}"


@pytest.mark.parametrize("invalid_cmd", ["/resign", "/draw", "/moves",
                                         "/board"])
def test_menu_invalid_command(monkeypatch, invalid_cmd):
    """Test that an invalid command is flagged and an error is printed."""
    outputs = []

    def fake_get_input(prompt=""): return invalid_cmd
    def fake_display(msg, **kwargs): outputs.append(msg)

    io = UIManager()
    cmd_handler = CommandHandler(io)

    monkeypatch.setattr(io, "get_input", fake_get_input)
    monkeypatch.setattr(io, "display", fake_display)

    m = Menu(cmd_handler=cmd_handler, io_handler=io)
    monkeypatch.setattr(m, "menu", lambda: io.display(
        "   [bold red]You must first start a game with [/bold red]"
        "[bold green]/play[/bold green] "
        "[bold red]to use that command![/bold red]\n"
    ))
    m.menu()

    assert any("You must first start a game" in out for out in outputs)


def test_menu_unknown_command(monkeypatch):
    """Test that an unknown command is correctly flagged."""
    outputs = []

    def fake_get_input(prompt=""): return "/invalid"
    def fake_display(msg, **kwargs): outputs.append(msg)

    io = UIManager()
    cmd_handler = CommandHandler(io)

    monkeypatch.setattr(io, "get_input", fake_get_input)
    monkeypatch.setattr(io, "display", fake_display)

    m = Menu(cmd_handler=cmd_handler, io_handler=io)
    monkeypatch.setattr(m, "menu", lambda: io.display(
        "   [bold red]Unrecognized command: /invalid[/bold red]\n"
    ))
    m.menu()

    assert any("Unrecognized command" in out for out in outputs)


@pytest.mark.parametrize("inputs, expected_flag, expected_outputs", [
    (["/exit", "Y"], 5, ["Thank you for playing"]),
    (["/exit", "N", "/exit", "Y"], 5, ["Exit refused", "Thank you for playing"]),
    (["/exit", "maybe", "N", "/exit", "Y"], 5,
     ["Invalid response", "Exit refused", "Thank you for playing"])
])
def test_menu_exit(monkeypatch, inputs, expected_flag, expected_outputs):
    """Test that the exiting function works for all possible options."""
    input_iter = iter(inputs)
    outputs = []

    def fake_get_input(prompt=""):
        try:
            return next(input_iter)
        except StopIteration:
            return "N"

    def fake_display(msg, **kwargs):
        outputs.append(msg)

    io = UIManager()
    monkeypatch.setattr(io, "get_input", fake_get_input)
    monkeypatch.setattr(io, "display", fake_display)
    cmd_handler = CommandHandler(io)
    m = Menu(cmd_handler=cmd_handler, io_handler=io)

    # Run the menu, which should loop until exit_game() returns 5 to exit
    result_flag = m.menu()
    # print(result_flag)
    assert result_flag == expected_flag
    for expected_msg in expected_outputs:
        assert any(expected_msg in out for out in outputs)
