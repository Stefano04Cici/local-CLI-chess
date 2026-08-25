# tests/test_board.py
import pytest
import numpy as np

from scacchi.core.board import Board
from scacchi.core.pawns import Bishop, King, Knight, Queen, Rook, Walker

# Testing basic functions

class MockIOHandler:
    """Mock class to simulate input/output interactions during testing."""

    def __init__(self):
        self.messages = []

    def display(self, msg):
        self.messages.append(msg)

    def clear(self):
        self.messages = []

def test_board_initialization():
    """Test the initialization of the board object."""
    io = MockIOHandler()
    b = Board(io)
    assert b.rows == 8
    assert b.columns == 8
    assert b.table.shape == (8, 8)
    assert isinstance(b.io_handler, MockIOHandler)
    assert not b.check_state["in_check"]
    assert b.check_state["player"] is None
    assert not b.checkMate["status"]
    assert b.checkMate["player"] is None

def test_set_pawns():
    """Test setting pawns on the board."""
    io = MockIOHandler()
    b = Board(io)

    for col in range(8):
        assert isinstance(b.table[1][col], Walker)
        assert b.table[1][col].color == 'black'
        assert isinstance(b.table[6][col], Walker)
        assert b.table[6][col].color == 'white'

    assert isinstance(b.table[0][0], Rook)
    assert isinstance(b.table[0][7], Rook)
    assert isinstance(b.table[7][0], Rook)
    assert isinstance(b.table[7][7], Rook)

    assert isinstance(b.table[0][1], Knight)
    assert isinstance(b.table[0][6], Knight)
    assert isinstance(b.table[7][1], Knight)
    assert isinstance(b.table[7][6], Knight)

    assert isinstance(b.table[0][2], Bishop)
    assert isinstance(b.table[0][5], Bishop)
    assert isinstance(b.table[7][2], Bishop)
    assert isinstance(b.table[7][5], Bishop)

    assert isinstance(b.table[0][3], Queen)
    assert isinstance(b.table[7][3], Queen)

    assert isinstance(b.table[0][4], King)
    assert isinstance(b.table[7][4], King)

def test_movement_basic(monkeypatch):
    """Test basic movement functionality with dummy I/O."""
    class DummyIO:
        def __init__(self):
            self.messages = []

        def display(self, msg):
            self.messages.append(msg)

    io = DummyIO()
    board = Board(io)
    turn = 1

    (pawn_type, row1, col1, eat, row2, col2, en_passant, ks_castling,
         ql_castling, promotion_piece) = board.input_extraction("e4")
    if isinstance(pawn_type, str):
        pawn_type = Walker
    row1, col1 = board.source_piece_finder(
        pawn_type, row2, col2, col1, row1, eat, en_passant, board.table, turn
    )

    piece = board.table[row1][col1]
    assert isinstance(piece, Walker)

    board.table[row2][col2] = piece
    board.table[row1][col1] = ' '
    assert isinstance(board.table[row2][col2], Walker)
    assert board.table[row1][col1] == ' '

# Testing some input related scenarios

@pytest.fixture
def board():
    """Fixture to create and return a new board instance."""
    io_handler = MockIOHandler()
    return Board(io_handler)

def test_input_extraction_pawn_move(board):
    """Test pawn move input extraction."""
    result = board.input_extraction("e4")
    assert result[0] == 'walker'
    assert result[4] == 4  # row2
    assert result[5] == 4  # col2 (e)

def test_input_extraction_knight_move(board):
    """Test knight move input extraction."""
    result = board.input_extraction("Nf3")
    assert result[0] == Knight
    assert result[4] == 5  # row2
    assert result[5] == 5  # col2 (f)

def test_input_extraction_capture(board):
    """Test piece capture input extraction."""
    result = board.input_extraction("Nxe5")
    assert result[0] == Knight
    assert result[3] is True
    assert result[4] == 3  # row2
    assert result[5] == 4  # col2 (e)

def test_input_extraction_castling_kingside(board):
    """Test kingside castling input extraction."""
    result = board.input_extraction("0-0")
    assert result[7] is True
    assert result[4] == 7  # row2
    assert result[5] == 6  # col2 (g)

def test_input_extraction_promotion(board):
    """Test promotion input extraction."""
    result = board.input_extraction("e8=Q")
    assert result[0] == 'walker'
    assert result[4] == 0  # row2
    assert result[5] == 4  # col2 (e)
    assert result[9] == 'Q'

# Testing some source_piece_finder possible outcomes

def test_source_piece_finder_pawn(board):
    """Test finding the source square for a pawn move."""
    (pawn_type, row1, col1, eat, row2, col2, en_passant, ks_castling,
     ql_castling, promotion_piece) = board.input_extraction("e4")
    if isinstance(pawn_type, str):
        pawn_type = Walker
    row1, col1 = board.source_piece_finder(pawn_type, row2, col2,
                        col1, row1, eat, en_passant, board.table, 1)
    assert (row1, col1) == (6, 4)

def test_source_piece_finder_knight(board):
    """Test finding the source square for a knight move."""
    (pawn_type, row1, col1, eat, row2, col2, en_passant, ks_castling,
     ql_castling, promotion_piece) = board.input_extraction("Nf3")
    if isinstance(pawn_type, str):
        pawn_type = Walker
    row1, col1 = board.source_piece_finder(pawn_type,
                    row2, col2, col1, row1, eat, en_passant, board.table, 1)
    assert (row1, col1) == (7, 6)

def test_source_piece_finder_eating():
    """Test source piece finding when capturing."""
    io = MockIOHandler()
    board = Board(io)
    board.movement("e4", 1, io)
    board.movement("f5", 0, io)
    board.draw()
    (pawn_type, row1, col1, eat, row2, col2, en_passant, ks_castling,
     ql_castling, promotion_piece) = board.input_extraction("xf5")
    if isinstance(pawn_type, str):
        pawn_type = Walker
    row1, col1 = board.source_piece_finder(
        pawn_type, row2, col2, col1, row1, eat, en_passant, board.table, 1
    )
    assert (row1, col1) == (4, 4)

def test_source_piece_finder_en_passant(board):
    """Test source piece finding for en passant captures."""
    board.movement("e4", 1, board.io_handler)
    board.movement("d5", 0, board.io_handler)
    board.movement("e5", 1, board.io_handler)
    board.movement("f5", 0, board.io_handler)
    board.draw()

    (pawn_type, row1, col1, eat, row2, col2, en_passant, ks_castling,
     ql_castling, promotion_piece) = board.input_extraction("xf6 e.p.")
    if isinstance(pawn_type, str):
        pawn_type = Walker
    row1, col1 = board.source_piece_finder(
        pawn_type, row2, col2, col1, row1, eat, en_passant, board.table, 1
    )
    assert en_passant is True
    assert (row1, col1) == (3, 4)  # e4 position

def test_position_conversion_single():
    """Test position string to coordinates conversion."""
    io = MockIOHandler()
    board = Board(io)

    assert board.position_conversion_single('a') == 0
    assert board.position_conversion_single('h') == 7
    assert board.position_conversion_single('d') == 3
    assert board.position_conversion_single('1') == 7
    assert board.position_conversion_single('8') == 0
    assert board.position_conversion_single('5') == 3

    with pytest.raises(ValueError):
        board.position_conversion_single('z')

    with pytest.raises(ValueError):
        board.position_conversion_single('0')

    with pytest.raises(ValueError):
        board.position_conversion_single('9')

    with pytest.raises(ValueError):
        board.position_conversion_single('*')

# Testing special moves

def test_promotions():
    """Test pawn promotions to other pieces."""
    io = MockIOHandler()
    board = Board(io)
    board.table[0][0] = Walker('white', (0, 0))
    pawn = board.table[0][0]

    board.promotion(pawn, 0, 0, "Q")
    assert isinstance(board.table[0][0], Queen)

    board.promotion(pawn, 1, 1, "N")
    assert isinstance(board.table[1][1], Knight)

    board.promotion(pawn, 2, 2, "R")
    assert isinstance(board.table[2][2], Rook)

    board.promotion(pawn, 3, 3, "B")
    assert isinstance(board.table[3][3], Bishop)

    board.table[0][0] = ' '
    board.table[1][0] = Walker('white', (1, 0))
    board.movement("a8Q", 1, io)
    board.draw()
    assert isinstance(board.table[0][0], Queen)

def test_castling_short_white(monkeypatch):
    """Test short (kingside) castling for white."""
    io = MockIOHandler()
    board = Board(io)
    board.table[7][4] = King("white", (7, 4))
    board.table[7][7] = Rook("white", (7, 7))
    board.table[7][5] = ' '
    board.table[7][6] = ' '
    monkeypatch.setattr("scacchi.core.pawns.whiteCastling_ks", True)
    monkeypatch.setattr("scacchi.core.pawns.whiteCastling_ql", True)
    monkeypatch.setattr("scacchi.core.pawns.blackCastling_ks", True)
    monkeypatch.setattr("scacchi.core.pawns.blackCastling_ql", True)
    result = board.castling_move(turn=1, c_type="short")

    assert result is True
    assert isinstance(board.table[7][6], King)
    assert isinstance(board.table[7][5], Rook)
    assert board.table[7][4] == ' '
    assert board.table[7][7] == ' '

def test_castling_long_black(monkeypatch):
    """Test long (queenside) castling for black."""
    io = MockIOHandler()
    board = Board(io)
    board.table[0][4] = King("black", (0, 4))
    board.table[0][0] = Rook("black", (0, 0))
    board.table[0][1] = ' '
    board.table[0][2] = ' '
    board.table[0][3] = ' '
    monkeypatch.setattr("scacchi.core.pawns.whiteCastling_ks", True)
    monkeypatch.setattr("scacchi.core.pawns.whiteCastling_ql", True)
    monkeypatch.setattr("scacchi.core.pawns.blackCastling_ks", True)
    monkeypatch.setattr("scacchi.core.pawns.blackCastling_ql", True)
    result = board.castling_move(turn=0, c_type="long")

    assert result is True
    assert isinstance(board.table[0][2], King)
    assert isinstance(board.table[0][3], Rook)
    assert board.table[0][4] == ' '
    assert board.table[0][0] == ' '

# Testing win scenarios

def test_king_in_check_by_queen():
    """Test check detection from a queen."""
    io = MockIOHandler()
    board = Board(io)
    board.table = np.full((8, 8), ' ', dtype=object)

    board.table[0][4] = King("white", (0, 4))
    board.table[4][4] = Queen("black", (4, 4))

    in_check = board.is_king_in_check("white")
    assert in_check is True

def test_king_not_in_check():
    """Test that a king is not falsely reported as in check."""
    io = MockIOHandler()
    board = Board(io)
    board.table = np.full((8, 8), ' ', dtype=object)
    board.table[0][4] = King("white", (0, 4))
    board.table[7][7] = Rook("black", (7, 7))  # Not attacking the king

    in_check = board.is_king_in_check("white")
    assert in_check is False

def test_checkmate_simple():
    """Test simple checkmate scenario."""
    io = MockIOHandler()
    board = Board(io)
    board.table = np.full((8, 8), ' ', dtype=object)
    board.table[0][0] = King("black", (0, 0))
    board.table[1][1] = Queen("white", (1, 1))
    board.table[1][0] = Rook("white", (1, 0))  # Block escape
    board.table[0][1] = Rook("white", (0, 1))  # Block escape

    assert board.is_checkmate("black") is True

def test_not_checkmate_can_escape():
    """Test that checkmate is not declared when escape is possible."""
    io = MockIOHandler()
    board = Board(io)
    board.table = np.full((8, 8), ' ', dtype=object)
    board.table[0][0] = King("black", (0, 0))
    board.table[2][2] = Queen("white", (2, 2))  # Puts king in check
    board.table[1][1] = ' '  # King can escape here

    assert board.is_checkmate("black") is False

def test_stalemate_true():
    """Test true stalemate detection."""
    io = MockIOHandler()
    board = Board(io)
    board.table = np.full((8, 8), ' ', dtype=object)
    board.table[0][7] = King("black", (0, 7))    # h8
    board.table[1][5] = King("white", (1, 5))    # f7
    board.table[2][6] = Queen("white", (2, 6))   # g6

    assert board.is_stalemate("black") is True

def test_stalemate_false_check_exists():
    """Test stalemate is not detected when check exists."""
    io = MockIOHandler()
    board = Board(io)
    board.table = np.full((8, 8), ' ', dtype=object)
    board.table[0][0] = King("black", (0, 0))       # a8
    board.table[0][1] = Queen("white", (0, 1))      # b8

    assert board.is_stalemate("black") is False

def test_stalemate_false_legal_move_exists():
    """Test stalemate is not detected when legal moves exist."""
    io = MockIOHandler()
    board = Board(io)
    board.table = np.full((8, 8), ' ', dtype=object)
    board.table[0][0] = King("black", (0, 0))
    board.table[2][2] = King("white", (2, 2))
    board.table[1][1] = Queen("white", (1, 1))
    board.table[0][1] = ' '  # Legal move

    assert board.is_stalemate("black") is False
