import datetime
from typing import Literal, TypeAlias, Union

import psycopg
from textual import on
from textual.containers import (
    Center,
    Container,
)
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Input,
    Static,
    TabbedContent,
    TabPane,
)

from .utils import load_config
from .widgets import TextInput

TomlType: TypeAlias = dict[str, dict[str, Union[int, float, str, "TomlType"]]]


class Base(Static):
    conn: reactive[psycopg.Connection | None] = reactive(None)

    def __init__(self):
        super().__init__()
        self.loading = True

    def on_mount(self):
        # self.call_after_refresh(self.init)
        ...

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
    timedelta = datetime.timedelta(days=-5)
    config: reactive[dict] = reactive({}, recompose=True)

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.config = load_config(filename)
        timestampConfig: dict | None = self.config.get("timestamp", None)
        if timestampConfig:
            self.setTimestampConfig()

    def setTimestampConfig(self) -> None:
        delta = self.config.get("timestamp", {}).get("delta", None)
        if delta:
            self.timedelta = datetime.timedelta(**delta)

    def compose(self):
        self.tabs = TabbedContent()
        with self.tabs:
            yield TabPane(
                "Goal",
                Settings(self.config),
                id="goalTab",
            )
            yield TabPane(
                "Settings",
                Settings(self.config),
                id="settingsTab",
            )

    def on_mount(self):
        self.log(Settings.ConfigChanged.handler_name)

    def on_settings_config_changed(self, event: Settings.ConfigChanged):
        self.config = event.config
        self.mutate_reactive(Main.config)

    def watch_config(self, old_config, new_config):
        url: str = new_config.get("database", {}).get("url", "")
        if url != self.get_conn_url() and url:
            self.call_after_refresh(self.db_init)
            self.notify(
                "Database connection activated",
                title="Database connection",
                timeout=5,
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
