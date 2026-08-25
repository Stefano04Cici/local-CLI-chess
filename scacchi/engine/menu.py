# from scacchi.engine.commands import CommandHandler
from scacchi.engine.match import Match


class Menu:
    """<<Boundary>> Manage the game's initial menu interface."""

    def __init__(self, cmd_handler, io_handler):
        self.exit_flag = 0
        self.cmd_handler = cmd_handler
        self.io_handler = io_handler

    def menu(self):
        """Interface function that manages the game's initial menu.

        Allows the user to enter commands to start a game, request help, or exit.
        It checks the validity of the commands and prevents the use of game commands
        if a match has not yet started.
        """
        exit_flag = 0
        while exit_flag != 5:
            input_string = self.io_handler.get_input(
                "\n - [bold green]Main Menu[/bold green] |"
                " Enter a command: ").strip()
            self.io_handler.display("\n")
            if not input_string.startswith("/"):
                self.io_handler.display("   [bold red]Not a command![/bold red]\n")
            elif input_string == "/play":
                exit_flag = self.play(cmd_handler=self.cmd_handler,
                                       io_handler=self.io_handler)
            elif input_string == "/help":
                self.cmd_handler.help_com()
            elif input_string == "/exit":
                exit_flag = self.cmd_handler.exit_game()
            elif input_string in [
                "/resign",
                "/draw",
                "/moves",
                "/board",
            ]:
                self.io_handler.display(
                    "   [bold red]You must first start a game with [/bold red]"
                    "[bold green]/play[/bold green] "
                    "[bold red]to use that command![/bold red]\n"
                )
            else:
                self.io_handler.display(f"   [bold red]Unrecognized command: "
                                        f"{input_string}[/bold red]\n")
        return exit_flag

    def play(self, cmd_handler, io_handler):
        """Create a new game by starting an instance of the Match class.

        Returns the final status of the match.
        """
        match1 = Match(cmd_handler=cmd_handler, io_handler=io_handler)
        return match1.status
