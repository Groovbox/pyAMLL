from ttml import *
import vlc
from vlc import State
import time
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
        self.volume = 100
    
    def change_volume(self, volume_offset):
        new_volume = self.volume + volume_offset
        if new_volume > 100 or new_volume < 0:
            volume_offset = 0
        self.player.audio_set_volume(new_volume)
        self.volume = new_volume
    
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
        self.volume = self.player.audio_get_volume()

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
    
    def seek(self, offset_seconds=None, partition=None):
        """Seek forward or backward by the specified offset in seconds."""
        current_time_ms = self.player.get_time()  # Current time in milliseconds

        if offset_seconds is None and partition is not None:
            total_length = self.player.get_length()
            segment_length = total_length / 10
            seek_pos = segment_length*partition
            offset_seconds = (seek_pos-current_time_ms)/1000

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

