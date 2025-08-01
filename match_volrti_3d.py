import os
import cv2
import numpy as np
import mediapipe as mp

# === CONFIG ===
DIR_VOLTI_3D = "volti_3d_antonio"
SOGLIA_MATCH = 0.08  # soglia su distanza media tra landmark

# === Inizializza MediaPipe FaceMesh ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# === Carica tutti i file .npy ===
volti_npy = {}
for file in os.listdir(DIR_VOLTI_3D):
    if file.endswith(".npy"):
        path = os.path.join(DIR_VOLTI_3D, file)
        nome = os.path.splitext(file)[0].replace("_landmarks", "")
        volti_npy[nome] = np.load(path)

print(f"[INFO] Caricati {len(volti_npy)} volti da {DIR_VOLTI_3D}")

# === Avvia Webcam ===
cap = cv2.VideoCapture(0)

def distanza_media(pts1, pts2):
    # confronta solo primi 468 punti se differenza nei dati
    min_len = min(len(pts1), len(pts2))
    d = np.linalg.norm(pts1[:min_len] - pts2[:min_len], axis=1)
    return np.mean(d)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    nome_match = "Sconosciuto"
    migliore_distanza = float("inf")

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            # Disegna mesh
            mp_drawing.draw_landmarks(
                frame,
                face_landmarks,
                mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
            )

            # Estrai punti
            live_pts = np.array([[l.x, l.y, l.z] for l in face_landmarks.landmark])

            # Confronta con tutti i volti salvati
            for nome, pts_salvati in volti_npy.items():
                dist = distanza_media(live_pts, pts_salvati)
                if dist < SOGLIA_MATCH and dist < migliore_distanza:
                    migliore_distanza = dist
                    nome_match = nome

            break  # considera solo il primo volto per semplicità

    # Mostra risultato
    testo = f"Match: {nome_match}"
    cv2.putText(frame, testo, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("Match Volto 3D", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
