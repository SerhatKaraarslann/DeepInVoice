## Projektinformation
Dieses Repository representiert meine Lösung für die Aufgaben von DeepInVoice. Ich habe das Projekt bewusst modular aufgebaut, damit Datenaufbereitung, Lösungen und Modellvergleich klar getrennt sind und sich die einzelnen Schritte nachvollziehbar erweitern lassen.

Ich habe versucht die Aufgaben mit professionellen Sichten zu lösen. Das bedeutet, dass ich nicht nur die Anforderungen erfülle, sondern auch darauf achte, dass die Lösung robust, effizient und gut dokumentiert ist.

## Ordnerstruktur

- `data/` enthält die Eingabedaten, den Goldstandard und das Regelwerk.
- `src/data_preparation.py` erstellt aus einem Datensatz eine kleinere, einheitlich formatierte JSONL-Datei.
- `src/model_compare.py` führt die eigentliche Benchmark durch, indem es verschiedene Modelle testet und die Ergebnisse auswertet.

## Installation

Ich empfehle die Nutzung einer virtuellen Umgebung.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Datenaufbereitung

Mit `src/data_preparation.py` werden aus dem Datensatz `ag_news` 30 zufällige Testbeispiele erzeugt und als JSONL-Datei gespeichert.

```bash
python src/data_preparation.py
```

## Modellvergleich

`src/model_compare.py` gibt die Möglichkeit, 3 verschieden Ollama Modelle zu testen. Die Ergebnisse werden in einer Tabelle zusammengefasst und als Plot visualisiert. 

```bash
python src/model_compare.py
```

## Fragen und Meine Antworten
# 1.Welches Modell, welche Quantisierung — und warum?
Um die richtige Modell und Quantisierung zu wählen, habe ich mich auf meinem lokalen Rechner 3 verschiedene Modelle (Llama3.1, Mistral, Qwen2.5) mit 2 verschiedenen Quantisierungen(4bit und 8bit) installiert. Ich wollte meine Modellauswahl nicht nur aus dem Bauch heraus treffen, sondern auch auf Basis von Performance- und Ressourcenüberlegungen. Mein lokales System hat eine Nvidia P2000 GPU mit 5 GB VRAM, was die Auswahl der Modelle und Quantisierungen stark beeinflusst hat. 
In dem model_compare.py Skript habe ich erste 3 Artikel aus dem aufgabe_a_data.jsonl datensatz genommen und wie die Anforderungen beschrieben, getestet. Ich habe die Antworten der Modelle nach Zeit, Richtigkeit und Vollständigkeit bewertet. Das Erebnis steht in der benchmark_results.png Datei.

# Quantisierung:
Wie in der Grafik zu sehen ist, sind die Q8 Modelle allgemein langsamer. Der Grund dafür ist, dass die Q8 Modelle nicht vollständig in meiner GPU passen und in den normelen RAM ausgelagert werden müssen. Die 8Q Modelle bringen in diesem Szenario keinen Vorteil, sondern kosten mehr Zeit/Performance. Darum habe ich mich für die 4bit Quantisierung entschieden, da sie deutlich schneller ist und für meine Hardware besser geeignet ist.
# Modell:
Unter 3 Modellen haben alle Modelle mit Testartikeln gut performt, keine Validationsfehler oder ähnliches. Somit wurde die Geschwindigkeit zum entscheidenden Faktor. Hier hat Mistral 7B in der 4bit Quantisierung am besten Performance gezeigt. Deswegen habe ich mich für Mistral 7B in der 4bit Quantisierung entschieden.