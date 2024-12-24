from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Tabs, Tab, Static, TextArea, Button, Label, Input
from textual.containers import Horizontal, Grid, Vertical
from textual.screen import Screen, ModalScreen

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
            content = open(location).read()
            self.dismiss(content)


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Button(
            label="Edit",
            id="nav_edit_button",
            tooltip="Switch to Edit Screen",
        )
        yield Button(
            label="Sync",
            id="nav_sync_button",
            tooltip="Switch to Sync Screen",
        )
        yield Button(
            label="Settings",
            id="nav_settings_button",
            tooltip="Switch to Settings Screen",
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "nav_edit_button":
            self.app.switch_mode("edit")
        elif event.button.id == "nav_sync_button":
            self.app.switch_mode("sync")
        elif event.button.id == "nav_settings_button":
            self.app.switch_mode("settings")
    
    def on_mount(self) -> None:
        if self.app.current_mode == "edit":
            self.query_one("#nav_edit_button").disabled = True
        elif self.app.current_mode == "sync":
            self.query_one("#nav_sync_button").disabled = True
        elif self.app.current_mode == "settings":
            self.query_one("#nav_settings_button").disabled = True
    


class Sync(Screen):
    def compose(self) -> ComposeResult:
        yield Sidebar(id="sidebar")

class Settings(Screen):
    def compose(self) -> ComposeResult:
        yield Sidebar(id="sidebar")

class Edit(Screen):
    def compose(self) -> ComposeResult:
        yield Sidebar(id="sidebar")
        
        yield Horizontal(
            Button("Load from File", name="load"),
            Button("Save", name="save"),
            classes="button_group"
        )

        yield TextArea.code_editor("", language="text", classes="editor")
    
    def on_mount(self) -> None:
        self.query_one("#sidebar").query_one("#nav_edit_button").disabled = True
    
    
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.name == "load":
            def get_lyrics(content: str):
                if content != "":
                    self.query_one(".editor").text = content

            self.app.push_screen(FileNamePicker(), get_lyrics)
        elif event.button.name == "save":
            self.remove_class("started")
    
    def on_tab_change(self, event: Tab.Clicked) -> None:
        quit()


class MainApp(App):
    """A Textual app to create ttml files."""
    CSS_PATH = "assets/styles.tcss"

    BINDINGS = [
                ("j", "move_down", "Move down"),
                ("k", "move_up", "Move up"),
                ("f", "move_right", "Move right"),
                ("d", "move_left", "Move left"),
                ("[", "decrease_speed", "Decrease speed"),
                ("]", "increase_speed", "Increase speed"),
                ("-", "seek_backward", "Seek backward"),
                ("=", "seek_forward", "Seek forward"),
                ("p", "pause", "Pause"),
                ("c", "set_start_time", "Set start time"),
                ("v", "set_end_time", "Set end time"),
                ("q", "quit", "Quit the app")]

    MODES = {
        "edit": Edit,
        "sync": Sync,
        "settings": Settings
    }


    def on_mount(self) -> None:
        # Push screen
        self.switch_mode("edit")



if __name__ == "__main__":
    app = MainApp()
    app.run()