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

from ..utils.types import TomlType
from ..utils.widgets import GoalEdit, TextInput, GoalEnable


class Settings(Static):
    def __init__(self, config: dict, conn: psycopg.Connection | None):
        super().__init__()
        self.config = config
        self.conn = conn

    def compose(self):
        with TabbedContent():
            yield TabPane("Goal", GoalSetting(self.conn))
            yield TabPane("General", GeneralSetting(self.config))


class GoalSetting(Static):
    def __init__(self, conn: psycopg.Connection | None):
        super().__init__()
        self.conn = conn

    def compose(self):
        yield GoalEnable(self.conn)
        yield GoalEdit(self.conn)

    async def on_goal_edit_updated(self, event: GoalEdit.Updated):
        await self.query_one("GoalEnable").recompose()


class GeneralSetting(Static):
    config: reactive[dict] = reactive({})

    class ConfigChanged(Message):
        def __init__(self, config: TomlType):
            self.config = config
            super().__init__()

    def __init__(self, config):
        super().__init__()
        self.config = config

    def compose(self):
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
