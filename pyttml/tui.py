from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Tabs, Tab, Static, TextArea, Button, Label, Input, ProgressBar, Digits, ListItem, ListView
from textual.containers import Horizontal, Grid, Vertical
from textual.screen import Screen, ModalScreen
import vlc
from player import MusicPlayer, PlayerState
import time
from textual.reactive import reactive
from textual import events

CURR_LYRICS = ""
PLAYER = MusicPlayer()

class CarouselElement(Vertical):
    def __init__(self, *children, name = None, id = None, classes = None, disabled = False,
                 start_time="00:00.00", end_time = "00.00.00", text = "Foo", is_active=False):
    
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        self.is_active = is_active

        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield Label(self.start_time, id="start_time")
        yield Label(self.text, classes="element_text")
        yield Label(self.end_time, id="end_time")
    
    def toggle_timestamps(self, hide=None):
        start_time_label = self.query_one("#start_time")
        end_time_label = self.query_one("#end_time")

        if hide is not None and isinstance(hide, bool):
            start_time_label.visible = not(hide)
            end_time_label.visible = not(hide)
            return
        
        start_time_label.visible = not(start_time_label.visible)
        start_time_label.visible = not(start_time_label.visible)
    
    def set_state(self, active):
        if active:
            self.is_active = True
            self.classes = "active"
            self.toggle_timestamps(False)
            return
        
        self.is_active = False
        self.classes = ""
        self.toggle_timestamps(True)
    
    def on_mount(self):
        self.set_state(self.is_active)
    
    def __str__(self):
        return self.text


class WordCarousel(Vertical):
    def compose(self) -> ComposeResult:
        yield(Horizontal(id="root"))
        
    def push(self, element_text:str, active:bool=False):
        root = self.query_one("#root")
        root.mount(CarouselElement(text=element_text, is_active=active))


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
            if location.endswith(".txt"):
                content = open(location).read()
            else:
                content = location
            self.dismiss(content)

class PlayerBox(Horizontal):
    time = reactive(0.0)

    def compose(self) -> ComposeResult:
        yield Button("⏵", id="play_button", disabled=True)
        yield Horizontal(
            Button("⏮", id="rewind_button"),
            Button("⏭", id="forward_button"),
            id="seek_buttons"
        )
        yield Horizontal(
            Button("⏪", id="decrease_speed_button"),
            Button("1.0", id="speed_reset"),
            Button("⏩", id="increase_speed_button"),
            id="speed_controls"
        )
        yield Digits("00:00.00",id="current_time")
        yield ProgressBar(id="progress_bar", show_eta=False)
        yield Label("00:00:000", id="total_time")
        yield Button("📂", id="open_file", tooltip="Enter path of music file.")
    
    def watch_time(self, time):
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
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
                t_time_label = self.query_one("#total_time", Label)
                total_time = PLAYER.player.get_length() / 1000 # in seconds
                minutes, seconds = divmod(total_time, 60)
                t_time_label.update(content=f"{minutes:02,.0f}:{seconds:05.2f}")
                return
            
            elif PLAYER.cstate == PlayerState.PAUSED:
                PLAYER.resume()
                self.query_one("#play_button").label = "⏸"
                return
            
            elif PLAYER.cstate == PlayerState.PLAYING:
                PLAYER.pause()
                self.query_one("#play_button").label = "⏵"
                return
        
        elif event.button.id == "rewind_button":
            PLAYER.seek(-5)
        
        elif event.button.id == "forward_button":
            PLAYER.seek(5)
        
        elif event.button.id == "decrease_speed_button":
            PLAYER.set_speed(PLAYER.playback_speed-0.25)
            speed_reset_button:Button = self.query_one("#speed_reset")
            speed_reset_button.label = str(PLAYER.playback_speed)

        if event.button.id == "increase_speed_button":
            PLAYER.set_speed(PLAYER.playback_speed+0.25)
            speed_reset_button:Button = self.query_one("#speed_reset")
            speed_reset_button.label = str(PLAYER.playback_speed)
            
        if event.button.id == "speed_reset":
            PLAYER.set_speed(1.0)
            speed_reset_button:Button = self.query_one("#speed_reset")
            speed_reset_button.label = str(PLAYER.playback_speed)
            

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
    lyrics_saved_state:str = ""
    def compose(self) -> ComposeResult:
        yield Static("These are the lyrics", id="lyrics_label")
        yield Sidebar(id="sidebar")
        yield WordCarousel(id="word-carousel")
        yield(Horizontal(
            Button("←", id="prev_word_button"),
            Button("→", id="next_word_button"),            
            id="carousel_control"
        ))
        yield ListView(id="lyric_list")
        yield PlayerBox(id="player_box")
    
    def prev_word(self):
        root = self.query_one("#root")
        elements = root._nodes

        for i,element in enumerate(elements):
            if element.is_active:
                if i == 0:
                    # TODO: Switch to next line if end element
                    break
                element.set_state(False)
                elements[i-1].set_state(True)
                break

    def next_word(self):
        root = self.query_one("#root")
        elements = root._nodes

        for i,element in enumerate(elements):
            if element.is_active:
                if i == len(elements) - 1:
                    # TODO: Switch to next line if end element
                    break
                element.set_state(False)
                elements[i+1].set_state(True)
                break
    
    def next_line(self, word_index:int=0):
        curr_active = self.query_one(".lyric-line-active", Label)
        curr_index = 0
    
    def on_button_pressed(self, event:Button.Pressed):
        if event.button.id == "next_word_button":
            self.next_word()
        if event.button.id == "prev_word_button":
            self.prev_word()

    def on_screen_resume(self, event:events.ScreenResume):
        label:Static = self.query_one("#lyrics_label", Static)

        if CURR_LYRICS == self.lyrics_saved_state:
            return

        if CURR_LYRICS == "":
            self.lyrics_saved_state = CURR_LYRICS
            self.query_one("#word-carousel").visible = False
            label.display = True
            label.update(content="No lyrics loaded")
            return

        self.lyrics_saved_state = CURR_LYRICS
        self.query_one("#word-carousel").visible = True
        self.remove_children(ListItem)
        label.display = False

        list_view = self.query_one(ListView)
        lines = CURR_LYRICS.split("\n")
        for i,line in enumerate(lines):
            if i == 0:
                active_line_index = i
                list_view.append(ListItem(Label(line, classes="lyric-line-active")))
            else:
                list_view.append(ListItem(Label(line)))

        carousel = self.query_one(WordCarousel)
        for i, word in enumerate(lines[active_line_index].split(" ")):
            if i == 0:
                carousel.push(word, True)
                continue
            carousel.push(word, False)
    

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

    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.name == "load":
            def get_lyrics(content: str):
                if content != "":
                    self.query_one(".editor").text = content

            self.app.push_screen(FileNamePicker(), get_lyrics)
        elif event.button.name == "save":
            global CURR_LYRICS
            CURR_LYRICS = self.query_one(".editor").text
    

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