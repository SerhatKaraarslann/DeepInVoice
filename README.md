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

# 2. Input-/Output-Token-Schätzung pro Dokument.
Ich wollte zuerst die Anzahl der Tokens pro Dokument schätzen. Dann habe ich micht entschieden, die Anzahl der Tokens pro Dokument zu messen, indem ich den nativen Tokenizer von Mistral verwendet habe. Ich habe von der Huggingface Transformers Bibliothek den Tokenizer geladen und die Anzahl der Tokens für jedes Dokument gezählt. Um die Inputs und Outsputs Token zu berechnen, habe ich die Anzahl der Tokens für die Eingabedokumente und die generierten Antworten gezählt. 
token_calculator.py Datei enthält die Logik für die Tokenzählung. Falls man diese Datei ausführt sieht man die Input und Output Token für jedes Dokument sowie minimum, maximum und durchschnittliche Anzahl der Tokens.

Als Zusammanfassung -> Input Tokens: Min: 150, Max: 197, Average: 175
                       Output Tokens: Min: 73, Max: 148, Average: 107

# 3. Was kann beim strukturierten Output schiefgehen, und wie fängst du es ab?
Generell kann beim strukturierten Output einiges schiefgehen, wie zum Beispiel:
Das Modell kann schließende Klammern vergessen oder die Struktur nicht korrekt einhalten. Das Modell kann Konversationtext vor oder nach der JSON-Struktur generieren, was die Verarbeitung erschwert. Es kann auch passieren, dass das Modell unverständliche oder unvollständige Antworten generiert, die nicht den Anforderungen entsprechen.

Bei mir habe ich andere, spezifische Fehler gesehen. Ich hatte bei der Flags Haluznationen beobachtet, was von der Modell selbst generiert wurde, obwohl sie nicht unter Flags vorgegeben waren. Da eine einfache List[str] in pydantic so viel Freiraum bietet, haben ich mich entschieden, die Flags als Literal umzusetzen, damit das Modell nur die vorgegebenen Flags generieren kann. 

Andres Problem war die Zusammenfassungslänge. Weil LLMs tokenbasiert arbeiten und keine Wörterzählen können, hat das Modell für manche Dokumente zu lange Zusammenfassungen generiert, die über die Token-Limit hinausgehen. Um das Problem zu beheben, habe ich striktere Anweisung gegeben(Ziel 10-15 Wörter), damit das Modell kürzere Zusammenfassungen generieren kann. Da hatte ich von 18/30 erfolgreiche Zusammenfassungen auf 28/30 erfolgreiche Zusammenfassungen erhöht.

Letztes Problem war die Flags wiederholung. Da das Modell Wahrscheinlichkeiten berechnet, wurde manchmal das gleiche Flag mehrmals generiert, was zu mehrmaliges Auftauchen in der Liste führte. Ich habe das Problem gelöst, indem ich die generierten Flags in ein Set umgewandelt habe und in dem Prompt klargestellt, dass jedes Flag nur einmal generiert werden soll.


# 4. Wenn du 1.000 statt 30 Dokumente verarbeiten müsstest - was würdest du anders machen?
Ich habe genutzte Modell und Quantisierung basierend auf meiner Hardware ausgewählt, um die 30 Dokumente zu verarbeiten. Dieses Modell mit synchrone for schleife hat gut funktioniert. Wenn ich 1.000 Dokumente verarbeiten müsste, würde ich nicht das Modell ändern, sondern auf eine leistungsfähigere Inferenz-Engine wechseln, die besser für die Verarbeitung großer Datenmengen geeignet ist. 
Ich habe die Dokumentation von der vllm und sglang gelesen und gesehen, dass vllm die Möglichkeit bietet, mehrere Dokumente parallel zu verarbeiten, was die Verarbeitungsgeschwindigkeit erheblich verbessern könnte. Sglang bietet auch die Möglichkeit, bei der gleiche Prompt für mehrere Dokumente zu verwenden, die strukturierten Output schneller zu generieren.

Außerdem würde ich wahrscheinlich die Verarbeitung in Batches durchführen, um die Effizienz zu steigern und die Ressourcen besser zu nutzen. Anstatt jedes Dokument einzeln zu verarbeiten, könnte ich mehrere Dokumente gleichzeitig an das Modell senden, indem ich asynchrone methoden,anstatt chain.invoke chain.ainvoke, verwende.

Als letztes würde ich Cloud Services nutzen, die mehrere GPUs und mehr Rechenleistung bieten. So könnte ich das Batching und die Parallelisierung von vLLM/SGLang voll ausnutzen, um die 1.000 Dokumente ohne lokale Hardware-Engpässe effizient zu  verarbeiten.