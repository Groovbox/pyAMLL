from textual.app import ComposeResult
from textual.widgets import Button, Label, Input, Pretty
from textual.containers import Grid
from textual.screen import ModalScreen

import os
from mutagen import File

from utils import FileType


class ValidationResult():
    SUCCESS = "success"
    FAILURE = "failure"

    result:str = None
    message:str = None

    def failure(self, message:str) -> None:
        self.result = self.FAILURE
        self.message = message
    def success(self) -> None:
        self.result = self.SUCCESS


def is_music_file(filepath:str) -> bool:
        """
        Checks if given file is an audio file or not
        """
        try:
            audio = File(filepath)
            return audio is not None and audio.mime[0].startswith('audio')
        except Exception:
            return False


def validate_input(value:str, type:FileType) -> ValidationResult:
    result = ValidationResult()
    if not os.path.exists(value):
        result.failure("File does not exist")
        return result

    if type == FileType.TEXT:
        try:
            open(value, "r").read(10)
        except UnicodeDecodeError:
            result.failure("Given file is not a text file")
            return result
    elif type == FileType.AUDIO:
        if not is_music_file(value):
            result.failure("Given file is not an audio file")
            return result
    result.success()

    return result


class FileNamePicker(ModalScreen[str]):
    _type:FileType = None
    def __init__(self, filetype:FileType):
        self._type = filetype
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Enter the path of file", id="file-picker-label"),
            Input(placeholder="", id="file-picker-input"),
            Button("Enter", variant="primary", id="submit"),
            Button("Cancel", variant="error", id="cancel"),
            id="dialog",
        )
    
    def on_button_pressed(self, event:Button.Pressed):
        if event.button.id == "submit":
            value:str = self.query_one(Input).value
            result:ValidationResult = validate_input(value, self._type)
            if result.result == ValidationResult.SUCCESS:
                self.query_one(Input).remove_class("-invalid")
                self.dismiss(value)
            elif result.result == ValidationResult.FAILURE:
                self.query_one(Input).add_class("-invalid")
                self.app.notify(result.message, severity="error")
        else:
            self.dismiss("")
