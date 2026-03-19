import tkinter as tk
from tkinter import messagebox
from yt_dlp import YoutubeDL
import vlc
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import os
import sys
import webbrowser

player = None
playlist = []
current_index = 0




#  FFmpeg Path

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, "ffmpeg", "ffmpeg.exe")

# Search
def search_songs(song_name):
    global playlist, current_index

    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'noplaylist': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch10:{song_name}", download=False)
        playlist = info['entries']
        current_index = 0

    listbox.delete(0, tk.END)
    for i, song in enumerate(playlist):
        listbox.insert(tk.END, f"{i+1}. {song['title']}")



#  الصورة بتاعت المغني
def show_thumbnail(url):
    try:
        img_data = requests.get(url).content
        img = Image.open(BytesIO(img_data))
        img = img.resize((180, 180))
        photo = ImageTk.PhotoImage(img)

        thumbnail_label.config(image=photo)
        thumbnail_label.image = photo
    except:
        pass

#  Play زرار
def play_current():
    global player

    if not playlist:
        return

    if player:
        player.stop()

    song = playlist[current_index]
    status_label.config(text=f"🎵 {song['title']}")
    show_thumbnail(song['thumbnail'])

    player = vlc.MediaPlayer(song['url'])
    player.audio_set_volume(volume_slider.get())
    player.play()




#  Play without lag
def play_song():
    song_name = entry.get()

    if not song_name:
        messagebox.showwarning("Warning", "Type song name!")
        return

    status_label.config(text="🔍 Searching...")
    threading.Thread(target=search_and_play, args=(song_name,), daemon=True).start()

def search_and_play(song_name):
    try:
        search_songs(song_name)
        root.after(0, play_current)
    except:
        messagebox.showerror("Error", "Search failed")




# ⏭️⏮️ 
def next_song():
    global current_index
    if playlist:
        current_index = (current_index + 1) % len(playlist)
        play_current()

def prev_song():
    global current_index
    if playlist:
        current_index = (current_index - 1) % len(playlist)
        play_current()

def select_song(event):
    global current_index
    if listbox.curselection():
        current_index = listbox.curselection()[0]
        play_current()




# ⏹️ توقف
def stop_song():
    global player
    if player:
        player.stop()
        status_label.config(text="⏹️ Stopped")




# 🔊 الصوت
def set_volume(val):
    if player:
        player.audio_set_volume(int(val))

# ⬇️ التحميل
def download_song():
    if not playlist:
        return

    song = playlist[current_index]
    url = song['webpage_url']

    status_label.config(text="⬇️ Downloading...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'ffmpeg_location': get_ffmpeg_path(),
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    try:
        os.makedirs("downloads", exist_ok=True)

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        status_label.config(text="✅ Downloaded")
        messagebox.showinfo("Done", "MP3 Downloaded 🎉")

    except Exception as e:
        status_label.config(text="❌ Error")
        messagebox.showerror("Error", str(e))



#  Links
def open_facebook():
    webbrowser.open("https://www.facebook.com/ninjafbi1")

def open_github():
    webbrowser.open("https://github.com/FBI0NINJA")



#  Auto Next
def auto_next():
    if player and player.get_state() == vlc.State.Ended:
        next_song()
    root.after(1000, auto_next)



#  Exit 
def on_close():
    if messagebox.askyesno("Exit", "🎧 Thanks for using my app!\nAhmed Sayed ❤️\nSee you again 😉"):
        root.destroy()




#  UI
root = tk.Tk()
root.title("Music Player Pro - Ahmed Sayed")
root.geometry("950x500")
root.config(bg="#121212")

root.protocol("WM_DELETE_WINDOW", on_close)




# Playlist
listbox = tk.Listbox(root, width=45, bg="#1e1e1e", fg="white", selectbackground="#00ffcc")
listbox.pack(side="left", fill="y", padx=10, pady=10)
listbox.bind("<<ListboxSelect>>", select_song)




# Main frame
frame = tk.Frame(root, bg="#121212")
frame.pack(side="left", fill="both", expand=True)
tk.Label(frame, text="🎧 Music Player Pro", font=("Arial", 18, "bold"), fg="#00ffcc", bg="#121212").pack(pady=5)




#  الاسم من فوق
tk.Label(frame, text="Ahmed Sayed", font=("Arial", 20, "bold"), fg="white", bg="#121212").pack(pady=5)

entry = tk.Entry(frame, width=30, bg="#1e1e1e", fg="white")
entry.pack(pady=10)

tk.Button(frame, text="▶️ Play", command=play_song, bg="#00ffcc").pack(pady=5)

controls = tk.Frame(frame, bg="#121212")
controls.pack()

tk.Button(controls, text="⏮️", command=prev_song).pack(side="left", padx=5)
tk.Button(controls, text="⏭️", command=next_song).pack(side="left", padx=5)
tk.Button(controls, text="⏹️", command=stop_song).pack(side="left", padx=5)

volume_slider = tk.Scale(frame, from_=0, to=100, orient="horizontal", command=set_volume, bg="#121212", fg="white")
volume_slider.set(70)
volume_slider.pack()

thumbnail_label = tk.Label(frame, bg="#121212")
thumbnail_label.pack(pady=10)

status_label = tk.Label(frame, text="Ready 🎵", fg="white", bg="#121212")
status_label.pack(pady=10)




# Download button
tk.Button(root, text="⬇️ Download MP3", bg="#ff9800", fg="white",
          command=lambda: threading.Thread(target=download_song, daemon=True).start()).pack(side="right", padx=10)




# Social text
social_frame = tk.Frame(root, bg="#121212")
social_frame.pack(side="bottom", pady=10)

tk.Button(social_frame, text="Facebook", command=open_facebook, bg="#1877f2", fg="white").pack(side="left", padx=10)
tk.Button(social_frame, text="GitHub", command=open_github, bg="#333", fg="white").pack(side="left", padx=10)

auto_next()
root.mainloop()