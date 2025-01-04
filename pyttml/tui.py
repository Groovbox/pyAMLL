from textual.app import App

from screens.edit import EditScreen
from screens.settings import SettingsScreen
from screens.sync import SyncScreen

from player import MusicPlayer
from ttml import Lyrics


class TTMLApp(App):
    """A Textual app to create ttml files."""

    CSS_PATH = [
        "styles/base.tcss",
        "styles/filenamepicker.tcss",
        "styles/sidebar.tcss",
        "styles/carousel.tcss",
        "styles/playerbox.tcss",
    ]

    CURR_LYRICS: Lyrics = None
    PLAYER = MusicPlayer()

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
