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
        
        # Container immagini
        images_container = tk.Frame(preview_frame, bg='#34495e')
        images_container.pack(pady=5)
        
        # Immagine Ricerca (target da identificare)
        frame_target = tk.Frame(images_container, bg='#2c3e50')
        frame_target.pack(side=tk.LEFT, padx=10)
        
        tk.Label(frame_target, text="TARGET (da identificare)", font=("Arial", 9, "bold"),
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.label_target = tk.Label(frame_target, bg='#2c3e50', width=300, height=300)
        self.label_target.pack()
        
        self.label_target_name = tk.Label(frame_target, text="---", font=("Arial", 8),
            bg='#2c3e50', fg='#ecf0f1')
        self.label_target_name.pack(pady=3)
        
        # Immagine Match (persona identificata con nome)
        frame_match = tk.Frame(images_container, bg='#2c3e50')
        frame_match.pack(side=tk.LEFT, padx=10)
        
        tk.Label(frame_match, text="MATCH IDENTIFICATO", font=("Arial", 9, "bold"),
                bg='#2c3e50', fg='#ecf0f1').pack()
        
        self.label_match = tk.Label(frame_match, bg='#2c3e50', width=300, height=300)
        self.label_match.pack()
        
        self.label_match_name = tk.Label(frame_match, text="---", font=("Arial", 10, "bold"),
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
                
                landmarks, img_land, error = self.elabora_immagine(filepath)
                
                if not error:
                    self.database_persone[nome_persona] = {
                        'file': filepath,
                        'landmarks': landmarks,
                        'img_landmarks': img_land
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
                landmarks_target, img_target_land, error_target = self.elabora_immagine(file_target)
                
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
                    
                    # Scrivi nome in alto
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    text = f"ID: {best_match}"
                    font_scale = 1.2
                    thickness = 3
                    
                    # Sfondo per il testo
                    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
                    cv2.rectangle(img_con_nome, (10, 10), (20 + text_w, 20 + text_h), (0, 0, 0), -1)
                    
                    # Testo
                    color = (0, 255, 0) if best_comp >= 80 else (0, 165, 255)
                    cv2.putText(img_con_nome, text, (15, 15 + text_h), font, font_scale, color, thickness)
                    
                    # Compatibilità
                    comp_text = f"{best_comp:.1f}%"
                    cv2.putText(img_con_nome, comp_text, (15, 60 + text_h), font, 0.8, color, 2)
                    
                    # Salva immagine
                    img_id = f"{timestamp}_{idx}"
                    target_save_path = os.path.join(results_dir, f'target_{img_id}.jpg')
                    cv2.imwrite(target_save_path, img_con_nome)
                    
                    match_save_path = os.path.join(results_dir, f'match_{img_id}.jpg')
                    cv2.imwrite(match_save_path, self.database_persone[best_match]['img_landmarks'])
                    
                    risultato = {
                        'target_file': file_target,
                        'target_nome': os.path.basename(file_target),
                        'persona_id': best_match,
                        'compatibilita': best_comp,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'target_img_path': target_save_path,
                        'match_img_path': match_save_path,
                        'target_img': img_con_nome,
                        'match_img': self.database_persone[best_match]['img_landmarks']
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
            max_size = 300
            
            def resize_img(img):
                h, w = img.shape[:2]
                scale = max_size / max(h, w)
                new_w, new_h = int(w * scale), int(h * scale)
                return cv2.resize(img, (new_w, new_h))
            
            # Target
            target_resized = resize_img(risultato['target_img'])
            target_rgb = cv2.cvtColor(target_resized, cv2.COLOR_BGR2RGB)
            target_pil = Image.fromarray(target_rgb)
            target_tk = ImageTk.PhotoImage(target_pil)
            self.label_target.config(image=target_tk)
            self.label_target.image = target_tk
            self.label_target_name.config(text=risultato['target_nome'])
            
            # Match
            match_resized = resize_img(risultato['match_img'])
            match_rgb = cv2.cvtColor(match_resized, cv2.COLOR_BGR2RGB)
            match_pil = Image.fromarray(match_rgb)
            match_tk = ImageTk.PhotoImage(match_pil)
            self.label_match.config(image=match_tk)
            self.label_match.image = match_tk
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
                    target_img = cv2.imread(risultato['target_img_path'])
                    match_img = cv2.imread(risultato['match_img_path'])
                    
                    risultato_temp = risultato.copy()
                    risultato_temp['target_img'] = target_img
                    risultato_temp['match_img'] = match_img
                    
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
        
        messagebox.showinfo("Report", "Funzione report HTML in sviluppo")

def main():
    root = tk.Tk()
    app = ComparatoreIdentificazioneGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
