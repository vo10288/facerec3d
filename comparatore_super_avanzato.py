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
import time

class ComparatoreSuperAvanzatoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparatore Biometrico Super Avanzato - Report Unificato")
        self.root.geometry("1600x1000")
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
        self.mostra_preview = tk.BooleanVar(value=True)
        
        # Per preview immagini
        self.current_preview_img1 = None
        self.current_preview_img2 = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Titolo
        title = tk.Label(
            self.root, 
            text="Comparatore Biometrico Super Avanzato - Report Unificato", 
            font=("Arial", 18, "bold"),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title.pack(pady=10)
        
        # Container principale con 2 colonne
        main_container = tk.Frame(self.root, bg='#2c3e50')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # === COLONNA SINISTRA: Controlli ===
        left_column = tk.Frame(main_container, bg='#2c3e50')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        
        # Frame directory
        dir_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        dir_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(dir_frame, text="DIRECTORY", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        # Dir 1
        btn_frame1 = tk.Frame(dir_frame, bg='#34495e')
        btn_frame1.pack(pady=3)
        
        self.btn_dir1 = tk.Button(
            btn_frame1,
            text="📁 Directory 1",
            command=self.seleziona_dir1,
            font=("Arial", 10, "bold"),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=6
        )
        self.btn_dir1.pack(side=tk.LEFT, padx=5)
        
        self.label_dir1 = tk.Label(
            btn_frame1,
            text="Non selezionata",
            font=("Arial", 9),
            bg='#34495e',
            fg='#ecf0f1',
            width=25
        )
        self.label_dir1.pack(side=tk.LEFT, padx=5)
        
        # Dir 2
        btn_frame2 = tk.Frame(dir_frame, bg='#34495e')
        btn_frame2.pack(pady=3, padx=10, fill=tk.X)
        
        self.btn_dir2 = tk.Button(
            btn_frame2,
            text="📁 Directory 2",
            command=self.seleziona_dir2,
            font=("Arial", 10, "bold"),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=6
        )
        self.btn_dir2.pack(side=tk.LEFT, padx=5)
        
        self.label_dir2 = tk.Label(
            btn_frame2,
            text="Non selezionata",
            font=("Arial", 9),
            bg='#34495e',
            fg='#ecf0f1',
            width=25
        )
        self.label_dir2.pack(side=tk.LEFT, padx=5)
        
        # Opzioni
        opt_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        opt_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(opt_frame, text="OPZIONI", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.check_html = tk.Checkbutton(
            opt_frame,
            text="Genera Report HTML Unificato",
            variable=self.genera_html,
            font=("Arial", 9),
            bg='#34495e',
            fg='#ecf0f1',
            selectcolor='#2c3e50',
            activebackground='#34495e'
        )
        self.check_html.pack(pady=2)
        
        self.check_preview = tk.Checkbutton(
            opt_frame,
            text="Mostra anteprima immagini (2 sec)",
            variable=self.mostra_preview,
            font=("Arial", 9),
            bg='#34495e',
            fg='#ecf0f1',
            selectcolor='#2c3e50',
            activebackground='#34495e'
        )
        self.check_preview.pack(pady=2)
        
        soglia_frame = tk.Frame(opt_frame, bg='#34495e')
        soglia_frame.pack(pady=5)
        
        tk.Label(soglia_frame, text="Soglia min %:",
                font=("Arial", 9), bg='#34495e', fg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        
        self.spin_soglia = tk.Spinbox(
            soglia_frame,
            from_=0,
            to=100,
            textvariable=self.soglia_compatibilita,
            width=8,
            font=("Arial", 9)
        )
        self.spin_soglia.pack(side=tk.LEFT, padx=2)
        
        # Controlli
        ctrl_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        ctrl_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(ctrl_frame, text="AZIONI", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.btn_compara = tk.Button(
            ctrl_frame,
            text="🔍 AVVIA",
            command=self.avvia_comparazione,
            font=("Arial", 11, "bold"),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.btn_compara.pack(pady=3)
        
        self.btn_stop = tk.Button(
            ctrl_frame,
            text="⏹ STOP",
            command=self.stop_comparazione,
            font=("Arial", 11, "bold"),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.btn_stop.pack(pady=3)
        
        btn_exp_frame = tk.Frame(ctrl_frame, bg='#34495e')
        btn_exp_frame.pack(pady=3)
        
        self.btn_export = tk.Button(
            btn_exp_frame,
            text="📊 CSV",
            command=self.esporta_csv,
            font=("Arial", 9, "bold"),
            bg='#9b59b6',
            fg='white',
            padx=12,
            pady=8,
            state=tk.DISABLED
        )
        self.btn_export.pack(side=tk.LEFT, padx=2)
        
        self.btn_html = tk.Button(
            btn_exp_frame,
            text="📄 HTML",
            command=self.apri_report_html,
            font=("Arial", 9, "bold"),
            bg='#16a085',
            fg='white',
            padx=12,
            pady=8,
            state=tk.DISABLED
        )
        self.btn_html.pack(side=tk.LEFT, padx=2)
        
        # Progress
        prog_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        prog_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(prog_frame, text="PROGRESS", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.progress = ttk.Progressbar(
            prog_frame,
            orient='horizontal',
            length=350,
            mode='determinate'
        )
        self.progress.pack(pady=5, padx=10)
        
        self.label_progress = tk.Label(
            prog_frame,
            text="Pronto",
            font=("Arial", 9),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.label_progress.pack(pady=3)
        
        # Statistiche
        stats_frame = tk.Frame(left_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        stats_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(stats_frame, text="STATISTICHE", font=("Arial", 11, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        self.label_stats = tk.Label(
            stats_frame,
            text="Totali: 0\nAlta: 0 | Media: 0 | Bassa: 0",
            font=("Arial", 9),
            bg='#34495e',
            fg='#ecf0f1',
            justify=tk.LEFT
        )
        self.label_stats.pack(pady=5)
        
        # === COLONNA DESTRA: Visualizzazione ===
        right_column = tk.Frame(main_container, bg='#2c3e50')
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Preview immagini correnti
        preview_frame = tk.Frame(right_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        preview_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(preview_frame, text="COMPARAZIONE CORRENTE", font=("Arial", 12, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        images_container = tk.Frame(preview_frame, bg='#34495e')
        images_container.pack(pady=5)
        
        # Immagine 1
        img1_frame = tk.Frame(images_container, bg='#2c3e50')
        img1_frame.pack(side=tk.LEFT, padx=10)
        
        self.label_preview1 = tk.Label(
            img1_frame,
            bg='#2c3e50',
            width=250,
            height=250
        )
        self.label_preview1.pack()
        
        self.label_name1 = tk.Label(
            img1_frame,
            text="---",
            font=("Arial", 8),
            bg='#34495e',
            fg='#ecf0f1',
            wraplength=200
        )
        self.label_name1.pack(pady=3)
        
        # Immagine 2
        img2_frame = tk.Frame(images_container, bg='#2c3e50')
        img2_frame.pack(side=tk.LEFT, padx=10)
        
        self.label_preview2 = tk.Label(
            img2_frame,
            bg='#2c3e50',
            width=250,
            height=250
        )
        self.label_preview2.pack()
        
        self.label_name2 = tk.Label(
            img2_frame,
            text="---",
            font=("Arial", 8),
            bg='#34495e',
            fg='#ecf0f1',
            wraplength=200
        )
        self.label_name2.pack(pady=3)
        
        # Risultato corrente
        self.label_current_result = tk.Label(
            preview_frame,
            text="---",
            font=("Arial", 14, "bold"),
            bg='#34495e',
            fg='#ecf0f1',
            pady=10
        )
        self.label_current_result.pack()
        
        # Tabella risultati
        result_frame = tk.Frame(right_column, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        result_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        tk.Label(result_frame, text="RISULTATI", font=("Arial", 12, "bold"),
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        
        scroll_frame = tk.Frame(result_frame, bg='#34495e')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            scroll_frame,
            columns=('File1', 'File2', 'Comp', 'Status'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=20
        )
        
        self.tree.heading('File1', text='File Dir 1')
        self.tree.heading('File2', text='File Dir 2')
        self.tree.heading('Comp', text='Compatibilità')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('File1', width=250)
        self.tree.column('File2', width=250)
        self.tree.column('Comp', width=100, anchor='center')
        self.tree.column('Status', width=120, anchor='center')
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Tag colors
        self.tree.tag_configure('alta', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('media', background='#fff3cd', foreground='#856404')
        self.tree.tag_configure('bassa', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('errore', background='#f5c6cb', foreground='#721c24')
    
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
    
    def mostra_preview_immagini(self, img1_landmarks, img2_landmarks, nome1, nome2, compatibilita):
        """Mostra preview delle immagini nella GUI"""
        if not self.mostra_preview.get():
            return
        
        try:
            # Ridimensiona immagini
            max_size = 250
            
            # Immagine 1
            h1, w1 = img1_landmarks.shape[:2]
            scale1 = max_size / max(h1, w1)
            new_w1, new_h1 = int(w1 * scale1), int(h1 * scale1)
            img1_resized = cv2.resize(img1_landmarks, (new_w1, new_h1))
            img1_rgb = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2RGB)
            img1_pil = Image.fromarray(img1_rgb)
            img1_tk = ImageTk.PhotoImage(img1_pil)
            
            self.label_preview1.config(image=img1_tk)
            self.label_preview1.image = img1_tk
            self.label_name1.config(text=nome1)
            
            # Immagine 2
            h2, w2 = img2_landmarks.shape[:2]
            scale2 = max_size / max(h2, w2)
            new_w2, new_h2 = int(w2 * scale2), int(h2 * scale2)
            img2_resized = cv2.resize(img2_landmarks, (new_w2, new_h2))
            img2_rgb = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2RGB)
            img2_pil = Image.fromarray(img2_rgb)
            img2_tk = ImageTk.PhotoImage(img2_pil)
            
            self.label_preview2.config(image=img2_tk)
            self.label_preview2.image = img2_tk
            self.label_name2.config(text=nome2)
            
            # Risultato
            if compatibilita >= 80:
                color = '#27ae60'
                status = 'ALTA'
            elif compatibilita >= 60:
                color = '#f39c12'
                status = 'MEDIA'
            else:
                color = '#e74c3c'
                status = 'BASSA'
            
            self.label_current_result.config(
                text=f"{compatibilita:.2f}% - {status}",
                fg=color
            )
            
            # Aggiorna GUI
            self.root.update()
            
            # Pausa 2 secondi
            time.sleep(2)
            
        except Exception as e:
            print(f"Errore preview: {e}")
    
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
            
            # Directory per salvare immagini del report
            reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports_unified')
            os.makedirs(reports_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for file1 in files_dir1:
                if self.stop_processing:
                    break
                
                landmarks1, img1_land, error1 = self.elabora_immagine(file1)
                
                if error1:
                    for file2 in files_dir2:
                        current += 1
                        self.aggiorna_progress(current, total)
                    continue
                
                for file2 in files_dir2:
                    if self.stop_processing:
                        break
                    
                    landmarks2, img2_land, error2 = self.elabora_immagine(file2)
                    
                    if not error2:
                        compatibilita, distanza = self.calcola_compatibilita(landmarks1, landmarks2)
                        
                        if compatibilita >= soglia:
                            # Salva immagini per report
                            img_ts = f"{timestamp}_{current}"
                            img1_land_path = os.path.join(reports_dir, f'img1_land_{img_ts}.jpg')
                            img2_land_path = os.path.join(reports_dir, f'img2_land_{img_ts}.jpg')
                            
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
                                'img1_land_rel': os.path.basename(img1_land_path),
                                'img2_land_rel': os.path.basename(img2_land_path)
                            }
                            
                            self.risultati.append(risultato)
                            self.root.after(0, self.aggiungi_risultato_tree, risultato)
                            
                            # Mostra preview
                            self.root.after(0, self.mostra_preview_immagini, 
                                          img1_land, img2_land, 
                                          risultato['nome1'], risultato['nome2'],
                                          compatibilita)
                    
                    current += 1
                    self.aggiorna_progress(current, total)
            
            # Genera report HTML unificato
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
        """Genera un unico report HTML con tutte le comparazioni e ordinamento dinamico"""
        try:
            html_path = os.path.join(reports_dir, f'report_unificato_{timestamp}.html')
            
            # Conta statistiche
            totali = len(self.risultati)
            alta = sum(1 for r in self.risultati if r['compatibilita'] >= 80)
            media = sum(1 for r in self.risultati if 60 <= r['compatibilita'] < 80)
            bassa = sum(1 for r in self.risultati if r['compatibilita'] < 60)
            
            # Genera righe HTML per tabella
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
                    <td>{idx}</td>
                    <td class="file-name" data-file1="{r['nome1']}">{r['nome1']}</td>
                    <td class="file-name" data-file2="{r['nome2']}">{r['nome2']}</td>
                    <td class="compatibility" data-comp="{comp:.2f}" style="font-weight: bold;">{comp:.2f}%</td>
                    <td>{r['distanza']:.6f}</td>
                    <td><b>{status}</b></td>
                    <td>
                        <button onclick="showImages('{r['img1_land_rel']}', '{r['img2_land_rel']}', '{r['nome1']}', '{r['nome2']}', {comp:.2f})" 
                                class="btn-view">👁️ Vedi</button>
                    </td>
                </tr>
                """
            
            html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report Unificato Comparazioni - {timestamp}</title>
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
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
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
        .stat-number {{ font-size: 36px; font-weight: bold; margin: 10px 0; }}
        .stat-label {{ font-size: 14px; color: #666; text-transform: uppercase; }}
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
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
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
            font-size: 14px;
            border: 2px solid #ddd;
            border-radius: 8px;
            width: 300px;
        }}
        .table-container {{
            padding: 20px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        th {{
            background: #343a40;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
            position: sticky;
            top: 0;
            cursor: pointer;
            user-select: none;
        }}
        th:hover {{ background: #495057; }}
        th.sortable::after {{
            content: ' ⇅';
            opacity: 0.5;
        }}
        th.sort-asc::after {{
            content: ' ▲';
            opacity: 1;
        }}
        th.sort-desc::after {{
            content: ' ▼';
            opacity: 1;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        tr:hover {{ background: #f1f3f5; }}
        .btn-view {{
            padding: 6px 12px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }}
        .btn-view:hover {{ background: #0056b3; }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
        }}
        .modal-content {{
            background: white;
            margin: 2% auto;
            padding: 30px;
            width: 90%;
            max-width: 1400px;
            border-radius: 15px;
            position: relative;
        }}
        .close {{
            position: absolute;
            right: 20px;
            top: 20px;
            font-size: 35px;
            font-weight: bold;
            color: #aaa;
            cursor: pointer;
        }}
        .close:hover {{ color: #000; }}
        .image-comparison {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        .image-box {{
            text-align: center;
            flex: 1;
            margin: 0 10px;
        }}
        .image-box img {{
            max-width: 100%;
            max-height: 400px;
            border: 3px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .image-box h3 {{ margin: 15px 0 10px; color: #333; }}
        .comp-result {{
            text-align: center;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            font-size: 24px;
            font-weight: bold;
        }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Report Unificato Comparazioni Biometriche</h1>
            <p>Generato il: {datetime.now().strftime('%d/%m/%Y alle %H:%M:%S')}</p>
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
                    📁 Ordina per File 1 A-Z
                </button>
                <button class="btn btn-info" onclick="sortTable('file2', 'asc')">
                    📁 Ordina per File 2 A-Z
                </button>
            </div>
            <div class="btn-group">
                <button class="btn btn-success" onclick="filterResults('alta')">
                    🟢 Solo Alta
                </button>
                <button class="btn btn-warning" onclick="filterResults('media')">
                    🟡 Solo Media
                </button>
                <button class="btn btn-danger" onclick="filterResults('bassa')">
                    🔴 Solo Bassa
                </button>
                <button class="btn btn-primary" onclick="filterResults('all')">
                    📋 Mostra Tutti
                </button>
            </div>
            <input type="text" class="search-box" id="searchBox" 
                   placeholder="🔍 Cerca per nome file..." 
                   onkeyup="searchTable()">
        </div>
        
        <div class="table-container">
            <table id="resultsTable">
                <thead>
                    <tr>
                        <th style="width: 50px;">#</th>
                        <th class="sortable" onclick="sortTable('file1', 'toggle')">File Directory 1</th>
                        <th class="sortable" onclick="sortTable('file2', 'toggle')">File Directory 2</th>
                        <th class="sortable" onclick="sortTable('compatibility', 'toggle')">Compatibilità</th>
                        <th>Distanza</th>
                        <th>Status</th>
                        <th style="width: 80px;">Azione</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    
    <div id="imageModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2 style="text-align: center; margin-bottom: 20px;">Comparazione Dettagliata</h2>
            <div id="modalResult" class="comp-result"></div>
            <div class="image-comparison">
                <div class="image-box">
                    <h3 id="modalFile1Name">File 1</h3>
                    <img id="modalImg1" src="" alt="Immagine 1">
                </div>
                <div class="image-box">
                    <h3 id="modalFile2Name">File 2</h3>
                    <img id="modalImg2" src="" alt="Immagine 2">
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentSort = {{ column: '', direction: '' }};
        let allRows = [];
        
        // Salva tutte le righe all'inizio
        document.addEventListener('DOMContentLoaded', function() {{
            allRows = Array.from(document.querySelectorAll('.result-row'));
        }});
        
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
            
            rows.sort((a, b) => {{
                let valA, valB;
                
                if (column === 'compatibility') {{
                    valA = parseFloat(a.querySelector('.compatibility').dataset.comp);
                    valB = parseFloat(b.querySelector('.compatibility').dataset.comp);
                }} else if (column === 'file1') {{
                    valA = a.querySelector('[data-file1]').dataset.file1.toLowerCase();
                    valB = b.querySelector('[data-file1]').dataset.file1.toLowerCase();
                }} else if (column === 'file2') {{
                    valA = a.querySelector('[data-file2]').dataset.file2.toLowerCase();
                    valB = b.querySelector('[data-file2]').dataset.file2.toLowerCase();
                }}
                
                if (direction === 'asc') {{
                    return valA > valB ? 1 : -1;
                }} else {{
                    return valA < valB ? 1 : -1;
                }}
            }});
            
            tbody.innerHTML = '';
            rows.forEach((row, idx) => {{
                row.querySelector('td:first-child').textContent = idx + 1;
                tbody.appendChild(row);
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
                if (th) {{
                    th.classList.add(currentSort.direction === 'asc' ? 'sort-asc' : 'sort-desc');
                }}
            }}
        }}
        
        function filterResults(type) {{
            const rows = document.querySelectorAll('.result-row');
            rows.forEach(row => {{
                if (type === 'all') {{
                    row.style.display = '';
                }} else {{
                    const comp = parseFloat(row.querySelector('.compatibility').dataset.comp);
                    let show = false;
                    if (type === 'alta' && comp >= 80) show = true;
                    if (type === 'media' && comp >= 60 && comp < 80) show = true;
                    if (type === 'bassa' && comp < 60) show = true;
                    row.style.display = show ? '' : 'none';
                }}
            }});
            updateRowNumbers();
        }}
        
        function searchTable() {{
            const input = document.getElementById('searchBox').value.toLowerCase();
            const rows = document.querySelectorAll('.result-row');
            
            rows.forEach(row => {{
                const file1 = row.querySelector('[data-file1]').dataset.file1.toLowerCase();
                const file2 = row.querySelector('[data-file2]').dataset.file2.toLowerCase();
                const match = file1.includes(input) || file2.includes(input);
                row.style.display = match ? '' : 'none';
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
        
        function showImages(img1, img2, name1, name2, comp) {{
            document.getElementById('modalImg1').src = img1;
            document.getElementById('modalImg2').src = img2;
            document.getElementById('modalFile1Name').textContent = name1;
            document.getElementById('modalFile2Name').textContent = name2;
            
            const resultDiv = document.getElementById('modalResult');
            let bgColor, status;
            if (comp >= 80) {{
                bgColor = '#d4edda';
                status = 'ALTA COMPATIBILITÀ';
            }} else if (comp >= 60) {{
                bgColor = '#fff3cd';
                status = 'COMPATIBILITÀ MEDIA';
            }} else {{
                bgColor = '#f8d7da';
                status = 'BASSA COMPATIBILITÀ';
            }}
            
            resultDiv.style.background = bgColor;
            resultDiv.innerHTML = `<b>${{comp.toFixed(2)}}%</b> - ${{status}}`;
            
            document.getElementById('imageModal').style.display = 'block';
        }}
        
        function closeModal() {{
            document.getElementById('imageModal').style.display = 'none';
        }}
        
        window.onclick = function(event) {{
            const modal = document.getElementById('imageModal');
            if (event.target === modal) {{
                closeModal();
            }}
        }}
        
        // Ordina per compatibilità all'avvio
        window.onload = function() {{
            sortTable('compatibility', 'desc');
        }};
    </script>
</body>
</html>"""
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.report_html_path = html_path
            messagebox.showinfo("Report Generato", 
                               f"Report HTML unificato creato!\n{len(self.risultati)} comparazioni incluse.\n\n"
                               f"Clicca 'Apri HTML' per visualizzarlo.")
            
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
        
        self.tree.insert('', 'end', 
                        values=(risultato['nome1'], risultato['nome2'],
                               f"{comp:.2f}%", status),
                        tags=(tag,))
    
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
        
        self.label_stats.config(
            text=f"Totali: {totali}\nAlta: {alta} | Media: {media} | Bassa: {bassa}"
        )
    
    def apri_report_html(self):
        if hasattr(self, 'report_html_path') and os.path.exists(self.report_html_path):
            os.system(f'open "{self.report_html_path}"')  # macOS
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
    app = ComparatoreSuperAvanzatoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
