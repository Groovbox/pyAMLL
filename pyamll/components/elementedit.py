from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input, Checkbox
from parser import VocalElement
from parser.modify import LyricModifyOperation, ModificationType

class ElementEditModal(ModalScreen[LyricModifyOperation]):
    """Screen with a dialog to edit a VocalElement."""
    def __init__(self, element:VocalElement):
        self.vocal_element = element
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Edit a VocalElement", id="element_edit_label"),
            Input("", id="vocal_element_text"),
            Checkbox("Is Explicit?", id="is_explicit_checkbox"),
            Button("Delete Element", variant="error", id="delete"),
            Button("Save", variant="primary"),
            Button("Cancel", id="cancel"),
            id="element-edit-dialog"
        )

    def on_mount(self) -> None:
        self.query_one(Input).value = self.vocal_element.text

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
        elif event.button.id == "delete":
            self.dismiss(LyricModifyOperation(ModificationType.DELETE, self.vocal_element))