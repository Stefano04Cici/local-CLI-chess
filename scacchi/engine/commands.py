class CommandHandler:
    """<<Control>> Handle in-game commands and move processing.

    Responsible for handling all user commands.
    """

    def __init__(self, io_handler):
        self.io_handler = io_handler

    def getCommands(self, board1, turn, match1=None):
        """Receive and interpret user commands during the match.

        Handles the invocation of functions associated with each command.

        :param board1: board to operate on
        :param turn: player's turn, e.g., "white"
        :param match1: ongoing match
        :return: flag indicating a change in the match
        """
        input_string = self.io_handler.get_input("   Enter a command: ").strip()
        flag_move = 0

        if input_string.startswith("/"):
            if input_string == "/help":
                self.help_com()
            elif input_string == "/play":
                self.io_handler.display(
                    "[bold yellow]   Game already in progress[/bold yellow]\n")
            elif input_string == "/draw" and match1:
                flag_move = self.draw(match1)
            elif input_string == "/board":
                self.show_board(board1)
            elif input_string == "/resign" and match1:
                flag_move = self.resign(match1, turn)
            elif input_string == "/exit":
                flag_move = self.exit_game()
            elif input_string == "/moves":
                self.moves(match1)
            else:
                self.io_handler.display(f"   [bold red]Unrecognized command:"
                                        f" {input_string}[/bold red]\n")
        else:
            # If it's not a known command, try to parse it as a movement
            if self.move(board1, turn, input_string, match1, self.io_handler):
                flag_move = 1

        return flag_move

    def help_com(self):
        """Display the list of available commands during the match."""
        self.io_handler.display("\n[bold purple]   Available commands: [/bold purple]")
        self.io_handler.display("\n- [bold magenta]"
                                "Move a piece[/bold magenta]."
                                " Correct example: Ne2xg4 or e2e4")
        self.io_handler.display("\n[bold magenta]- /help [/bold magenta]-"
                                " Show the list of commands.")
        self.io_handler.display("\n[bold magenta]- /exit [/bold magenta]-"
                                " Exit the game.")
        self.io_handler.display("\n[bold magenta]- /play [/bold magenta]-"
                                " Start a new game.")
        self.io_handler.display("\n[bold magenta]- /resign [/bold magenta]-"
                                " Resign from the game and return to the main menu.")
        self.io_handler.display("\n[bold magenta]- /moves [/bold magenta]-"
                                " Show the move history.")
        self.io_handler.display("\n[bold magenta]- /draw [/bold magenta]-"
                                " Propose a draw.")
        self.io_handler.display("\n[bold magenta]- /board [/bold magenta]-"
                                " Display the board. \n\n")

    def move(self, board1, turn, move_str, match, io_handler):
        """Handle the movement of a piece on the board.

        If no positions are provided, it asks the user for input.
        Records the move in the history if successful.
        """
        if not move_str or len(move_str) > 11:
            self.io_handler.display("[bold red]   "
                                    "Unrecognized move [/bold red]\n")
            return False

        success = board1.movement(move_str, turn, io_handler)
        opponent_color = 'black' if turn == 1 else 'white'
        if board1.is_king_in_check(opponent_color):
            if board1.is_checkmate(opponent_color):
                move_str += "#"
            else:
                move_str += "+"

        if success:
            if turn == 1:
                match.move_history.append([move_str])
            else:
                if match.move_history:
                    match.move_history[-1].append(move_str)
                else:
                    match.move_history.append(["", move_str])
        return success

    def draw(self, match1):
        """Handle a draw proposal from a player.

        If accepted, sets the match status to draw.
        """
        flag = 3
        temp = True
        while temp:
            if match1.status:
                flag = 0
                self.io_handler.display(
                    "\n [bold cyan]- Draw proposal[/bold cyan] \n")
                input_string = self.io_handler.get_input(
                    "   Do you accept the draw? (Y/N): ")
                if input_string.lower() == "y":
                    self.io_handler.display(
                        " [bold cyan]  Draw accepted[/bold cyan]\n")
                    flag = 3
                    temp = False
                elif input_string.lower() == "n":
                    self.io_handler.display(
                        "  [bold yellow] Draw not accepted [/bold yellow]\n")
                    temp = False
                else:
                    self.io_handler.display(
                        "[bold red]   Invalid response [/bold red]\n")
        return flag

    def show_board(self, board1):
        """Display the board."""
        board1.draw()

    def resign(self, match1, turn):
        """Handle a player's voluntary resignation.

        Confirms the intent, awards victory to the opponent,
        and updates the match status.
        """
        flag = 0
        temp = True
        while temp:
            if match1.status:
                response = self.io_handler.get_input(
                    "\n - Do you really want to resign? (Y/N): ")
                if response.lower() == 'n':
                    self.io_handler.display(
                        "[bold yellow]   Resignation"
                        " request refused.[/bold yellow]\n")
                    temp = False
                elif response.lower() == 'y':
                    if turn == 0:
                        self.io_handler.display(
                            "\n   [bold green]Player [/bold green]"
                            "[bold purple]black[/bold purple]"
                            " [bold green]wins by resignation.[/bold green]\n")
                    elif turn == 1:
                        self.io_handler.display(
                            "\n   [bold green]Player [/bold green]"
                            " [bold white]white[/bold white] "
                            "[bold green]wins by resignation.[/bold green]\n")
                    flag = 2
                    temp = False
                else:
                    self.io_handler.display(
                        "   [bold red]Invalid response [/bold red]\n")
        return flag

    def exit_game(self):
        """Exit the game.

        Asks for confirmation and terminates execution if confirmed.
        """
        flag = 0
        temp = True
        while temp:
            response = self.io_handler.get_input(
                "\n - Do you really want to exit? (Y/N): ")
            if response.lower() == 'n':
                self.io_handler.display(
                    "[bold yellow]   Exit"
                    " refused.[/bold yellow]\n")
                temp = False
            elif response.lower() == 'y':
                self.io_handler.display(
                    "\n[bold green]   Thank you for"
                    " playing : ) [/bold green]\n \n \n")
                flag = 5
                temp = False
            else:
                self.io_handler.display(
                    "   [bold red]Invalid response [/bold red]\n")
        return flag

    def moves(self, match):
        """Display the move history."""
        if not match.move_history:
            self.io_handler.display(
                "   [bold yellow]No moves recorded [/bold yellow]\n")
            return

        self.io_handler.display(
            "\n   [bold blue]Move history: [/bold blue]\n")
        for i, turn in enumerate(match.move_history, 1):
            white = turn[0] if len(turn) > 0 else ""
            black = turn[1] if len(turn) > 1 else ""
            self.io_handler.display(f"   [bold blue]{i}.[/bold blue]"
                                    f" [bold]{white}[/bold],"
                                    f" [bold purple]{black}[/bold purple]\n")
