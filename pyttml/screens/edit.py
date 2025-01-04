from components.filepicker import FileNamePicker, FileType
from components.sidebar import Sidebar
from ttml import process_lyrics


from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, TextArea


class EditScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Sidebar(id="sidebar")

        yield Horizontal(
            Button("Load from File", name="load"),
            Button("Save", name="save"),
        )

        yield TextArea.code_editor("", language="text", classes="editor")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.name == "load":
            def get_lyrics(location: str):
                if location != "":
                    self.query_one(".editor").text = open(location, 'r').read()

            self.app.push_screen(FileNamePicker(FileType.TEXT), get_lyrics)

        elif event.button.name == "save":
            self.app.CURR_LYRICS = process_lyrics(self.query_one(".editor").text)
            self.app.notify("Saved Lyrics")