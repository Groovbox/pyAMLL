from enum import Enum


def convert_seconds_to_format(seconds:float, show_milliseconds:bool=True) -> str:
    """
    Converts time to MM:ss:mm string
    """
    minutes = int(seconds // 60)
    _seconds = int(seconds % 60)
    if show_milliseconds:
        milliseconds = int((seconds % 1) * 100)
        return f"{minutes:02}:{_seconds:02}.{milliseconds:02}"
    return f"{minutes:02}:{_seconds:02}"


class FileType(Enum):
    TEXT = "text"
    AUDIO = "audio"
