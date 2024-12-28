from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Tabs, Tab, Static, TextArea, Button, Label, Input, ProgressBar, Digits
from textual.containers import Horizontal, Grid, Vertical
from textual.screen import Screen, ModalScreen
import vlc
from player import MusicPlayer, PlayerState
import time
from textual.reactive import reactive

CURR_LYRICS = ""
PLAYER = MusicPlayer()

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
        yield Digits("00:00:000",id="current_time")
        yield ProgressBar(id="progress_bar", show_eta=False)
        yield Label("00:00:000", id="total_time")
        yield Button("📂", id="open_file", tooltip="Enter path of music file.")
    
    def watch_time(self, time):
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        digit_widget = self.query_one("#current_time", Digits)
        digit_widget.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

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
        
        if event.button.id == "play_button":
            if PLAYER.cstate == PlayerState.STOPPED:
                PLAYER.play()
                self.query_one("#progress_bar").total = PLAYER.player.get_length() / 1000
                self.query_one("#play_button").label = "⏸"
                t_time_label = self.query_one("#total_time", Label)
                total_time = PLAYER.player.get_length() / 1000 # in seconds
                minutes, seconds = divmod(total_time, 60)
                t_time_label.update(content=f"{minutes:02,.0f}:{seconds:05.2f}")
                return
            
            if PLAYER.cstate == PlayerState.PAUSED:
                PLAYER.resume()
                self.query_one("#play_button").label = "⏸"
                return
            
            if PLAYER.cstate == PlayerState.PLAYING:
                PLAYER.pause()
                self.query_one("#play_button").label = "⏵"
                return
        
        if event.button.id == "rewind_button":
            PLAYER.seek(-5)
        
        if event.button.id == "forward_button":
            PLAYER.seek(5)


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
        yield Static("These are the lyrics", id="lyrics_label")
        yield PlayerBox(id="player_box")
    
    def on_mount(self) -> None:
        label:Static = self.query_one("#lyrics_label", Static)
        if CURR_LYRICS == "":
            label.update(content="No lyrics loaded")
        else:
            statics = []
            for line in CURR_LYRICS.split("\n"):
                statics.append(Static(line))
            self.mount_all(statics)
            


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