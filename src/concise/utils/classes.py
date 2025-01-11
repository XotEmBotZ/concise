import datetime
from typing import TypeAlias, Union

import psycopg
from textual.containers import (
    Center,
    Container,
)
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Static,
    TabbedContent,
    TabPane,
    Input,
)
from textual import on

from textual.message import Message

from .utils import load_config
from .widgets import TextInput

TomlType: TypeAlias = dict[str, dict[str, Union[int, float, str, "TomlType"]]]


class Base(Static):
    timedelta = datetime.timedelta(days=-5)
    conn: reactive[psycopg.Connection | None] = reactive(None)
    config: reactive[TomlType] = reactive({}, recompose=True)

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
        self.conn = self.connect_db()
        self.loading = False

    def connect_db(self) -> psycopg.Connection:
        return psycopg.connect(
            self.config.get("database").get("url")  # type: ignore
        )

    def setTimestampConfig(self, config: dict) -> None:
        delta = config.get("delta", None)
        if delta:
            self.timedelta = datetime.timedelta(**delta)

    def __del__(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


class Settings(Static):
    config: reactive[dict] = reactive({})

    class ConfigChanged(Message):
        def __init__(self, config: TomlType):
            self.config = config
            super().__init__()

    def __init__(self, config):
        super().__init__()
        self.config = config

    def compose(self):
        self.log("In Compose")
        dbStrInput = Container(id="DbContainer")
        dbStrInput.border_title = "Database"
        with dbStrInput:
            yield TextInput(
                placeholder=r"<db>://<username>:<password>@<host>:<port>/<database>",
                id="dbStr",
                lable="Database String",
                value=self.config.get("database", {}).get("url", None),
            )
        timedeltaContainer = Container(id="timedeltaContainer")
        timedeltaContainer.border_title = "Timedelta"
        with timedeltaContainer:
            yield TextInput(
                type="integer",
                placeholder=r"days",
                id="days",
                lable="Days",
                value=str(
                    self.config.get("timestamp", {}).get("delta", {}).get("days", None)
                ),
            )
            yield TextInput(
                type="integer",
                placeholder=r"hours",
                id="hours",
                lable="Hours",
                value=str(
                    self.config.get("timestamp", {}).get("delta", {}).get("hours", None)
                ),
            )
            yield TextInput(
                type="integer",
                placeholder=r"minutes",
                id="minutes",
                lable="Minutes",
                value=str(
                    self.config.get("timestamp", {})
                    .get("delta", {})
                    .get("minutes", None)
                ),
            )
        yield Center(
            Button("Save", variant="success", id="save"),
            Button("Reset", variant="error", id="reset"),
            id="submitBtnGrp",
        )

    @on(Button.Pressed, "#reset")
    async def handle_text_input_reset(self, event):
        await self.recompose()

    @on(Button.Pressed, "#save")
    def handle_text_input_save(self, event):
        self.config.update(database={"url": self.query_one("#dbStr", Input).value})
        self.config.update(
            timestamp={
                "delta": {
                    "days": int(self.query_one("#days", Input).value),
                    "hours": int(self.query_one("#hours", Input).value),
                    "minutes": int(self.query_one("#minutes", Input).value),
                }
            }
        )
        self.post_message(self.ConfigChanged(self.config))


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
            ),
        )
        self.log(Settings.ConfigChanged.handler_name)

    def on_settings_config_changed(self, event: Settings.ConfigChanged):
        self.config = event.config
        # self.mutate_reactive(Main.config)

    def watch_config(self, old_config, new_config):
        self.log(old_config)
        self.log(new_config)


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
