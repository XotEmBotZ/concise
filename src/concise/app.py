from typing import Iterable

from textual.app import App
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Footer, Header

from .utils.classes import Main


class MainApp(App):
    CSS_PATH = "app.css"
    TITLE = "Concise"
    SUB_TITLE = "Terminal Based Journaling and goal tracking"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    def compose(self) -> Iterable[Widget]:
        yield Header(name="Concise", show_clock=True)
        yield Main(filename="config.toml")
        yield Footer()
