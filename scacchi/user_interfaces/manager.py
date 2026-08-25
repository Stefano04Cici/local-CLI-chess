from .user_input import TerminalInput, UserInputInterface
from .user_output import TerminalOutput, UserOutputInterface
from typing import Optional, cast


class UI:
    """Defines the configuration of the game's UI."""

    def __init__(self):
        """Initialize the game's UI with default settings."""
        self._ACCENT_COLOR: str = "red"
        self.RICH_COLORS = {
            "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
            "bright_black", "bright_red", "bright_green", "bright_yellow",
            "bright_blue", "bright_magenta", "bright_cyan", "bright_white"
        }

    def set_accent_color(self, accent_color: str):
        """Set the accent color for the game's UI.

        Args:
            accent_color (str): the accent color to be used in the game's UI
        Raises:
            ValueError: if the accent color is not supported by the Rich library

        """
        # If the user provides an accent color, then use it
        if accent_color in self.RICH_COLORS:
            self._ACCENT_COLOR = accent_color
        else:
            raise ValueError(
                f"Invalid accent color '{accent_color}'. "
                "Please choose a color supported by the Rich library."
            )

    def get_accent_color(self) -> str:
        """Get the accent color for the game's UI.

        Returns:
            accent color

        """
        return self._ACCENT_COLOR


class UIManager:
    """Manages the user interface components (input/output and color settings)."""

    def __init__(self, input_handler: Optional[UserInputInterface] = None,
                 output_handler: Optional[UserOutputInterface] = None):
        self.ui = UI()
        self.input_handler = input_handler if input_handler else TerminalInput()
        self.output_handler = output_handler if output_handler else TerminalOutput()

    def set_accent_color(self, color: str):
        self.ui.set_accent_color(color)

    def get_accent_color(self):
        return self.ui.get_accent_color()

    def get_input(self, prompt=""):
        if prompt:
            self.output_handler.display(prompt)
        # ``UserInputInterface`` does not expose the concrete input method to
        # the type checker, while the configured handlers provide it.
        return cast(TerminalInput, self.input_handler).get_input()

    def display(self, message: str, end=""):
        # color = self.get_accent_color()
        # styled = f"[bold {color}]{message}[/bold {color}]"
        self.output_handler.display(message)
