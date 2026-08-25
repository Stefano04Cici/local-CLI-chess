import pytest

from scacchi.core.board import Board
from scacchi.engine.commands import CommandHandler
from scacchi.engine.match import Match
from scacchi.user_interfaces.manager import UIManager


def test_unknown_command(monkeypatch):
    """Test that an unknown command is flagged as an error."""
    outputs = []

    class DummyMatch(Match):
        def logic(self, board1):
            pass  # override to prevent starting the logic loop

    def fake_display(message: str, end: str = "") -> None:
        outputs.append(message)

    def fake_input(prompt=""):
        return next(inputs)

    io = UIManager()
    io.display = fake_display
    io.get_input = fake_input
    cmd_handler = CommandHandler(io)

    match = DummyMatch(cmd_handler, io)
    # board = Board(io)
    inputs = iter(['/unknowncommand'])

    flag = cmd_handler.getCommands(match.board1, 1, match)

    with pytest.raises(KeyError):
        {}['missing_key']

    assert flag == 0
    assert any("Unrecognized command" in out for out in outputs)
    assert any("/unknowncommand" in out for out in outputs)

def test_play(monkeypatch):
    """Test that /play returns the 'already in a game' error."""
    outputs = []

    class DummyMatch(Match):
        def logic(self, board1):
            pass  # override to prevent starting the logic loop

    def fake_display(message: str, end: str = "") -> None:
        outputs.append(message)

    def fake_input(prompt=""):
        return next(inputs)

    io = UIManager()
    io.display = fake_display
    io.get_input = fake_input
    cmd_handler = CommandHandler(io)

    match = DummyMatch(cmd_handler, io)

    inputs = iter(['/play'])
    flag = cmd_handler.getCommands(match.board1, 1, match)

    assert flag == 0
    assert any("Game already in progress" in out for out in outputs)

def test_draw(monkeypatch):
    """Test that the draw function works for all possible inputs."""

    class DummyMatch:
        def __init__(self):
            self.status = 1
            self.move_history = []

    io_calls = []

    class DummyIO:
        def __init__(self):
            self.displayed = []
            self.inputs = iter(['y', 'n', 'invalid', 'y'])

        def get_input(self, prompt):
            return next(self.inputs)

        def display(self, text):
            io_calls.append(text)

    io = DummyIO()
    cmd_handler = CommandHandler(io)
    match = DummyMatch()

    # First input 'y' accept draw
    flag = cmd_handler.draw(match)
    assert flag == 3
    assert any("Draw accepted" in s for s in io_calls)

    io_calls.clear()
    match.status = 1
    io.inputs = iter(['n'])  # reject draw
    flag = cmd_handler.draw(match)
    assert flag == 0
    assert any("Draw not accepted" in s for s in io_calls)

    io_calls.clear()
    match.status = 1
    io.inputs = iter(['invalid', 'y'])  # invalid input, then accept
    flag = cmd_handler.draw(match)
    assert flag == 3
    assert any("Invalid response" in s for s in io_calls)

def test_show_board(monkeypatch):
    """Test that the show_board function correctly calls the board.draw function."""
    io = UIManager()
    cmd_handler = CommandHandler(io)
    board = Board(io)  # real board
    called = {"draw": False}

    def fake_draw():  # not to waste time printing
        called["draw"] = True

    monkeypatch.setattr(board, "draw", fake_draw)
    cmd_handler.show_board(board)

    assert called["draw"]

def test_resign(monkeypatch):
    """Test that the resign function works for all possible inputs."""
    class DummyMatch:
        def __init__(self):
            self.status = 1
            self.move_history = []

    io_calls = []

    class DummyIO:
        def __init__(self):
            self.inputs = iter(['n', 'y', 'invalid', 'y'])

        def get_input(self, prompt):
            return next(self.inputs)

        def display(self, text):
            io_calls.append(text)

    io = DummyIO()
    cmd_handler = CommandHandler(io)
    match = DummyMatch()

    # Reject resignation
    flag = cmd_handler.resign(match, turn=1)
    assert flag == 0
    assert any("resignation request refused" in s.lower() for s in io_calls)

    io_calls.clear()
    match.status = 1
    # Accept resignation as white (turn=1)
    flag = cmd_handler.resign(match, turn=1)
    assert flag == 2
    assert any("player" in s.lower() and "wins" in s.lower() for s in io_calls)

    io_calls.clear()
    match.status = 1
    # Invalid input followed by accept
    io.inputs = iter(['invalid', 'y'])
    flag = cmd_handler.resign(match, turn=0)
    assert flag == 2
    assert any("invalid response" in s.lower() for s in io_calls)

def test_simple_movement(monkeypatch):
    """Test a simple movement for movement function."""
    outputs = []
    inputs = iter(['a4', '/exit', 'Y'])

    class DummyMatch(Match):
        def logic(self, board1):
            # self.board1.draw()
            while self.status == 1:
                if self.turn == 1:
                    self.io_handler.display("\n[bold] - White's turn[/bold]\n")
                    return self.cmd_handler.getCommands(self.board1, self.turn, self)

    def fake_display(message: str, end: str = "") -> None:
        outputs.append(message)

    def fake_input(prompt=""):
        return next(inputs)

    io = UIManager()
    io.display = fake_display
    io.get_input = fake_input
    cmd_handler = CommandHandler(io)
    match = DummyMatch(cmd_handler, io)
    flag = match.logic(match.board1)

    # print(outputs)
    assert flag == 5
    assert match.move_history == [["a4"]]
    assert any("a4" in line for line in outputs)

def test_moves():
    """Test that the moves function prints the correct output."""
    outputs = []
    inputs = iter(['a4', 'a6', '/moves', '/exit', 'Y'])

    def fake_display(message: str, end: str = "") -> None:
        outputs.append(message)

    def fake_input(prompt=""):
        return next(inputs)

    io = UIManager()
    io.display = fake_display
    io.get_input = fake_input
    cmd_handler = CommandHandler(io)
    match = Match(cmd_handler, io)

    assert match.move_history == [["a4", "a6"]]
    moves_found = (any("a4" in msg for msg in outputs)
                   and any("a6" in msg for msg in outputs))
    assert moves_found, "Moves not printed in the output display"
