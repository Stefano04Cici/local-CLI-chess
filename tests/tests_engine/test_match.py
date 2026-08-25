import pytest

from scacchi.core.board import Board
from scacchi.engine.commands import CommandHandler
from scacchi.engine.match import Match
from scacchi.user_interfaces.manager import UIManager


def test_match_initialization(monkeypatch):
    """Test that match values are initialized correctly (except logic function)."""
    class DummyMatch(Match):
        def logic(self, board1):
            pass  # override to prevent starting the logic loop

    io = UIManager()
    cmd_handler = CommandHandler(io)
    match = DummyMatch(cmd_handler, io)

    assert match.turn == 1
    assert match.move_history == []
    assert match.status == 1
    assert match.io_handler is io
    assert match.cmd_handler is cmd_handler
    assert match.board1 is not None
    assert match.board1.io_handler is io

@pytest.mark.parametrize("responses, expected_status, "
                         "expected_turn, expected_outputs", [
    ([2], 2, 1, ["\n[bold] - White's turn[/bold]\n"]),
    ([1, 2], 2, 0, ["\n[bold] - White's turn[/bold]\n",
                    "\n[bold] - Black's turn[/bold]\n"]),
    ([1, 1, 5], 5, 1, [
        "\n[bold] - White's turn[/bold]\n",
        "\n[bold] - Black's turn[/bold]\n",
        "\n[bold] - White's turn[/bold]\n"
    ]),
])
def test_match_logic(monkeypatch, responses, expected_status,
                     expected_turn, expected_outputs):
    """Test that match.logic() works for all possible options."""
    io = UIManager()
    cmd_handler = CommandHandler(io)
    output_log = []

    def fake_display(msg):
        output_log.append(msg)

    monkeypatch.setattr(io, "display", fake_display)
    response_iter = iter(responses)

    def fake_getCommands(board, turn, match):
        return next(response_iter, 0)

    monkeypatch.setattr(cmd_handler, "getCommands", fake_getCommands)
    monkeypatch.setattr(Board, "draw", lambda self: None)
    match = Match(cmd_handler, io)

    assert match.status == expected_status
    assert match.turn == expected_turn
    assert output_log == expected_outputs


def test_match_detects_checkmate():
    """Unit test to verify that the Match class correctly detects a checkmate condition.

    This test sets up a custom board state where the black king is in checkmate
    by placing a white queen and white king in positions that deliver checkmate.
    It uses dummy classes to simulate user input/output and command handling.

    Asserts:
        - The match status is set to 3 (indicating checkmate).
        - The output message includes "Checkmate" and the name of the losing player.
        - One input call is made to simulate user acknowledgment after game ends.
    """

    class DummyIO:
        def __init__(self):
            self.messages = []
            self.input_calls = 0

        def display(self, msg):
            self.messages.append(msg)

        def get_input(self, prompt):
            self.input_calls += 1
            return ""  # simulate pressing enter

    class DummyCmdHandler:
        def getCommands(self, board, turn, match):
            return 5

    io = DummyIO()
    cmd = DummyCmdHandler()
    match = Match(cmd, io)
    match.board1.table[:] = " "
    from scacchi.core.pawns import King, Queen

    match.board1.table[7][7] = King("black", (7, 7))
    match.board1.table[6][6] = Queen("white", (6, 6))
    match.board1.table[5][5] = King("white", (5, 5))
    match.turn = 0
    match.check_win()

    assert match.status == 3
    output = "\n".join(io.messages)
    assert "Checkmate" in output
    assert ("black" in output or "white" in output)
    assert io.input_calls == 1
