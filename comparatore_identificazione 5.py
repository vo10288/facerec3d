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

class ComparatoreIdentificazioneGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparatore Identificazione Persone - Database")
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
        self.database_path = None
        self.ricerca_path = None
        self.database_persone = {}  # {nome_persona: {file, landmarks}}
        self.risultati = []
        self.stop_processing = False
        self.soglia_minima = tk.DoubleVar(value=60.0)  # Almeno Media
        
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
            text="Identificazione\nPersone", 
            font=("Arial", 16, "bold"),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title.pack(pady=10)
        
        # Database
        db_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        db_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(db_frame, text="DATABASE", font=("Arial", 10, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        tk.Label(db_frame, text="(Nome file = Nome persona)", font=("Arial", 7, "italic"),
                bg='#34495e', fg='#bdc3c7').pack()
        
        self.btn_database = tk.Button(db_frame, text="📁 Seleziona Database", 
            command=self.seleziona_database,
            font=("Arial", 9, "bold"), bg='#3498db', fg='white', padx=10, pady=5)
        self.btn_database.pack(pady=3)
        
        self.label_database = tk.Label(db_frame, text="---", font=("Arial", 8),
            bg='#34495e', fg='#ecf0f1', wraplength=200)
        self.label_database.pack(pady=3)
        
        self.btn_indicizza = tk.Button(db_frame, text="🔍 Indicizza Database", 
            command=self.indicizza_database,
            font=("Arial", 9, "bold"), bg='#27ae60', fg='white', padx=10, pady=5, state=tk.DISABLED)
        self.btn_indicizza.pack(pady=3)
        
        self.label_db_status = tk.Label(db_frame, text="Non indicizzato", font=("Arial", 8),
            bg='#34495e', fg='#e74c3c')
        self.label_db_status.pack(pady=3)
        
        # Ricerca
        search_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        search_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(search_frame, text="RICERCA", font=("Arial", 10, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        tk.Label(search_frame, text="(Volti da identificare)", font=("Arial", 7, "italic"),
                bg='#34495e', fg='#bdc3c7').pack()
        
        self.btn_ricerca = tk.Button(search_frame, text="📁 Directory Ricerca", 
            command=self.seleziona_ricerca,
            font=("Arial", 9, "bold"), bg='#3498db', fg='white', padx=10, pady=5)
        self.btn_ricerca.pack(pady=3)
        
        self.label_ricerca = tk.Label(search_frame, text="---", font=("Arial", 8),
            bg='#34495e', fg='#ecf0f1', wraplength=200)
        self.label_ricerca.pack(pady=3)
        
        # Opzioni
        opt_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        opt_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(opt_frame, text="OPZIONI", font=("Arial", 10, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        soglia_frame = tk.Frame(opt_frame, bg='#34495e')
        soglia_frame.pack(pady=3)
        
        tk.Label(soglia_frame, text="Soglia %:", font=("Arial", 8),
                bg='#34495e', fg='#ecf0f1').pack(side=tk.LEFT, padx=3)
        
        self.spin_soglia = tk.Spinbox(soglia_frame, from_=0, to=100,
            textvariable=self.soglia_minima, width=6, font=("Arial", 8))
        self.spin_soglia.pack(side=tk.LEFT)
        
        tk.Label(opt_frame, text="(≥60% consigliato)", font=("Arial", 7, "italic"),
                bg='#34495e', fg='#bdc3c7').pack()
        
        # Controlli
        ctrl_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        ctrl_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(ctrl_frame, text="AZIONI", font=("Arial", 10, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.btn_identifica = tk.Button(ctrl_frame, text="🔍 IDENTIFICA", 
            command=self.avvia_identificazione,
            font=("Arial", 10, "bold"), bg='#27ae60', fg='white', padx=15, pady=8, state=tk.DISABLED)
        self.btn_identifica.pack(pady=3)
        
        self.btn_stop = tk.Button(ctrl_frame, text="⏹ STOP", command=self.stop_identificazione,
            font=("Arial", 10, "bold"), bg='#e74c3c', fg='white', padx=15, pady=8, state=tk.DISABLED)
        self.btn_stop.pack(pady=3)
        
        self.btn_export = tk.Button(ctrl_frame, text="📊 CSV", command=self.esporta_csv,
            font=("Arial", 9), bg='#9b59b6', fg='white', padx=15, pady=6, state=tk.DISABLED)
        self.btn_export.pack(pady=2)
        
        self.btn_report = tk.Button(ctrl_frame, text="📄 Report", command=self.genera_report,
            font=("Arial", 9), bg='#16a085', fg='white', padx=15, pady=6, state=tk.DISABLED)
        self.btn_report.pack(pady=2)
        
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
        
        self.label_stats = tk.Label(stats_frame, text="Database: 0\nIdentificati: 0\nAlta: 0\nMedia: 0",
            font=("Arial", 8), bg='#34495e', fg='#ecf0f1', justify=tk.LEFT)
        self.label_stats.pack(pady=5)
        
        # === COLONNA DESTRA ===
        right_column = tk.Frame(main_container, bg='#2c3e50')
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Preview identificazione corrente
        preview_frame = tk.Frame(right_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        preview_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(preview_frame, text="IDENTIFICAZIONE CORRENTE", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        # Container immagini - Layout 2x2
        images_container = tk.Frame(preview_frame, bg='#34495e')
        images_container.pack(pady=5)
        
        # Riga superiore - ORIGINALI
        row_originali = tk.Frame(images_container, bg='#34495e')
        row_originali.pack()
        
        # Target Originale
        frame_target_orig = tk.Frame(row_originali, bg='#2c3e50')
        frame_target_orig.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_target_orig, text="TARGET - Originale", font=("Arial", 8, "bold"),
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.label_target_orig = tk.Label(frame_target_orig, bg='#2c3e50')
        self.label_target_orig.pack()
        
        # Match Originale
        frame_match_orig = tk.Frame(row_originali, bg='#2c3e50')
        frame_match_orig.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_match_orig, text="MATCH - Originale", font=("Arial", 8, "bold"),
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.label_match_orig = tk.Label(frame_match_orig, bg='#2c3e50')
        self.label_match_orig.pack()
        
        # Riga inferiore - LANDMARKS
        row_landmarks = tk.Frame(images_container, bg='#34495e')
        row_landmarks.pack(pady=5)
        
        # Target con Landmarks + Nome
        frame_target_land = tk.Frame(row_landmarks, bg='#2c3e50')
        frame_target_land.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_target_land, text="TARGET - Con ID", font=("Arial", 8, "bold"),
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.label_target = tk.Label(frame_target_land, bg='#2c3e50')
        self.label_target.pack()
        
        self.label_target_name = tk.Label(frame_target_land, text="---", font=("Arial", 8),
            bg='#2c3e50', fg='#ecf0f1')
        self.label_target_name.pack(pady=3)
        
        # Match con Landmarks
        frame_match_land = tk.Frame(row_landmarks, bg='#2c3e50')
        frame_match_land.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_match_land, text="MATCH - Landmarks", font=("Arial", 8, "bold"),
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.label_match = tk.Label(frame_match_land, bg='#2c3e50')
        self.label_match.pack()
        
        self.label_match_name = tk.Label(frame_match_land, text="---", font=("Arial", 10, "bold"),
            bg='#2c3e50', fg='#27ae60')
        self.label_match_name.pack(pady=3)
        
        # Risultato
        self.label_result = tk.Label(preview_frame, text="---", font=("Arial", 12, "bold"),
            bg='#34495e', fg='#ecf0f1')
        self.label_result.pack(pady=5)
        
        # Tabella risultati
        result_frame = tk.Frame(right_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        result_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        tk.Label(result_frame, text="RISULTATI IDENTIFICAZIONE", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        scroll_frame = tk.Frame(result_frame, bg='#34495e')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(scroll_frame, 
            columns=('Target', 'PersonaID', 'Comp', 'Status'),
            show='headings', yscrollcommand=scrollbar.set, height=15)
        
        self.tree.heading('Target', text='File Target')
        self.tree.heading('PersonaID', text='Persona Identificata')
        self.tree.heading('Comp', text='Comp %')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('Target', width=250)
        self.tree.column('PersonaID', width=250)
        self.tree.column('Comp', width=100, anchor='center')
        self.tree.column('Status', width=100, anchor='center')
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        self.tree.tag_configure('alta', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('media', background='#fff3cd', foreground='#856404')
    
    def seleziona_database(self):
        directory = filedialog.askdirectory(title="Seleziona Directory Database Persone")
        if directory:
            self.database_path = directory
            num = len(self.get_image_files(directory))
            self.label_database.config(text=f"{num} immagini")
            self.btn_indicizza.config(state=tk.NORMAL)
            self.label_db_status.config(text="Da indicizzare", fg='#e67e22')
    
    def seleziona_ricerca(self):
        directory = filedialog.askdirectory(title="Seleziona Directory Ricerca")
        if directory:
            self.ricerca_path = directory
            num = len(self.get_image_files(directory))
            self.label_ricerca.config(text=f"{num} immagini")
            self.verifica_stato_identifica()
    
    def verifica_stato_identifica(self):
        if self.database_persone and self.ricerca_path:
            self.btn_identifica.config(state=tk.NORMAL)
    
    def get_image_files(self, directory):
        extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP')
        return sorted([os.path.join(directory, f) for f in os.listdir(directory) 
                      if f.endswith(extensions)])
    
    def elabora_immagine(self, filepath):
        try:
            img = cv2.imread(filepath)
            if img is None:
                return None, None, None, "Load error"
            
            img_orig = img.copy()  # Salva originale
            
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = self.face_mesh.process(rgb)
            
            if not result.multi_face_landmarks:
                return None, None, None, "No face"
            
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
            
            return landmarks_array, img_landmarks, img_orig, None
        except Exception as e:
            return None, None, None, str(e)[:15]
    
    def calcola_compatibilita(self, pts1, pts2):
        min_len = min(len(pts1), len(pts2))
        distanze = np.linalg.norm(pts1[:min_len] - pts2[:min_len], axis=1)
        distanza_media = np.mean(distanze)
        compatibilita = max(0, min(100, (1 - distanza_media / 0.2) * 100))
        return compatibilita, distanza_media
    
    def indicizza_database(self):
        self.btn_indicizza.config(state=tk.DISABLED)
        self.label_db_status.config(text="Indicizzazione...", fg='#f39c12')
        
        thread = threading.Thread(target=self.esegui_indicizzazione)
        thread.daemon = True
        thread.start()
    
    def esegui_indicizzazione(self):
        try:
            files = self.get_image_files(self.database_path)
            self.database_persone = {}
            
            total = len(files)
            for idx, filepath in enumerate(files):
                # Nome persona = nome file senza estensione
                nome_persona = os.path.splitext(os.path.basename(filepath))[0]
                
                landmarks, img_land, img_orig, error = self.elabora_immagine(filepath)
                
                if not error:
                    self.database_persone[nome_persona] = {
                        'file': filepath,
                        'landmarks': landmarks,
                        'img_landmarks': img_land,
                        'img_original': img_orig
                    }
                
                # Aggiorna progress
                perc = ((idx + 1) / total) * 100
                self.root.after(0, self.progress.config, {'value': perc})
                self.root.after(0, self.label_progress.config, 
                               {'text': f'Indicizzazione: {idx+1}/{total}'})
            
            self.root.after(0, self.label_db_status.config, 
                           {'text': f'✓ {len(self.database_persone)} persone', 'fg': '#27ae60'})
            self.root.after(0, self.label_progress.config, {'text': 'Pronto'})
            self.root.after(0, self.progress.config, {'value': 0})
            self.root.after(0, self.btn_indicizza.config, {'state': tk.NORMAL})
            self.root.after(0, messagebox.showinfo, "Completato", 
                           f"Database indicizzato!\n{len(self.database_persone)} persone caricate.")
            
            self.root.after(0, self.verifica_stato_identifica)
            self.root.after(0, self.aggiorna_statistiche)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Errore", str(e))
            self.root.after(0, self.btn_indicizza.config, {'state': tk.NORMAL})
    
    def stop_identificazione(self):
        self.stop_processing = True
    
    def avvia_identificazione(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.risultati = []
        self.stop_processing = False
        
        self.btn_identifica.config(state=tk.DISABLED)
        self.btn_database.config(state=tk.DISABLED)
        self.btn_ricerca.config(state=tk.DISABLED)
        self.btn_indicizza.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_export.config(state=tk.DISABLED)
        self.btn_report.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.esegui_identificazione)
        thread.daemon = True
        thread.start()
    
    def esegui_identificazione(self):
        try:
            files_ricerca = self.get_image_files(self.ricerca_path)
            
            # Directory per salvare risultati
            results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'identificazioni')
            os.makedirs(results_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            total = len(files_ricerca)
            soglia = self.soglia_minima.get()
            
            for idx, file_target in enumerate(files_ricerca):
                if self.stop_processing:
                    break
                
                # Elabora target
                landmarks_target, img_target_land, img_target_orig, error_target = self.elabora_immagine(file_target)
                
                if error_target:
                    self.aggiorna_progress(idx + 1, total)
                    continue
                
                # Cerca nel database
                best_match = None
                best_comp = 0
                
                for nome_persona, dati in self.database_persone.items():
                    comp, dist = self.calcola_compatibilita(landmarks_target, dati['landmarks'])
                    
                    if comp > best_comp:
                        best_comp = comp
                        best_match = nome_persona
                
                # Salva solo se supera soglia
                if best_match and best_comp >= soglia:
                    # Aggiungi nome sulla immagine con landmarks
                    img_con_nome = img_target_land.copy()
                    img_height, img_width = img_con_nome.shape[:2]
                    
                    # Calcola dimensione font adattiva (proporzionale alla larghezza)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    text = f"ID: {best_match}"
                    
                    # Font scale basato sulla larghezza (tra 0.4 e 2.0)
                    base_font_scale = img_width / 400.0
                    font_scale = max(0.4, min(2.0, base_font_scale))
                    thickness = max(1, int(font_scale * 2))
                    
                    # Calcola dimensioni testo
                    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
                    
                    # Se il testo è troppo largo, riduci font
                    max_text_width = img_width - 30
                    if text_w > max_text_width:
                        font_scale = font_scale * (max_text_width / text_w)
                        thickness = max(1, int(font_scale * 2))
                        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
                    
                    # Posizione e sfondo
                    padding = 5
                    bg_x1 = 10
                    bg_y1 = 10
                    bg_x2 = bg_x1 + text_w + (padding * 2)
                    bg_y2 = bg_y1 + text_h + (padding * 2)
                    
                    # Sfondo nero per il testo
                    cv2.rectangle(img_con_nome, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
                    
                    # Testo
                    color = (0, 255, 0) if best_comp >= 80 else (0, 165, 255)
                    text_x = bg_x1 + padding
                    text_y = bg_y1 + text_h + padding
                    cv2.putText(img_con_nome, text, (text_x, text_y), font, font_scale, color, thickness)
                    
                    # Compatibilità (leggermente più piccola)
                    comp_text = f"{best_comp:.1f}%"
                    comp_font_scale = font_scale * 0.7
                    comp_thickness = max(1, int(comp_font_scale * 2))
                    (comp_w, comp_h), _ = cv2.getTextSize(comp_text, font, comp_font_scale, comp_thickness)
                    
                    comp_bg_y1 = bg_y2 + 5
                    comp_bg_y2 = comp_bg_y1 + comp_h + (padding * 2)
                    comp_bg_x2 = bg_x1 + comp_w + (padding * 2)
                    
                    cv2.rectangle(img_con_nome, (bg_x1, comp_bg_y1), (comp_bg_x2, comp_bg_y2), (0, 0, 0), -1)
                    cv2.putText(img_con_nome, comp_text, (text_x, comp_bg_y1 + comp_h + padding), 
                               font, comp_font_scale, color, comp_thickness)
                    
                    # Salva immagini
                    img_id = f"{timestamp}_{idx}"
                    
                    target_orig_path = os.path.join(results_dir, f'target_orig_{img_id}.jpg')
                    target_land_path = os.path.join(results_dir, f'target_land_{img_id}.jpg')
                    match_orig_path = os.path.join(results_dir, f'match_orig_{img_id}.jpg')
                    match_land_path = os.path.join(results_dir, f'match_land_{img_id}.jpg')
                    
                    cv2.imwrite(target_orig_path, img_target_orig)
                    cv2.imwrite(target_land_path, img_con_nome)
                    cv2.imwrite(match_orig_path, self.database_persone[best_match]['img_original'])
                    cv2.imwrite(match_land_path, self.database_persone[best_match]['img_landmarks'])
                    
                    risultato = {
                        'target_file': file_target,
                        'target_nome': os.path.basename(file_target),
                        'persona_id': best_match,
                        'compatibilita': best_comp,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'target_orig_path': target_orig_path,
                        'target_land_path': target_land_path,
                        'match_orig_path': match_orig_path,
                        'match_land_path': match_land_path,
                        'target_orig_img': img_target_orig,
                        'target_land_img': img_con_nome,
                        'match_orig_img': self.database_persone[best_match]['img_original'],
                        'match_land_img': self.database_persone[best_match]['img_landmarks']
                    }
                    
                    self.risultati.append(risultato)
                    self.root.after(0, self.aggiungi_risultato_tree, risultato)
                    
                    # Mostra preview
                    self.root.after(0, self.mostra_preview, risultato)
                
                self.aggiorna_progress(idx + 1, total)
            
            # Completato
            if self.stop_processing:
                self.root.after(0, self.label_progress.config, {'text': 'Interrotto'})
            else:
                self.root.after(0, self.label_progress.config, 
                               {'text': f'Completato! {len(self.risultati)} identificati'})
                self.root.after(0, messagebox.showinfo, "Completato", 
                               f"{len(self.risultati)} persone identificate\n(soglia ≥{soglia}%)")
            
            self.root.after(0, self.btn_identifica.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_database.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_ricerca.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_indicizza.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_stop.config, {'state': tk.DISABLED})
            if self.risultati:
                self.root.after(0, self.btn_export.config, {'state': tk.NORMAL})
                self.root.after(0, self.btn_report.config, {'state': tk.NORMAL})
            
            self.root.after(0, self.aggiorna_statistiche)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Errore", str(e))
    
    def mostra_preview(self, risultato):
        try:
            max_size = 250
            
            def resize_img(img):
                h, w = img.shape[:2]
                scale = max_size / max(h, w)
                new_w, new_h = int(w * scale), int(h * scale)
                return cv2.resize(img, (new_w, new_h))
            
            # Target Originale
            target_orig_resized = resize_img(risultato['target_orig_img'])
            target_orig_rgb = cv2.cvtColor(target_orig_resized, cv2.COLOR_BGR2RGB)
            target_orig_pil = Image.fromarray(target_orig_rgb)
            target_orig_tk = ImageTk.PhotoImage(target_orig_pil)
            self.label_target_orig.config(image=target_orig_tk)
            self.label_target_orig.image = target_orig_tk
            
            # Match Originale
            match_orig_resized = resize_img(risultato['match_orig_img'])
            match_orig_rgb = cv2.cvtColor(match_orig_resized, cv2.COLOR_BGR2RGB)
            match_orig_pil = Image.fromarray(match_orig_rgb)
            match_orig_tk = ImageTk.PhotoImage(match_orig_pil)
            self.label_match_orig.config(image=match_orig_tk)
            self.label_match_orig.image = match_orig_tk
            
            # Target Landmarks (con nome)
            target_land_resized = resize_img(risultato['target_land_img'])
            target_land_rgb = cv2.cvtColor(target_land_resized, cv2.COLOR_BGR2RGB)
            target_land_pil = Image.fromarray(target_land_rgb)
            target_land_tk = ImageTk.PhotoImage(target_land_pil)
            self.label_target.config(image=target_land_tk)
            self.label_target.image = target_land_tk
            self.label_target_name.config(text=risultato['target_nome'])
            
            # Match Landmarks
            match_land_resized = resize_img(risultato['match_land_img'])
            match_land_rgb = cv2.cvtColor(match_land_resized, cv2.COLOR_BGR2RGB)
            match_land_pil = Image.fromarray(match_land_rgb)
            match_land_tk = ImageTk.PhotoImage(match_land_pil)
            self.label_match.config(image=match_land_tk)
            self.label_match.image = match_land_tk
            self.label_match_name.config(text=risultato['persona_id'])
            
            # Risultato
            comp = risultato['compatibilita']
            if comp >= 80:
                color = '#27ae60'
                status = 'ALTA CONFIDENZA'
            else:
                color = '#f39c12'
                status = 'MEDIA CONFIDENZA'
            
            self.label_result.config(text=f"{comp:.2f}% - {status}", fg=color)
            self.root.update()
            
        except Exception as e:
            print(f"Errore preview: {e}")
    
    def aggiungi_risultato_tree(self, risultato):
        comp = risultato['compatibilita']
        if comp >= 80:
            status, tag = "ALTA", 'alta'
        else:
            status, tag = "MEDIA", 'media'
        
        item = self.tree.insert('', 'end', 
                        values=(risultato['target_nome'], risultato['persona_id'],
                               f"{comp:.2f}%", status),
                        tags=(tag,))
        risultato['tree_item'] = item
    
    def on_tree_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        
        for risultato in self.risultati:
            if risultato.get('tree_item') == item:
                try:
                    target_orig_img = cv2.imread(risultato['target_orig_path'])
                    target_land_img = cv2.imread(risultato['target_land_path'])
                    match_orig_img = cv2.imread(risultato['match_orig_path'])
                    match_land_img = cv2.imread(risultato['match_land_path'])
                    
                    risultato_temp = risultato.copy()
                    risultato_temp['target_orig_img'] = target_orig_img
                    risultato_temp['target_land_img'] = target_land_img
                    risultato_temp['match_orig_img'] = match_orig_img
                    risultato_temp['match_land_img'] = match_land_img
                    
                    self.mostra_preview(risultato_temp)
                except Exception as e:
                    print(f"Errore: {e}")
                break
    
    def aggiorna_progress(self, current, total):
        percentage = (current / total) * 100
        self.root.after(0, self.progress.config, {'value': percentage})
        self.root.after(0, self.label_progress.config, 
                       {'text': f'{current}/{total} ({percentage:.0f}%)'})
    
    def aggiorna_statistiche(self):
        db_count = len(self.database_persone)
        total = len(self.risultati)
        alta = sum(1 for r in self.risultati if r['compatibilita'] >= 80)
        media = sum(1 for r in self.risultati if 60 <= r['compatibilita'] < 80)
        
        self.label_stats.config(
            text=f"Database: {db_count}\nIdentificati: {total}\nAlta: {alta}\nMedia: {media}"
        )
    
    def esporta_csv(self):
        if not self.risultati:
            messagebox.showwarning("Attenzione", "Nessun risultato")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"identificazioni_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("FileTarget,PersonaIdentificata,Compatibilità%,Status,Timestamp\n")
                    for r in self.risultati:
                        comp = r['compatibilita']
                        status = "ALTA" if comp >= 80 else "MEDIA"
                        f.write(f"{r['target_nome']},{r['persona_id']},{comp:.2f},"
                               f"{status},{r['timestamp']}\n")
                messagebox.showinfo("Successo", f"CSV esportato:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Errore", str(e))
    
    def genera_report(self):
        if not self.risultati:
            messagebox.showwarning("Attenzione", "Nessun risultato")
            return
        
        try:
            results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'identificazioni')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_path = os.path.join(results_dir, f'report_identificazioni_{timestamp}.html')
            
            totali = len(self.risultati)
            alta = sum(1 for r in self.risultati if r['compatibilita'] >= 80)
            media = sum(1 for r in self.risultati if 60 <= r['compatibilita'] < 80)
            db_persone = len(self.database_persone)
            
            # Genera righe HTML con tutte le 4 immagini visibili
            rows_html = ""
            for idx, r in enumerate(self.risultati, 1):
                comp = r['compatibilita']
                if comp >= 80:
                    bg_color, status = '#d4edda', 'ALTA'
                elif comp >= 60:
                    bg_color, status = '#fff3cd', 'MEDIA'
                else:
                    bg_color, status = '#f8d7da', 'BASSA'
                
                # Percorsi relativi
                target_orig_rel = os.path.basename(r['target_orig_path'])
                target_land_rel = os.path.basename(r['target_land_path'])
                match_orig_rel = os.path.basename(r['match_orig_path'])
                match_land_rel = os.path.basename(r['match_land_path'])
                
                rows_html += f"""
                <tr style="background-color: {bg_color};" class="result-row">
                    <td style="text-align: center; font-weight: bold;">{idx}</td>
                    <td class="file-name" data-target="{r['target_nome']}">{r['target_nome']}</td>
                    <td class="persona-id" data-persona="{r['persona_id']}">{r['persona_id']}</td>
                    <td style="text-align: center; font-weight: bold;" class="compatibility" data-comp="{comp:.2f}">{comp:.2f}%</td>
                    <td style="text-align: center;"><b>{status}</b></td>
                    <td style="text-align: center; font-size: 11px;">{r['timestamp']}</td>
                </tr>
                <tr style="background-color: {bg_color};">
                    <td colspan="6" style="padding: 15px;">
                        <div style="text-align: center; margin-bottom: 10px; font-size: 13px; font-weight: bold; color: #555;">
                            ORIGINALI
                        </div>
                        <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
                            <div style="text-align: center; flex: 1; margin: 0 5px;">
                                <div style="font-weight: bold; margin-bottom: 5px; color: #555;">Target Originale</div>
                                <img src="{target_orig_rel}" style="max-width: 300px; max-height: 300px; border: 2px solid #aaa; border-radius: 5px;">
                            </div>
                            <div style="text-align: center; flex: 1; margin: 0 5px;">
                                <div style="font-weight: bold; margin-bottom: 5px; color: #555;">Match Originale</div>
                                <img src="{match_orig_rel}" style="max-width: 300px; max-height: 300px; border: 2px solid #aaa; border-radius: 5px;">
                            </div>
                        </div>
                        <div style="text-align: center; margin-bottom: 10px; font-size: 13px; font-weight: bold; color: #555;">
                            LANDMARKS
                        </div>
                        <div style="display: flex; justify-content: space-around;">
                            <div style="text-align: center; flex: 1; margin: 0 5px;">
                                <div style="font-weight: bold; margin-bottom: 5px; color: #555;">Target con ID</div>
                                <img src="{target_land_rel}" style="max-width: 300px; max-height: 300px; border: 2px solid #28a745; border-radius: 5px;">
                            </div>
                            <div style="text-align: center; flex: 1; margin: 0 5px;">
                                <div style="font-weight: bold; margin-bottom: 5px; color: #555;">Match Landmarks</div>
                                <img src="{match_land_rel}" style="max-width: 300px; max-height: 300px; border: 2px solid #28a745; border-radius: 5px;">
                            </div>
                        </div>
                    </td>
                </tr>
                <tr><td colspan="6" style="height: 20px; background: #f8f9fa;"></td></tr>
                """
            
            html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report Identificazioni - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1600px;
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
        .stat-box.database {{ background: #e3f2fd; border: 2px solid #2196f3; }}
        .stat-box.total {{ background: #e7f3ff; border: 2px solid #0077cc; }}
        .stat-box.alta {{ background: #d4edda; border: 2px solid #28a745; }}
        .stat-box.media {{ background: #fff3cd; border: 2px solid #ffc107; }}
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
            <h1>📊 Report Identificazioni Persone</h1>
            <p>Generato il: {datetime.now().strftime('%d/%m/%Y alle %H:%M:%S')}</p>
            <p style="font-size: 12px; margin-top: 5px;">Sistema di identificazione biometrica con database</p>
        </div>
        
        <div class="stats-bar">
            <div class="stat-box database">
                <div class="stat-number">{db_persone}</div>
                <div class="stat-label">Database</div>
            </div>
            <div class="stat-box total">
                <div class="stat-number">{totali}</div>
                <div class="stat-label">Identificati</div>
            </div>
            <div class="stat-box alta">
                <div class="stat-number">{alta}</div>
                <div class="stat-label">Alta (≥80%)</div>
            </div>
            <div class="stat-box media">
                <div class="stat-number">{media}</div>
                <div class="stat-label">Media (60-79%)</div>
            </div>
        </div>
        
        <div class="controls">
            <div class="btn-group">
                <button class="btn btn-primary" onclick="sortTable('compatibility', 'desc')">
                    📊 Ordina per Compatibilità ↓
                </button>
                <button class="btn btn-info" onclick="sortTable('target', 'asc')">
                    📁 Ordina per Target (A-Z)
                </button>
                <button class="btn btn-info" onclick="sortTable('persona', 'asc')">
                    👤 Ordina per Persona (A-Z)
                </button>
            </div>
            <div class="btn-group">
                <button class="btn btn-success" onclick="filterResults('alta')">🟢 Alta</button>
                <button class="btn btn-warning" onclick="filterResults('media')">🟡 Media</button>
                <button class="btn btn-primary" onclick="filterResults('all')">📋 Tutti</button>
            </div>
            <input type="text" class="search-box" id="searchBox" 
                   placeholder="🔍 Cerca per nome file o persona..." onkeyup="searchTable()">
        </div>
        
        <div class="table-container">
            <table id="resultsTable">
                <thead>
                    <tr>
                        <th style="width: 50px;">#</th>
                        <th class="sortable" onclick="sortTable('target', 'toggle')">File Target</th>
                        <th class="sortable" onclick="sortTable('persona', 'toggle')">Persona Identificata</th>
                        <th class="sortable" onclick="sortTable('compatibility', 'toggle')" style="width: 120px;">Compatibilità</th>
                        <th style="width: 100px;">Status</th>
                        <th style="width: 150px;">Timestamp</th>
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
                }} else if (column === 'target') {{
                    valA = a.dataRow.querySelector('[data-target]').dataset.target.toLowerCase();
                    valB = b.dataRow.querySelector('[data-target]').dataset.target.toLowerCase();
                }} else if (column === 'persona') {{
                    valA = a.dataRow.querySelector('[data-persona]').dataset.persona.toLowerCase();
                    valB = b.dataRow.querySelector('[data-persona]').dataset.persona.toLowerCase();
                }}
                
                return direction === 'asc' ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
            }});
            
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
                const target = row.querySelector('[data-target]').dataset.target.toLowerCase();
                const persona = row.querySelector('[data-persona]').dataset.persona.toLowerCase();
                const match = target.includes(input) || persona.includes(input);
                
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
                               f"Report HTML creato con {len(self.risultati)} identificazioni!\n\n"
                               f"Tutte le 4 immagini sono visibili direttamente nel report.\n\n"
                               f"File: {os.path.basename(html_path)}")
            
            # Apri automaticamente il report
            import webbrowser
            webbrowser.open('file://' + html_path)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione report: {str(e)}")

def main():
    root = tk.Tk()
    app = ComparatoreIdentificazioneGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
