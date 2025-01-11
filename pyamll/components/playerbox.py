from components.filepicker import FileNamePicker, FileType
from player import PlayerState, MusicPlayer
from utils import convert_seconds_to_format as fsec

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Digits, Label, ProgressBar

import time


class PlayerBox(Horizontal):
    time = reactive(0.0)
    player:MusicPlayer = None

    def __init__(self, *children, name = None, id = None, player:MusicPlayer,classes = None, disabled = False):
        self.player = player
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield Button("⏵", id="play", disabled=True)
        yield Horizontal(
            Button("⏮", id="rewind"),
            Button("⏭", id="forward"),
            id="seek_buttons",
            classes="button_group"
        )
        yield Horizontal(
            Button("⏪", id="speed_decrease"),
            Button("1.0", id="speed_reset"),
            Button("⏩", id="speed_increase"),
            id="speed_controls",
            classes="button_group"
        )
        yield Digits("00:00.00", id="current_time")
        yield Vertical(
            ProgressBar(id="progress_bar", show_eta=False,
                        show_percentage=False),
            Horizontal(id="position_control")
        )
        yield Label("00:00.00", id="total_time")

        yield Horizontal(
            Button("🔉", id="vol_down", tooltip="Decrease Volume"),
            Button("100", id="vol_reset", tooltip="Reset Volume"),
            Button("🔊", id="vol_up", tooltip="Increase Volume"),
            classes="button_group"
        )
        yield Button("📂", id="open_file", tooltip="Enter path of music file.")

    def watch_time(self, time_in_seconds):
        digit_widget = self.query_one("#current_time", Digits)
        digit_widget.update(fsec(time_in_seconds))

        # Update progress bar
        progress_bar: ProgressBar = self.query_one("#progress_bar", ProgressBar)
        progress_bar.progress = time_in_seconds

        try:
            if progress_bar.progress >= self.player.player.get_length()/1000:
                self.query_one("#play").label = "⏵"
                self.query_one("#play").variant = "warning"
        except TypeError:
            pass
        except AttributeError:
            pass

    def update_time(self) -> None:
        self.time = self.player.get_timestamp()

    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.update_time)

        _h_element = self.query_one("#position_control", Horizontal)
        for i in range(10):
            _h_element.mount(Button(str(i), id=f"seek_pos_{i}", classes="position-button"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        PLAYER = self.player
        def get_path(path: str):
            if path != "":
                PLAYER.set_file(path)
                time.sleep(0.3)
                self.query_one("#play").disabled = False

        if event.button.id == "open_file":
            self.app.push_screen(FileNamePicker(FileType.AUDIO), get_path)

        elif event.button.id == "play":
            if self.player.cstate == PlayerState.STOPPED:                
                self.player.play()
                file_length = self.player.player.get_length() / 1000
                self.query_one("#progress_bar").total = file_length
                self.query_one("#play").label = "⏸"
                self.query_one("#play").variant = "success"
                t_time_label = self.query_one("#total_time", Label)
                t_time_label.update(content=fsec(
                    file_length, show_milliseconds=False))
                return

            elif self.player.cstate == PlayerState.PAUSED:
                self.player.resume()
                self.query_one("#play").label = "⏸"
                self.query_one("#play").variant = "success"
                return

            elif self.player.cstate == PlayerState.PLAYING:
                self.player.pause()
                self.query_one("#play").label = "⏵"
                self.query_one("#play").variant = "warning"
                return

        elif event.button.id == "rewind":
            self.player.seek(-5)
        elif event.button.id == "forward":
            self.player.seek(5)

        # Speed Controls
        elif event.button.id.startswith("speed_"):
            speed_label: Button = self.query_one("#speed_reset")

            if event.button.id == "speed_decrease":
                self.player.set_speed(self.player.playback_speed-0.25)
            elif event.button.id == "speed_increase":
                self.player.set_speed(self.player.playback_speed+0.25)
            else:
                self.player.set_speed(1.0)
            speed_label.label = str(self.player.playback_speed)
        
        # Volume Controls
        elif event.button.id.startswith("vol_"):
            vol_label: Button = self.query_one("#vol_reset")

            if event.button.id == "vol_down":
                self.player.change_volume(-10)
            elif event.button.id == "vol_up":
                self.player.change_volume(10)
                vol_label.label = str(self.player.volume)
            else:
                # TODO: Define default volume
                self.player.volume = 75
                self.player.player.audio_set_volume(75)
            vol_label.label = str(self.player.volume)

        elif "seek_pos_" in event.button.id:
            partition = int(event.button.id.split("_")[-1])
            self.player.seek(partition=partition)

    def on_resize(self, event: events.Resize) -> None:
        progress_bar = self.query_one(ProgressBar)
        if self.size.width < 105:
            self.query_one("#position_control").display = False
            progress_bar.styles.margin = (1, 1, 0, 1)
            if self.size.width < 40:
                self.query_one("#total_time").display = False
            else:
                self.query_one("#total_time").display = True
        else:
            self.query_one("#position_control").display = True
            progress_bar.styles.margin = (0, 1, 0, 1)
            self.query_one("#total_time").display = True