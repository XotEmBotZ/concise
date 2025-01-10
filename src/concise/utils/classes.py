import datetime
import time

import psycopg
import pytz
from textual.reactive import reactive
from textual.widgets import Button, Static


class Base(Static):
    timedelta = datetime.timedelta(days=-5)
    conn: reactive[psycopg.Connection | None] = reactive(None, repaint=True)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init(self.config)  # type: ignore

    def init(self, config: dict):
        self.loading = True
        self.config = config
        timestampConfig: dict | None = self.config.get("timestamp", None)
        if timestampConfig:
            self.setTimestampConfig(timestampConfig)
        self.conn = self.connect_db(config)
        # await asyncio.sleep(5)
        time.sleep(5)
        self.loading = False

    def compose(self):
        yield Button("sd")

    def connect_db(self, config) -> psycopg.Connection:
        return psycopg.connect(
            f"postgresql://{config['db']['user']}:{config['db']['passwd']}@{config['db']['host']}:{config['db']['port']}/{config['db']['db']}"
        )

    def setTimestampConfig(self, config: dict):
        delta = config.get("delta", None)
        if delta:
            self.timedelta = datetime.timedelta(**delta)

    def __del__(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


class Main(Base):
    def d1_goal(self):
        if not self.conn:
            return
        timezone: str = self.conn.execute("SHOW timezone").fetchone()[0]  # type: ignore
        date = (
            datetime.datetime.now(tz=pytz.timezone(timezone)) + self.timedelta
        ).date()
        questions = []
        goalChoices = []
        goals = self.conn.execute(
            "SELECT id,name FROM goal_info WHERE is_enabled"
        ).fetchall()
        for id, name in goals:
            goalChoices.append((name, id))
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
