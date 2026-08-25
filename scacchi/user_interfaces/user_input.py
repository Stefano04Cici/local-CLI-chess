
class UserInputInterface:
    """Interface for retrieving user input."""

    def get_command(self) -> str:
        """Retrieve a command or input from the user."""
        raise NotImplementedError("Must implement get_command method")


class TerminalInput(UserInputInterface):
    """Concrete implementation of input retrieval from the terminal."""

    def get_input(self) -> str:
        return input()
