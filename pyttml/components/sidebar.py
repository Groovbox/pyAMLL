from textual.app import ComposeResult
from textual.widgets import Button
from textual.containers import Vertical


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
