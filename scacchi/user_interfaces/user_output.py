from rich import print


class UserOutputInterface:
    """Interface for displaying messages to the user."""

    def display(self, message: str) -> None:
        """Display a message to the user."""
        raise NotImplementedError("Must implement display method")


class TerminalOutput(UserOutputInterface):
    """Concrete implementation for outputting messages to the terminal."""

    def display(self, message, end=""):
        print(message, end=end)
