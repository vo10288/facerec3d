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

class ComparatoreBatchAvanzatoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparatore Biometrico Batch Avanzato - Report HTML Unificato")
        self.root.geometry("1600x950")
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
        
        # Variabili
        self.dir1_path = None
        self.dir2_path = None
        self.risultati = []
        self.stop_processing = False
        self.genera_html = tk.BooleanVar(value=True)
        self.soglia_compatibilita = tk.DoubleVar(value=0.0)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Container principale
        main_container = tk.Frame(self.root, bg='#2c3e50')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === COLONNA SINISTRA ===
        left_column = tk.Frame(main_container, bg='#2c3e50')
        left_column.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Titolo
        title = tk.Label(
            left_column, 
            text="Comparatore Batch\nAvanzato", 
            font=("Arial", 16, "bold"),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title.pack(pady=10)
        
        # Directory
        dir_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        dir_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(dir_frame, text="DIRECTORY", font=("Arial", 10, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.btn_dir1 = tk.Button(dir_frame, text="📁 Dir 1", command=self.seleziona_dir1,
            font=("Arial", 9, "bold"), bg='#3498db', fg='white', padx=10, pady=5)
        self.btn_dir1.pack(pady=3)
        
        self.label_dir1 = tk.Label(dir_frame, text="---", font=("Arial", 8),
            bg='#34495e', fg='#ecf0f1', wraplength=200)
        self.label_dir1.pack(pady=3)
        
        self.btn_dir2 = tk.Button(dir_frame, text="📁 Dir 2", command=self.seleziona_dir2,
            font=("Arial", 9, "bold"), bg='#3498db', fg='white', padx=10, pady=5)
        self.btn_dir2.pack(pady=3)
        
        self.label_dir2 = tk.Label(dir_frame, text="---", font=("Arial", 8),
            bg='#34495e', fg='#ecf0f1', wraplength=200)
        self.label_dir2.pack(pady=3)
        
        # Opzioni
        opt_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        opt_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(opt_frame, text="OPZIONI", font=("Arial", 10, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.check_html = tk.Checkbutton(opt_frame, text="Report HTML",
            variable=self.genera_html, font=("Arial", 8), bg='#34495e', fg='#ecf0f1',
            selectcolor='#2c3e50', activebackground='#34495e')
        self.check_html.pack(pady=2)
        
        soglia_frame = tk.Frame(opt_frame, bg='#34495e')
        soglia_frame.pack(pady=3)
        
        tk.Label(soglia_frame, text="Soglia %:", font=("Arial", 8),
                bg='#34495e', fg='#ecf0f1').pack(side=tk.LEFT, padx=3)
        
        self.spin_soglia = tk.Spinbox(soglia_frame, from_=0, to=100,
            textvariable=self.soglia_compatibilita, width=6, font=("Arial", 8))
        self.spin_soglia.pack(side=tk.LEFT)
        
        # Controlli
        ctrl_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        ctrl_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(ctrl_frame, text="AZIONI", font=("Arial", 10, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.btn_compara = tk.Button(ctrl_frame, text="🔍 AVVIA", command=self.avvia_comparazione,
            font=("Arial", 10, "bold"), bg='#27ae60', fg='white', padx=15, pady=8, state=tk.DISABLED)
        self.btn_compara.pack(pady=3)
        
        self.btn_stop = tk.Button(ctrl_frame, text="⏹ STOP", command=self.stop_comparazione,
            font=("Arial", 10, "bold"), bg='#e74c3c', fg='white', padx=15, pady=8, state=tk.DISABLED)
        self.btn_stop.pack(pady=3)
        
        self.btn_export = tk.Button(ctrl_frame, text="📊 CSV", command=self.esporta_csv,
            font=("Arial", 9), bg='#9b59b6', fg='white', padx=15, pady=6, state=tk.DISABLED)
        self.btn_export.pack(pady=2)
        
        self.btn_html = tk.Button(ctrl_frame, text="📄 HTML", command=self.apri_report_html,
            font=("Arial", 9), bg='#16a085', fg='white', padx=15, pady=6, state=tk.DISABLED)
        self.btn_html.pack(pady=2)
        
        # Progress
        prog_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        prog_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(prog_frame, text="PROGRESS", font=("Arial", 10, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.progress = ttk.Progressbar(prog_frame, orient='horizontal', length=200, mode='determinate')
        self.progress.pack(pady=5, padx=5)
        
        self.label_progress = tk.Label(prog_frame, text="Pronto", font=("Arial", 8),
            bg='#34495e', fg='#ecf0f1')
        self.label_progress.pack(pady=3)
        
        # Statistiche
        stats_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        stats_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(stats_frame, text="STATS", font=("Arial", 10, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.label_stats = tk.Label(stats_frame, text="Totali: 0\nAlta: 0\nMedia: 0\nBassa: 0",
            font=("Arial", 8), bg='#34495e', fg='#ecf0f1', justify=tk.LEFT)
        self.label_stats.pack(pady=5)
        
        # === COLONNA DESTRA ===
        right_column = tk.Frame(main_container, bg='#2c3e50')
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Preview comparazione corrente
        preview_frame = tk.Frame(right_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        preview_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(preview_frame, text="COMPARAZIONE CORRENTE", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        # Container per le 4 immagini (2x2)
        images_container = tk.Frame(preview_frame, bg='#34495e')
        images_container.pack(pady=5)
        
        # Riga superiore (originali)
        row1 = tk.Frame(images_container, bg='#34495e')
        row1.pack()
        
        # Immagine 1 Originale
        frame_img1_orig = tk.Frame(row1, bg='#2c3e50')
        frame_img1_orig.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_img1_orig, text="Dir 1 - Originale", font=("Arial", 8, "bold"),
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.label_img1_orig = tk.Label(frame_img1_orig, bg='#2c3e50', width=200, height=150)
        self.label_img1_orig.pack()
        
        # Immagine 2 Originale
        frame_img2_orig = tk.Frame(row1, bg='#2c3e50')
        frame_img2_orig.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_img2_orig, text="Dir 2 - Originale", font=("Arial", 8, "bold"),
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.label_img2_orig = tk.Label(frame_img2_orig, bg='#2c3e50', width=200, height=150)
        self.label_img2_orig.pack()
        
        # Riga inferiore (landmarks)
        row2 = tk.Frame(images_container, bg='#34495e')
        row2.pack(pady=5)
        
        # Immagine 1 Landmarks
        frame_img1_land = tk.Frame(row2, bg='#2c3e50')
        frame_img1_land.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_img1_land, text="Dir 1 - Landmarks", font=("Arial", 8, "bold"),
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.label_img1_land = tk.Label(frame_img1_land, bg='#2c3e50', width=200, height=150)
        self.label_img1_land.pack()
        
        # Immagine 2 Landmarks
        frame_img2_land = tk.Frame(row2, bg='#2c3e50')
        frame_img2_land.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_img2_land, text="Dir 2 - Landmarks", font=("Arial", 8, "bold"),
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.label_img2_land = tk.Label(frame_img2_land, bg='#2c3e50', width=200, height=150)
        self.label_img2_land.pack()
        
        # Nomi file e risultato
        self.label_names = tk.Label(preview_frame, text="---", font=("Arial", 8),
            bg='#34495e', fg='#ecf0f1')
        self.label_names.pack(pady=3)
        
        self.label_result = tk.Label(preview_frame, text="---", font=("Arial", 12, "bold"),
            bg='#34495e', fg='#ecf0f1')
        self.label_result.pack(pady=5)
        
        # Tabella risultati
        result_frame = tk.Frame(right_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        result_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        tk.Label(result_frame, text="RISULTATI", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        scroll_frame = tk.Frame(result_frame, bg='#34495e')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(scroll_frame, columns=('File1', 'File2', 'Comp', 'Status'),
            show='headings', yscrollcommand=scrollbar.set, height=15)
        
        self.tree.heading('File1', text='File Dir 1')
        self.tree.heading('File2', text='File Dir 2')
        self.tree.heading('Comp', text='Comp %')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('File1', width=250)
        self.tree.column('File2', width=250)
        self.tree.column('Comp', width=80, anchor='center')
        self.tree.column('Status', width=100, anchor='center')
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Bind click sulla riga
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        self.tree.tag_configure('alta', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('media', background='#fff3cd', foreground='#856404')
        self.tree.tag_configure('bassa', background='#f8d7da', foreground='#721c24')
    
    def mostra_preview(self, img1_orig, img2_orig, img1_land, img2_land, nome1, nome2, comp):
        """Mostra le 4 immagini nella GUI"""
        try:
            max_size = 200
            
            # Funzione helper per ridimensionare
            def resize_img(img):
                h, w = img.shape[:2]
                scale = max_size / max(h, w)
                new_w, new_h = int(w * scale), int(h * scale)
                return cv2.resize(img, (new_w, new_h))
            
            # Immagine 1 Originale
            img1_o_resized = resize_img(img1_orig)
            img1_o_rgb = cv2.cvtColor(img1_o_resized, cv2.COLOR_BGR2RGB)
            img1_o_pil = Image.fromarray(img1_o_rgb)
            img1_o_tk = ImageTk.PhotoImage(img1_o_pil)
            self.label_img1_orig.config(image=img1_o_tk)
            self.label_img1_orig.image = img1_o_tk
            
            # Immagine 2 Originale
            img2_o_resized = resize_img(img2_orig)
            img2_o_rgb = cv2.cvtColor(img2_o_resized, cv2.COLOR_BGR2RGB)
            img2_o_pil = Image.fromarray(img2_o_rgb)
            img2_o_tk = ImageTk.PhotoImage(img2_o_pil)
            self.label_img2_orig.config(image=img2_o_tk)
            self.label_img2_orig.image = img2_o_tk
            
            # Immagine 1 Landmarks
            img1_l_resized = resize_img(img1_land)
            img1_l_rgb = cv2.cvtColor(img1_l_resized, cv2.COLOR_BGR2RGB)
            img1_l_pil = Image.fromarray(img1_l_rgb)
            img1_l_tk = ImageTk.PhotoImage(img1_l_pil)
            self.label_img1_land.config(image=img1_l_tk)
            self.label_img1_land.image = img1_l_tk
            
            # Immagine 2 Landmarks
            img2_l_resized = resize_img(img2_land)
            img2_l_rgb = cv2.cvtColor(img2_l_resized, cv2.COLOR_BGR2RGB)
            img2_l_pil = Image.fromarray(img2_l_rgb)
            img2_l_tk = ImageTk.PhotoImage(img2_l_pil)
            self.label_img2_land.config(image=img2_l_tk)
            self.label_img2_land.image = img2_l_tk
            
            # Nomi
            self.label_names.config(text=f"{nome1}  ←→  {nome2}")
            
            # Risultato
            if comp >= 80:
                color = '#27ae60'
                status = 'ALTA'
            elif comp >= 60:
                color = '#f39c12'
                status = 'MEDIA'
            else:
                color = '#e74c3c'
                status = 'BASSA'
            
            self.label_result.config(text=f"{comp:.2f}% - {status}", fg=color)
            
            self.root.update()
            
        except Exception as e:
            print(f"Errore preview: {e}")
    
    def on_tree_select(self, event):
        """Gestisce il click su una riga della lista risultati"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Prendi il primo item selezionato
        item = selection[0]
        
        # Trova il risultato corrispondente
        for risultato in self.risultati:
            if risultato.get('tree_item') == item:
                # Ricarica le immagini dai file salvati
                try:
                    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports_batch_unified')
                    
                    img1_orig_path = os.path.join(reports_dir, risultato['img1_orig_rel'])
                    img2_orig_path = os.path.join(reports_dir, risultato['img2_orig_rel'])
                    img1_land_path = os.path.join(reports_dir, risultato['img1_land_rel'])
                    img2_land_path = os.path.join(reports_dir, risultato['img2_land_rel'])
                    
                    img1_orig = cv2.imread(img1_orig_path)
                    img2_orig = cv2.imread(img2_orig_path)
                    img1_land = cv2.imread(img1_land_path)
                    img2_land = cv2.imread(img2_land_path)
                    
                    # Mostra le immagini
                    self.mostra_preview(
                        img1_orig, img2_orig, img1_land, img2_land,
                        risultato['nome1'], risultato['nome2'],
                        risultato['compatibilita']
                    )
                    
                except Exception as e:
                    print(f"Errore caricamento immagini: {e}")
                    messagebox.showerror("Errore", f"Impossibile caricare le immagini: {str(e)}")
                
                break
    
    def seleziona_dir1(self):
        directory = filedialog.askdirectory(title="Seleziona Directory 1")
        if directory:
            self.dir1_path = directory
            num = len(self.get_image_files(directory))
            self.label_dir1.config(text=f"({num} img)")
            self.verifica_stato_pulsante()
    
    def seleziona_dir2(self):
        directory = filedialog.askdirectory(title="Seleziona Directory 2")
        if directory:
            self.dir2_path = directory
            num = len(self.get_image_files(directory))
            self.label_dir2.config(text=f"({num} img)")
            self.verifica_stato_pulsante()
    
    def verifica_stato_pulsante(self):
        if self.dir1_path and self.dir2_path:
            self.btn_compara.config(state=tk.NORMAL)
    
    def get_image_files(self, directory):
        extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP')
        return sorted([os.path.join(directory, f) for f in os.listdir(directory) 
                      if f.endswith(extensions)])
    
    def calcola_hash(self, filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def elabora_immagine(self, filepath):
        try:
            img = cv2.imread(filepath)
            if img is None:
                return None, None, "Load error"
            
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = self.face_mesh.process(rgb)
            
            if not result.multi_face_landmarks:
                return None, None, "No face"
            
            face_landmarks = result.multi_face_landmarks[0]
            landmarks_array = np.array([[l.x, l.y, l.z] for l in face_landmarks.landmark])
            
            img_landmarks = img.copy()
            self.mp_drawing.draw_landmarks(
                image=img_landmarks,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=1, circle_radius=1
                )
            )
            
            self.mp_drawing.draw_landmarks(
                image=img_landmarks,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(255, 0, 0), thickness=2, circle_radius=1
                )
            )
            
            return landmarks_array, img_landmarks, None
        except Exception as e:
            return None, None, str(e)[:15]
    
    def calcola_compatibilita(self, pts1, pts2):
        min_len = min(len(pts1), len(pts2))
        distanze = np.linalg.norm(pts1[:min_len] - pts2[:min_len], axis=1)
        distanza_media = np.mean(distanze)
        compatibilita = max(0, min(100, (1 - distanza_media / 0.2) * 100))
        return compatibilita, distanza_media
    
    def stop_comparazione(self):
        self.stop_processing = True
    
    def avvia_comparazione(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.risultati = []
        self.stop_processing = False
        
        self.btn_compara.config(state=tk.DISABLED)
        self.btn_dir1.config(state=tk.DISABLED)
        self.btn_dir2.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_export.config(state=tk.DISABLED)
        self.btn_html.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.esegui_comparazione_batch)
        thread.daemon = True
        thread.start()
    
    def esegui_comparazione_batch(self):
        try:
            files_dir1 = self.get_image_files(self.dir1_path)
            files_dir2 = self.get_image_files(self.dir2_path)
            
            total = len(files_dir1) * len(files_dir2)
            current = 0
            soglia = self.soglia_compatibilita.get()
            
            reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports_batch_unified')
            os.makedirs(reports_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            self.root.after(0, self.label_progress.config, {'text': f'0/{total}'})
            
            for file1 in files_dir1:
                if self.stop_processing:
                    break
                
                landmarks1, img1_land, error1 = self.elabora_immagine(file1)
                img1_orig = cv2.imread(file1)
                
                if error1:
                    for file2 in files_dir2:
                        current += 1
                        self.aggiorna_progress(current, total)
                    continue
                
                for file2 in files_dir2:
                    if self.stop_processing:
                        break
                    
                    landmarks2, img2_land, error2 = self.elabora_immagine(file2)
                    img2_orig = cv2.imread(file2)
                    
                    if not error2:
                        compatibilita, distanza = self.calcola_compatibilita(landmarks1, landmarks2)
                        
                        if compatibilita >= soglia:
                            # Salva tutte le immagini
                            img_id = f"{timestamp}_{current}"
                            
                            img1_orig_path = os.path.join(reports_dir, f'img1_orig_{img_id}.jpg')
                            img2_orig_path = os.path.join(reports_dir, f'img2_orig_{img_id}.jpg')
                            img1_land_path = os.path.join(reports_dir, f'img1_land_{img_id}.jpg')
                            img2_land_path = os.path.join(reports_dir, f'img2_land_{img_id}.jpg')
                            
                            cv2.imwrite(img1_orig_path, img1_orig)
                            cv2.imwrite(img2_orig_path, img2_orig)
                            cv2.imwrite(img1_land_path, img1_land)
                            cv2.imwrite(img2_land_path, img2_land)
                            
                            risultato = {
                                'file1': file1,
                                'file2': file2,
                                'nome1': os.path.basename(file1),
                                'nome2': os.path.basename(file2),
                                'compatibilita': compatibilita,
                                'distanza': distanza,
                                'hash1': self.calcola_hash(file1),
                                'hash2': self.calcola_hash(file2),
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'img1_orig_rel': os.path.basename(img1_orig_path),
                                'img2_orig_rel': os.path.basename(img2_orig_path),
                                'img1_land_rel': os.path.basename(img1_land_path),
                                'img2_land_rel': os.path.basename(img2_land_path)
                            }
                            
                            self.risultati.append(risultato)
                            self.root.after(0, self.aggiungi_risultato_tree, risultato)
                            
                            # Mostra preview nella GUI
                            self.root.after(0, self.mostra_preview, 
                                          img1_orig, img2_orig, img1_land, img2_land,
                                          risultato['nome1'], risultato['nome2'], compatibilita)
                    
                    current += 1
                    self.aggiorna_progress(current, total)
            
            if self.genera_html.get() and self.risultati:
                self.root.after(0, self.genera_report_html_unificato, reports_dir, timestamp)
            
            if self.stop_processing:
                self.root.after(0, self.label_progress.config, {'text': 'Interrotto'})
            else:
                self.root.after(0, self.label_progress.config, 
                               {'text': f'Completato! {len(self.risultati)} risultati'})
                self.root.after(0, messagebox.showinfo, "Completato", 
                               f"{len(self.risultati)} comparazioni salvate")
            
            self.root.after(0, self.btn_compara.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_dir1.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_dir2.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_stop.config, {'state': tk.DISABLED})
            if self.risultati:
                self.root.after(0, self.btn_export.config, {'state': tk.NORMAL})
                self.root.after(0, self.btn_html.config, {'state': tk.NORMAL})
            
            self.root.after(0, self.aggiorna_statistiche)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Errore", str(e))
    
    def genera_report_html_unificato(self, reports_dir, timestamp):
        """Genera report HTML con TUTTE le immagini visibili direttamente"""
        try:
            html_path = os.path.join(reports_dir, f'report_unificato_{timestamp}.html')
            
            totali = len(self.risultati)
            alta = sum(1 for r in self.risultati if r['compatibilita'] >= 80)
            media = sum(1 for r in self.risultati if 60 <= r['compatibilita'] < 80)
            bassa = sum(1 for r in self.risultati if r['compatibilita'] < 60)
            
            # Genera righe con TUTTE le immagini visibili
            rows_html = ""
            for idx, r in enumerate(self.risultati, 1):
                comp = r['compatibilita']
                if comp >= 80:
                    bg_color, status = '#d4edda', 'ALTA'
                elif comp >= 60:
                    bg_color, status = '#fff3cd', 'MEDIA'
                else:
                    bg_color, status = '#f8d7da', 'BASSA'
                
                rows_html += f"""
                <tr style="background-color: {bg_color};" class="result-row">
                    <td style="text-align: center; font-weight: bold;">{idx}</td>
                    <td class="file-name" data-file1="{r['nome1']}">{r['nome1']}</td>
                    <td class="file-name" data-file2="{r['nome2']}">{r['nome2']}</td>
                    <td style="text-align: center; font-weight: bold;" class="compatibility" data-comp="{comp:.2f}">{comp:.2f}%</td>
                    <td style="text-align: center;"><b>{status}</b></td>
                </tr>
                <tr style="background-color: {bg_color};">
                    <td colspan="5" style="padding: 15px;">
                        <div style="display: flex; justify-content: space-around;">
                            <div style="text-align: center; flex: 1; margin: 0 5px;">
                                <div style="font-weight: bold; margin-bottom: 5px; color: #555;">Dir 1 - Originale</div>
                                <img src="{r['img1_orig_rel']}" style="max-width: 250px; max-height: 250px; border: 2px solid #aaa; border-radius: 5px;">
                            </div>
                            <div style="text-align: center; flex: 1; margin: 0 5px;">
                                <div style="font-weight: bold; margin-bottom: 5px; color: #555;">Dir 2 - Originale</div>
                                <img src="{r['img2_orig_rel']}" style="max-width: 250px; max-height: 250px; border: 2px solid #aaa; border-radius: 5px;">
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-around; margin-top: 15px;">
                            <div style="text-align: center; flex: 1; margin: 0 5px;">
                                <div style="font-weight: bold; margin-bottom: 5px; color: #555;">Dir 1 - Landmarks</div>
                                <img src="{r['img1_land_rel']}" style="max-width: 250px; max-height: 250px; border: 2px solid #28a745; border-radius: 5px;">
                            </div>
                            <div style="text-align: center; flex: 1; margin: 0 5px;">
                                <div style="font-weight: bold; margin-bottom: 5px; color: #555;">Dir 2 - Landmarks</div>
                                <img src="{r['img2_land_rel']}" style="max-width: 250px; max-height: 250px; border: 2px solid #28a745; border-radius: 5px;">
                            </div>
                        </div>
                    </td>
                </tr>
                <tr><td colspan="5" style="height: 20px; background: #f8f9fa;"></td></tr>
                """
            
            html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report Unificato - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .stats-bar {{
            background: #f8f9fa;
            padding: 20px;
            display: flex;
            justify-content: space-around;
            border-bottom: 2px solid #dee2e6;
        }}
        .stat-box {{
            text-align: center;
            padding: 15px;
            border-radius: 10px;
            flex: 1;
            margin: 0 10px;
        }}
        .stat-box.total {{ background: #e7f3ff; border: 2px solid #0077cc; }}
        .stat-box.alta {{ background: #d4edda; border: 2px solid #28a745; }}
        .stat-box.media {{ background: #fff3cd; border: 2px solid #ffc107; }}
        .stat-box.bassa {{ background: #f8d7da; border: 2px solid #dc3545; }}
        .stat-number {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .stat-label {{ font-size: 13px; color: #666; text-transform: uppercase; }}
        .controls {{
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        .btn-group {{ display: flex; gap: 10px; margin: 5px 0; }}
        .btn {{
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-warning {{ background: #ffc107; color: black; }}
        .btn-danger {{ background: #dc3545; color: white; }}
        .btn-info {{ background: #17a2b8; color: white; }}
        .search-box {{
            padding: 10px;
            font-size: 13px;
            border: 2px solid #ddd;
            border-radius: 8px;
            width: 300px;
        }}
        .table-container {{ padding: 20px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        th {{
            background: #343a40;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            cursor: pointer;
            user-select: none;
        }}
        th:hover {{ background: #495057; }}
        th.sortable::after {{ content: ' ⇅'; opacity: 0.5; }}
        th.sort-asc::after {{ content: ' ▲'; opacity: 1; }}
        th.sort-desc::after {{ content: ' ▼'; opacity: 1; }}
        td {{ padding: 10px; border-bottom: 1px solid #dee2e6; }}
        tr:hover {{ opacity: 0.95; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Report Unificato Comparazioni Biometriche</h1>
            <p>Generato il: {datetime.now().strftime('%d/%m/%Y alle %H:%M:%S')}</p>
            <p style="font-size: 12px; margin-top: 5px;">Tutte le immagini (originali + landmarks) visibili direttamente</p>
        </div>
        
        <div class="stats-bar">
            <div class="stat-box total">
                <div class="stat-number">{totali}</div>
                <div class="stat-label">Totali</div>
            </div>
            <div class="stat-box alta">
                <div class="stat-number">{alta}</div>
                <div class="stat-label">Alta (≥80%)</div>
            </div>
            <div class="stat-box media">
                <div class="stat-number">{media}</div>
                <div class="stat-label">Media (60-79%)</div>
            </div>
            <div class="stat-box bassa">
                <div class="stat-number">{bassa}</div>
                <div class="stat-label">Bassa (&lt;60%)</div>
            </div>
        </div>
        
        <div class="controls">
            <div class="btn-group">
                <button class="btn btn-primary" onclick="sortTable('compatibility', 'desc')">
                    📊 Ordina per Compatibilità ↓
                </button>
                <button class="btn btn-info" onclick="sortTable('file1', 'asc')">
                    📁 Ordina per File 1 (A-Z)
                </button>
                <button class="btn btn-info" onclick="sortTable('file2', 'asc')">
                    📁 Ordina per File 2 (A-Z)
                </button>
            </div>
            <div class="btn-group">
                <button class="btn btn-success" onclick="filterResults('alta')">🟢 Alta</button>
                <button class="btn btn-warning" onclick="filterResults('media')">🟡 Media</button>
                <button class="btn btn-danger" onclick="filterResults('bassa')">🔴 Bassa</button>
                <button class="btn btn-primary" onclick="filterResults('all')">📋 Tutti</button>
            </div>
            <input type="text" class="search-box" id="searchBox" 
                   placeholder="🔍 Cerca per nome file..." onkeyup="searchTable()">
        </div>
        
        <div class="table-container">
            <table id="resultsTable">
                <thead>
                    <tr>
                        <th style="width: 50px;">#</th>
                        <th class="sortable" onclick="sortTable('file1', 'toggle')">File Directory 1</th>
                        <th class="sortable" onclick="sortTable('file2', 'toggle')">File Directory 2</th>
                        <th class="sortable" onclick="sortTable('compatibility', 'toggle')" style="width: 120px;">Compatibilità</th>
                        <th style="width: 100px;">Status</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        let currentSort = {{ column: '', direction: '' }};
        
        function sortTable(column, direction) {{
            const tbody = document.getElementById('tableBody');
            let rows = Array.from(tbody.querySelectorAll('.result-row'));
            
            if (direction === 'toggle') {{
                if (currentSort.column === column) {{
                    direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
                }} else {{
                    direction = 'desc';
                }}
            }}
            
            // Crea array di gruppi (riga dati + riga immagini + riga spaziatore)
            let groups = rows.map(row => {{
                return {{
                    dataRow: row,
                    imgRow: row.nextElementSibling,
                    spacerRow: row.nextElementSibling.nextElementSibling
                }};
            }});
            
            groups.sort((a, b) => {{
                let valA, valB;
                
                if (column === 'compatibility') {{
                    valA = parseFloat(a.dataRow.querySelector('.compatibility').dataset.comp);
                    valB = parseFloat(b.dataRow.querySelector('.compatibility').dataset.comp);
                }} else if (column === 'file1') {{
                    valA = a.dataRow.querySelector('[data-file1]').dataset.file1.toLowerCase();
                    valB = b.dataRow.querySelector('[data-file1]').dataset.file1.toLowerCase();
                }} else if (column === 'file2') {{
                    valA = a.dataRow.querySelector('[data-file2]').dataset.file2.toLowerCase();
                    valB = b.dataRow.querySelector('[data-file2]').dataset.file2.toLowerCase();
                }}
                
                return direction === 'asc' ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
            }});
            
            // Ricostruisci tabella
            tbody.innerHTML = '';
            groups.forEach((group, idx) => {{
                group.dataRow.querySelector('td:first-child').textContent = idx + 1;
                tbody.appendChild(group.dataRow);
                tbody.appendChild(group.imgRow);
                tbody.appendChild(group.spacerRow);
            }});
            
            currentSort = {{ column, direction }};
            updateSortIndicators();
        }}
        
        function updateSortIndicators() {{
            document.querySelectorAll('th.sortable').forEach(th => {{
                th.classList.remove('sort-asc', 'sort-desc');
            }});
            if (currentSort.column) {{
                const th = document.querySelector(`th.sortable[onclick*="${{currentSort.column}}"]`);
                if (th) th.classList.add(currentSort.direction === 'asc' ? 'sort-asc' : 'sort-desc');
            }}
        }}
        
        function filterResults(type) {{
            const tbody = document.getElementById('tableBody');
            const rows = tbody.querySelectorAll('.result-row');
            
            rows.forEach(row => {{
                const imgRow = row.nextElementSibling;
                const spacerRow = imgRow ? imgRow.nextElementSibling : null;
                
                if (type === 'all') {{
                    row.style.display = '';
                    if (imgRow) imgRow.style.display = '';
                    if (spacerRow) spacerRow.style.display = '';
                }} else {{
                    const comp = parseFloat(row.querySelector('.compatibility').dataset.comp);
                    let show = false;
                    if (type === 'alta' && comp >= 80) show = true;
                    if (type === 'media' && comp >= 60 && comp < 80) show = true;
                    if (type === 'bassa' && comp < 60) show = true;
                    
                    row.style.display = show ? '' : 'none';
                    if (imgRow) imgRow.style.display = show ? '' : 'none';
                    if (spacerRow) spacerRow.style.display = show ? '' : 'none';
                }}
            }});
            updateRowNumbers();
        }}
        
        function searchTable() {{
            const input = document.getElementById('searchBox').value.toLowerCase();
            const tbody = document.getElementById('tableBody');
            const rows = tbody.querySelectorAll('.result-row');
            
            rows.forEach(row => {{
                const imgRow = row.nextElementSibling;
                const spacerRow = imgRow ? imgRow.nextElementSibling : null;
                const file1 = row.querySelector('[data-file1]').dataset.file1.toLowerCase();
                const file2 = row.querySelector('[data-file2]').dataset.file2.toLowerCase();
                const match = file1.includes(input) || file2.includes(input);
                
                row.style.display = match ? '' : 'none';
                if (imgRow) imgRow.style.display = match ? '' : 'none';
                if (spacerRow) spacerRow.style.display = match ? '' : 'none';
            }});
            updateRowNumbers();
        }}
        
        function updateRowNumbers() {{
            const visibleRows = Array.from(document.querySelectorAll('.result-row'))
                .filter(row => row.style.display !== 'none');
            visibleRows.forEach((row, idx) => {{
                row.querySelector('td:first-child').textContent = idx + 1;
            }});
        }}
        
        window.onload = function() {{ sortTable('compatibility', 'desc'); }};
    </script>
</body>
</html>"""
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.report_html_path = html_path
            messagebox.showinfo("Report Generato", 
                               f"Report HTML unificato creato!\n{len(self.risultati)} comparazioni.\n\n"
                               f"Tutte le immagini sono visibili direttamente nel report!")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione HTML: {str(e)}")
    
    def aggiungi_risultato_tree(self, risultato):
        comp = risultato['compatibilita']
        if comp >= 80:
            status, tag = "ALTA", 'alta'
        elif comp >= 60:
            status, tag = "MEDIA", 'media'
        else:
            status, tag = "BASSA", 'bassa'
        
        # Inserisci nella tree e salva l'indice del risultato
        item = self.tree.insert('', 'end', 
                        values=(risultato['nome1'], risultato['nome2'],
                               f"{comp:.2f}%", status),
                        tags=(tag,))
        
        # Associa l'indice del risultato all'item della tree
        risultato['tree_item'] = item
    
    def aggiorna_progress(self, current, total):
        percentage = (current / total) * 100
        self.root.after(0, self.progress.config, {'value': percentage})
        self.root.after(0, self.label_progress.config, 
                       {'text': f'{current}/{total} ({percentage:.0f}%)'})
    
    def aggiorna_statistiche(self):
        totali = len(self.risultati)
        alta = sum(1 for r in self.risultati if r['compatibilita'] >= 80)
        media = sum(1 for r in self.risultati if 60 <= r['compatibilita'] < 80)
        bassa = sum(1 for r in self.risultati if r['compatibilita'] < 60)
        
        self.label_stats.config(text=f"Totali: {totali}\nAlta: {alta}\nMedia: {media}\nBassa: {bassa}")
    
    def apri_report_html(self):
        if hasattr(self, 'report_html_path') and os.path.exists(self.report_html_path):
            os.system(f'open "{self.report_html_path}"')
        else:
            messagebox.showwarning("Attenzione", "Report HTML non trovato")
    
    def esporta_csv(self):
        if not self.risultati:
            messagebox.showwarning("Attenzione", "Nessun risultato")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("File1,File2,Compatibilità%,Distanza,Status,Hash1,Hash2,Timestamp\n")
                    for r in self.risultati:
                        comp = r['compatibilita']
                        status = "ALTA" if comp >= 80 else "MEDIA" if comp >= 60 else "BASSA"
                        f.write(f"{r['nome1']},{r['nome2']},{comp:.2f},{r['distanza']:.6f},"
                               f"{status},{r['hash1']},{r['hash2']},{r['timestamp']}\n")
                messagebox.showinfo("Successo", f"CSV esportato:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

def main():
    root = tk.Tk()
    app = ComparatoreBatchAvanzatoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
