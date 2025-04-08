import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, ttk
import pygame

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Music Player")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Track variables
        self.current_track = ""
        self.paused = False
        self.playing = False
        self.songs_list = []
        self.current_index = 0
        self.progress_value = 0
        self.song_length = 0
        
        # Create GUI elements
        self.create_frames()
        self.create_header()
        self.create_playlist()
        self.create_controls()
        self.create_progress_bar()
        self.create_volume_control()
        
        # Start the thread for updating progress
        self.progress_thread = threading.Thread(target=self.update_progress)
        self.progress_thread.daemon = True
        self.progress_thread.start()
    
    def create_frames(self):
        # Header frame
        self.header_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.header_frame.pack(pady=10)
        
        # Playlist frame
        self.playlist_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.playlist_frame.pack(pady=10, fill="both", expand=True)
        
        # Controls frame
        self.controls_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.controls_frame.pack(pady=10)
        
        # Progress frame
        self.progress_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.progress_frame.pack(pady=5)
        
        # Volume frame
        self.volume_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.volume_frame.pack(pady=10)
    
    def create_header(self):
        self.title_label = tk.Label(
            self.header_frame, 
            text="Python Music Player", 
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        )
        self.title_label.grid(row=0, column=0, padx=10)
        
        self.add_btn = tk.Button(
            self.header_frame,
            text="Add Songs",
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            padx=10,
            command=self.add_songs
        )
        self.add_btn.grid(row=0, column=1, padx=10)
    
    def create_playlist(self):
        self.playlist = tk.Listbox(
            self.playlist_frame,
            selectbackground="#4CAF50",
            selectmode=tk.SINGLE,
            bg="white",
            fg="black",
            font=("Arial", 10),
            width=60,
            height=10
        )
        self.playlist.pack(fill="both", expand=True, padx=10)
        
        # Bind double-click to play selected song
        self.playlist.bind("<Double-1>", self.play_selected)
    
    def create_controls(self):
        # Previous button
        self.prev_btn = tk.Button(
            self.controls_frame,
            text="⏮",
            font=("Arial", 16),
            bg="#f0f0f0",
            width=3,
            command=self.play_prev
        )
        self.prev_btn.grid(row=0, column=0, padx=5)
        
        # Play button
        self.play_btn = tk.Button(
            self.controls_frame,
            text="▶",
            font=("Arial", 16),
            bg="#4CAF50",
            fg="white",
            width=3,
            command=self.play_pause
        )
        self.play_btn.grid(row=0, column=1, padx=5)
        
        # Stop button
        self.stop_btn = tk.Button(
            self.controls_frame,
            text="⏹",
            font=("Arial", 16),
            bg="#f0f0f0",
            width=3,
            command=self.stop
        )
        self.stop_btn.grid(row=0, column=2, padx=5)
        
        # Next button
        self.next_btn = tk.Button(
            self.controls_frame,
            text="⏭",
            font=("Arial", 16),
            bg="#f0f0f0",
            width=3,
            command=self.play_next
        )
        self.next_btn.grid(row=0, column=3, padx=5)
    
    def create_progress_bar(self):
        # Current time label
        self.current_time_label = tk.Label(
            self.progress_frame,
            text="00:00",
            bg="#f0f0f0",
            font=("Arial", 8)
        )
        self.current_time_label.grid(row=0, column=0, padx=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=350,
            mode="determinate"
        )
        self.progress_bar.grid(row=0, column=1, padx=5)
        
        # Total time label
        self.total_time_label = tk.Label(
            self.progress_frame,
            text="00:00",
            bg="#f0f0f0",
            font=("Arial", 8)
        )
        self.total_time_label.grid(row=0, column=2, padx=5)
    
    def create_volume_control(self):
        # Volume label
        self.volume_label = tk.Label(
            self.volume_frame,
            text="Volume:",
            bg="#f0f0f0",
            font=("Arial", 10)
        )
        self.volume_label.grid(row=0, column=0, padx=5)
        
        # Volume slider
        self.volume_slider = ttk.Scale(
            self.volume_frame,
            orient=tk.HORIZONTAL,
            length=200,
            from_=0,
            to=100,
            command=self.set_volume
        )
        self.volume_slider.set(70)  # Default volume
        self.volume_slider.grid(row=0, column=1, padx=5)
        
        # Set initial volume
        pygame.mixer.music.set_volume(0.7)
    
    def add_songs(self):
        songs = filedialog.askopenfilenames(
            title="Select Music Files",
            filetypes=(
                ("MP3 Files", "*.mp3"),
                ("WAV Files", "*.wav"),
                ("OGG Files", "*.ogg"),
                ("All Files", "*.*")
            )
        )
        
        for song in songs:
            song_name = os.path.basename(song)
            self.songs_list.append(song)
            self.playlist.insert(tk.END, song_name)
    
    def play_selected(self, event=None):
        try:
            # Get the selected song index
            self.current_index = self.playlist.curselection()[0]
            self.play_music()
        except:
            pass
    
    def play_music(self):
        if self.songs_list:
            # Reset paused state
            self.paused = False
            
            # Update play button text
            self.play_btn.config(text="⏸")
            
            # Get the selected song
            self.current_track = self.songs_list[self.current_index]
            
            # Select the item in the listbox
            self.playlist.selection_clear(0, tk.END)
            self.playlist.activate(self.current_index)
            self.playlist.selection_set(self.current_index)
            
            # Load and play the song
            pygame.mixer.music.load(self.current_track)
            pygame.mixer.music.play()
            
            # Set playing flag
            self.playing = True
            
            # Get song length
            sound = pygame.mixer.Sound(self.current_track)
            self.song_length = sound.get_length()
            
            # Update total time label
            mins, secs = divmod(self.song_length, 60)
            self.total_time_label.config(text=f"{int(mins):02d}:{int(secs):02d}")
    
    def play_pause(self):
        if not self.songs_list:
            return
        
        if not self.playing:
            # If nothing is playing, start playing the selected song
            if not self.current_track:
                try:
                    self.current_index = self.playlist.curselection()[0]
                except:
                    self.current_index = 0
                self.play_music()
            else:
                # If paused, unpause
                if self.paused:
                    pygame.mixer.music.unpause()
                    self.paused = False
                    self.playing = True
                    self.play_btn.config(text="⏸")
                else:
                    # If stopped, play from beginning
                    self.play_music()
        else:
            # If playing, pause
            pygame.mixer.music.pause()
            self.paused = True
            self.playing = False
            self.play_btn.config(text="▶")
    
    def stop(self):
        # Stop the music
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.play_btn.config(text="▶")
        
        # Reset progress bar
        self.progress_bar["value"] = 0
        self.current_time_label.config(text="00:00")
    
    def play_next(self):
        if not self.songs_list:
            return
            
        # Get the next song index
        if self.current_index < len(self.songs_list) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        
        # Stop current and play next
        self.stop()
        self.play_music()
    
    def play_prev(self):
        if not self.songs_list:
            return
            
        # Get the previous song index
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.songs_list) - 1
        
        # Stop current and play previous
        self.stop()
        self.play_music()
    
    def set_volume(self, val):
        volume = float(val) / 100
        pygame.mixer.music.set_volume(volume)
    
    def update_progress(self):
        while True:
            if self.playing and not self.paused:
                try:
                    # Get current position in seconds
                    current_time = pygame.mixer.music.get_pos() / 1000
                    
                    # Update progress bar
                    progress_percentage = (current_time / self.song_length) * 100
                    self.progress_bar["value"] = progress_percentage
                    
                    # Update current time label
                    mins, secs = divmod(current_time, 60)
                    self.current_time_label.config(text=f"{int(mins):02d}:{int(secs):02d}")
                    
                    # Check if song has ended
                    if current_time >= self.song_length:
                        self.play_next()
                except:
                    pass
            time.sleep(0.1)


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
