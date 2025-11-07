# 🔍 Comparatore Identificazione Persone - Database

Sistema di identificazione biometrica con database persone e ricerca automatica.

---

## 🎯 Concetto

### **Database**
- Cartella con immagini di persone note
- **Nome file = Nome persona** (es: `mario_rossi.jpg` → "Mario Rossi")
- Il sistema indicizza automaticamente tutti i volti

### **Ricerca**
- Cartella con foto da identificare
- Il sistema cerca ogni volto nel database
- Mostra solo match con confidenza **Media (≥60%)** o **Alta (≥80%)**

---

## 🚀 Come Usare

### **1. Prepara il Database**

Crea una cartella con le foto delle persone note:

```
database_persone/
├── mario_rossi.jpg
├── lucia_bianchi.jpg
├── giovanni_verdi.jpg
├── anna_neri.jpg
└── ...
```

**IMPORTANTE**: Il nome del file (senza estensione) diventerà il nome della persona!

### **2. Prepara le Foto da Identificare**

Crea una cartella con le foto da identificare:

```
foto_da_identificare/
├── foto1.jpg
├── foto2.jpg
├── volto_sconosciuto.jpg
└── ...
```

### **3. Usa l'Applicazione**

```bash
python comparatore_identificazione.py
```

#### **Step A: Indicizza Database**
1. Click **"📁 Seleziona Database"**
2. Scegli la cartella `database_persone/`
3. Click **"🔍 Indicizza Database"**
4. Aspetta che carichi tutte le persone

#### **Step B: Seleziona Ricerca**
1. Click **"📁 Directory Ricerca"**
2. Scegli la cartella `foto_da_identificare/`

#### **Step C: Identifica**
1. (Opzionale) Imposta soglia minima (default 60%)
2. Click **"🔍 IDENTIFICA"**
3. Guarda i risultati nella GUI!

---

## 📊 Interfaccia GUI

```
┌─────────────────────────────────────────────────────────┐
│ TARGET (da identificare)    MATCH IDENTIFICATO          │
├─────────────────────────────────────────────────────────┤
│  [Immagine con nome]        [Immagine del database]    │
│  ID: Mario Rossi            (con landmarks)             │
│  87.5%                                                  │
│                                                         │
│  foto1.jpg                  Mario Rossi                 │
│                                                         │
│           87.45% - ALTA CONFIDENZA                     │
└─────────────────────────────────────────────────────────┘

LISTA RISULTATI:
┌────────────────────────────────────────────────────────┐
│ foto1.jpg  │ Mario Rossi    │ 87.45% │ ALTA          │
│ foto2.jpg  │ Lucia Bianchi  │ 73.21% │ MEDIA         │
│ foto3.jpg  │ Giovanni Verdi │ 81.90% │ ALTA          │
└────────────────────────────────────────────────────────┘
```

---

## 🎨 Caratteristiche

### **Nome sulla Immagine**
- Il nome identificato appare **direttamente sull'immagine** con landmarks
- Colore verde per alta confidenza (≥80%)
- Colore arancione per media confidenza (60-79%)

### **Filtro Automatico**
- Mostra solo match ≥ soglia impostata (default 60%)
- **Scarta automaticamente** le basse confidenze (<60%)
- Evita falsi positivi

### **Click sulla Lista**
- Clicca su una riga → vedi le immagini nella GUI
- Naviga facilmente tra i risultati

### **Esportazione**
- **CSV**: Esporta tutti i risultati in formato tabella
- **Report**: (in sviluppo) Report HTML completo

---

## 💡 Esempi d'Uso

### **1. Sistema di Sicurezza**
```
Database: Dipendenti autorizzati
Ricerca: Foto telecamere ingresso
Risultato: Identifica chi entra
```

### **2. Organizzazione Foto**
```
Database: Membri famiglia
Ricerca: Collezione foto vacanze
Risultato: Identifica automaticamente le persone
```

### **3. Verifica Identità**
```
Database: Database clienti noti
Ricerca: Nuove richieste accesso
Risultato: Verifica identità veloce
```

### **4. Ricerca Persona**
```
Database: 1 foto della persona cercata
Ricerca: Grande collezione di foto
Risultato: Trova tutte le foto con quella persona
```

---

## ⚙️ Opzioni

### **Soglia Minima (%)**
- **0-59%**: BASSA (scartata automaticamente)
- **60-79%**: MEDIA (mostrata, colore arancione)
- **80-100%**: ALTA (mostrata, colore verde)

**Consigliato**: 60% o superiore

---

## 📁 File Generati

```
identificazioni/
├── target_20250107_143045_0.jpg  ← Foto con nome identificato
├── match_20250107_143045_0.jpg   ← Foto dal database
├── target_20250107_143045_1.jpg
├── match_20250107_143045_1.jpg
└── ...
```

---

## 🔧 Workflow Completo

```
1. PREPARA DATABASE
   ↓
   Crea cartella con foto persone note
   Nome file = nome persona

2. INDICIZZA
   ↓
   L'app analizza ogni foto
   Estrae landmarks biometrici
   Salva in memoria

3. PREPARA RICERCA
   ↓
   Crea cartella con foto da identificare

4. IDENTIFICA
   ↓
   Per ogni foto ricerca:
   - Compara con TUTTE le persone nel DB
   - Trova il miglior match
   - Se ≥ soglia → salva risultato
   - Scrive nome sulla immagine

5. RISULTATI
   ↓
   - Vedi nella GUI
   - Click per navigare
   - Esporta CSV
   - Salva immagini con nomi
```

---

## 📊 Statistiche Mostrate

```
Database: 150        ← Persone nel database
Identificati: 47     ← Target identificati con successo
Alta: 32            ← Match ad alta confidenza (≥80%)
Media: 15           ← Match a media confidenza (60-79%)
```

---

## 🎯 Logica di Identificazione

```python
Per ogni foto_target in directory_ricerca:
    
    1. Estrai landmarks biometrici
    
    2. Compara con OGNI persona nel database
    
    3. Trova la persona con compatibilità massima
    
    4. Se compatibilità ≥ soglia:
       - Salva risultato
       - Scrivi nome sulla immagine
       - Mostra nella lista
    
    5. Altrimenti:
       - Scarta (confidenza troppo bassa)
```

---

## 💪 Vantaggi

✅ **Automatico**: Identifica tutte le foto in un colpo  
✅ **Nome file = Nome persona**: Semplice da gestire  
✅ **Filtro intelligente**: Solo match affidabili  
✅ **Nome su immagine**: Vedi subito chi è  
✅ **Navigazione facile**: Click sulla lista  
✅ **Esportabile**: CSV per ulteriori analisi  

---

## ⚠️ Note Importanti

### **Nomi File**
- Usa nomi descrittivi: `mario_rossi.jpg` ✅
- Evita simboli strani: `m@rio#rossi.jpg` ❌
- Gli spazi vanno bene: `Mario Rossi.jpg` ✅

### **Qualità Foto**
- Foto frontali funzionano meglio
- Buona illuminazione
- Volto ben visibile
- Evita foto sfocate

### **Database Grande**
- Più persone nel DB = più tempo di indicizzazione
- Ma una volta indicizzato, la ricerca è veloce!

### **Soglia**
- Troppo bassa (es. 40%) → Molti falsi positivi
- Troppo alta (es. 90%) → Perde match validi
- **Consigliato**: 60-70%

---

## 🚀 Pronto all'Uso!

```bash
python comparatore_identificazione.py
```

1. Indicizza database persone
2. Seleziona directory ricerca
3. Identifica!

**Sistema completo di identificazione biometrica! 🎉**

---

## 📈 Prestazioni

| Database | Ricerca | Tempo Indicizzazione | Tempo Identificazione |
|----------|---------|---------------------|---------------------|
| 50 persone | 10 foto | ~1 min | ~30 sec |
| 100 persone | 20 foto | ~2 min | ~1 min |
| 500 persone | 50 foto | ~10 min | ~5 min |

*Tempi approssimativi su Mac Intel*

---

**Versione**: 1.0 Identificazione  
**Data**: Novembre 2025  
**Basato su**: MediaPipe FaceMesh 3D
