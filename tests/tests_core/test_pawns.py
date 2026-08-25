from scacchi.core.board import Board
from scacchi.core.pawns import (
    Bishop,
    King,
    Knight,
    Queen,
    Rook,
    Walker,
)
from scacchi.user_interfaces.manager import UIManager


def test__str__():
    """Test to verify that the __str__() method returns the piece's symbol.

    Checks that the __str__() method of all piece types returns the correct
    Unicode symbol, both for directly created pieces and those on the initialized board.
    """
    white_pawn = Walker('white', (6, 0))
    assert white_pawn.__str__() == '\u2659'
    assert str(white_pawn) == '\u2659'

    black_pawn = Walker('black', (1, 0))
    assert black_pawn.__str__() == '\u265f'
    assert str(black_pawn) == '\u265f'

    white_rook = Rook('white', (7, 0))
    assert white_rook.__str__() == '\u2656'

    black_knight = Knight('black', (0, 1))
    assert black_knight.__str__() == '\u265e'

    white_bishop = Bishop('white', (7, 2))
    assert white_bishop.__str__() == '\u2657'

    black_queen = Queen('black', (0, 3))
    assert black_queen.__str__() == '\u265b'

    white_king = King('white', (7, 4))
    assert white_king.__str__() == '\u2654'

    io_handler = UIManager()
    board = Board(io_handler)

    for row in board.table:
        for piece in row:
            if piece != ' ':
                assert str(piece) == piece.symbol
                assert piece.__str__() == piece.symbol

def test_getRow():
    """Test that verifies getRow() returns the correct row of the pieces.

    Checks that the getRow() method correctly returns the row coordinate
    for all types of pieces on the board.
    """
    test_cases = [
        Walker('white', (6, 3)),
        Walker('black', (1, 4)),
        Rook('white', (7, 0)),
        Rook('black', (0, 7)),
        Bishop('white', (7, 2)),
        Bishop('black', (0, 5)),
        Knight('white', (7, 1)),
        Knight('black', (0, 6)),
        Queen('white', (7, 3)),
        Queen('black', (0, 3)),
        King('white', (7, 4)),
        King('black', (0, 4))
    ]

    for pawn in test_cases:
        expected_row = pawn.position[0]
        assert pawn.getRow() == expected_row

def test_getColumn():
    """Test that verifies getColumn() returns the correct column.

    Checks that the getColumn() method correctly returns the column coordinate
    for all types of pieces on the board.
    """
    test_cases = [
        Walker('white', (6, 3)),
        Walker('black', (1, 4)),
        Rook('white', (7, 0)),
        Rook('black', (0, 7)),
        Bishop('white', (7, 2)),
        Bishop('black', (0, 5)),
        Knight('white', (7, 1)),
        Knight('black', (0, 6)),
        Queen('white', (7, 3)),
        Queen('black', (0, 3)),
        King('white', (7, 4)),
        King('black', (0, 4))
    ]

    for pawn in test_cases:
        expected_col = pawn.position[1]
        assert pawn.getColumn() == expected_col

def test_movementCheck():
    """Comprehensive test for movementCheck() of all pieces using a real Board."""
    io_handler = UIManager()
    board = Board(io_handler)
    test_cases = [
        {
            'name': 'White pawn',
            'piece': board.table[6][3],
            'valid_moves': [
                ((6, 3), (5, 3), False, False),
                ((6, 3), (4, 3), False, False),
            ],
            'invalid_moves': [
                ((6, 3), (7, 3), False, False),
                ((6, 3), (5, 4), False, False)
            ]
        },
        {
            'name': 'White rook',
            'piece': board.table[7][0],
            'valid_moves': [],
            'invalid_moves': [
                ((7, 0), (7, 1), False, False),
                ((7, 0), (6, 0), False, False),
                ((7, 0), (7, 4), False, False)
            ]
        }

    ]

    for case in test_cases:
        piece = case['piece']
        for (start, end, eat, en_passant) in case['valid_moves']:
            row1, col1 = start
            row2, col2 = end
            if isinstance(piece, Walker):
                assert piece.movementCheck(
                    row1, col1, row2, col2, eat, board.table, 1, en_passant)
            else:
                assert piece.movementCheck(
                    row1, col1, row2, col2, eat, board.table, 1)

        for (start, end, eat, en_passant) in case['invalid_moves']:
            row1, col1 = start
            row2, col2 = end
            if isinstance(piece, Walker):
                assert not piece.movementCheck(
                    row1, col1, row2, col2, eat, board.table, 1, en_passant)
            else:
                assert not piece.movementCheck(
                    row1, col1, row2, col2, eat, board.table, 1)

def test_is_king_attacked():
    """Check whether the king is in check."""
    io_handler = UIManager()
    board = Board(io_handler)
    king_pos = (7, 4)
    king = board.table[7][4]
    assert not king.is_king_attacked(
        board.table, king_pos[0], king_pos[1], 'white')

    board.table[6][3] = Walker('black', (6, 3))
    assert king.is_king_attacked(
        board.table, 7, 4, 'white')

    for r in range(1, 7):
        board.table[r][4] = ' '
    board.table[7][4] = Rook('white', (7, 4))
    assert king.is_king_attacked(
        board.table, 0, 4, 'black')

    board = Board(io_handler)
    board.table[5][5] = Knight('black', (5, 5))
    assert king.is_king_attacked(
        board.table, 7, 4, 'white')

    assert not king.is_king_attacked(
        board.table, 0, 4, 'black')
