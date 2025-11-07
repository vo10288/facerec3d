# Comparatore Biometrico Volti 3D

Applicazione GUI per la comparazione biometrica tra due immagini di volti utilizzando MediaPipe FaceMesh 3D.

## 🌟 Caratteristiche

- **Interfaccia grafica intuitiva** con Tkinter
- **Estrazione automatica di 468 landmarks 3D** per volto
- **Visualizzazione side-by-side** delle immagini originali e con landmarks
- **Calcolo compatibilità biometrica** in percentuale
- **Hash SHA256** dei file originali per integrità
- **Report HTML automatico** con timestamp
- **Immagini cliccabili** nei report per visualizzazione a schermo intero

## 📋 Requisiti

```bash
pip install opencv-python mediapipe pillow numpy
```

## 🚀 Installazione

1. Assicurati di avere Python 3.8+ installato
2. Installa le dipendenze:
   ```bash
   pip install opencv-python mediapipe pillow numpy
   ```
3. Scarica il file `comparatore_volti_gui.py`

## 💻 Utilizzo

1. Esegui l'applicazione:
   ```bash
   python comparatore_volti_gui.py
   ```

2. Usa l'interfaccia grafica:
   - **Carica Immagine 1**: Seleziona la prima immagine da comparare
   - **Carica Immagine 2**: Seleziona la seconda immagine da comparare
   - **Compara Volti**: Avvia l'analisi biometrica
   - **Reset**: Pulisci tutto e ricomincia

3. Visualizza i risultati:
   - Immagini originali e con landmarks affiancate
   - Percentuale di compatibilità biometrica
   - Hash SHA256 di entrambi i file
   - Report HTML salvato automaticamente

## 📊 Interpretazione Risultati

- **≥ 80%**: 🟢 Alta compatibilità (stesso volto o molto simile)
- **60-79%**: 🟡 Compatibilità media (volti simili)
- **< 60%**: 🔴 Bassa compatibilità (volti diversi)

## 📁 Output

I report HTML vengono salvati automaticamente nella cartella `reports/` con nome:
```
report_YYYYMMDD_HHMMSS.html
```

Ogni report include:
- Timestamp di generazione
- Compatibilità biometrica in percentuale
- Distanza media tra landmarks
- 4 immagini (originali e con landmarks)
- Hash SHA256 dei file originali
- Dettagli tecnici dell'analisi

## 🔍 Dettagli Tecnici

- **Algoritmo**: MediaPipe FaceMesh
- **Landmarks**: 468 punti 3D (x, y, z) per volto
- **Metrica**: Distanza Euclidea media tra landmarks corrispondenti
- **Hash**: SHA256 per verificare l'integrità dei file originali

## 📸 Screenshot Funzionalità

L'interfaccia mostra:
- 2 colonne per le due immagini da comparare
- Ogni colonna mostra: immagine originale + immagine con landmarks
- Hash SHA256 sotto ogni coppia di immagini
- Risultato della comparazione in evidenza
- Pulsanti per caricare, comparare e resettare

## 🛠️ Risoluzione Problemi

**"Nessun volto rilevato"**
- Assicurati che l'immagine contenga un volto ben visibile
- Il volto deve essere rivolto verso la camera
- Usa immagini con buona illuminazione

**"Impossibile caricare l'immagine"**
- Verifica che il file sia un'immagine valida (JPG, PNG, BMP)
- Controlla che il file non sia corrotto

## 📝 Note

- L'applicazione analizza solo il primo volto rilevato in ogni immagine
- Per risultati ottimali, usa immagini con volti frontali
- I landmarks 3D includono coordinate x, y e profondità z
- La compatibilità è inversamente proporzionale alla distanza media

## 🔐 Privacy e Sicurezza

- Tutte le elaborazioni avvengono localmente
- Gli hash permettono di verificare l'autenticità dei file
- I report HTML possono essere archiviati per tracciabilità

## 📄 Licenza

Questo progetto è basato su MediaPipe di Google.

## 🤝 Contributi

Basato sul codice originale `match_volrti_3d.py` e esteso con interfaccia GUI e funzionalità di reporting.
