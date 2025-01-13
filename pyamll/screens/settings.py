from components.sidebar import Sidebar

from textual.app import ComposeResult
from textual.screen import Screen


class SettingsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Sidebar(id="sidebar")