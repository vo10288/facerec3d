import cv2
import face_recognition
import mediapipe as mp
import numpy as np

# === CONFIGURAZIONE ===
NOME_IMMAGINE = "antonio.jpg"
ETICHETTA = "Antonio"

# === Inizializza MediaPipe FaceMesh ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, refine_landmarks=True)

# === Carica immagine di riferimento e ottieni encoding ===
immagine_ref = face_recognition.load_image_file(NOME_IMMAGINE)
encoding_ref_list = face_recognition.face_encodings(immagine_ref)
if len(encoding_ref_list) == 0:
    raise ValueError(f"Nessun volto trovato in {NOME_IMMAGINE}. Usa un'immagine con un volto visibile.")
encoding_ref = encoding_ref_list[0]

# === Avvia webcam ===
cap = cv2.VideoCapture(0)

# === Funzione per stimare l'orientamento 3D del volto ===
def stima_orientamento(landmarks, shape):
    try:
        image_points = np.array([
            landmarks[33],  # naso
            landmarks[263], # occhio destro
            landmarks[362], # occhio sinistro
            landmarks[1],   # mento
            landmarks[61],  # bocca sx
            landmarks[291]  # bocca dx
        ], dtype='float').reshape(-1, 2)

        model_points = np.array([
            [0.0, 0.0, 0.0],
            [-30.0, -125.0, -30.0],
            [30.0, -125.0, -30.0],
            [0.0, -250.0, -30.0],
            [-70.0, -50.0, -50.0],
            [70.0, -50.0, -50.0]
        ])

        h, w = shape[:2]
        focal = w
        center = (w / 2, h / 2)
        cam_matrix = np.array([
            [focal, 0, center[0]],
            [0, focal, center[1]],
            [0, 0, 1]
        ], dtype="double")
        dist_coeffs = np.zeros((4, 1))

        success, rvec, _ = cv2.solvePnP(model_points, image_points, cam_matrix, dist_coeffs)
        if not success:
            return None
        rmat, _ = cv2.Rodrigues(rvec)
        proj = np.hstack((rmat, np.zeros((3,1))))
        _, _, _, _, _, _, euler = cv2.decomposeProjectionMatrix(proj)
        yaw, pitch, roll = euler[1][0], euler[0][0], euler[2][0]
        return yaw, pitch, roll
    except:
        return None

# === Loop principale ===
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Ridimensiona per riconoscimento
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small = small_frame[:, :, ::-1]
    rgb_full = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Trova volti nel frame
    locations = face_recognition.face_locations(rgb_small)
    encodings = []
    valid_locations = []

    for loc in locations:
        try:
            enc = face_recognition.face_encodings(rgb_small, [loc])
            if len(enc) > 0:
                encodings.append(enc[0])
                valid_locations.append(loc)
        except Exception as e:
            print(f"[!] Errore encoding volto: {e}")

    # Ottieni landmark 3D dal frame intero
    results = face_mesh.process(rgb_full)
    landmarks_list = results.multi_face_landmarks if results.multi_face_landmarks else []

    for i, (top, right, bottom, left) in enumerate(valid_locations):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        face_encoding = encodings[i]
        match = face_recognition.compare_faces([encoding_ref], face_encoding, tolerance=0.5)
        distance = face_recognition.face_distance([encoding_ref], face_encoding)[0]
        similarity = 100 - distance * 100
        name = ETICHETTA if match[0] else "Sconosciuto"
        color = (0, 255, 0) if match[0] else (0, 0, 255)

        orientation_txt = "Orientamento non disponibile"
        if i < len(landmarks_list):
            lm = landmarks_list[i].landmark
            coords = [(int(l.x * frame.shape[1]), int(l.y * frame.shape[0])) for l in lm]
            coords_np = np.array(coords)

            # Stima 3D
            orientamento = stima_orientamento(coords_np, frame.shape)
            if orientamento:
                yaw, pitch, roll = orientamento
                orientation_txt = f"Yaw: {yaw:.1f}°, Pitch: {pitch:.1f}°, Roll: {roll:.1f}°"

            # Disegna landmark
            for (x, y) in coords_np:
                cv2.circle(frame, (x, y), 1, (0, 255, 255), -1)

        # Disegna rettangolo e testi
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, f"{name} ({similarity:.1f}%)", (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, orientation_txt, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow("Riconoscimento Facciale 3D - Antonio", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
