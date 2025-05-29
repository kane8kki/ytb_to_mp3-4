import tkinter as tk
from tkinter import messagebox, filedialog
from pytubefix import YouTube  # This is solution
import os

# Création de la fenêtre principale
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("400x200")
root.configure(bg="#2C3E50")

def download_video():
    url = entry_url.get()
    file_format = format_var.get()
    
    if not url:
        messagebox.showerror("Erreur", "Veuillez entrer une URL YouTube valide.")
        return
    
    try:
        download_folder = filedialog.askdirectory(title="Choisir un dossier de téléchargement")
        if not download_folder:
            return  # L'utilisateur a annulé la sélection
        
        yt = YouTube(url)
        if file_format == "mp4":
            stream = yt.streams.get_highest_resolution()
            filename = stream.download(output_path=download_folder)
        else:  # mp3
            stream = yt.streams.filter(only_audio=True).first()
            filename = stream.download(output_path=download_folder)
            base, ext = os.path.splitext(filename)
            new_file = base + ".mp3"
            os.rename(filename, new_file)
        
        messagebox.showinfo("Succès", "Téléchargement terminé !")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

# Titre
label_title = tk.Label(root, text="YouTube Downloader", fg="white", bg="#2C3E50", font=("Arial", 14, "bold"))
label_title.pack(pady=10)

# Champ d'entrée
entry_url = tk.Entry(root, width=40)
entry_url.pack(pady=5)

# Options MP4 / MP3
format_var = tk.StringVar(value="mp4")
frame_format = tk.Frame(root, bg="#2C3E50")
tk.Radiobutton(frame_format, text="MP4", variable=format_var, value="mp4", bg="#2C3E50", fg="white").pack(side="left", padx=10)
tk.Radiobutton(frame_format, text="MP3", variable=format_var, value="mp3", bg="#2C3E50", fg="white").pack(side="left", padx=10)
frame_format.pack(pady=5)

# Bouton de téléchargement
btn_download = tk.Button(root, text="Télécharger", command=download_video, bg="#27AE60", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5)
btn_download.pack(pady=10)

root.mainloop()
