# DXHeat Discord Bot

Ein Discord-Bot, der alle 10 Minuten DX-Spots von [DXHeat](https://dxheat.com/dxc/) abruft und in einen Discord-Kanal postet.

---

## Features

- Holt aktuelle DX-Spots automatisch von DXHeat
- Postet die Spots in einen definierten Discord-Kanal
- Läuft kontinuierlich im Hintergrund (z.B. auf Railway)

---

## Voraussetzungen

- Ein Discord-Bot-Token mit Schreibrechten im gewünschten Kanal
- Die ID des Discord-Kanals, in den die Spots gepostet werden sollen
- Python 3.8+ für lokalen Test (optional)

---

## Installation & Deployment

### Lokal testen

1. Repository klonen oder ZIP entpacken  
2. Virtuelle Umgebung erstellen und aktivieren:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
