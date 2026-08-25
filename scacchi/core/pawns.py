# core/pawns.py
from abc import abstractmethod

en_passant_square = None
whiteCastling_ks = True
whiteCastling_ql = True
blackCastling_ks = True
blackCastling_ql = True


class Pawn:
    """<<Boundary>> Abstract class representing a general pawn."""

    def __init__(self, name, symbol, color, position):
        """Initialize the pawn.

        :param name: name of the pawn type, e.g., "Rook"
        :param symbol: Unicode symbol of the pawn, e.g., "♟"
        :param color: pawn color, depends on the player, e.g., "white"
        :param position: pawn position on the board, e.g., "00 00" (top-left)
        """
        self.name = name
        self.symbol = symbol
        self.color = color
        self.position = position

    def __str__(self):
        """Get the symbol of the pawn as a string."""
        return self.symbol

    def getRow(self):
        return self.position[0]

    def getColumn(self):
        return self.position[1]

    @abstractmethod
    def movementCheck(self, row1, col1, row2, col2, eat, board, turn, **kwargs):
        """Check if a move is valid and update the game.

        Checks if a move is valid depending on the piece and updates
        the state of the game or of some global variables if necessary.

        :param row1: row of the starting position in the board
        :param col1: column of the starting position in the board
        :param row2: row of the destination position in the board
        :param col2: column of the destination position in the board
        :param eat: whether the movement is a capture
        :param board: the game board
        :param turn: current player, e.g., "1" (white player)
        :return: whether the move is allowed
        """
        raise NotImplementedError("Not implemented yet")


class Walker(Pawn):
    """<<Entity>> Pawn."""

    def __init__(self, color, position):
        symbol = '\u2659' if color == 'white' else '\u265f'
        super().__init__("walker", symbol, color, position)

    def movementCheck(self, row1, col1, row2, col2, eat, board, turn, en_passant):
        global en_passant_square
        direction = -1 if self.color == 'white' else 1

        # Normal movement
        if not eat:
            if col1 == col2 and row2 == row1 + direction:
                if board[row2][col2] == ' ':
                    en_passant_square = None
                    return True

            # Initial two-square move
            elif (col1 == col2 and row2 == row1 + 2 * direction and
                  ((self.color == 'white' and row1 == 6)
                   or (self.color == 'black' and row1 == 1)) and
                  board[row1 + direction][col1] == ' ' and board[row2][col2] == ' '):
                en_passant_square = ((row1 + row2) // 2, col1)
                return True

        elif eat:
            # Diagonal movement
            if abs(col2 - col1) == 1 and row2 == row1 + direction:
                target = board[row2][col2]
                if (
                        target != ' '
                        and isinstance(target, Pawn)
                        and target.color != self.color
                ):
                    en_passant_square = None
                    return True

            if en_passant and en_passant_square is not None:
                en_passant_row, en_passant_col = en_passant_square
                if ((row2, col2) == (en_passant_row, en_passant_col) and
                        ((self.color == 'white' and row1 == 3) or
                         (self.color == 'black' and row1 == 4)) and
                        abs(col2 - col1) == 1 and row2 == row1 + direction):
                    # Confirm the pawn to capture is
                    # in the right place (adjacent square)
                    captured_pawn_pos = (row1, col2)
                    # The pawn to be captured
                    # is on the same row, adjacent column
                    captured_pawn = \
                        board[captured_pawn_pos[0]][captured_pawn_pos[1]]
                    if (
                            isinstance(captured_pawn, Pawn)
                            and captured_pawn.color != self.color
                            and captured_pawn.name == "walker"
                    ):
                        en_passant_square = None
                        return True

        else:
            return False
        return False


class Bishop(Pawn):
    """<<Entity>> Bishop."""

    def __init__(self, color, position):
        symbol = '\u2657' if color == 'white' else '\u265d'
        super().__init__("bishop", symbol, color, position)

    def movementCheck(self, row1, col1, row2, col2, eat, board, turn, **kwargs):
        row_diff = abs(row2 - row1)
        col_diff = abs(col2 - col1)

        if row_diff != col_diff:
            return False

        row_step = 1 if row2 > row1 else -1
        col_step = 1 if col2 > col1 else -1

        current_row = row1 + row_step
        current_col = col1 + col_step
        while current_row != row2 and current_col != col2:
            if board[current_row][current_col] != ' ':
                return False
            current_row += row_step
            current_col += col_step

        target = board[row2][col2]
        if target == ' ' or (eat and isinstance(target, Pawn)
                             and target.color != self.color):
            return True


class Knight(Pawn):
    """<<Entity>> Knight."""

    def __init__(self, color, position):
        symbol = '\u2658' if color == 'white' else '\u265e'
        super().__init__("knight", symbol, color, position)

    def movementCheck(self, row1, col1, row2, col2, eat, board, turn, **kwargs):
        row_diff = abs(row2 - row1)
        col_diff = abs(col2 - col1)

        if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
            target = board[row2][col2]
            if target == ' ' or (eat and isinstance(target, Pawn)
                                 and target.color != self.color):
                return True

        return False


def CastlingCheck(board1, turn, type):
    """Check if a castling is possible."""
    row = 7 if turn == 1 else 0
    king_col = 4

    king = board1.table[row][king_col]
    if (not isinstance(king, King) or
            king.color != ('white' if turn == 1 else 'black')):
        return False

    global whiteCastling_ks, whiteCastling_ql, blackCastling_ks, blackCastling_ql

    if turn == 1:  # White
        if ((type == "short" and not whiteCastling_ks)
                or (type == "long" and not whiteCastling_ql)):
            return False
    else:  # Black
        if ((type == "short" and not blackCastling_ks)
                or (type == "long" and not blackCastling_ql)):
            return False

    return not (
        (type == "short" and (board1.table[row][5] != ' ' or
                            board1.table[row][6] != ' '))
    or (type == "long" and (board1.table[row][1] != ' ' or
                             board1.table[row][2] != ' ' or
                             board1.table[row][3] != ' ')))


class King(Pawn):
    """<<Entity>> King."""

    def __init__(self, color, position):
        symbol = '\u2654' if color == 'white' else '\u265a'
        super().__init__("king", symbol, color, position)

    def movementCheck(self, row1, col1, row2, col2, eat, board, turn, **kwargs):
        row_diff = abs(row2 - row1)
        col_diff = abs(col2 - col1)

        if row_diff <= 1 and col_diff <= 1:
            target = board[row2][col2]
            if target == ' ' or (eat and isinstance(target, Pawn)
                                 and target.color != self.color):

                original_from = board[row1][col1]
                original_to = board[row2][col2]
                board[row1][col1] = ' '
                board[row2][col2] = self

                in_check = self.is_king_attacked(board, row2, col2, self.color)

                board[row1][col1] = original_from
                board[row2][col2] = original_to
                if self.color == "white":
                    global whiteCastling_ks, whiteCastling_ql
                    whiteCastling_ks = False
                    whiteCastling_ql = False
                elif self.color == "black":
                    global blackCastling_ks, blackCastling_ql
                    blackCastling_ks = False
                    blackCastling_ql = False

                return not in_check

        return False

    def is_king_attacked(self, board, king_row, king_col, king_color):
        """Check if the king can move in a spot threatened by another pawn."""
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == ' ' or piece.color == king_color:
                    continue
                if isinstance(piece, Walker):
                    if piece.movementCheck(r, c, king_row, king_col, True, board, 1 if
                    piece.color == 'white' else 0, en_passant=False):
                        return True
                else:
                    if piece.movementCheck(r, c, king_row, king_col, True, board, 1 if
                    piece.color == 'white' else 0):
                        return True
        return False


class Queen(Pawn):
    """<<Entity>> Queen."""

    def __init__(self, color, position):
        symbol = '\u2655' if color == 'white' else '\u265b'
        super().__init__("queen", symbol, color, position)

    def movementCheck(self, row1, col1, row2, col2, eat, board, turn, **kwargs):
        row_diff = abs(row2 - row1)
        col_diff = abs(col2 - col1)

        if row_diff == col_diff:
            row_step = 1 if row2 > row1 else -1
            col_step = 1 if col2 > col1 else -1
        elif row1 == row2:
            row_step = 0
            col_step = 1 if col2 > col1 else -1
        elif col1 == col2:
            row_step = 1 if row2 > row1 else -1
            col_step = 0
        else:
            return False

        current_row = row1 + row_step
        current_col = col1 + col_step
        while (current_row, current_col) != (row2, col2):
            if board[current_row][current_col] != ' ':
                return False
            current_row += row_step
            current_col += col_step

        target = board[row2][col2]
        if target == ' ' or (eat and isinstance(target, Pawn)
                             and target.color != self.color):
            return True


class Rook(Pawn):
    """<<Entity>> Rook."""

    def __init__(self, color, position):
        symbol = '\u2656' if color == "white" else '\u265c'
        super().__init__("rook", symbol, color, position)

    def movementCheck(self, row1, col1, row2, col2, eat, board, turn, **kwargs):
        global Castling
        if row1 != row2 and col1 != col2:
            return False

        if row1 == row2:
            step = 1 if col2 > col1 else -1
            for current_col in range(col1 + step, col2, step):
                if board[row1][current_col] != " ":
                    return False
        else:
            step = 1 if row2 > row1 else -1
            for current_row in range(row1 + step, row2, step):
                if board[current_row][col1] != " ":
                    return False

        target = board[row2][col2]
        if target == ' ' or (eat and isinstance(target, Pawn)
                             and target.color != self.color):
            global whiteCastling_ks, whiteCastling_ql, \
                blackCastling_ks, blackCastling_ql
            if self.color == "white":
                if col1 == 0:  # Queenside rook
                    whiteCastling_ql = False
                elif col1 == 7:  # Kingside rook
                    whiteCastling_ks = False
            elif self.color == "black":
                if col1 == 0:
                    blackCastling_ql = False
                elif col1 == 7:
                    blackCastling_ks = False
            return True
