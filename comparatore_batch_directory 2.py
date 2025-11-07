import os
import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import hashlib
from datetime import datetime
import threading

class ComparatoreBatchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparatore Biometrico Batch - Directory vs Directory")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # Inizializza MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Variabili per le directory
        self.dir1_path = None
        self.dir2_path = None
        self.risultati = []
        self.stop_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Titolo
        title = tk.Label(
            self.root, 
            text="Comparatore Biometrico Batch - Directory vs Directory", 
            font=("Arial", 22, "bold"),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title.pack(pady=20)
        
        # Frame per i pulsanti directory
        dir_frame = tk.Frame(self.root, bg='#2c3e50')
        dir_frame.pack(pady=10)
        
        # Directory 1
        self.btn_dir1 = tk.Button(
            dir_frame,
            text="📁 Seleziona Directory 1",
            command=self.seleziona_dir1,
            font=("Arial", 12, "bold"),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.btn_dir1.pack(side=tk.LEFT, padx=10)
        
        self.label_dir1 = tk.Label(
            dir_frame,
            text="Nessuna directory selezionata",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            width=40
        )
        self.label_dir1.pack(side=tk.LEFT, padx=10)
        
        # Directory 2
        dir_frame2 = tk.Frame(self.root, bg='#2c3e50')
        dir_frame2.pack(pady=10)
        
        self.btn_dir2 = tk.Button(
            dir_frame2,
            text="📁 Seleziona Directory 2",
            command=self.seleziona_dir2,
            font=("Arial", 12, "bold"),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.btn_dir2.pack(side=tk.LEFT, padx=10)
        
        self.label_dir2 = tk.Label(
            dir_frame2,
            text="Nessuna directory selezionata",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            width=40
        )
        self.label_dir2.pack(side=tk.LEFT, padx=10)
        
        # Frame controlli
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(pady=20)
        
        self.btn_compara = tk.Button(
            control_frame,
            text="🔍 Avvia Comparazione Batch",
            command=self.avvia_comparazione,
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            padx=30,
            pady=12,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.btn_compara.pack(side=tk.LEFT, padx=10)
        
        self.btn_stop = tk.Button(
            control_frame,
            text="⏹ Stop",
            command=self.stop_comparazione,
            font=("Arial", 12, "bold"),
            bg='#e74c3c',
            fg='white',
            padx=30,
            pady=12,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=10)
        
        self.btn_export = tk.Button(
            control_frame,
            text="📊 Esporta Report CSV",
            command=self.esporta_csv,
            font=("Arial", 12, "bold"),
            bg='#9b59b6',
            fg='white',
            padx=30,
            pady=12,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.btn_export.pack(side=tk.LEFT, padx=10)
        
        # Progress bar
        progress_frame = tk.Frame(self.root, bg='#2c3e50')
        progress_frame.pack(pady=10, fill=tk.X, padx=40)
        
        self.progress = ttk.Progressbar(
            progress_frame,
            orient='horizontal',
            length=800,
            mode='determinate'
        )
        self.progress.pack(pady=5)
        
        self.label_progress = tk.Label(
            progress_frame,
            text="Pronto",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.label_progress.pack(pady=5)
        
        # Frame risultati con scrollbar
        result_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        result_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(
            result_frame,
            text="RISULTATI COMPARAZIONI",
            font=("Arial", 14, "bold"),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=10)
        
        # Scrollbar
        scroll_frame = tk.Frame(result_frame, bg='#34495e')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            scroll_frame,
            columns=('File1', 'File2', 'Compatibilità', 'Distanza', 'Status'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )
        
        self.tree.heading('File1', text='Immagine Directory 1')
        self.tree.heading('File2', text='Immagine Directory 2')
        self.tree.heading('Compatibilità', text='Compatibilità %')
        self.tree.heading('Distanza', text='Distanza')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('File1', width=250)
        self.tree.column('File2', width=250)
        self.tree.column('Compatibilità', width=120, anchor='center')
        self.tree.column('Distanza', width=120, anchor='center')
        self.tree.column('Status', width=150, anchor='center')
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Tag colors
        self.tree.tag_configure('alta', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('media', background='#fff3cd', foreground='#856404')
        self.tree.tag_configure('bassa', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('errore', background='#f5c6cb', foreground='#721c24')
        
        # Statistiche
        stats_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        stats_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.label_stats = tk.Label(
            stats_frame,
            text="Statistiche: Totali: 0 | Alta: 0 | Media: 0 | Bassa: 0 | Errori: 0",
            font=("Arial", 11, "bold"),
            bg='#34495e',
            fg='#ecf0f1',
            pady=10
        )
        self.label_stats.pack()
    
    def seleziona_dir1(self):
        directory = filedialog.askdirectory(title="Seleziona Directory 1")
        if directory:
            self.dir1_path = directory
            num_images = len(self.get_image_files(directory))
            self.label_dir1.config(text=f"{directory} ({num_images} immagini)")
            self.verifica_stato_pulsante()
    
    def seleziona_dir2(self):
        directory = filedialog.askdirectory(title="Seleziona Directory 2")
        if directory:
            self.dir2_path = directory
            num_images = len(self.get_image_files(directory))
            self.label_dir2.config(text=f"{directory} ({num_images} immagini)")
            self.verifica_stato_pulsante()
    
    def verifica_stato_pulsante(self):
        if self.dir1_path and self.dir2_path:
            self.btn_compara.config(state=tk.NORMAL)
        else:
            self.btn_compara.config(state=tk.DISABLED)
    
    def get_image_files(self, directory):
        """Ottiene tutti i file immagine dalla directory"""
        extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP')
        image_files = []
        for file in os.listdir(directory):
            if file.endswith(extensions):
                image_files.append(os.path.join(directory, file))
        return sorted(image_files)
    
    def calcola_hash(self, filepath):
        """Calcola SHA256 hash del file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def elabora_immagine(self, filepath):
        """Elabora l'immagine ed estrae i landmarks"""
        try:
            img = cv2.imread(filepath)
            if img is None:
                return None, None, "Impossibile caricare l'immagine"
            
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = self.face_mesh.process(rgb)
            
            if not result.multi_face_landmarks:
                return None, None, "Nessun volto rilevato"
            
            face_landmarks = result.multi_face_landmarks[0]
            landmarks_array = np.array([[l.x, l.y, l.z] for l in face_landmarks.landmark])
            
            # Crea immagine con landmarks
            img_landmarks = img.copy()
            self.mp_drawing.draw_landmarks(
                image=img_landmarks,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(0, 255, 0), 
                    thickness=1, 
                    circle_radius=1
                )
            )
            
            return landmarks_array, img_landmarks, None
        except Exception as e:
            return None, None, str(e)
    
    def calcola_compatibilita(self, pts1, pts2):
        """Calcola la compatibilità biometrica tra due set di landmarks"""
        min_len = min(len(pts1), len(pts2))
        pts1 = pts1[:min_len]
        pts2 = pts2[:min_len]
        
        distanze = np.linalg.norm(pts1 - pts2, axis=1)
        distanza_media = np.mean(distanze)
        
        compatibilita = max(0, min(100, (1 - distanza_media / 0.2) * 100))
        
        return compatibilita, distanza_media
    
    def stop_comparazione(self):
        self.stop_processing = True
        self.label_progress.config(text="Interruzione in corso...")
    
    def avvia_comparazione(self):
        # Pulisci risultati precedenti
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.risultati = []
        self.stop_processing = False
        
        # Disabilita pulsanti
        self.btn_compara.config(state=tk.DISABLED)
        self.btn_dir1.config(state=tk.DISABLED)
        self.btn_dir2.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_export.config(state=tk.DISABLED)
        
        # Avvia in thread separato
        thread = threading.Thread(target=self.esegui_comparazione_batch)
        thread.daemon = True
        thread.start()
    
    def esegui_comparazione_batch(self):
        """Esegue la comparazione di tutte le immagini"""
        try:
            # Ottieni file
            files_dir1 = self.get_image_files(self.dir1_path)
            files_dir2 = self.get_image_files(self.dir2_path)
            
            total = len(files_dir1) * len(files_dir2)
            current = 0
            
            self.root.after(0, self.label_progress.config, 
                           {'text': f'Elaborazione: 0/{total} comparazioni'})
            
            # Compara ogni immagine di dir1 con ogni immagine di dir2
            for file1 in files_dir1:
                if self.stop_processing:
                    break
                
                # Elabora immagine 1
                landmarks1, img1_land, error1 = self.elabora_immagine(file1)
                
                if error1:
                    # Aggiungi errore per tutte le comparazioni con questa immagine
                    for file2 in files_dir2:
                        self.aggiungi_risultato_errore(file1, file2, f"Dir1: {error1}")
                        current += 1
                        self.aggiorna_progress(current, total)
                    continue
                
                for file2 in files_dir2:
                    if self.stop_processing:
                        break
                    
                    # Elabora immagine 2
                    landmarks2, img2_land, error2 = self.elabora_immagine(file2)
                    
                    if error2:
                        self.aggiungi_risultato_errore(file1, file2, f"Dir2: {error2}")
                    else:
                        # Calcola compatibilità
                        compatibilita, distanza = self.calcola_compatibilita(landmarks1, landmarks2)
                        
                        # Salva risultato
                        risultato = {
                            'file1': file1,
                            'file2': file2,
                            'nome1': os.path.basename(file1),
                            'nome2': os.path.basename(file2),
                            'compatibilita': compatibilita,
                            'distanza': distanza,
                            'hash1': self.calcola_hash(file1),
                            'hash2': self.calcola_hash(file2),
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        self.risultati.append(risultato)
                        
                        # Aggiungi a treeview
                        self.root.after(0, self.aggiungi_risultato_tree, risultato)
                    
                    current += 1
                    self.aggiorna_progress(current, total)
            
            # Completato
            if self.stop_processing:
                self.root.after(0, self.label_progress.config, 
                               {'text': 'Comparazione interrotta'})
            else:
                self.root.after(0, self.label_progress.config, 
                               {'text': f'Completato! {len(self.risultati)} comparazioni eseguite'})
                self.root.after(0, messagebox.showinfo, 
                               "Completato", 
                               f"Comparazione completata!\n{len(self.risultati)} confronti eseguiti.")
            
            # Riabilita pulsanti
            self.root.after(0, self.btn_compara.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_dir1.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_dir2.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_stop.config, {'state': tk.DISABLED})
            self.root.after(0, self.btn_export.config, {'state': tk.NORMAL})
            
            # Aggiorna statistiche
            self.root.after(0, self.aggiorna_statistiche)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Errore", f"Errore durante la comparazione: {str(e)}")
    
    def aggiungi_risultato_tree(self, risultato):
        """Aggiunge un risultato alla treeview"""
        comp = risultato['compatibilita']
        
        if comp >= 80:
            status = "ALTA"
            tag = 'alta'
        elif comp >= 60:
            status = "MEDIA"
            tag = 'media'
        else:
            status = "BASSA"
            tag = 'bassa'
        
        self.tree.insert('', 'end', 
                        values=(
                            risultato['nome1'],
                            risultato['nome2'],
                            f"{comp:.2f}%",
                            f"{risultato['distanza']:.4f}",
                            status
                        ),
                        tags=(tag,))
    
    def aggiungi_risultato_errore(self, file1, file2, errore):
        """Aggiunge un risultato di errore"""
        self.root.after(0, self.tree.insert, '', 'end', 
                       {'values': (
                           os.path.basename(file1),
                           os.path.basename(file2),
                           "N/A",
                           "N/A",
                           f"ERRORE: {errore}"
                       ),
                       'tags': ('errore',)})
    
    def aggiorna_progress(self, current, total):
        """Aggiorna la progress bar"""
        percentage = (current / total) * 100
        self.root.after(0, self.progress.config, {'value': percentage})
        self.root.after(0, self.label_progress.config, 
                       {'text': f'Elaborazione: {current}/{total} comparazioni ({percentage:.1f}%)'})
    
    def aggiorna_statistiche(self):
        """Aggiorna le statistiche"""
        totali = len(self.risultati)
        alta = sum(1 for r in self.risultati if r['compatibilita'] >= 80)
        media = sum(1 for r in self.risultati if 60 <= r['compatibilita'] < 80)
        bassa = sum(1 for r in self.risultati if r['compatibilita'] < 60)
        
        # Conta errori nella treeview
        errori = len([item for item in self.tree.get_children() 
                     if 'errore' in self.tree.item(item)['tags']])
        
        self.label_stats.config(
            text=f"Statistiche: Totali: {totali} | Alta (≥80%): {alta} | "
                 f"Media (60-79%): {media} | Bassa (<60%): {bassa} | Errori: {errori}"
        )
    
    def esporta_csv(self):
        """Esporta i risultati in CSV"""
        if not self.risultati:
            messagebox.showwarning("Attenzione", "Nessun risultato da esportare")
            return
        
        # Chiedi dove salvare
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"comparazione_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Header
                f.write("File Directory 1,File Directory 2,Compatibilità %,Distanza,Status,"
                       "Hash File 1,Hash File 2,Timestamp\n")
                
                # Dati
                for r in self.risultati:
                    comp = r['compatibilita']
                    if comp >= 80:
                        status = "ALTA"
                    elif comp >= 60:
                        status = "MEDIA"
                    else:
                        status = "BASSA"
                    
                    f.write(f"{r['nome1']},{r['nome2']},{comp:.2f},{r['distanza']:.6f},"
                           f"{status},{r['hash1']},{r['hash2']},{r['timestamp']}\n")
            
            messagebox.showinfo("Successo", f"Report esportato con successo in:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esportazione: {str(e)}")

def main():
    root = tk.Tk()
    app = ComparatoreBatchGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
