# 🌍 Terraquake Discord Bot

Bot Discord sviluppato in Python per monitorare e distribuire aggiornamenti sismici in tempo reale tramite TerraquakeAPI.
Il bot recupera i dati JSON dall’API e li trasforma in messaggi embedded strutturati e leggibili direttamente nei server Discord.

## 🚀 Funzionalità

### 🔎 Ultimo terremoto – Recupera l’evento sismico più recente.

### 📊 Ultimi N terremoti – Comando dinamico ($earthquake 10) per ottenere gli ultimi 10 eventi.

### 📍 Dati completi evento

- Magnitudo
- Localizzazione
- Profondità
- Data e ora

## ⚡ Integrazione API in tempo reale

### 📦 Messaggi Embedded Discord per una visualizzazione chiara e professionale

### 🛠 Tecnologie Utilizzate

Python 3.x
discord.py
TerraquakeAPI

## 📌 Installazione

### Clona il repository:

```bash
git clone https://github.com/tuo-username/terraquake-discord-bot.git
cd terraquake-discord-bot
```

### Crea ambiente virtuale:

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

### Installa dipendenze:

```bash
pip install -r requirements.txt
```

### Crea un bot su Discord Developer Portal

```bash
Copia il BOT TOKEN
```

### Inserisci il token nel file .env:

```bash
TOKEN_DISCORD=Inserisci il tuo token discord
```

## 💻 Utilizzo

Nel server Discord:

```bash
$earthquake 10
```

Dove 10 indica il numero di eventi sismici recenti da visualizzare.
