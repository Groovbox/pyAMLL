from textual.app import App, ComposeResult
from textual.widgets import Static, TextArea, Button, Label, ProgressBar, Digits, ListItem
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from player import MusicPlayer, PlayerState
import time
from textual.reactive import reactive
from textual import events
from ttml import process_lyrics, Lyrics
from components.filepicker import FileNamePicker
from components.sidebar import Sidebar
from components.carousel import Carousel, ScrollDirection, VerticalScroller


CURR_LYRICS:Lyrics = None
PLAYER = MusicPlayer()


class PlayerBox(Horizontal):
    time = reactive(0.0)

    def compose(self) -> ComposeResult:
        yield Button("⏵", id="play_button", disabled=True)
        yield Horizontal(
            Button("⏮", id="rewind_button"),
            Button("⏭", id="forward_button"),
            id="seek_buttons",
            classes="button_group"
        )
        yield Horizontal(
            Button("⏪", id="decrease_speed_button"),
            Button("1.0", id="speed_reset"),
            Button("⏩", id="increase_speed_button"),
            id="speed_controls",
            classes="button_group"
        )
        yield Digits("00:00.00",id="current_time")
        yield Vertical(
            ProgressBar(id="progress_bar", show_eta=False, show_percentage=False),
            Horizontal (
                Button("0", id="seek_pos_0", classes="position-button"),
                Button("1", id="seek_pos_1", classes="position-button"),
                Button("2", id="seek_pos_2", classes="position-button"),
                Button("3", id="seek_pos_3", classes="position-button"),
                Button("4", id="seek_pos_4", classes="position-button"),
                Button("5", id="seek_pos_5", classes="position-button"),
                Button("6", id="seek_pos_6", classes="position-button"),
                Button("7", id="seek_pos_7", classes="position-button"),
                Button("8", id="seek_pos_8", classes="position-button"),
                Button("9", id="seek_pos_9", classes="position-button"),
                id="position_control"
            )
        )
        
        yield Label("00:00.00", id="total_time")
        yield Button("📂", id="open_file", tooltip="Enter path of music file.")

        yield Horizontal(
            Button("🔉", id="vol_down_button", tooltip="Decrease Volume"),
            Button("🔊", id="vol_up_button", tooltip="Increase Volume"),
            classes="button_group"
        )
    
    def watch_time(self, time):
        minutes, seconds = divmod(time, 60)
        _,minutes = divmod(minutes, 60)
        digit_widget = self.query_one("#current_time", Digits)
        digit_widget.update(f"{minutes:02.0f}:{seconds:05.2f}")

        # Update progress bar
        progress_bar:ProgressBar = self.query_one("#progress_bar", ProgressBar)
        progress_bar.progress = time
        

    def update_time(self) -> None:
        self.time = PLAYER.get_timestamp()
    
    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.update_time)
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        def get_path(path: str):
                if path != "":
                    global PLAYER
                    PLAYER.set_file(path)
                    time.sleep(0.3)
                    self.query_one("#play_button").disabled = False

        if event.button.id == "open_file":
            self.app.push_screen(FileNamePicker(), get_path)
        
        elif event.button.id == "play_button":
            if PLAYER.cstate == PlayerState.STOPPED:
                PLAYER.play()
                self.query_one("#progress_bar").total = PLAYER.player.get_length() / 1000
                self.query_one("#play_button").label = "⏸"
                self.query_one("#play_button").variant = "success"
                t_time_label = self.query_one("#total_time", Label)
                total_time = PLAYER.player.get_length() / 1000 # in seconds
                minutes, seconds = divmod(total_time, 60)
                t_time_label.update(content=f"{minutes:02,.0f}:{seconds:05.2f}")
                return
            
            elif PLAYER.cstate == PlayerState.PAUSED:
                PLAYER.resume()
                self.query_one("#play_button").label = "⏸"
                self.query_one("#play_button").variant = "success"
                return
            
            elif PLAYER.cstate == PlayerState.PLAYING:
                PLAYER.pause()
                self.query_one("#play_button").label = "⏵"
                self.query_one("#play_button").variant = "warning"
                return
        
        elif event.button.id == "rewind_button":
            PLAYER.seek(-5)
        
        elif event.button.id == "forward_button":
            PLAYER.seek(5)
        
        elif event.button.id == "decrease_speed_button":
            PLAYER.set_speed(PLAYER.playback_speed-0.25)
            speed_reset_button:Button = self.query_one("#speed_reset")
            speed_reset_button.label = str(PLAYER.playback_speed)

        elif event.button.id == "increase_speed_button":
            PLAYER.set_speed(PLAYER.playback_speed+0.25)
            speed_reset_button:Button = self.query_one("#speed_reset")
            speed_reset_button.label = str(PLAYER.playback_speed)
            
        elif event.button.id == "speed_reset":
            PLAYER.set_speed(1.0)
            speed_reset_button:Button = self.query_one("#speed_reset")
            speed_reset_button.label = str(PLAYER.playback_speed)
        
        elif event.button.id == "vol_down_button":
            PLAYER.change_volume(-10)
        elif event.button.id == "vol_up_button":
            PLAYER.change_volume(10)  
        
        elif "seek_pos_" in event.button.id:
            partition = int(event.button.id.split("_")[-1])
            PLAYER.seek(partition=partition)

    def on_resize(self, event:events.Resize) -> None:
        progress_bar = self.query_one(ProgressBar)
        if self.size.width < 105:
            self.query_one("#position_control").display = False
            progress_bar.styles.margin = (1,1,0,1)
            if self.size.width < 40:
                self.query_one("#total_time").display = False
            else:
                self.query_one("#total_time").display = True
        else:
            self.query_one("#position_control").display = True
            progress_bar.styles.margin = (0,1,0,1)
            self.query_one("#total_time").display = True


class Sync(Screen):
    lyrics_saved_state:Lyrics = None
    active_line_index:int = 0

    def compose(self) -> ComposeResult:
        yield Static("No Lyrics Loaded", id="lyrics_label")
        yield Sidebar(id="sidebar")
        yield Carousel(id="word-carousel", lyrics=CURR_LYRICS)
        yield(Horizontal(
            Button("←", id="prev_word_button"),
            Button("→", id="next_word_button"),  
            Button("F", id="set_start_time", tooltip="Set timestamp as the startime of the word"),
            Button("G", id="set_end_move", tooltip="Set timestamp as the end of current word and start time of the next word"),
            Button("H", id="set_end_time", tooltip="Set Timestamp as the endtime of the current word and stay there"),
            id="carousel_control"
        ))
        yield PlayerBox(id="player_box")

    def update_scroller(self) -> None:
        carousel:Carousel = self.query_one(Carousel)
        vertical_scroller:VerticalScroller = self.query_one(VerticalScroller)
        active_word_index = CURR_LYRICS.element_map[CURR_LYRICS.get_element_map_index(carousel.active_item.element)][1]

        if vertical_scroller.active_line_index>active_word_index:
            vertical_scroller.scroll(ScrollDirection.backward)
        elif vertical_scroller.active_line_index<active_word_index:
            vertical_scroller.scroll(ScrollDirection.forward)

    
    def on_button_pressed(self, event:Button.Pressed):
        carousel:Carousel = self.query_one(Carousel)

        if event.button.id == "next_word_button":
            carousel.move(ScrollDirection.forward)
            self.update_scroller()
        if event.button.id == "prev_word_button":
            carousel.move(ScrollDirection.backward)
            self.update_scroller()
        elif event.button.id == "set_start_time":
            active_word_index:int = CURR_LYRICS.get_element_map_index(carousel.active_item.element)
            CURR_LYRICS.element_map[active_word_index][0].start_time = round(PLAYER.get_timestamp(),3)
            active_item_index = carousel.query_one("#root")._nodes.index(carousel.active_item)
            carousel.query_one("#root")._nodes[active_item_index].update()
        elif event.button.id == "set_end_time":
            active_word_index:int = CURR_LYRICS.get_element_map_index(carousel.active_item.element)
            CURR_LYRICS.element_map[active_word_index][0].end_time = round(PLAYER.get_timestamp(),3)
            active_item_index = carousel.query_one("#root")._nodes.index(carousel.active_item)
            carousel.query_one("#root")._nodes[active_item_index].update()
        elif event.button.id == "set_end_move":
            active_word_index:int = CURR_LYRICS.get_element_map_index(carousel.active_item.element)
            CURR_LYRICS.element_map[active_word_index][0].end_time = round(PLAYER.get_timestamp(),3)
            active_item_index = carousel.query_one("#root")._nodes.index(carousel.active_item)
            carousel.query_one("#root")._nodes[active_item_index].update()
            carousel.move(ScrollDirection.forward)
            self.update_scroller()
            CURR_LYRICS.element_map[active_word_index+1][0].start_time = round(PLAYER.get_timestamp(),3)+0.02        
            carousel.query_one("#root")._nodes[active_item_index+1].update()


    def on_screen_resume(self, event:events.ScreenResume):
        label:Static = self.query_one("#lyrics_label", Static)

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