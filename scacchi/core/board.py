# core/board.py
import numpy as np
from typing import Any

from scacchi.core.pawns import (
    Bishop,
    CastlingCheck,
    King,
    Knight,
    Pawn,
    Queen,
    Rook,
    Walker,
)


class Board:
    """<<Entity>> Chessboard.

    Define the chessboard at the start of the game and
    manage piece movements and board updates.
    """

    def __init__(self, io_handler):
        self.rows = 8
        self.columns = 8
        self.table = np.full((self.rows, self.columns), ' ', dtype=object)
        self.io_handler = io_handler
        self.check_state = {
            "in_check": False,
            "player": None  # "white" or "black"
        }
        self.checkMate = {
            "status": False,
            "player": None
        }
        self.setPawns()

    def setPawns(self):
        """Set the initial positions of the pieces."""
        for col in range(8):
            self.table[6][col] = Walker('white', (6, col))
            self.table[1][col] = Walker('black', (1, col))

        self.table[0][0] = Rook('black', (0, 0))
        self.table[0][7] = Rook('black', (0, 7))
        self.table[7][0] = Rook('white', (7, 0))
        self.table[7][7] = Rook('white', (7, 7))

        self.table[0][1] = Knight('black', (0, 1))
        self.table[0][6] = Knight('black', (0, 6))
        self.table[7][1] = Knight('white', (7, 1))
        self.table[7][6] = Knight('white', (7, 6))

        self.table[0][2] = Bishop('black', (0, 2))
        self.table[0][5] = Bishop('black', (0, 5))
        self.table[7][2] = Bishop('white', (7, 2))
        self.table[7][5] = Bishop('white', (7, 5))

        self.table[0][3] = Queen('black', (0, 3))
        self.table[7][3] = Queen('white', (7, 3))

        self.table[0][4] = King('black', (0, 4))
        self.table[7][4] = King('white', (7, 4))

        '''self.table[0][7] = King('black', (0, 7))
        self.table[1][6] = Walker('black', (1, 6))
        self.table[1][7] = Walker('black', (1, 7))
        self.table[2][5] = Queen('white', (2, 5))
        self.table[7][4] = King('white', (7, 4))'''


    def movement(self, input_movement, turn, io_handler):
        """Handle and validate a player's move.

        Parses the input move, checks the validity of the selected piece
        and destination, updates the board accordingly and redraws it.

        :param input_movement: string in algebraic chess notation (e.g., 'e2e4')
        :param turn: integer representing the current turn (1 for white, 0 for black)
        :param io_handler: handler for output statements
        :return: True if the move is valid and executed, False otherwise
        """
        promotion_flag = False
        try:
            (pawn_type, row1, col1, eat, row2, col2, en_passant, ks_castling,
             ql_castling, promotion_piece) = self.input_extraction(input_movement)

            if ks_castling:
                self.castling_move(turn, c_type="short")
                return True

            if ql_castling:
                self.castling_move(turn, c_type="long")
                return True

            if isinstance(pawn_type, str):
                pawn_type = Walker

            row1, col1 = self.source_piece_finder(
                pawn_type, row2, col2, col1, row1, eat, en_passant, self.table, turn
            )

        except ValueError as e:
            io_handler.display(f"[bold red]   Error: {e}[/bold red]\n")
            return False

        # NumPy's type stubs infer a chained object-array index as an ndarray,
        # although this board cell contains a chess piece.
        piece: Any = self.table[row1][col1]
        opponent_color = 'black' if turn == 1 else 'white'
        player_color = 'white' if turn == 1 else 'black'
        original_piece = self.table[row2][col2]  # Save board state in case of rollback
        original_en_passant = self.table[row1][col2] if en_passant else None
        if en_passant:
            self.table[row1][col2] = ' '
        self.table[row2][col2] = piece
        self.table[row1][col1] = ' '

        # Checking if my king is in check because of a recent opponent move
        if self.is_king_in_check(player_color):
            self.table[row1][col1] = piece
            self.table[row2][col2] = original_piece
            if en_passant:
                self.table[row1][col2] = original_en_passant
            io_handler.display("[bold red]   Illegal move: "
                               "your king would be in check.[/bold red]\n")
            return False

        if hasattr(piece, 'position'):
            piece.position = (row2, col2)
            if (isinstance(piece, Walker) and
                    ((piece.color == 'white' and row2 == 0)
                     or (piece.color == 'black' and row2 == 7))):
                self.promotion(piece, col2, row2, promotion_piece)
                promotion_flag = True

        self.draw()
        io_handler.display(
            f"   {piece} "
            f"[bold green]moved from [/bold green]"
            f"[bold]{chr(col1 + 97)}{8 - row1}[/bold] "
            f"[bold green]to[/bold green]"
            f"[bold] {chr(col2 + 97)}{8 - row2}[/bold]"
        )
        if promotion_flag:
            io_handler.display("[bold green] and promoted![/bold green]")

        io_handler.display("\n")

        # Checking if the opponent king is in check for my recent move
        if self.is_king_in_check(opponent_color):
            self.check_state["in_check"] = True
            self.check_state["player"] = opponent_color
            if opponent_color == "white":
                io_handler.display("\n   [bold red]White player"
                               " is in check![/bold red]\n")
            elif opponent_color == "black":
                io_handler.display("\n   [bold red]Black player"
                                   " is in check![/bold red]\n")

            if self.is_checkmate(opponent_color):
                self.checkMate["status"] = True
                self.checkMate["player"] = opponent_color
        else:
            self.check_state["in_check"] = False
            self.check_state["player"] = None

        return True

    def draw(self):
        files = "[bold cyan]    a   b   c   d   e   f   g   h[/bold cyan]"
        self.io_handler.display(f"\n   [bold]{files}[/bold]")
        self.io_handler.display("\n   [bold]  +[/bold]" + "[bold]---+[/bold]" * 8)
        self.io_handler.display("\n")
        for i in range(8):
            row = self.table[i]
            line = f"   [bold]{8 - i} |[/bold]"
            for cell in row:
                if cell == ' ' or cell is None:
                    symbol = "   "
                else:
                    # If the cell contains a pawn, we use the Symbol
                    symbol = f" {getattr(cell, 'symbol', ' ')} "
                line += symbol + "[bold]|[/bold]"
            self.io_handler.display(line + f" [bold]{8 - i}[/bold]\n")
            self.io_handler.display("   [bold]  +[/bold]" +
                                    "[bold]---+[/bold]" * 8 + "\n")
        self.io_handler.display(f"   [bold]{files}[/bold]\n\n")

    def input_extraction(self, move_str):
        """Parse and interpret the input string representing a move.

        Extracts the necessary information to identify the piece type,
        the optional starting position (for disambiguation),
        the destination, and whether the move is a capture.

        :param move_str: string in chess notation (e.g., 'Nxa3', 'e4', 'Rg1f1')
        :return: tuple containing piece type, starting row and column (if specified),
        capture flag, destination row and column, en passant flag, castling flag
        (if applied), and promotion piece (if applied).
        """
        move_str = move_str.strip()
        kingside_short_castling = False
        queenside_long_castling = False
        promotion_piece = None
        if '0-0-0' in move_str:
            pawn_type = King
            eat = False
            en_passant = False
            row1, col1 = 7, 4
            row2, col2 = 7, 2
            queenside_long_castling = True
            return (pawn_type, row1, col1, eat, row2, col2, en_passant,
                    kingside_short_castling, queenside_long_castling,
                    promotion_piece)

        if '0-0' in move_str:
            pawn_type = King
            eat = False
            en_passant = False
            row1, col1 = 7, 4
            row2, col2 = 7, 6
            kingside_short_castling = True
            return (pawn_type, row1, col1, eat, row2, col2, en_passant,
                    kingside_short_castling, queenside_long_castling,
                    promotion_piece)

        if len(move_str) > 2:
            # Check if there's a promotion piece at the end or after '='
            if '=' in move_str:
                idx = move_str.index('=')
                if (idx + 1 < len(move_str) and move_str[idx + 1]
                        in ['Q', 'R', 'B', 'N']):
                    promotion_piece = move_str[idx + 1]
                    move_str = move_str[:idx]
            elif move_str[-1] in ['Q', 'R', 'B', 'N']:
                promotion_piece = move_str[-1]
                move_str = move_str[:-1]

        eat = 'x' in move_str
        en_passant = 'e.p.' in move_str or 'e.p' in move_str or 'ep' in move_str
        move_str = move_str.replace('x', '').replace('-', '').replace(" ", "")
        move_str = move_str.replace('#', '').replace('+', '').replace("++", "")
        move_str = move_str.replace('e.p.', '').replace('e.p', '').replace('ep', '')
        destination = move_str[-2:]
        if (len(destination) != 2 or
                destination[0] not in 'abcdefgh' or
                destination[1] not in '12345678'):
            raise ValueError("Invalid position format!"
                             " Correct example: Ne2xg4 or e2e4")
        col2 = self.position_conversion_single(destination[0])
        row2 = self.position_conversion_single(destination[1])
        origin_hint = move_str[:-2]

        piece_letters = {
            'N': Knight,
            'R': Rook,
            'B': Bishop,
            'Q': Queen,
            'K': King
        }

        pawn_type = 'walker'
        if origin_hint and origin_hint[0] in piece_letters:
            pawn_type = piece_letters[origin_hint[0]]
            origin_hint = origin_hint[1:]

        row1 = col1 = None
        if origin_hint:
            for ch in origin_hint:
                if ch in 'abcdefgh':
                    col1 = self.position_conversion_single(ch)
                elif ch in '12345678':
                    row1 = self.position_conversion_single(ch)

        return (pawn_type, row1, col1, eat, row2, col2,
                en_passant, kingside_short_castling,
                queenside_long_castling, promotion_piece)

    def position_conversion_single(self, value):
        """Convert a single algebraic notation value to a numeric value.

        If the value is a letter, it converts the column (a-h) to a number (0-7).
        If the value is a number, it converts the row (1-8) to a number (7-0).
        Includes bounds checking for invalid values.
        """
        if value in 'abcdefgh':
            return ord(value) - ord('a')
        elif value in '12345678':
            return 8 - int(value)
        raise ValueError(f"Invalid value: {value}")

    def source_piece_finder(self, pawn_type, row2, col2, col1, row1, eat,
                            en_passant, table, turn):
        """Validate the position of the piece to move on the board.

        Searches for the correct piece to move based on its type, destination,
        player color, and any starting position hints.
        If a starting position (row/column) is specified, it verifies
        the piece at that location by checking if the movement is possible.
        Otherwise, it looks for all compatible pieces on the board, finds
        the piece and checks if the movement is possible. If multiple
        pieces apply for the same move, an error is returned and the user
        will have to specify the starting row and column.

        :param pawn_type: class of the piece to move (e.g., Knight, Queen)
        :param row2: row of the destination square (0-7)
        :param col2: column of the destination square (0-7)
        :param col1: suggested source column, if provided (0-7 or None)
        :param row1: suggested source row, if provided (0-7 or None)
        :param table: 8x8 matrix representing the current board state
        :param turn: integer (1 for white, 0 for black), indicates the player's color
        :return: a tuple (row1, col1) with the valid position of the piece to move
        :raises ValueError:
        - If the piece at the specified position is invalid or cannot move.
        - If no compatible pieces exist for the move.
        - If multiple compatible pieces exist and disambiguation is missing.
        """
        color = 'white' if turn == 1 else 'black'

        if row1 is not None and col1 is not None:
            piece = table[row1][col1]
            # target = table[row2][col2]

            if piece == ' ':
                raise ValueError("You cannot move an empty space!")
            if piece.color != color:
                raise ValueError("You cannot move opponent's pieces!")
            if isinstance(piece, Walker):
                if not piece.movementCheck(row1, col1, row2, col2, eat,
                                           table, turn, en_passant):
                    raise ValueError("Illegal move!")
            elif not piece.movementCheck(row1, col1, row2, col2, eat,
                                         table, turn):
                raise ValueError("Illegal move! That piece cannot make "
                                 "that movement!")

            return row1, col1

        else:
            candidates = []

            for r in range(8):
                for c in range(8):
                    piece = table[r][c]
                    if piece == ' ':
                        continue

                    if not isinstance(piece, pawn_type):
                        continue

                    if piece.color != color:
                        continue

                    if isinstance(piece, Walker):
                        if not piece.movementCheck(r, c, row2, col2, eat,
                                                   table, turn, en_passant):
                            continue
                    else:
                        if not piece.movementCheck(r, c, row2, col2, eat,
                                                   table, turn):
                            continue

                    if row1 is not None and r != row1:
                        continue
                    if col1 is not None and c != col1:
                        continue

                    candidates.append((r, c))

            if len(candidates) == 0:
                raise ValueError("No valid piece found for this move.")
            elif len(candidates) > 1:
                raise ValueError("Ambiguity: specify the starting row or column.")

        return candidates[0]

    def promotion(self, piece, col2, row2, choice):
        """Promote a pawn."""
        if choice is None:
            choice = "Q"

        self.table[row2][col2] = ' '
        if choice == "Q":
            self.io_handler.display("\n   You chose"
                                    " the [bold cyan]Queen[/bold cyan].\n")
            self.table[row2][col2] = Queen(piece.color, (row2, col2))
        elif choice == "N":
            self.io_handler.display("\n   You chose"
                                    " the [bold cyan]Knight[/bold cyan].\n")
            self.table[row2][col2] = Knight(piece.color, (row2, col2))
        elif choice == "R":
            self.io_handler.display("\n   You chose"
                                    " the [bold cyan]Rook[/bold cyan].\n")
            self.table[row2][col2] = Rook(piece.color, (row2, col2))
        elif choice == "B":
            self.io_handler.display("\n   You chose"
                                    " the [bold cyan]Bishop[/bold cyan].\n")
            self.table[row2][col2] = Bishop(piece.color, (row2, col2))

    '''def choose(self):
        """Choose a piece to promote."""
        self.io_handler.display("\n[bold green] - A pawn has"
                                " reached the last rank![/bold green]")
        self.io_handler.display("\n - Choose a new piece: ")
        self.io_handler.display("\n[bold cyan]   [Q][/bold cyan] Queen")
        self.io_handler.display("\n[bold cyan]   [R][/bold cyan] Rook")
        self.io_handler.display("\n[bold cyan]   [B][/bold cyan] Bishop")
        self.io_handler.display("\n[bold cyan]   [N][/bold cyan] Knight")

        while True:
            choice = self.io_handler.get_input(
                "\n   Choose an option: (Q/R/B/N): ").strip().upper()
            if choice in ['Q', 'R', 'B', 'N']:
                return choice
            else:
                self.io_handler.display(
                    "   [bold red]Invalid input."
                    " Choose between Q, R, B, or N.[/bold red]\n")'''

    def castling_move(self, turn, c_type):
        """Do the special move short or long castling."""
        if not CastlingCheck(self, turn, c_type):
            raise ValueError("Invalid castling: rules not satisfied.")

        else:
            row = 7 if turn == 1 else 0
            king_col = 4
            king = self.table[row][king_col]
            if c_type == "short":
                self.table[row][6] = king
                self.table[row][4] = ' '
                king.position = (row, 6)

                rook = self.table[row][7]
                self.table[row][5] = rook
                self.table[row][7] = ' '
                rook.position = (row, 5)
                self.io_handler.display("\n")
                self.draw()
                self.io_handler.display("[bold green]  Kingside castling"
                                    " performed successfully! [/bold green]\n")
                return True

            elif c_type == "long":
                self.table[row][2] = king
                self.table[row][4] = ' '
                king.position = (row, 2)

                rook = self.table[row][0]
                self.table[row][3] = rook
                self.table[row][0] = ' '
                rook.position = (row, 3)
                self.io_handler.display("\n")
                self.draw()
                self.io_handler.display("[bold green]  Queenside castling "
                                        "performed successfully! [/bold green]\n")
                return True

    def is_king_in_check(self, color):
        """Find king position and check whether it is in check."""
        for r in range(8):
            for c in range(8):
                piece = self.table[r][c]
                if isinstance(piece, King) and piece.color == color:
                    return piece.is_king_attacked(self.table, r, c, color)
        return False

    def is_checkmate(self, color_in_check):
        """Find king position and check if it is in a checkmate."""
        if not self.is_king_in_check(color_in_check):
            return False  # Not in check

        turn = 1 if color_in_check == 'white' else 0

        for r in range(8):
            for c in range(8):
                piece = self.table[r][c]
                if piece == ' ' or piece.color != color_in_check:
                    continue

                # Try every possible destination
                for dst_r in range(8):
                    for dst_c in range(8):
                        eat = isinstance(self.table[dst_r][dst_c], Pawn) and \
                              self.table[dst_r][dst_c].color != color_in_check
                        if isinstance(piece, Walker):
                            if not piece.movementCheck(r, c, dst_r, dst_c, eat,
                                                       self.table, turn, False):
                                continue
                        else:
                            if not piece.movementCheck(r, c, dst_r, dst_c, eat,
                                                       self.table, turn):
                                continue
                        # Simulate move
                        orig_src, orig_dst = self.table[r][c], self.table[dst_r][dst_c]
                        self.table[dst_r][dst_c] = piece
                        self.table[r][c] = ' '
                        safe = not self.is_king_in_check(color_in_check)
                        self.table[r][c] = orig_src
                        self.table[dst_r][dst_c] = orig_dst

                        if safe:
                            return False  # There's at least one escape

        return True  # No legal escape moves = checkmate

    def is_stalemate(self, color):
        if self.is_king_in_check(color):
            return False  # If it's in a check it cant be in a stalemate

        for r in range(8):
            for c in range(8):
                piece = self.table[r][c]
                if piece == ' ' or piece.color != color:
                    continue

                for dst_r in range(8):
                    for dst_c in range(8):
                        turn = 1 if color == 'white' else 0
                        eat = (isinstance(self.table[dst_r][dst_c], Walker)
                               and self.table[dst_r][dst_c].color != color)
                        if isinstance(piece, Walker):
                            if not piece.movementCheck(r, c, dst_r, dst_c, eat,
                                                self.table, turn, False):
                                continue
                        else:
                            if not piece.movementCheck(r, c, dst_r, dst_c, eat,
                                                       self.table, turn):
                                continue

                        orig_src, orig_dst = self.table[r][c], self.table[dst_r][dst_c]
                        self.table[dst_r][dst_c] = piece
                        self.table[r][c] = ' '

                        safe = not self.is_king_in_check(color)

                        self.table[r][c] = orig_src
                        self.table[dst_r][dst_c] = orig_dst

                        if safe:
                            return False  # At least 1 legal move

        return True  # No legal move + no check = stalemate
