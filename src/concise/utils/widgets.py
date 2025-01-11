from typing import Any, Generator, Iterable

from rich.console import RenderableType
from rich.highlighter import Highlighter
from textual.binding import Binding
from textual.containers import Container
from textual.suggester import Suggester
from textual.validation import Validator
from textual.widgets import Input, Static, TabPane, Button
from textual.widgets._input import InputType, InputValidationOn


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
        self.log(f"SOMETHING HERE=>{self.app.query_one(TabPane)}")
        self.app.set_focus(self.app.query_one(Button))