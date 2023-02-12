# Strommessung mit Janitza UMG 96

Skriptsammlung zum Auslesen von Janitza UMG 96 via Modbus RTU

Getrennt nach Logger (Aufzeichnung) und Display (Anzeige der zuletzt geloggten Werte)

Ein Skript zum Finden von Janitzas auf einem Modbus ist auch dabei.

Am geschicktesten ist es, das Python in eine venv einzusperren

```sh
git clone https://github.com/DF3MS/janiza.git
python3 -m venv janitza-venv
source janitza-venv/bin/activate
pip3 install -r requirements.txt
```

Um den den notwendigen Seriell-Port auch für normale User erreichbar zu machen muss sich der User in der Gruppe `dialout` befinden
