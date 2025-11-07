import os
import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import hashlib
from datetime import datetime

class ComparatoreVoltiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparatore Biometrico Volti 3D")
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
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Variabili per le immagini
        self.img1_path = None
        self.img2_path = None
        self.img1_original = None
        self.img2_original = None
        self.img1_landmarks = None
        self.img2_landmarks = None
        self.landmarks1 = None
        self.landmarks2 = None
        self.hash1 = None
        self.hash2 = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Titolo
        title = tk.Label(
            self.root, 
            text="Comparatore Biometrico Volti 3D", 
            font=("Arial", 24, "bold"),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title.pack(pady=20)
        
        # Frame per i pulsanti
        btn_frame = tk.Frame(self.root, bg='#2c3e50')
        btn_frame.pack(pady=10)
        
        self.btn_img1 = tk.Button(
            btn_frame,
            text="📁 Carica Immagine 1",
            command=self.carica_immagine1,
            font=("Arial", 12, "bold"),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.btn_img1.pack(side=tk.LEFT, padx=10)
        
        self.btn_img2 = tk.Button(
            btn_frame,
            text="📁 Carica Immagine 2",
            command=self.carica_immagine2,
            font=("Arial", 12, "bold"),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.btn_img2.pack(side=tk.LEFT, padx=10)
        
        self.btn_compara = tk.Button(
            btn_frame,
            text="🔍 Compara Volti",
            command=self.compara_volti,
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.btn_compara.pack(side=tk.LEFT, padx=10)
        
        self.btn_reset = tk.Button(
            btn_frame,
            text="🔄 Reset",
            command=self.reset,
            font=("Arial", 12, "bold"),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.btn_reset.pack(side=tk.LEFT, padx=10)
        
        # Frame principale per le immagini
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Frame Immagine 1
        frame1 = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        frame1.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame1, 
            text="IMMAGINE 1", 
            font=("Arial", 14, "bold"),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=5)
        
        img_frame1 = tk.Frame(frame1, bg='#34495e')
        img_frame1.pack(pady=5)
        
        self.label_img1_orig = tk.Label(img_frame1, bg='#2c3e50', text="Originale")
        self.label_img1_orig.pack(side=tk.LEFT, padx=5)
        
        self.label_img1_land = tk.Label(img_frame1, bg='#2c3e50', text="Landmarks")
        self.label_img1_land.pack(side=tk.LEFT, padx=5)
        
        self.label_hash1 = tk.Label(
            frame1, 
            text="Hash: --", 
            font=("Arial", 9),
            bg='#34495e',
            fg='#bdc3c7',
            wraplength=600
        )
        self.label_hash1.pack(pady=5)
        
        # Frame Immagine 2
        frame2 = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        frame2.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame2, 
            text="IMMAGINE 2", 
            font=("Arial", 14, "bold"),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=5)
        
        img_frame2 = tk.Frame(frame2, bg='#34495e')
        img_frame2.pack(pady=5)
        
        self.label_img2_orig = tk.Label(img_frame2, bg='#2c3e50', text="Originale")
        self.label_img2_orig.pack(side=tk.LEFT, padx=5)
        
        self.label_img2_land = tk.Label(img_frame2, bg='#2c3e50', text="Landmarks")
        self.label_img2_land.pack(side=tk.LEFT, padx=5)
        
        self.label_hash2 = tk.Label(
            frame2, 
            text="Hash: --", 
            font=("Arial", 9),
            bg='#34495e',
            fg='#bdc3c7',
            wraplength=600
        )
        self.label_hash2.pack(pady=5)
        
        # Frame risultato
        result_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, borderwidth=3)
        result_frame.pack(pady=20, padx=20, fill=tk.X)
        
        self.label_risultato = tk.Label(
            result_frame,
            text="Compatibilità Biometrica: -- %",
            font=("Arial", 18, "bold"),
            bg='#34495e',
            fg='#ecf0f1',
            pady=15
        )
        self.label_risultato.pack()
        
        self.label_status = tk.Label(
            result_frame,
            text="Carica due immagini per iniziare",
            font=("Arial", 11),
            bg='#34495e',
            fg='#95a5a6'
        )
        self.label_status.pack(pady=5)
    
    def calcola_hash(self, filepath):
        """Calcola SHA256 hash del file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def carica_immagine1(self):
        filepath = filedialog.askopenfilename(
            title="Seleziona Immagine 1",
            filetypes=[("Immagini", "*.jpg *.jpeg *.png *.bmp"), ("Tutti i file", "*.*")]
        )
        if filepath:
            self.img1_path = filepath
            self.hash1 = self.calcola_hash(filepath)
            self.elabora_immagine(filepath, 1)
            self.label_hash1.config(text=f"Hash SHA256: {self.hash1}")
            self.verifica_stato_pulsante_compara()
    
    def carica_immagine2(self):
        filepath = filedialog.askopenfilename(
            title="Seleziona Immagine 2",
            filetypes=[("Immagini", "*.jpg *.jpeg *.png *.bmp"), ("Tutti i file", "*.*")]
        )
        if filepath:
            self.img2_path = filepath
            self.hash2 = self.calcola_hash(filepath)
            self.elabora_immagine(filepath, 2)
            self.label_hash2.config(text=f"Hash SHA256: {self.hash2}")
            self.verifica_stato_pulsante_compara()
    
    def elabora_immagine(self, filepath, numero):
        """Elabora l'immagine ed estrae i landmarks"""
        # Carica immagine
        img = cv2.imread(filepath)
        if img is None:
            messagebox.showerror("Errore", f"Impossibile caricare l'immagine {numero}")
            return
        
        # Crea copia per landmarks
        img_landmarks = img.copy()
        
        # Converti in RGB per MediaPipe
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Processa con FaceMesh
        result = self.face_mesh.process(rgb)
        
        if not result.multi_face_landmarks:
            messagebox.showwarning(
                "Attenzione", 
                f"Nessun volto rilevato nell'immagine {numero}"
            )
            return
        
        # Estrai landmarks
        face_landmarks = result.multi_face_landmarks[0]
        landmarks_array = np.array([[l.x, l.y, l.z] for l in face_landmarks.landmark])
        
        # Disegna landmarks
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
        
        # Disegna anche i contorni principali
        self.mp_drawing.draw_landmarks(
            image=img_landmarks,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.mp_drawing.DrawingSpec(
                color=(255, 0, 0), 
                thickness=2, 
                circle_radius=1
            )
        )
        
        # Salva le immagini e i landmarks
        if numero == 1:
            self.img1_original = img
            self.img1_landmarks = img_landmarks
            self.landmarks1 = landmarks_array
            self.mostra_immagini(img, img_landmarks, self.label_img1_orig, self.label_img1_land)
        else:
            self.img2_original = img
            self.img2_landmarks = img_landmarks
            self.landmarks2 = landmarks_array
            self.mostra_immagini(img, img_landmarks, self.label_img2_orig, self.label_img2_land)
    
    def mostra_immagini(self, img_orig, img_land, label_orig, label_land):
        """Mostra le immagini nei label"""
        max_height = 300
        
        # Ridimensiona immagine originale
        h, w = img_orig.shape[:2]
        scale = max_height / h
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        img_orig_resized = cv2.resize(img_orig, (new_w, new_h))
        img_orig_rgb = cv2.cvtColor(img_orig_resized, cv2.COLOR_BGR2RGB)
        img_orig_pil = Image.fromarray(img_orig_rgb)
        img_orig_tk = ImageTk.PhotoImage(img_orig_pil)
        
        label_orig.config(image=img_orig_tk, text="")
        label_orig.image = img_orig_tk
        
        # Ridimensiona immagine con landmarks
        img_land_resized = cv2.resize(img_land, (new_w, new_h))
        img_land_rgb = cv2.cvtColor(img_land_resized, cv2.COLOR_BGR2RGB)
        img_land_pil = Image.fromarray(img_land_rgb)
        img_land_tk = ImageTk.PhotoImage(img_land_pil)
        
        label_land.config(image=img_land_tk, text="")
        label_land.image = img_land_tk
    
    def verifica_stato_pulsante_compara(self):
        """Abilita il pulsante compara se entrambe le immagini sono caricate"""
        if self.landmarks1 is not None and self.landmarks2 is not None:
            self.btn_compara.config(state=tk.NORMAL)
            self.label_status.config(text="Pronto per la comparazione")
    
    def calcola_compatibilita(self, pts1, pts2):
        """Calcola la compatibilità biometrica tra due set di landmarks"""
        # Assicurati che abbiano la stessa lunghezza
        min_len = min(len(pts1), len(pts2))
        pts1 = pts1[:min_len]
        pts2 = pts2[:min_len]
        
        # Calcola la distanza euclidea media
        distanze = np.linalg.norm(pts1 - pts2, axis=1)
        distanza_media = np.mean(distanze)
        
        # Converti in percentuale di compatibilità
        # Una distanza di 0 = 100%, una distanza di 0.2 o più = 0%
        compatibilita = max(0, min(100, (1 - distanza_media / 0.2) * 100))
        
        return compatibilita, distanza_media
    
    def compara_volti(self):
        """Esegue la comparazione tra i due volti"""
        if self.landmarks1 is None or self.landmarks2 is None:
            messagebox.showwarning("Attenzione", "Carica entrambe le immagini prima di comparare")
            return
        
        # Calcola compatibilità
        compatibilita, distanza = self.calcola_compatibilita(self.landmarks1, self.landmarks2)
        
        # Determina colore in base alla compatibilità
        if compatibilita >= 80:
            colore = '#27ae60'  # Verde
            stato = "ALTA COMPATIBILITÀ"
        elif compatibilita >= 60:
            colore = '#f39c12'  # Arancione
            stato = "COMPATIBILITÀ MEDIA"
        else:
            colore = '#e74c3c'  # Rosso
            stato = "BASSA COMPATIBILITÀ"
        
        # Aggiorna UI
        self.label_risultato.config(
            text=f"Compatibilità Biometrica: {compatibilita:.2f}%",
            fg=colore
        )
        self.label_status.config(
            text=f"{stato} - Distanza media landmarks: {distanza:.4f}"
        )
        
        # Salva report HTML
        self.salva_report_html(compatibilita, distanza, stato)
        
        messagebox.showinfo(
            "Comparazione Completata", 
            f"Compatibilità: {compatibilita:.2f}%\n{stato}\n\nReport HTML salvato con successo!"
        )
    
    def salva_report_html(self, compatibilita, distanza, stato):
        """Salva il report in formato HTML"""
        # Crea directory per i report se non esiste
        os.makedirs("reports", exist_ok=True)
        
        # Timestamp per nome file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"reports/report_{timestamp}.html"
        
        # Salva le immagini
        img1_orig_filename = f"reports/img1_orig_{timestamp}.jpg"
        img1_land_filename = f"reports/img1_land_{timestamp}.jpg"
        img2_orig_filename = f"reports/img2_orig_{timestamp}.jpg"
        img2_land_filename = f"reports/img2_land_{timestamp}.jpg"
        
        cv2.imwrite(img1_orig_filename, self.img1_original)
        cv2.imwrite(img1_land_filename, self.img1_landmarks)
        cv2.imwrite(img2_orig_filename, self.img2_original)
        cv2.imwrite(img2_land_filename, self.img2_landmarks)
        
        # Crea HTML
        html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report Comparazione Biometrica - {timestamp}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .result-box {{
            background-color: {'#d4edda' if compatibilita >= 80 else '#fff3cd' if compatibilita >= 60 else '#f8d7da'};
            border: 2px solid {'#28a745' if compatibilita >= 80 else '#ffc107' if compatibilita >= 60 else '#dc3545'};
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .compatibility {{
            font-size: 48px;
            font-weight: bold;
            color: {'#28a745' if compatibilita >= 80 else '#ffc107' if compatibilita >= 60 else '#dc3545'};
            margin: 10px 0;
        }}
        .status {{
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .container {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .image-section {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin: 10px;
            flex: 1;
            min-width: 300px;
        }}
        .image-section h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .image-pair {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            flex-wrap: wrap;
        }}
        .image-wrapper {{
            text-align: center;
            margin: 10px;
        }}
        .image-wrapper img {{
            max-width: 100%;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 5px;
            cursor: pointer;
            transition: transform 0.3s;
        }}
        .image-wrapper img:hover {{
            transform: scale(1.05);
            border-color: #667eea;
        }}
        .image-label {{
            margin-top: 10px;
            font-weight: bold;
            color: #555;
        }}
        .info-section {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .info-section h3 {{
            color: #667eea;
            margin-top: 0;
        }}
        .hash {{
            font-family: 'Courier New', monospace;
            font-size: 12px;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            word-break: break-all;
            margin: 5px 0;
        }}
        .metadata {{
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 10px;
            margin: 10px 0;
        }}
        .metadata-label {{
            font-weight: bold;
            color: #555;
        }}
        .footer {{
            text-align: center;
            color: #999;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Report Comparazione Biometrica Volti 3D</h1>
        <p>Generato il: {datetime.now().strftime("%d/%m/%Y alle %H:%M:%S")}</p>
    </div>

    <div class="result-box">
        <h2>RISULTATO COMPARAZIONE</h2>
        <div class="compatibility">{compatibilita:.2f}%</div>
        <div class="status">{stato}</div>
        <p>Distanza media landmarks: {distanza:.6f}</p>
        <p>Numero di landmarks analizzati: {len(self.landmarks1)}</p>
    </div>

    <div class="container">
        <div class="image-section">
            <h2>📷 Immagine 1</h2>
            <div class="image-pair">
                <div class="image-wrapper">
                    <a href="{os.path.basename(img1_orig_filename)}" target="_blank">
                        <img src="{os.path.basename(img1_orig_filename)}" alt="Immagine 1 Originale" width="300">
                    </a>
                    <div class="image-label">Originale</div>
                </div>
                <div class="image-wrapper">
                    <a href="{os.path.basename(img1_land_filename)}" target="_blank">
                        <img src="{os.path.basename(img1_land_filename)}" alt="Immagine 1 Landmarks" width="300">
                    </a>
                    <div class="image-label">Landmarks 3D</div>
                </div>
            </div>
        </div>

        <div class="image-section">
            <h2>📷 Immagine 2</h2>
            <div class="image-pair">
                <div class="image-wrapper">
                    <a href="{os.path.basename(img2_orig_filename)}" target="_blank">
                        <img src="{os.path.basename(img2_orig_filename)}" alt="Immagine 2 Originale" width="300">
                    </a>
                    <div class="image-label">Originale</div>
                </div>
                <div class="image-wrapper">
                    <a href="{os.path.basename(img2_land_filename)}" target="_blank">
                        <img src="{os.path.basename(img2_land_filename)}" alt="Immagine 2 Landmarks" width="300">
                    </a>
                    <div class="image-label">Landmarks 3D</div>
                </div>
            </div>
        </div>
    </div>

    <div class="info-section">
        <h3>🔐 Informazioni Hash File Originali</h3>
        <div class="metadata">
            <div class="metadata-label">File Immagine 1:</div>
            <div>{os.path.basename(self.img1_path)}</div>
            <div class="metadata-label">Hash SHA256 (Img 1):</div>
            <div class="hash">{self.hash1}</div>
            <div class="metadata-label">File Immagine 2:</div>
            <div>{os.path.basename(self.img2_path)}</div>
            <div class="metadata-label">Hash SHA256 (Img 2):</div>
            <div class="hash">{self.hash2}</div>
        </div>
    </div>

    <div class="info-section">
        <h3>📊 Dettagli Tecnici</h3>
        <div class="metadata">
            <div class="metadata-label">Algoritmo:</div>
            <div>MediaPipe FaceMesh 3D (468 landmarks)</div>
            <div class="metadata-label">Metrica:</div>
            <div>Distanza Euclidea Media tra landmarks 3D</div>
            <div class="metadata-label">Threshold Compatibilità:</div>
            <div>Alta: ≥80% | Media: 60-79% | Bassa: &lt;60%</div>
            <div class="metadata-label">Dimensioni Immagine 1:</div>
            <div>{self.img1_original.shape[1]} x {self.img1_original.shape[0]} px</div>
            <div class="metadata-label">Dimensioni Immagine 2:</div>
            <div>{self.img2_original.shape[1]} x {self.img2_original.shape[0]} px</div>
        </div>
    </div>

    <div class="footer">
        <p>Report generato automaticamente dal Sistema di Comparazione Biometrica Volti 3D</p>
        <p>© {datetime.now().year} - Tutti i diritti riservati</p>
    </div>
</body>
</html>"""
        
        # Salva il file HTML
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[INFO] Report salvato: {report_filename}")
    
    def reset(self):
        """Reset dell'applicazione"""
        self.img1_path = None
        self.img2_path = None
        self.img1_original = None
        self.img2_original = None
        self.img1_landmarks = None
        self.img2_landmarks = None
        self.landmarks1 = None
        self.landmarks2 = None
        self.hash1 = None
        self.hash2 = None
        
        # Reset UI
        self.label_img1_orig.config(image='', text="Originale")
        self.label_img1_land.config(image='', text="Landmarks")
        self.label_img2_orig.config(image='', text="Originale")
        self.label_img2_land.config(image='', text="Landmarks")
        
        self.label_hash1.config(text="Hash: --")
        self.label_hash2.config(text="Hash: --")
        
        self.label_risultato.config(
            text="Compatibilità Biometrica: -- %",
            fg='#ecf0f1'
        )
        self.label_status.config(text="Carica due immagini per iniziare")
        
        self.btn_compara.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = ComparatoreVoltiGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
