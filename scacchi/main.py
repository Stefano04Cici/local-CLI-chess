import argparse

from scacchi.engine.commands import CommandHandler
from scacchi.engine.menu import Menu
from scacchi.user_interfaces.manager import UIManager


def main():
    """Run the Scacchi game and activate the GH workflows."""
    io_handler = UIManager()
    io_handler.set_accent_color("blue")
    cmd_handler = CommandHandler(io_handler)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true',
                        help='Show available commands')
    args = parser.parse_args()
    if args.help:
        cmd_handler.help_com()

    exit_flag = False
    while not exit_flag:
        name = io_handler.get_input(
            "\n - Welcome to [bold]chess[/bold]! Enter your name: ")

        color = io_handler.get_accent_color()
        styled_name = f"[bold {color}]{name}[/bold {color}]"
        io_handler.display(f"\n   Hello {styled_name}! "
        f"Let's start playing [bold]chess[/bold]! \n   "
        f"Type [bold green]/help[/bold green] for the list of commands ", end="\n")

        game_menu = Menu(cmd_handler=cmd_handler, io_handler=io_handler)
        game_menu.menu()
        exit_flag = True


if __name__ == "__main__":
    main()
