from typing import Any, Generator, Iterable

import psycopg
from rich.console import RenderableType
from rich.highlighter import Highlighter
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.suggester import Suggester
from textual.validation import Validator
from textual.widgets import (
    Button,
    ContentSwitcher,
    Input,
    Select,
    SelectionList,
    Static,
)
from textual.widgets._input import InputType, InputValidationOn
from textual.widgets.selection_list import Selection


class EscapeInput(Input):
    BINDINGS = [Binding("escape", "escape", "Focus Next")]

    def action_escape(self):
        self.screen.focus_next()


class TextInput(Static):
    BINDINGS = [
        Binding("escape", "escape", "Escape"),
    ]

    class Changed(Input.Changed): ...

    class Submitted(Input.Submitted): ...

    def __init__(
        self,
        value: str | None = None,
        placeholder: str = "",
        highlighter: Highlighter | None = None,
        password: bool = False,
        lable: str | None = None,
        restrict: str | None = None,
        type: InputType = "text",  # type: ignore
        max_length: int = 0,
        suggester: Suggester | None = None,
        validators: Validator | Iterable[Validator] | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        select_on_focus: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
    ):
        super().__init__()
        self.cust_value = value
        self.cust_placeholder = placeholder
        self.cust_highlighter = highlighter
        self.cust_password = password
        self.cust_lable = lable
        self.cust_restrict = restrict
        self.cust_type = type
        self.cust_max_length = max_length
        self.cust_suggester = suggester
        self.cust_validators = validators
        self.cust_validate_on = validate_on
        self.cust_valid_empty = valid_empty
        self.cust_select_on_focus = select_on_focus
        self.cust_name = name  # type: ignore
        self.cust_id = id  # type: ignore
        self.cust_classes = classes
        self.cust_disabled = disabled
        self.cust_tooltip = tooltip

    DEFAULT_CSS = """
        .TextInputClass {
            height: auto;
            border: solid $secondary;
            border-title-align: left;
        }
        """

    def compose(self) -> Generator[Input, Any, None]:
        self.container = Container(
            id="cont_" + self.cust_id if self.cust_id else None,
            name="cont_" + self.cust_name if self.cust_name else None,
            classes=self.cust_classes + " TextInputClass"
            if self.cust_classes
            else " TextInputClass",
            disabled=self.cust_disabled,
        )
        self.container.border_title = self.cust_lable
        with self.container:
            yield Input(
                value=self.cust_value,
                placeholder=self.cust_placeholder,
                highlighter=self.cust_highlighter,
                password=self.cust_password,
                restrict=self.cust_restrict,
                type=self.cust_type,  # type: ignore
                max_length=self.cust_max_length,
                suggester=self.cust_suggester,
                validators=self.cust_validators,
                validate_on=self.cust_validate_on,
                valid_empty=self.cust_valid_empty,
                select_on_focus=self.cust_select_on_focus,
                name=self.cust_name,
                id=self.cust_id,
                classes=self.cust_classes,
                disabled=self.cust_disabled,
                tooltip=self.cust_tooltip,
            )

    def action_escape(self) -> None:
        self.app.set_focus(self.app.query_one(Button))


class GoalEnable(Static):
    def __init__(self, conn: psycopg.Connection | None):
        super().__init__()
        self.conn = conn
        self.id = "goalSettingEnable"
        self.border_title = "Enabled Goals"

    def fetch_goals(self) -> list[Any | tuple[int, str, bool]]:
        if not self.conn:
            return []
        return self.conn.execute("SELECT id,name,is_enabled FROM goal_info").fetchall()

    def set_enabled_goals(self, goals: tuple[tuple[int]]):
        if not self.conn:
            return
        self.cur = self.conn.cursor()
        self.cur.execute("UPDATE goal_info SET is_enabled=False;")
        self.cur.executemany(
            "UPDATE goal_info SET is_enabled=TRUE where id=%s",
            goals,
        )
        self.conn.commit()
        self.cur.close()

    def compose(self):
        self.selectionList = SelectionList(
            *[Selection(goal[1], goal[0], goal[2]) for goal in self.fetch_goals()],
            id="goalEnableList",
        )
        self.selectionList.border_title = "Select which goals to enable."
        yield self.selectionList

    def on_selection_list_selected_changed(self, event: SelectionList.SelectedChanged):
        enabledGoals: tuple[tuple[int]] = (
            (goal,) for goal in self.selectionList.selected
        )  # type: ignore
        self.set_enabled_goals(enabledGoals)


class SubmitBtn(Button): ...


class BackBtn(Button): ...


class GoalEdit(Static):
    goal: reactive[list[tuple[str, int]]] = reactive(list(tuple()))

    BINDINGS = [
        Binding("a", "add", "Add Goal"),
        Binding("u", "update", "Update Goal"),
        Binding("r", "remove", "Remove Goal"),
        Binding("s", "confirm", "Confirm"),
        Binding("b", "back", "Back"),
    ]

    class Updated(Message): ...

    def __init__(self, conn: psycopg.Connection | None):
        super().__init__()
        self.conn = conn
        self.id = "goalSettingEdit"
        self.border_title = "Edit Goals"
        self.update_goal()

    def fetch_goals(self) -> list[tuple[int, str, bool]]:
        if not self.conn:
            return []
        return self.conn.execute("SELECT id,name,is_enabled FROM goal_info").fetchall()

    def compose(self):
        self.contentSwitcher = ContentSwitcher(initial="goalEditBtn")
        with self.contentSwitcher:
            with Container(id="goalEditBtn"):
                yield Button("Add Goal", variant="success", id="goalEditActionAdd")
                yield Button(
                    "Update Goal",
                    variant="primary",
                    id="goalEditActionUpdate",
                )
                yield Button("Remove Goal", variant="error", id="goalEditActionDelete")
            with Container(id="goalEditInp"):
                yield EscapeInput(placeholder="Name")
                yield SubmitBtn("Add", id="goalEditInpAct", variant="success")
                yield BackBtn("Back", id="goalEditInpBack", variant="error")
            with Container(id="goalEditDel"):
                yield Select(
                    self.goal,  # type: ignore
                    prompt="Select Goal",
                )
                yield SubmitBtn("Delete Goal", variant="error", id="goalEditDelBtn")
                yield BackBtn("Back", id="goalEditDelBack")
            with Container(id="goalEditUpd"):
                yield Select(
                    self.goal,  # type: ignore
                    prompt="Select Goal",
                    id="goalEditUpdSel",
                )
                yield EscapeInput(id="goalEditUptInp", placeholder="Name")
                yield SubmitBtn("Update", variant="primary", id="goalEditUptBtn")
                yield BackBtn("Back", id="goalEditUpdBack")

    def set_goal_inp(self):
        self.contentSwitcher.current = "goalEditInp"
        self.app.set_focus(self.query_one("#goalEditInp Input", expect_type=Input))

    def add_goal_db(self, goal: str):
        if not self.conn:
            return
        cur = self.conn.cursor()
        cur.execute("INSERT INTO goal_info(name) VALUES (%s)", (goal,))
        self.conn.commit()
        cur.close()

    def delete_goal_db(self, goalId: int):
        if not self.conn:
            return
        cur = self.conn.cursor()
        cur.execute("DELETE FROM goal_info WHERE id=(%s)", (goalId,))
        self.conn.commit()
        cur.close()

    def update_goal_name_db(self, goalId: int, name: str):
        if not self.conn:
            return
        cur = self.conn.cursor()
        cur.execute("UPDATE goal_info SET name=%s WHERE id=(%s)", (name, goalId))
        self.conn.commit()
        cur.close()

    def watch_goal(self):
        for select in self.query(Select):
            select.set_options(self.goal)
            self.log(f"Found it {select._options},{list(self.goal)}")

    def update_goal(self):
        self.goal = [(goal[1], goal[0]) for goal in self.fetch_goals()]

    def on_select_changed(self, event: Select.Changed):
        if event.select.id == "goalEditUpdSel" and not event.select.is_blank():
            self.query_one("#goalEditUptInp", Input).value = [
                goalName for goalName, id in self.goal if id == event.select.value
            ][0]

    def action_add(self):
        self.query_one("#goalEditActionAdd", Button).press()

    def action_update(self):
        self.query_one("#goalEditActionUpdate", Button).press()

    def action_remove(self):
        self.query_one("#goalEditActionDelete", Button).press()

    def action_confirm(self):
        self.query_one(f"#{self.contentSwitcher.current} SubmitBtn", SubmitBtn).press()

    def action_back(self):
        self.query_one(f"#{self.contentSwitcher.current} BackBtn", BackBtn).press()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "add" or action == "update" or action == "remove":
            return self.contentSwitcher.current == "goalEditBtn"
        else:
            return not self.contentSwitcher.current == "goalEditBtn"

    async def on_button_pressed(self, event: Button.Pressed):
        self.log(event.button.id)
        if event.button.id == "goalEditActionAdd":
            self.set_goal_inp()
        elif event.button.id == "goalEditActionUpdate":
            self.contentSwitcher.current = "goalEditUpd"
            self.app.set_focus(self.query_one("#goalEditUpd Select"))
        elif event.button.id == "goalEditActionDelete":
            self.contentSwitcher.current = "goalEditDel"
            self.app.set_focus(self.query_one("#goalEditDel Select"))

        elif event.button.id == "goalEditInpAct":
            self.add_goal_db(
                self.query_one("#goalEditInp Input", expect_type=Input).value
            )
            self.post_message(self.Updated())
            self.contentSwitcher.current = "goalEditBtn"
            self.app.set_focus(self.query_one("#goalEditBtn Button"))
            self.update_goal()
        elif event.button.id == "goalEditDelBtn":
            select = self.query_one("#goalEditDel Select", Select)
            if select.is_blank():
                self.notify(
                    message="Please select a goal to delete",
                    title="No goal selected for deletion",
                    severity="error",
                    timeout=3,
                )
            else:
                self.delete_goal_db(select.value)  # type: ignore
                self.post_message(self.Updated())
                self.contentSwitcher.current = "goalEditBtn"
                self.app.set_focus(self.query_one("#goalEditBtn Button"))
                self.update_goal()
        elif event.button.id == "goalEditUptBtn":
            select = self.query_one("#goalEditUpdSel", Select)
            name = self.query_one("#goalEditUptInp", Input)
            if select.is_blank():
                self.notify(
                    message="Please select a goal to update",
                    title="No goal selected for updation",
                    severity="error",
                    timeout=3,
                )
            else:
                self.update_goal_name_db(select.value, name.value)  # type: ignore
                self.post_message(self.Updated())
                self.contentSwitcher.current = "goalEditBtn"
                self.app.set_focus(self.query_one("#goalEditBtn Button"))
                self.update_goal()
        elif (
            event.button.id == "goalEditInpBack"
            or event.button.id == "goalEditDelBack"
            or event.button.id == "goalEditUpdBack"
        ):
            self.contentSwitcher.current = "goalEditBtn"
            self.app.set_focus(self.query_one("#goalEditBtn Button"))
        self.refresh_bindings()
