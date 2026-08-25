from scacchi.core.board import Board
from scacchi.engine.commands import CommandHandler


class Match:
    """<<Control>> Class that manages a chess match.

    Responsible for creating the board, managing turns,
    controlling the game flow, and tracking the match status.
    """

    def __init__(self, cmd_handler, io_handler):
        self.turn = 1  # white
        self.move_history = []
        self.status = 1
        # 1 = ongoing, 2 = ended, 3 = White Wins, 4 = Black Wins, 5 = exit, 6=Stalemate
        self.io_handler = io_handler
        self.cmd_handler = cmd_handler if cmd_handler else CommandHandler(io_handler)
        self.board1 = Board(io_handler)
        self.logic(self.board1)

    def changeTurn(self):
        self.turn = 0 if self.turn == 1 else 1

    def logic(self, board1):
        """Start the main game logic.

        Contains the main game loop: draws the board,
        takes possible input commands, manages player turns,
        and updates the match status.
        """
        self.board1.draw()
        while self.status == 1:
            if self.turn == 1:
                self.check_win()
                if self.status != 1:
                    break
                self.io_handler.display("\n[bold] - White's turn[/bold]\n")
                flag_command = (
                    self.cmd_handler.getCommands(self.board1, self.turn, self))
                if flag_command == 1:
                    self.changeTurn()
                elif flag_command != 1 and flag_command != 0:
                    self.status = flag_command

            elif self.turn == 0:
                self.check_win()
                if self.status != 1:
                    break
                self.io_handler.display("\n[bold] - Black's turn[/bold]\n")
                flag_command = (
                    self.cmd_handler.getCommands(self.board1, self.turn, self))
                if flag_command == 1:
                    self.changeTurn()
                elif flag_command != 1 and flag_command != 0:
                    self.status = flag_command

    def check_win(self):
        player_color = 'white' if self.turn == 1 else 'black'
        if self.board1.is_king_in_check(player_color):
            if self.board1.is_checkmate(player_color):
                self.status = 4 if self.turn == 1 else 3
                winner = "black" if self.turn == 1 \
                    else "white"
                self.io_handler.display(f"\n   [bold red]Checkmate!"
                                        f" Player {winner} wins.[/bold red]\n")
                self.io_handler.get_input("\n   Press enter to return"
                                          " to the main menu: ")
            else:
                pass
        else:
            if self.board1.is_stalemate(player_color):
                self.status = 6
                self.io_handler.display("\n   [bold yellow]Stalemate!"
                        " Game ended in a draw.[/bold yellow]\n")
                self.io_handler.get_input("\n   Press enter to return"
                                          " to the main menu: ")
