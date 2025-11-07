import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime

# === Configurazione ===
NOME = "antonio"
DIR_SALVATAGGI = f"volti_3d_{NOME}"
os.makedirs(DIR_SALVATAGGI, exist_ok=True)

# === MediaPipe ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# === Avvia webcam ===
cap = cv2.VideoCapture(0)
salvataggio_count = 0

def salva_dati_landmark(landmarks, frame, count):
    # Estrai coordinate
    punti = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])

    # Salva immagine
    nome_base = f"{NOME}_{count:02d}"
    path_img = os.path.join(DIR_SALVATAGGI, f"{nome_base}.png")
    cv2.imwrite(path_img, frame)

    # Salva .npy
    path_npy = os.path.join(DIR_SALVATAGGI, f"{nome_base}_landmarks.npy")
    np.save(path_npy, punti)

    # Salva .csv
    path_csv = os.path.join(DIR_SALVATAGGI, f"{nome_base}_landmarks.csv")
    np.savetxt(path_csv, punti, delimiter=",", header="x,y,z", comments="")

    # Salva .obj (visualizzabile in Blender)
    path_obj = os.path.join(DIR_SALVATAGGI, f"{nome_base}_landmarks.obj")
    with open(path_obj, 'w') as f:
        for x, y, z in punti:
            f.write(f"v {x} {y} {z}\n")

    print(f"[✓] Salvati landmark in .npy, .csv e .obj come {nome_base}")

print("[INFO] Premi 's' per salvare il volto 3D, 'ESC' per uscire.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip + RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks:
        for landmarks in result.multi_face_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                landmarks,
                mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=1)
            )

            # Salvataggio se premi 's'
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                salva_dati_landmark(landmarks.landmark, frame, salvataggio_count)
                salvataggio_count += 1
                continue

    cv2.imshow("Mesh 3D in tempo reale - Premi 's' per salvare", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
