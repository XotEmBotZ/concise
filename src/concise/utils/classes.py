import datetime
import time

import psycopg
import pytz
from textual import on
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Label,
    Pretty,
    Input,
    Static,
    TabbedContent,
    TabPane,
)

from .utils import dump_config, load_config


class Base(Static):
    timedelta = datetime.timedelta(days=-5)
    conn: reactive[psycopg.Connection | None] = reactive(None, repaint=True)
    config = reactive({})

    def __init__(self, filename: str):
        super().__init__()
        self.loading = True
        self.config = load_config(filename)

    def on_mount(self):
        self.call_after_refresh(self.init)

    def init(self):
        timestampConfig: dict | None = self.config.get("timestamp", None)
        if timestampConfig:
            self.setTimestampConfig(timestampConfig)
        self.conn = self.connect_db(self.config)
        self.loading = False

    def connect_db(self, config) -> psycopg.Connection:
        return psycopg.connect(
            f"postgresql://{config['database']['user']}:{config['database']['passwd']}@{config['database']['host']}:{config['database']['port']}/{config['database']['db']}"
        )

    def setTimestampConfig(self, config: dict) -> None:
        delta = config.get("delta", None)
        if delta:
            self.timedelta = datetime.timedelta(**delta)

    def __del__(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


class Settings(Static):
    config = reactive({})

    def __init__(self, config):
        super().__init__()
        self.config = config

    def compose(self):
        yield Label("Host")
        yield Input()


class Main(Base):
    def compose(self):
        self.tabs = TabbedContent()
        yield self.tabs

    def on_mount(self):
        self.tabs.add_pane(
            TabPane(
                "Settings",
                Settings(self.config),
                id="settingsTab",
            )
        )


# class Main(Base):
#     def d1_goal(self):
#         if not self.conn:
#             return
#         timezone: str = self.conn.execute("SHOW timezone").fetchone()[0]  # type: ignore
#         date = (
#             datetime.datetime.now(tz=pytz.timezone(timezone)) + self.timedelta
#         ).date()
#         questions = []
#         goalChoices = []
#         goals = self.conn.execute(
#             "SELECT id,name FROM goal_info WHERE is_enabled"
#         ).fetchall()
#         for id, name in goals:
#             goalChoices.append((name, id))
# questions.append(
#     inquirer.Checkbox(
#         name="goal",
#         message="What habbit have to performed today?",
#         choices=goalChoices,
#     )
# )
# answers: dict[str, list] = inquirer.prompt(questions)  # type: ignore
# goalIdSet: set[int] = {goal[0] for goal in goals}
# acheivedGoalIdSet = set(answers["goal"])
# query = "INSERT INTO d1_goal (goal,timestamp,is_acheived) VALUES (%s,%s,%s)"
# for id in goalIdSet:
#     self.conn.execute(query, (id, date, id in acheivedGoalIdSet))
# self.conn.commit()
