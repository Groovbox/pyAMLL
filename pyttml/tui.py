from textual.app import App, ComposeResult
from textual.widgets import Static, TextArea, Button, ListItem
from textual.containers import Horizontal
from textual.screen import Screen
from components.playerbox import PlayerBox
from player import MusicPlayer
from textual import events
from ttml import process_lyrics, Lyrics
from components.filepicker import FileNamePicker
from components.sidebar import Sidebar
from components.carousel import Carousel, ScrollDirection, VerticalScroller


CURR_LYRICS: Lyrics = None
PLAYER = MusicPlayer()


class Sync(Screen):
    lyrics_saved_state: Lyrics = None
    active_line_index: int = 0

    def compose(self) -> ComposeResult:
        yield Static("No Lyrics Loaded", id="lyrics_label")
        yield Sidebar(id="sidebar")
        yield Carousel(id="word-carousel", lyrics=CURR_LYRICS)
        yield (Horizontal(
            Button("←", id="prev_word_button"),
            Button("→", id="next_word_button"),
            Button("F", id="set_start_time",
                   tooltip="Set timestamp as the startime of the word"),
            Button("G", id="set_end_move",
                   tooltip="Set timestamp as the end of current word and start time of the next word"),
            Button("H", id="set_end_time",
                   tooltip="Set Timestamp as the endtime of the current word and stay there"),
            id="carousel_control"
        ))
        yield PlayerBox(id="player_box", player=PLAYER)

    def update_scroller(self) -> None:
        carousel: Carousel = self.query_one(Carousel)
        vertical_scroller: VerticalScroller = self.query_one(VerticalScroller)
        active_word_index = CURR_LYRICS.element_map[CURR_LYRICS.get_element_map_index(
            carousel.active_item.element)][1]

        if vertical_scroller.active_line_index > active_word_index:
            vertical_scroller.scroll(ScrollDirection.backward)
        elif vertical_scroller.active_line_index < active_word_index:
            vertical_scroller.scroll(ScrollDirection.forward)

    def on_button_pressed(self, event: Button.Pressed):
        carousel: Carousel = self.query_one(Carousel)

        if event.button.id == "next_word_button":
            carousel.move(ScrollDirection.forward)
            self.update_scroller()
        if event.button.id == "prev_word_button":
            carousel.move(ScrollDirection.backward)
            self.update_scroller()
        elif event.button.id == "set_start_time":
            active_word_index: int = CURR_LYRICS.get_element_map_index(
                carousel.active_item.element)
            CURR_LYRICS.element_map[active_word_index][0].start_time = round(
                PLAYER.get_timestamp(), 3)
            active_item_index = carousel.query_one(
                "#root")._nodes.index(carousel.active_item)
            carousel.query_one("#root")._nodes[active_item_index].update()
        elif event.button.id == "set_end_time":
            active_word_index: int = CURR_LYRICS.get_element_map_index(
                carousel.active_item.element)
            CURR_LYRICS.element_map[active_word_index][0].end_time = round(
                PLAYER.get_timestamp(), 3)
            active_item_index = carousel.query_one(
                "#root")._nodes.index(carousel.active_item)
            carousel.query_one("#root")._nodes[active_item_index].update()
        elif event.button.id == "set_end_move":
            active_word_index: int = CURR_LYRICS.get_element_map_index(
                carousel.active_item.element)
            CURR_LYRICS.element_map[active_word_index][0].end_time = round(
                PLAYER.get_timestamp(), 3)
            active_item_index = carousel.query_one(
                "#root")._nodes.index(carousel.active_item)
            carousel.query_one("#root")._nodes[active_item_index].update()
            carousel.move(ScrollDirection.forward)
            self.update_scroller()
            CURR_LYRICS.element_map[active_word_index +
                                    1][0].start_time = round(PLAYER.get_timestamp(), 3)+0.02
            carousel.query_one("#root")._nodes[active_item_index+1].update()

    def on_screen_resume(self, event: events.ScreenResume):
        label: Static = self.query_one("#lyrics_label", Static)

        if CURR_LYRICS == self.lyrics_saved_state:
            return

        if CURR_LYRICS.element_map == []:
            self.lyrics_saved_state = CURR_LYRICS
            self.query_one("#word-carousel").visible = False
            label.display = True
            return

        self.lyrics_saved_state = CURR_LYRICS
        self.query_one("#word-carousel").visible = True
        self.remove_children(ListItem)
        label.display = False

        self.mount(VerticalScroller(lyrics=CURR_LYRICS))


class Settings(Screen):
    def compose(self) -> ComposeResult:
        yield Sidebar(id="sidebar")


class Edit(Screen):
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
            def get_lyrics(content: str):
                if content != "":
                    self.query_one(".editor").text = content

            self.app.push_screen(FileNamePicker(), get_lyrics)

        elif event.button.name == "save":
            global CURR_LYRICS
            CURR_LYRICS = process_lyrics(self.query_one(".editor").text)
            self.app.notify("Saved Lyrics")


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
        self.switch_mode("edit")


if __name__ == "__main__":
    app = MainApp()
    app.run()
