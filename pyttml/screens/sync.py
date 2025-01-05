from components.carousel import Carousel, ScrollDirection, VerticalScroller
from components.playerbox import PlayerBox
from components.sidebar import Sidebar
from ttml import Lyrics, process_lyrics
from screens.edit import EditScreen


from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, ListItem, Static


class SyncScreen(Screen):
    lyrics_saved_state: Lyrics = None
    active_line_index: int = 0

    def compose(self) -> ComposeResult:
        yield Static("No Lyrics Loaded", id="lyrics_label")
        yield Sidebar(id="sidebar")
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
        yield PlayerBox(id="player_box", player=self.app.PLAYER)

    def update_scroller(self) -> None:
        vertical_scroller: VerticalScroller = self.query_one(VerticalScroller)
        carousel_item_line_index = self.query_one(Carousel).active_item.element.line_index

        if vertical_scroller.active_line_index > carousel_item_line_index:
            vertical_scroller.scroll(ScrollDirection.backward)
        elif vertical_scroller.active_line_index < carousel_item_line_index:
            vertical_scroller.scroll(ScrollDirection.forward)

    def on_button_pressed(self, event: Button.Pressed):
        carousel: Carousel = self.query_one(Carousel)

        if event.button.id == "next_word_button":
            carousel.move(ScrollDirection.forward)
            self.update_scroller()

        elif event.button.id == "prev_word_button":
            carousel.move(ScrollDirection.backward)
            self.update_scroller()

        elif event.button.id in ["set_start_time", "set_end_time", "set_end_move"]:
            active_word_index = self.app.CURR_LYRICS.get_element_map_index(carousel.active_item.element)
            timestamp = round(self.app.PLAYER.get_timestamp(), 3)
            active_item_index = carousel._nodes.index(carousel.active_item)
            
            if event.button.id == "set_start_time":
                self.app.CURR_LYRICS.element_map[active_word_index][0].start_time = timestamp
            
            elif event.button.id in ["set_end_time", "set_end_move"]:
                self.app.CURR_LYRICS.element_map[active_word_index][0].end_time = timestamp
                
                if event.button.id == "set_end_move":
                    carousel.move(ScrollDirection.forward)
                    self.update_scroller()
                    self.app.CURR_LYRICS.element_map[active_word_index + 1][0].start_time = timestamp + 0.02
                    carousel._nodes[active_item_index + 1].update()

            carousel._nodes[active_item_index].update()

    def on_screen_resume(self, event: events.ScreenResume):
        label: Static = self.query_one("#lyrics_label", Static)

        if self.app.CURR_LYRICS == self.lyrics_saved_state:
            return

        if self.app.CURR_LYRICS is None:
            label.display = True
            return

        self.lyrics_saved_state = self.app.CURR_LYRICS
        self.remove_children(ListItem)
        label.display = False
        self.mount(Carousel(id="word-carousel"))
        self.mount(VerticalScroller())

        self.move_child(self.query_one("#carousel_control"), after=self.query_one(Carousel))