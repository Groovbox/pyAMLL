from models import *
import os
from rich.console import Console
import sys, tty, termios
import vlc
from vlc import State
import time
import threading
from enum import Enum

class PlayerState(Enum):
    PLAYING = 1
    PAUSED = 2
    STOPPED = 3

class MusicPlayer:
    def __init__(self):
        self.player = vlc.MediaPlayer()
        self.last_known_time = 0  # Last known playback position in milliseconds
        self.last_real_time = None  # Real-world time when last known time was fetched
        self.playback_speed = 1.0  # Current playback speed
        self.file = ""
        self.player:vlc.MediaPlayer = None
        self.cstate:PlayerState = PlayerState.STOPPED
    
    def set_file(self, file_path):
        self.file = file_path
        self.player = vlc.MediaPlayer(file_path)

    def play(self):
        self.stop()  # Stop any current playback
        self.player.play()
        time.sleep(0.1)  # Allow VLC to load the file
        self.last_known_time = self.player.get_time()
        self.last_real_time = time.time()
        self.set_speed(self.playback_speed)
        self.cstate = PlayerState.PLAYING

    def pause(self):
        if self.player.is_playing():
            self.update_time()  # Save the current playback position
            self.player.pause()
            self.last_real_time = None
            self.cstate = PlayerState.PAUSED

    def resume(self):
        if not self.player.is_playing():
            self.last_real_time = time.time()  # Update the real-time tracker
            self.player.play()
            self.cstate = PlayerState.PLAYING


    def stop(self):
        self.player.stop()
        self.last_known_time = 0
        self.last_real_time = None
        self.cstate = PlayerState.STOPPED

    def set_speed(self, speed):
        self.playback_speed = speed
        self.player.set_rate(speed)


    def update_time(self):
        """Update the last known time based on real-time tracking."""
        if self.last_real_time is not None:
            elapsed_real_time = time.time() - self.last_real_time
            self.last_known_time += elapsed_real_time * 1000 * self.playback_speed
            self.last_real_time = time.time()

    def get_timestamp(self):
        """Get the accurate current playback time in seconds."""
        self.update_time()
        if self.last_known_time >= 0:
            current_time_s = self.last_known_time / 1000  # Convert to seconds
            return current_time_s
    
    def seek(self, offset_seconds):
        """Seek forward or backward by the specified offset in seconds."""
        current_time_ms = self.player.get_time()  # Current time in milliseconds

        if self.cstate == PlayerState.STOPPED or self.cstate == PlayerState.PAUSED:
            new_time_ms = current_time_ms + (offset_seconds * 1000)  # Calculate new time
            self.player.set_time(int(new_time_ms))
            self.last_known_time = new_time_ms
            return
        
        if current_time_ms >= 0:
            new_time_ms = current_time_ms + (offset_seconds * 1000)  # Calculate new time
            new_time_ms = max(0, new_time_ms)  # Ensure the new time is not negative
            self.player.set_time(int(new_time_ms))  # Set the new playback position
            self.last_known_time = new_time_ms  # Update last known time
            self.last_real_time = time.time()  # Reset the real-time tracker


# player = MusicPlayer()
# FILE = "/server/mnt/data/Music/Music/Halsey/Manic/9. Without Me.opus"
# player.set_file(FILE)

def getch():
    old_settings = termios.tcgetattr(0)
    new_settings = old_settings[:]
    new_settings[3] &= ~termios.ICANON
    try:
        termios.tcsetattr(0, termios.TCSANOW, new_settings)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(0, termios.TCSANOW, old_settings)
        return ch

# def display_lines(lines, curr_line:int):
#     current_line = lines[curr_line]

#     if curr_line > 0:
#         print(curr_line-1, "  ", lines[curr_line -1 ])
#     else:
#         print("-")
    
#     console.print(str(curr_line), "  ", str(current_line), style="bold red")

#     if curr_line < len(lines) - 1:
#         print(curr_line+1, "  ", lines[curr_line+1])

# def display_words(line, curr_word:int):

#     _index = 0
#     selected_word = line.elements[curr_word]
#     for word in line.elements:
#         if word.index > _index:
#             print(" ", end="")
#         _index = word.index

#         if line.elements.index(word) == curr_word:
#             console.print(f"[bold red]{word}[/bold red]", end="")
#         else:
#             print(word, end="")
        
#     print("\n")
#     print(f"Start time: {selected_word.start_time} | End time: {selected_word.end_time}")

# def display_player():
#     console.print("[bold red]⏸︎[/bold red]" if not player.player.is_playing() else "[bold green]⏵︎[/bold green]", end="\t")
#     print(player.get_timestamp(), end="\t")
#     print(round(player.playback_speed,2))
    


def main():
    print("Reading lyrics from file...")
    lyrics = open("lyrics.txt", "r").read()

    text_lines= lyrics.split("\n")

    lines = []

    for line_counter in range(len(text_lines)):
        text_line = text_lines[line_counter]

        # If line starts and ends with () then it is a backing vocal line
        if text_line.startswith("(") and text_line.endswith(")"):
            is_backing = True
        else:
            is_backing = False
        line = Line(index=line_counter, elements=[], vocal=Vocal.STANDARD, is_backing=is_backing)

        for word_counter in range(len(text_line.split(" "))):
            word = text_line.split(" ")[word_counter]
            if '/' in word:
                syllables = word.split('/')
                for syllable_counter in range(len(syllables)):
                    line.elements.append(Element(index=word_counter, start_time=0, end_time=0, text=syllables[syllable_counter], is_part_of_word=True))
            else:
                line.elements.append(Element(index=word_counter, start_time=0, end_time=0, text=word, is_part_of_word=False))
        lines.append(line)


    line_counter = 0
    word_counter = 0
    player.play()
    while True:        
        os.system("clear")
        display_lines(lines, line_counter)
        print("\n\n")
        display_words(lines[line_counter], word_counter)
        print("\n\n")
        display_player()
        
        char = getch()
        player_time = player.get_timestamp()
        
        match char:
            case "q":
                exit()
            case "j":
                line_counter += 1
            case "k":
                line_counter -= 1
            case "d":
                word_counter -= 1
            case "f":
                word_counter += 1
            case "^[[H":
                word_counter = 0
            case "\n":
                lines[line_counter].elements[word_counter].start_time = float(input("Start time: "))
                lines[line_counter].elements[word_counter].end_time = float(input("End time: "))
            case "c":
                # Set the player timestamp to the start time of the current word
                lines[line_counter].elements[word_counter].start_time = player_time
            case "v":
                # Set the player timestamp to the end time of the current word
                lines[line_counter].elements[word_counter].end_time = player_time
            case "p":
                if player.player.is_playing():
                    player.pause()
                else:
                    player.resume()
            case "[":
                player.set_speed(player.playback_speed - 0.1)
            case "]":
                player.set_speed(player.playback_speed + 0.1)
            case "-":
                player.seek(-1)
            case "=":
                player.seek(1)
                

        if word_counter < 0:
            word_counter = 0
            line_counter -= 1
        elif word_counter >= len(lines[line_counter].elements):
            word_counter = 0
            line_counter += 1
        
        if line_counter < 0:
            line_counter = 0
        elif line_counter >= len(lines):
            line_counter = len(lines) - 1
        

if __name__ == "__main__":
    file = "music.opus"
    player = MusicPlayer()
    player.set_file(file)
    player.play()
    print(player.player.get_length())
    while True:
        pass