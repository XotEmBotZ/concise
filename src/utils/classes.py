import datetime

import inquirer
import psycopg
import pytz

# from .utils import *


class Base:
    timedelta = datetime.timedelta(days=-5)

    def __init__(self, config: dict):
        self.config = config
        timestampConfig: dict | None = self.config.get("timestamp", None)
        if timestampConfig:
            self.setTimestampConfig(timestampConfig)
        self.conn = self.connect_db(config)
        print("Connected")

    def connect_db(self, config) -> psycopg.Connection:
        return psycopg.connect(
            f'postgresql://{config['db']['user']}:{config['db']['passwd']}@{config['db']['host']}:{config['db']['port']}/{config['db']['db']}'
        )

    def setTimestampConfig(self, config: dict):
        delta = config.get("delta", None)
        if delta:
            self.timedelta = datetime.timedelta(**delta)

    def __del__(self):
        self.conn.close()


class Main(Base):
    def d1_goal(self):
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
        questions.append(
            inquirer.Checkbox(
                name="goal",
                message="What habbit have to performed today?",
                choices=goalChoices,
            )
        )
        answers: dict[str, list] = inquirer.prompt(questions)  # type: ignore
        goalIdSet: set[int] = {goal[0] for goal in goals}
        acheivedGoalIdSet = set(answers["goal"])
        query = "INSERT INTO d1_goal (goal,timestamp,is_acheived) VALUES (%s,%s,%s)"
        for id in goalIdSet:
            self.conn.execute(query, (id, date, id in acheivedGoalIdSet))
        self.conn.commit()
