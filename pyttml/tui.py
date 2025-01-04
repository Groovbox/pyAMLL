from textual.app import App

from screens.edit import EditScreen
from screens.settings import SettingsScreen
from screens.sync import SyncScreen

from player import MusicPlayer
from ttml import Lyrics


class TTMLApp(App):
    """A Textual app to create ttml files."""
    CSS_PATH = "assets/styles.tcss"
    CURR_LYRICS: Lyrics = None
    PLAYER = MusicPlayer()

    BINDINGS = [
        ("q", "quit", "Quit the app"),
        ("x", "switch_mode('settings')", "Go to Settings"),
        ("e", "switch_mode('edit')", "Switch to Edit mode"),
        ("r", "switch_mode('sync')", "Switch to Sync Mode")
    ]

    SCREENS = {
        "edit": EditScreen,
        "sync": SyncScreen,
        "settings": SettingsScreen
    }

    MODES = {
        "edit": "edit",
        "sync": "sync",
        "settings": "settings"
    }

    def on_mount(self) -> None:
        self.switch_mode("edit")


if __name__ == "__main__":
    app = TTMLApp()
    app.run()
