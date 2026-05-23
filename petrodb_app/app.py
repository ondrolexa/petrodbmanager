from textual.app import App
from textual.binding import Binding

from petrodb_app.api import APIClient
from petrodb_app.screens import LoginScreen


class PetroDBApp(App[None]):
    CSS = """
    Screen {
        background: $surface;
    }
    DataTable {
        border: solid $border;
    }
    Button {
        min-width: 12;
    }
    Input:focus {
        border: solid $accent;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.api = APIClient()

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())
