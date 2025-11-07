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
        self.root.title("Comparatore Biometrico Batch Avanzato - Con Report HTML")
        self.root.geometry("1400x950")
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
        self.genera_html = tk.BooleanVar(value=False)
        self.soglia_compatibilita = tk.DoubleVar(value=0.0)  # Soglia minima per salvare
        
        self.setup_ui()
    
    def setup_ui(self):
        # Titolo
        title = tk.Label(
            self.root, 
            text="Comparatore Biometrico Batch Avanzato", 
            font=("Arial", 20, "bold"),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title.pack(pady=15)
        
        # Frame directory
        dir_container = tk.Frame(self.root, bg='#2c3e50')
        dir_container.pack(pady=5)
        
        # Directory 1
        dir_frame1 = tk.Frame(dir_container, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        dir_frame1.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(dir_frame1, text="DIRECTORY 1", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.btn_dir1 = tk.Button(
            dir_frame1,
            text="📁 Seleziona",
            command=self.seleziona_dir1,
            font=("Arial", 11, "bold"),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=8
        )
        self.btn_dir1.pack(pady=5)
        
        self.label_dir1 = tk.Label(
            dir_frame1,
            text="Nessuna directory",
            font=("Arial", 9),
            bg='#34495e',
            fg='#ecf0f1',
            wraplength=250
        )
        self.label_dir1.pack(pady=5, padx=10)
        
        # Directory 2
        dir_frame2 = tk.Frame(dir_container, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        dir_frame2.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(dir_frame2, text="DIRECTORY 2", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.btn_dir2 = tk.Button(
            dir_frame2,
            text="📁 Seleziona",
            command=self.seleziona_dir2,
            font=("Arial", 11, "bold"),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=8
        )
        self.btn_dir2.pack(pady=5)
        
        self.label_dir2 = tk.Label(
            dir_frame2,
            text="Nessuna directory",
            font=("Arial", 9),
            bg='#34495e',
            fg='#ecf0f1',
            wraplength=250
        )
        self.label_dir2.pack(pady=5, padx=10)
        
        # Opzioni
        options_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        options_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(options_frame, text="OPZIONI", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        opt_inner = tk.Frame(options_frame, bg='#34495e')
        opt_inner.pack(pady=5)
        
        # Checkbox HTML
        self.check_html = tk.Checkbutton(
            opt_inner,
            text="Genera Report HTML per ogni comparazione",
            variable=self.genera_html,
            font=("Arial", 10),
            bg='#34495e',
            fg='#ecf0f1',
            selectcolor='#2c3e50',
            activebackground='#34495e'
        )
        self.check_html.pack(side=tk.LEFT, padx=20)
        
        # Soglia minima
        tk.Label(opt_inner, text="Soglia minima compatibilità per salvare:",
                font=("Arial", 10), bg='#34495e', fg='#ecf0f1').pack(side=tk.LEFT, padx=10)
        
        self.spin_soglia = tk.Spinbox(
            opt_inner,
            from_=0,
            to=100,
            textvariable=self.soglia_compatibilita,
            width=10,
            font=("Arial", 10)
        )
        self.spin_soglia.pack(side=tk.LEFT, padx=5)
        
        tk.Label(opt_inner, text="%", font=("Arial", 10),
                bg='#34495e', fg='#ecf0f1').pack(side=tk.LEFT)
        
        # Frame controlli
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(pady=15)
        
        self.btn_compara = tk.Button(
            control_frame,
            text="🔍 Avvia Comparazione Batch",
            command=self.avvia_comparazione,
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            padx=25,
            pady=12,
            state=tk.DISABLED
        )
        self.btn_compara.pack(side=tk.LEFT, padx=8)
        
        self.btn_stop = tk.Button(
            control_frame,
            text="⏹ Stop",
            command=self.stop_comparazione,
            font=("Arial", 12, "bold"),
            bg='#e74c3c',
            fg='white',
            padx=25,
            pady=12,
            state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=8)
        
        self.btn_export_csv = tk.Button(
            control_frame,
            text="📊 Esporta CSV",
            command=self.esporta_csv,
            font=("Arial", 11, "bold"),
            bg='#9b59b6',
            fg='white',
            padx=20,
            pady=12,
            state=tk.DISABLED
        )
        self.btn_export_csv.pack(side=tk.LEFT, padx=8)
        
        self.btn_apri_reports = tk.Button(
            control_frame,
            text="📁 Apri Cartella Reports",
            command=self.apri_cartella_reports,
            font=("Arial", 11, "bold"),
            bg='#16a085',
            fg='white',
            padx=20,
            pady=12,
            state=tk.DISABLED
        )
        self.btn_apri_reports.pack(side=tk.LEFT, padx=8)
        
        # Progress bar
        progress_frame = tk.Frame(self.root, bg='#2c3e50')
        progress_frame.pack(pady=5, fill=tk.X, padx=40)
        
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
        self.label_progress.pack(pady=2)
        
        # Frame risultati
        result_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        result_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(
            result_frame,
            text="RISULTATI COMPARAZIONI",
            font=("Arial", 12, "bold"),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=8)
        
        # Scrollbar
        scroll_frame = tk.Frame(result_frame, bg='#34495e')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            scroll_frame,
            columns=('File1', 'File2', 'Comp', 'Dist', 'Status', 'Report'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=12
        )
        
        self.tree.heading('File1', text='File Directory 1')
        self.tree.heading('File2', text='File Directory 2')
        self.tree.heading('Comp', text='Comp. %')
        self.tree.heading('Dist', text='Distanza')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Report', text='Report HTML')
        
        self.tree.column('File1', width=230)
        self.tree.column('File2', width=230)
        self.tree.column('Comp', width=90, anchor='center')
        self.tree.column('Dist', width=100, anchor='center')
        self.tree.column('Status', width=120, anchor='center')
        self.tree.column('Report', width=100, anchor='center')
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Tag colors
        self.tree.tag_configure('alta', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('media', background='#fff3cd', foreground='#856404')
        self.tree.tag_configure('bassa', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('errore', background='#f5c6cb', foreground='#721c24')
        
        # Double click per aprire report
        self.tree.bind('<Double-1>', self.apri_report_selezionato)
        
        # Statistiche
        stats_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        stats_frame.pack(pady=5, padx=20, fill=tk.X)
        
        self.label_stats = tk.Label(
            stats_frame,
            text="Statistiche: Totali: 0 | Alta: 0 | Media: 0 | Bassa: 0 | Errori: 0",
            font=("Arial", 10, "bold"),
            bg='#34495e',
            fg='#ecf0f1',
            pady=8
        )
        self.label_stats.pack()
    
    def seleziona_dir1(self):
        directory = filedialog.askdirectory(title="Seleziona Directory 1")
        if directory:
            self.dir1_path = directory
            num_images = len(self.get_image_files(directory))
            short_path = directory if len(directory) < 40 else "..." + directory[-37:]
            self.label_dir1.config(text=f"{short_path}\n({num_images} immagini)")
            self.verifica_stato_pulsante()
    
    def seleziona_dir2(self):
        directory = filedialog.askdirectory(title="Seleziona Directory 2")
        if directory:
            self.dir2_path = directory
            num_images = len(self.get_image_files(directory))
            short_path = directory if len(directory) < 40 else "..." + directory[-37:]
            self.label_dir2.config(text=f"{short_path}\n({num_images} immagini)")
            self.verifica_stato_pulsante()
    
    def verifica_stato_pulsante(self):
        if self.dir1_path and self.dir2_path:
            self.btn_compara.config(state=tk.NORMAL)
        else:
            self.btn_compara.config(state=tk.DISABLED)
    
    def get_image_files(self, directory):
        """Ottiene tutti i file immagine dalla directory"""
        extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP')
        return sorted([os.path.join(directory, f) for f in os.listdir(directory) 
                      if f.endswith(extensions)])
    
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
                return None, None, "Impossibile caricare"
            
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = self.face_mesh.process(rgb)
            
            if not result.multi_face_landmarks:
                return None, None, "Nessun volto"
            
            face_landmarks = result.multi_face_landmarks[0]
            landmarks_array = np.array([[l.x, l.y, l.z] for l in face_landmarks.landmark])
            
            # Immagine con landmarks
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
            return None, None, str(e)[:20]
    
    def calcola_compatibilita(self, pts1, pts2):
        """Calcola compatibilità"""
        min_len = min(len(pts1), len(pts2))
        distanze = np.linalg.norm(pts1[:min_len] - pts2[:min_len], axis=1)
        distanza_media = np.mean(distanze)
        compatibilita = max(0, min(100, (1 - distanza_media / 0.2) * 100))
        return compatibilita, distanza_media
    
    def genera_report_html(self, risultato, img1_landmarks, img2_landmarks):
        """Genera report HTML per una singola comparazione"""
        try:
            # Crea directory reports
            reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports_batch')
            os.makedirs(reports_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:17]
            
            # Salva immagini con landmarks
            img1_land_path = os.path.join(reports_dir, f'img1_land_{timestamp}.jpg')
            img2_land_path = os.path.join(reports_dir, f'img2_land_{timestamp}.jpg')
            
            cv2.imwrite(img1_land_path, img1_landmarks)
            cv2.imwrite(img2_land_path, img2_landmarks)
            
            # Copia immagini originali
            img1_orig_path = os.path.join(reports_dir, f'img1_orig_{timestamp}.jpg')
            img2_orig_path = os.path.join(reports_dir, f'img2_orig_{timestamp}.jpg')
            
            img1_orig = cv2.imread(risultato['file1'])
            img2_orig = cv2.imread(risultato['file2'])
            cv2.imwrite(img1_orig_path, img1_orig)
            cv2.imwrite(img2_orig_path, img2_orig)
            
            # Genera HTML
            comp = risultato['compatibilita']
            if comp >= 80:
                bg_color, border_color, text_color = '#d4edda', '#28a745', '#28a745'
                stato = 'ALTA COMPATIBILITÀ'
            elif comp >= 60:
                bg_color, border_color, text_color = '#fff3cd', '#ffc107', '#ffc107'
                stato = 'COMPATIBILITÀ MEDIA'
            else:
                bg_color, border_color, text_color = '#f8d7da', '#dc3545', '#dc3545'
                stato = 'BASSA COMPATIBILITÀ'
            
            html_path = os.path.join(reports_dir, f'report_{timestamp}.html')
            
            html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Report Comparazione - {timestamp}</title>
    <style>
        body {{ font-family: Arial; max-width: 1200px; margin: 20px auto; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; 
                   padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
        .result-box {{ background: {bg_color}; border: 2px solid {border_color}; padding: 20px; 
                      border-radius: 10px; margin-bottom: 20px; text-align: center; }}
        .compatibility {{ font-size: 42px; font-weight: bold; color: {text_color}; margin: 10px 0; }}
        .container {{ display: flex; justify-content: space-around; margin-bottom: 20px; }}
        .image-section {{ background: white; padding: 15px; border-radius: 8px; 
                         box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin: 10px; }}
        .image-pair {{ display: flex; justify-content: space-around; }}
        .image-wrapper {{ text-align: center; margin: 5px; }}
        .image-wrapper img {{ max-width: 250px; border: 2px solid #ddd; border-radius: 5px; }}
        .info-section {{ background: white; padding: 15px; border-radius: 8px; 
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; }}
        .info-grid {{ display: grid; grid-template-columns: 180px 1fr; gap: 8px; font-size: 13px; }}
        .info-label {{ font-weight: bold; color: #555; }}
        .hash {{ font-family: monospace; font-size: 11px; background: #f8f9fa; 
                padding: 5px; border-radius: 3px; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Report Comparazione Biometrica</h1>
        <p>{risultato['timestamp']}</p>
    </div>
    <div class="result-box">
        <h2>RISULTATO</h2>
        <div class="compatibility">{comp:.2f}%</div>
        <div style="font-size: 20px; font-weight: bold;">{stato}</div>
        <p>Distanza media: {risultato['distanza']:.6f}</p>
    </div>
    <div class="container">
        <div class="image-section">
            <h3>📷 Immagine 1</h3>
            <div class="image-pair">
                <div class="image-wrapper">
                    <img src="{os.path.basename(img1_orig_path)}">
                    <p><b>Originale</b></p>
                </div>
                <div class="image-wrapper">
                    <img src="{os.path.basename(img1_land_path)}">
                    <p><b>Landmarks</b></p>
                </div>
            </div>
        </div>
        <div class="image-section">
            <h3>📷 Immagine 2</h3>
            <div class="image-pair">
                <div class="image-wrapper">
                    <img src="{os.path.basename(img2_orig_path)}">
                    <p><b>Originale</b></p>
                </div>
                <div class="image-wrapper">
                    <img src="{os.path.basename(img2_land_path)}">
                    <p><b>Landmarks</b></p>
                </div>
            </div>
        </div>
    </div>
    <div class="info-section">
        <h3>🔐 Hash Files</h3>
        <div class="info-grid">
            <div class="info-label">File 1:</div><div>{risultato['nome1']}</div>
            <div class="info-label">Hash SHA256:</div><div class="hash">{risultato['hash1']}</div>
            <div class="info-label">File 2:</div><div>{risultato['nome2']}</div>
            <div class="info-label">Hash SHA256:</div><div class="hash">{risultato['hash2']}</div>
        </div>
    </div>
    <div class="info-section">
        <h3>📊 Dettagli Tecnici</h3>
        <div class="info-grid">
            <div class="info-label">Algoritmo:</div><div>MediaPipe FaceMesh (468 landmarks 3D)</div>
            <div class="info-label">Metrica:</div><div>Distanza Euclidea Media</div>
            <div class="info-label">Landmarks:</div><div>468 punti 3D</div>
        </div>
    </div>
</body>
</html>"""
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return html_path
            
        except Exception as e:
            print(f"Errore generazione HTML: {e}")
            return None
    
    def stop_comparazione(self):
        self.stop_processing = True
    
    def avvia_comparazione(self):
        # Pulisci risultati
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.risultati = []
        self.stop_processing = False
        
        # Disabilita pulsanti
        self.btn_compara.config(state=tk.DISABLED)
        self.btn_dir1.config(state=tk.DISABLED)
        self.btn_dir2.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_export_csv.config(state=tk.DISABLED)
        self.btn_apri_reports.config(state=tk.DISABLED)
        
        # Thread
        thread = threading.Thread(target=self.esegui_comparazione_batch)
        thread.daemon = True
        thread.start()
    
    def esegui_comparazione_batch(self):
        """Esegue comparazione batch"""
        try:
            files_dir1 = self.get_image_files(self.dir1_path)
            files_dir2 = self.get_image_files(self.dir2_path)
            
            total = len(files_dir1) * len(files_dir2)
            current = 0
            soglia = self.soglia_compatibilita.get()
            
            self.root.after(0, self.label_progress.config, {'text': f'0/{total}'})
            
            for file1 in files_dir1:
                if self.stop_processing:
                    break
                
                landmarks1, img1_land, error1 = self.elabora_immagine(file1)
                
                if error1:
                    for file2 in files_dir2:
                        self.aggiungi_risultato_errore(file1, file2, f"Dir1: {error1}")
                        current += 1
                        self.aggiorna_progress(current, total)
                    continue
                
                for file2 in files_dir2:
                    if self.stop_processing:
                        break
                    
                    landmarks2, img2_land, error2 = self.elabora_immagine(file2)
                    
                    if error2:
                        self.aggiungi_risultato_errore(file1, file2, f"Dir2: {error2}")
                    else:
                        compatibilita, distanza = self.calcola_compatibilita(landmarks1, landmarks2)
                        
                        # Controlla soglia
                        if compatibilita >= soglia:
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
                                'report_html': None
                            }
                            
                            # Genera HTML se richiesto
                            if self.genera_html.get():
                                html_path = self.genera_report_html(risultato, img1_land, img2_land)
                                risultato['report_html'] = html_path
                            
                            self.risultati.append(risultato)
                            self.root.after(0, self.aggiungi_risultato_tree, risultato)
                    
                    current += 1
                    self.aggiorna_progress(current, total)
            
            # Completato
            if self.stop_processing:
                self.root.after(0, self.label_progress.config, {'text': 'Interrotto'})
            else:
                self.root.after(0, self.label_progress.config, 
                               {'text': f'Completato! {len(self.risultati)} risultati'})
                self.root.after(0, messagebox.showinfo, "Completato", 
                               f"{len(self.risultati)} comparazioni salvate\n(soglia ≥{soglia}%)")
            
            # Riabilita
            self.root.after(0, self.btn_compara.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_dir1.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_dir2.config, {'state': tk.NORMAL})
            self.root.after(0, self.btn_stop.config, {'state': tk.DISABLED})
            if self.risultati:
                self.root.after(0, self.btn_export_csv.config, {'state': tk.NORMAL})
                self.root.after(0, self.btn_apri_reports.config, {'state': tk.NORMAL})
            
            self.root.after(0, self.aggiorna_statistiche)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Errore", str(e))
    
    def aggiungi_risultato_tree(self, risultato):
        comp = risultato['compatibilita']
        if comp >= 80:
            status, tag = "ALTA", 'alta'
        elif comp >= 60:
            status, tag = "MEDIA", 'media'
        else:
            status, tag = "BASSA", 'bassa'
        
        report_text = "✓ Sì" if risultato['report_html'] else "✗ No"
        
        self.tree.insert('', 'end', 
                        values=(risultato['nome1'], risultato['nome2'],
                               f"{comp:.2f}%", f"{risultato['distanza']:.4f}",
                               status, report_text),
                        tags=(tag,))
    
    def aggiungi_risultato_errore(self, file1, file2, errore):
        self.root.after(0, self.tree.insert, '', 'end', 
                       {'values': (os.path.basename(file1), os.path.basename(file2),
                                  "N/A", "N/A", f"ERR: {errore}", "✗ No"),
                        'tags': ('errore',)})
    
    def aggiorna_progress(self, current, total):
        percentage = (current / total) * 100
        self.root.after(0, self.progress.config, {'value': percentage})
        self.root.after(0, self.label_progress.config, 
                       {'text': f'{current}/{total} ({percentage:.1f}%)'})
    
    def aggiorna_statistiche(self):
        totali = len(self.risultati)
        alta = sum(1 for r in self.risultati if r['compatibilita'] >= 80)
        media = sum(1 for r in self.risultati if 60 <= r['compatibilita'] < 80)
        bassa = sum(1 for r in self.risultati if r['compatibilita'] < 60)
        errori = len([i for i in self.tree.get_children() if 'errore' in self.tree.item(i)['tags']])
        
        self.label_stats.config(
            text=f"Totali: {totali} | Alta: {alta} | Media: {media} | Bassa: {bassa} | Errori: {errori}"
        )
    
    def apri_report_selezionato(self, event):
        """Apri report HTML con doppio click"""
        item = self.tree.selection()[0]
        values = self.tree.item(item)['values']
        
        if values[5] == "✓ Sì":
            # Trova il risultato corrispondente
            nome1, nome2 = values[0], values[1]
            for r in self.risultati:
                if r['nome1'] == nome1 and r['nome2'] == nome2 and r['report_html']:
                    os.system(f'open "{r["report_html"]}"')  # macOS
                    break
    
    def apri_cartella_reports(self):
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports_batch')
        if os.path.exists(reports_dir):
            os.system(f'open "{reports_dir}"')  # macOS
    
    def esporta_csv(self):
        if not self.risultati:
            messagebox.showwarning("Attenzione", "Nessun risultato")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("All", "*.*")],
            initialfile=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("File1,File2,Compatibilità%,Distanza,Status,Hash1,Hash2,Timestamp,ReportHTML\n")
                    for r in self.risultati:
                        comp = r['compatibilita']
                        status = "ALTA" if comp >= 80 else "MEDIA" if comp >= 60 else "BASSA"
                        html = r['report_html'] if r['report_html'] else "N/A"
                        f.write(f"{r['nome1']},{r['nome2']},{comp:.2f},{r['distanza']:.6f},"
                               f"{status},{r['hash1']},{r['hash2']},{r['timestamp']},{html}\n")
                messagebox.showinfo("Successo", f"Esportato in:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

def main():
    root = tk.Tk()
    app = ComparatoreBatchAvanzatoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
