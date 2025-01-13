from typing import Iterable

from textual.app import App
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Footer, Header

import datetime
from typing import Literal

import psycopg
from textual.reactive import reactive
from textual.widgets import (
    Static,
    TabbedContent,
    TabPane,
)

from concise.panes.settings import GeneralSetting

from .utils.utils import dump_config, load_config
from .panes import Settings


class Base(Static):
    conn: reactive[psycopg.Connection | None] = reactive(None, recompose=True)

    def __init__(self):
        super().__init__()
        self.loading = True

    def db_init(self):
        self.loading = True
        self.conn = self.connect_db()
        self.loading = False

    def connect_db(self) -> psycopg.Connection:
        return psycopg.connect(
            self.config.get("database").get("url")  # type: ignore
        )

    def get_conn_url(self) -> str | Literal[False]:
        if not self.conn:
            return False
        connInfo = self.conn.info
        return f"postgresql://{connInfo.user}:{connInfo.password}@{connInfo.host}:{connInfo.port}/{connInfo.dbname}"

    def __del__(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


class Main(Base):
    timedelta = datetime.timedelta(days=-5)
    config: reactive[dict] = reactive({}, recompose=True)

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename: str = filename
        self.config = load_config(filename)
        timestampConfig: dict | None = self.config.get("timestamp", {})
        if timestampConfig:
            self.set_timestamp_config(timestampConfig)

    def set_timestamp_config(self, config: dict) -> None:
        delta = config.get("delta", None)
        if delta:
            self.timedelta = datetime.timedelta(**delta)

    def compose(self):
        self.tabs = TabbedContent()
        with self.tabs:
            yield TabPane(
                "Settings",
                Settings(self.config, self.conn),
                id="settingsTab",
            )

    def on_mount(self):
        self.log(GeneralSetting.ConfigChanged.handler_name)

    def on_general_setting_config_changed(self, event: GeneralSetting.ConfigChanged):
        self.config = event.config
        self.mutate_reactive(Main.config)

    def watch_config(self, old_config, new_config):
        dump_config(new_config, self.filename)
        url: str = new_config.get("database", {}).get("url", "")
        if url != self.get_conn_url() and url:
            self.call_after_refresh(self.db_init)
            self.notify(
                "Database connection activated",
                title="Database connection",
                timeout=5,
            )
        timestampConfig = new_config.get("timestamp", {})
        self.set_timestamp_config(timestampConfig)


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
