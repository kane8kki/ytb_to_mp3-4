import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pytubefix import YouTube
from pytube.exceptions import RegexMatchError, VideoUnavailable
import threading
import os

class YouTubeDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Téléchargeur YouTube")
        master.geometry("800x450") # Augmentation de la taille pour une meilleure lisibilité
        master.configure(bg="#2c3e50") # Couleur de fond principale

        # Définir l'icône de la fenêtre
        # Assurez-vous que le fichier 'ytmp3.ico' est dans le même répertoire que le script
        try:
            # Le chemin vers l'icône. Si le script est compilé avec PyInstaller,
            # sys._MEIPASS est le répertoire temporaire où les fichiers sont extraits.
            # Sinon, c'est le répertoire du script.
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'ytmp3.ico')
            else:
                icon_path = 'ytmp3.ico' # Chemin relatif si l'icône est dans le même dossier
            
            if os.path.exists(icon_path):
                master.iconbitmap(icon_path)
            else:
                print(f"Avertissement: Fichier icône '{icon_path}' non trouvé. L'icône par défaut sera utilisée.")
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône: {e}. L'icône par défaut sera utilisée.")


        self.selected_format = tk.StringVar(value="MP4") # Format par défaut
        self.download_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads")) # Dossier de téléchargement par défaut

        # Styles ttk
        self.style = ttk.Style()
        self.style.theme_use('clam') # Un thème ttk plus moderne

        self.style.configure("TFrame", background="#2c3e50")
        self.style.configure("Sidebar.TFrame", background="#34495e") # Couleur plus foncée pour la sidebar
        self.style.configure("Content.TFrame", background="#ecf0f1") # Couleur claire pour le contenu

        self.style.configure("TLabel", background="#ecf0f1", foreground="#2c3e50", font=("Arial", 12))
        self.style.configure("Sidebar.TLabel", background="#34495e", foreground="#ecf0f1", font=("Arial", 12, "bold"))
        self.style.configure("Status.TLabel", background="#ecf0f1", foreground="#2c3e50", font=("Arial", 10))
        
        self.style.configure("TButton", font=("Arial", 12, "bold"), padding=10)
        self.style.configure("Download.TButton", background="#27ae60", foreground="white") # Vert pour le bouton télécharger
        self.style.map("Download.TButton", background=[('active', '#2ecc71')])
        self.style.configure("Browse.TButton", background="#3498db", foreground="white") # Bleu pour parcourir
        self.style.map("Browse.TButton", background=[('active', '#5dade2')])

        self.style.configure("Format.TRadiobutton", background="#34495e", foreground="#ecf0f1", font=("Arial", 12), padding=5)
        self.style.map("Format.TRadiobutton",
                       background=[('active', '#4a6278')],
                       indicatorcolor=[('selected', '#2ecc71'), ('!selected', '#bdc3c7')],
                       foreground=[('active', '#ffffff')])


        self.style.configure("TEntry", font=("Arial", 12), padding=5)
        self.style.configure("TProgressbar", thickness=20, background="#2ecc71")


        # --- Structure principale ---
        main_frame = ttk.Frame(master, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Barre latérale ---
        sidebar_frame = ttk.Frame(main_frame, width=200, style="Sidebar.TFrame")
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        sidebar_frame.pack_propagate(False) # Empêche le frame de se redimensionner avec le contenu

        sidebar_label = ttk.Label(sidebar_frame, text="Format", style="Sidebar.TLabel", anchor="center")
        sidebar_label.pack(pady=20, fill=tk.X)

        mp4_button = ttk.Radiobutton(sidebar_frame, text="MP4 (Vidéo)", variable=self.selected_format, value="MP4", style="Format.TRadiobutton", command=self.update_format_selection)
        mp4_button.pack(pady=10, padx=20, fill=tk.X)

        mp3_button = ttk.Radiobutton(sidebar_frame, text="MP3 (Audio)", variable=self.selected_format, value="MP3", style="Format.TRadiobutton", command=self.update_format_selection)
        mp3_button.pack(pady=10, padx=20, fill=tk.X)
        
        self.current_format_label = ttk.Label(sidebar_frame, text="Format actuel: MP4", style="Sidebar.TLabel", anchor="center")
        self.current_format_label.pack(pady=20, side=tk.BOTTOM)


        # --- Zone de contenu principal ---
        content_frame = ttk.Frame(main_frame, style="Content.TFrame")
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # URL Input
        url_label = ttk.Label(content_frame, text="URL de la vidéo YouTube:")
        url_label.pack(pady=(20,5), padx=10, anchor="w")
        self.url_entry = ttk.Entry(content_frame, width=60) # Augmentation de la largeur
        self.url_entry.pack(pady=5, padx=10, fill=tk.X)

        # Download Path
        path_frame = ttk.Frame(content_frame, style="Content.TFrame")
        path_frame.pack(fill=tk.X, padx=10, pady=5)

        path_label = ttk.Label(path_frame, text="Enregistrer dans:")
        path_label.pack(side=tk.LEFT, pady=5)
        
        self.path_display_label = ttk.Label(path_frame, textvariable=self.download_path, wraplength=350, style="Status.TLabel") # Pour afficher le chemin
        self.path_display_label.pack(side=tk.LEFT, pady=5, padx=5, fill=tk.X, expand=True)

        browse_button = ttk.Button(path_frame, text="Parcourir...", command=self.browse_path, style="Browse.TButton")
        browse_button.pack(side=tk.RIGHT, pady=5)


        # Download Button
        self.download_button = ttk.Button(content_frame, text="Télécharger", command=self.start_download_thread, style="Download.TButton")
        self.download_button.pack(pady=20, padx=10, ipady=5) # ipady pour hauteur interne

        # Progress Bar
        self.progress_bar = ttk.Progressbar(content_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.pack(pady=10, padx=10, fill=tk.X)

        # Status Label
        self.status_label = ttk.Label(content_frame, text="Prêt", style="Status.TLabel", anchor="center")
        self.status_label.pack(pady=10, padx=10, fill=tk.X)
        
        self.update_format_selection() # Initialiser le label du format

    def update_format_selection(self):
        self.current_format_label.config(text=f"Format actuel: {self.selected_format.get()}")

    def browse_path(self):
        path = filedialog.askdirectory(initialdir=self.download_path.get())
        if path:
            self.download_path.set(path)

    def start_download_thread(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL YouTube.")
            return

        self.download_button.config(state=tk.DISABLED)
        self.status_label.config(text="Préparation du téléchargement...")
        self.progress_bar["value"] = 0
        
        # Démarrer le téléchargement dans un thread séparé pour ne pas bloquer l'interface
        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.daemon = True # Permet à l'application de se fermer même si le thread est en cours
        thread.start()

    def download_video(self, url):
        try:
            yt = YouTube(url, on_progress_callback=self.on_progress, on_complete_callback=self.on_complete)
            
            self.status_label.config(text=f"Récupération des informations: {yt.title[:30]}...")
            
            file_extension = ""
            stream = None

            if self.selected_format.get() == "MP4":
                stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
                file_extension = ".mp4"
            elif self.selected_format.get() == "MP3":
                stream = yt.streams.filter(only_audio=True).first() 
                # Pytube télécharge souvent l'audio en .mp4 (conteneur) ou .webm.
                # Nous le sauvegardons avec .mp3, ce qui fonctionne pour la plupart des lecteurs
                # si le codec interne est AAC (commun pour .mp4) ou Opus/Vorbis (pour .webm).
                # Pour une vraie conversion en .mp3, ffmpeg serait nécessaire.
                file_extension = ".mp3"
            
            if not stream:
                messagebox.showerror("Erreur", f"Aucun flux {self.selected_format.get()} disponible pour cette vidéo.")
                self.reset_ui()
                return

            # Nettoyer le titre pour le nom de fichier
            safe_title = "".join([c for c in yt.title if c.isalnum() or c in (' ', '-', '_')]).rstrip()
            filename = f"{safe_title}{file_extension}"
            
            self.status_label.config(text=f"Téléchargement de \"{yt.title[:30]}...\" en {self.selected_format.get()}")
            stream.download(output_path=self.download_path.get(), filename=filename)

        except RegexMatchError:
            messagebox.showerror("Erreur", "URL YouTube invalide.")
            self.reset_ui()
        except VideoUnavailable:
            messagebox.showerror("Erreur", "Vidéo non disponible ou privée.")
            self.reset_ui()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
            self.reset_ui()

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.progress_bar["value"] = percentage
        self.status_label.config(text=f"Téléchargement... {percentage:.2f}%")
        self.master.update_idletasks() # Met à jour l'interface

    def on_complete(self, stream, file_path):
        self.status_label.config(text=f"Téléchargement terminé! Sauvegardé dans: {file_path}")
        self.progress_bar["value"] = 100
        messagebox.showinfo("Succès", f"Téléchargement terminé!\nFichier sauvegardé ici: {file_path}")
        self.reset_ui()

    def reset_ui(self):
        self.download_button.config(state=tk.NORMAL)
        # self.progress_bar["value"] = 0 # Garder la barre pleine en cas de succès, ou la réinitialiser ?
        # self.status_label.config(text="Prêt") # Ou garder le message de succès/erreur

if __name__ == '__main__':
    root = tk.Tk()
    # Importer sys pour la gestion du chemin de l'icône lors de la compilation
    import sys 
    app = YouTubeDownloaderApp(root)
    root.mainloop()
