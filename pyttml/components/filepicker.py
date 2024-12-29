from textual.app import ComposeResult
from textual.widgets import Button, Label, Input
from textual.containers import Grid
from textual.screen import ModalScreen


class FileNamePicker(ModalScreen[str]):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Enter the path of file", id="file-picker-label"),
            Input(placeholder="", id="file-picker-input"),
            Button("Enter", variant="primary", id="submit"),
            Button("Cancel", variant="error", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss("")
        else:
            location = self.query_one("#file-picker-input").value
            if location.endswith(".txt"):
                content = open(location).read()
            else:
                content = location
            self.dismiss(content)