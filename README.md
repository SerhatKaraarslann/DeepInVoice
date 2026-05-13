## Projektinformation
Dieses Repository repräsentiert meine Lösung für die Aufgaben von DeepInVoice. Ich habe das Projekt bewusst modular aufgebaut, damit Datenaufbereitung, Lösungen und Modellvergleich klar getrennt sind und sich die einzelnen Schritte nachvollziehbar erweitern lassen.

Ich habe versucht die Aufgaben mit professionellen Sichten zu lösen. Das bedeutet, dass ich nicht nur die Anforderungen erfülle, sondern auch darauf achte, dass die Lösung robust, effizient und gut dokumentiert ist.

## Ordnerstruktur

- `data/` enthält die Eingabedaten, den Goldstandard und das Regelwerk.
- `src/aufgabe_a` beinhaltet die Datenaufbereitung und die Lösung für Aufgabe A.
- `src/aufgabe_b` beinhaltet die Datenaufbereitung und die Lösung für Aufgabe B.
- `requirements.txt` listet die benötigten Python-Pakete auf.
- `README.md` enthält die Dokumentation und Anweisungen zur Nutzung des Projekts.
- `benchmark_results.png` zeigt die Ergebnisse des Modellvergleichs für Aufgabe A.
- `gitignore` enthält die Dateien und Ordner, die von Git ignoriert werden sollen.

## Installation

Ich empfehle die Nutzung einer virtuellen Umgebung.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Datenaufbereitung für Aufgabe A

Mit `src/aufgabe_a/data_preparation.py` werden aus dem Datensatz `ag_news` 30 zufällige Testbeispiele erzeugt und als JSONL-Datei gespeichert.

```bash
python src/aufgabe_a/data_preparation.py
```

## Modellvergleich

`src/aufgabe_a/model_compare.py` gibt die Möglichkeit, 3 verschiedene Ollama Modelle zu testen. Die Ergebnisse werden in einer Tabelle zusammengefasst und als Plot visualisiert. 

```bash
python src/aufgabe_a/model_compare.py
```
## Lösung für Aufgabe A
Die Lösung für Aufgabe A befindet sich in `src/aufgabe_a/solution.py`. Das Skript liest 30 Dokumente aus der JSONL-Datei ein, verarbeitet sie mit dem ausgewählten Modell und speichert die Ergebnisse in `data/aufgabe_a_results.json`.

```bash
python src/aufgabe_a/structured_news_extractor.py
```

## Datenaufbereitung für Aufgabe B
`src/aufgabe_b/data_preparation.py` bereitet die Daten für Aufgabe B vor, indem es 50 Verträge aus dem CUAD-Datensatz extrahiert und in `data/aufgabe_b_contracts.jsonl` Datei speichert.

```bash
python src/aufgabe_b/data_preparation.py
```

## Lösung für Aufgabe B
Die Lösung für Aufgabe B befindet sich in `src/aufgabe_b/structured_contract_analyzer.py` und `src/aufgabe_b/structured_contract_analyzer_chunked.py`. Das Skript liest die Verträge ein, verarbeitet sie mit dem ausgewählten Modell und speichert die Ergebnisse in `data/aufgabe_b_results.json` bzw. `data/aufgabe_b_results_chunked.json`.

```bash
python src/aufgabe_b/structured_contract_analyzer.py
```

```bash
python src/aufgabe_b/structured_contract_analyzer_chunked.py
```


## Fragen und meine Antworten
# AUFGABE A
# 1.Welches Modell, welche Quantisierung — und warum?
Um die richtige Modell und Quantisierung zu wählen, habe ich auf meinem lokalen Rechner 3 verschiedene Modelle (Llama3.1, Mistral 7B, Qwen2.5) mit 2 verschiedenen Quantisierungen(4bit und 8bit) installiert. Ich wollte meine Modellauswahl nicht nur aus dem Bauch heraus treffen, sondern auch auf Basis von Performance- und Ressourcenüberlegungen. Mein lokales System hat eine Nvidia P2000 GPU mit 5 GB VRAM, was die Auswahl der Modelle und Quantisierungen stark beeinflusst hat. 
In dem model_compare.py Skript habe ich erste 3 Artikel aus dem aufgabe_a_data.jsonl datensatz genommen und wie die Anforderungen beschrieben, getestet. Ich habe die Antworten der Modelle nach Zeit, Richtigkeit und Vollständigkeit bewertet. Das Ergebnis steht in der benchmark_results.png Datei.

# Quantisierung:
Wie in der Grafik zu sehen ist, sind die Q8 Modelle allgemein langsamer. Der Grund dafür ist, dass die Q8 Modelle nicht vollständig in meiner GPU passen und in den normalen RAM ausgelagert werden müssen. Die 8Q Modelle bringen in diesem Szenario keinen Vorteil, sondern kosten mehr Zeit/Performance. Darum habe ich mich für die 4bit Quantisierung entschieden, da sie deutlich schneller und für meine Hardware besser geeignet ist.
# Modell:
Von 3 Modellen haben alle Modelle mit Testartikeln gut performt, keine Validationsfehler oder ähnliches. Somit wurde die Geschwindigkeit zum entscheidenden Faktor. Hier hat Mistral 7B in der 4bit Quantisierung die beste Performance gezeigt. Deswegen habe ich mich für Mistral 7B in der 4bit Quantisierung entschieden.

# 2. Input-/Output-Token-Schätzung pro Dokument.
Ich wollte zuerst die Anzahl der Tokens pro Dokument schätzen. Dann habe ich mich entschieden, die Anzahl der Tokens pro Dokument zu messen, indem ich den nativen Tokenizer von Mistral verwendet habe. Ich habe von der Huggingface Transformers Bibliothek den Tokenizer geladen und die Anzahl der Tokens für jedes Dokument gezählt. Um die Inputs und Outsputs Token zu berechnen, habe ich die Anzahl der Tokens für die Eingabedokumente und die generierten Antworten gezählt. 
token_calculator.py Datei enthält die Logik für die Tokenzählung. Falls man diese Datei ausführt, sieht man die Input und Output Token für jedes Dokument sowie minimum, maximum und durchschnittliche Anzahl der Tokens.

Als Zusammanfassung -> Input Tokens: Min: 150, Max: 197, Average: 175
                       Output Tokens: Min: 73, Max: 148, Average: 107

# 3. Was kann beim strukturierten Output schiefgehen, und wie fängst du es ab?
Generell kann beim strukturierten Output einiges schiefgehen, wie zum Beispiel:
Das Modell kann schließende Klammern vergessen oder die Struktur nicht korrekt einhalten. Das Modell kann Konversationtexte vor oder nach der JSON-Struktur generieren, was die Verarbeitung erschwert. Es kann auch passieren, dass das Modell unverständliche oder unvollständige Antworten generiert, die nicht den Anforderungen entsprechen.

Bei mir habe ich andere, spezifische Fehler gesehen. Ich hatte bei der Flags Haluzinationen beobachtet, was von dem Modell selbst generiert wurde, obwohl sie nicht unter Flags vorgegeben waren. Da eine einfache List[str] in pydantic so viel Freiraum bietet, habe ich mich entschieden, die Flags als Literal umzusetzen, damit das Modell nur die vorgegebenen Flags generieren kann. 

Ein anderes Problem war die Zusammenfassungslänge. Weil LLMs tokenbasiert arbeiten und keine Wörter zählen können, hat das Modell für manche Dokumente zu lange Zusammenfassungen generiert, die über das Token-Limit hinausgehen. Um das Problem zu beheben, habe ich eine striktere Anweisung gegeben(Ziel 10-15 Wörter), damit das Modell kürzere Zusammenfassungen generieren kann. Daraufhin habe ich die erfolgreichen Zusammenfassungen von 18/30 auf 28/30 erhöht.

Das letzte Problem war die Flagswiederholung. Da das Modell Wahrscheinlichkeiten berechnet, wurde manchmal das gleiche Flag mehrmals generiert, was zu mehrmaligem Auftauchen in der Liste führte. Ich habe das Problem gelöst, indem ich die generierten Flags in ein Set umgewandelt und in dem Prompt klargestellt habe, dass jedes Flag nur einmal generiert werden soll.


# 4. Wenn du 1.000 statt 30 Dokumente verarbeiten müsstest - was würdest du anders machen?
Ich habe das genutzte Modell und die Quantisierung basierend auf meiner Hardware ausgewählt, um die 30 Dokumente zu verarbeiten. Dieses Modell hat mit der synchronen Funktion(chain.invoke) in einer Schleife gut funktioniert. Wenn ich 1.000 Dokumente verarbeiten müsste, würde ich nicht das Modell ändern, sondern auf eine leistungsfähigere Inferenz-Engine wechseln, die besser für die Verarbeitung großer Datenmengen geeignet ist. 
Ich habe die Dokumentation von der vllm und sglang gelesen und gesehen, dass vllm die Möglichkeit bietet, mehrere Dokumente parallel zu verarbeiten, was die Verarbeitungsgeschwindigkeit erheblich verbessern könnte. Sglang bietet auch die Möglichkeit, denselben Prompt für mehrere Dokumente zu verwenden, um den strukturierten Output schneller zu generieren.

Außerdem würde ich wahrscheinlich die Verarbeitung in Batches durchführen, um die Effizienz zu steigern und die Ressourcen besser zu nutzen. Anstatt jedes Dokument einzeln zu verarbeiten, könnte ich mehrere Dokumente gleichzeitig an das Modell senden, indem ich asynchrone Methoden, anstatt chain.invoke chain.ainvoke, verwende.

Als letztes würde ich Cloud Services nutzen, die mehrere GPUs und mehr Rechenleistung bieten. So könnte ich das Batching und die Parallelisierung von vLLM/SGLang voll ausnutzen, um die 1.000 Dokumente ohne lokale Hardware-Engpässe effizient zu  verarbeiten.

# AUFGABE B

## Bemerkung: 
Wenn ich den mir gegebenen Code für Aufgabe B ausführe, habe ich folgenden Fehler bekommen: `trust_remote_code` is not supported anymore. Please check that the Hugging Face dataset 'theatticusproject/cuad-qa' isn't based on a loading script and remove `trust_remote_code`. Dieser Fehler tritt auf, weil die Hugging Face Bibliothek die Option `trust_remote_code` nicht mehr unterstützt. Um diesen Fehler zu beheben, habe ich die datasets Bibliothek durch die Version 2.19.1 ersetzt, da diese Version die `trust_remote_code` Option noch unterstützt.

# 5. Welchen Pfad hast Du gewählt und warum? Welche Alternativen hast Du ausgeschlossen und warum?
Wie schon bei Aufgabe A habe ich mich für Pfad 1 entschieden. Der Grund dafür ist meine lokale Hardware. LLMs sind sehr gut zum Lesen und Verstehen bei langen Dokumenten, wenn man ihnen jedoch zu viel Freiraum lässt, halluzinieren sie gerne. Bei Pfad 1 zwinge ich das LLM durch ein striktes Pydantic-Schema dazu, nur die Extraktion (True/False) vorzunehmen, während ich die Logik und das Sammeln der Ergebnisse in meinem Code kontrolliere. Das gibt mir mehr Sicherheit, die Regeln genau so anzuwenden, wie sie definiert sind.

Pfad 2 und Pfad 3 habe ich ausgeschlossen, weil schon Ollama fast alle Ressourcen meines Rechners nutzt und es noch mehr Ressourcen benötigen würde, eine Vektordatenbank und ein Embedding-Modell aufzubauen.

# 6. Wenn RAG: Welches Embedding-Modell, welcher Chunking-Ansatz, welche Retrieval-Strategie? Hast Du Alternativen ausprobiert?
Da ich mich für Pfad 1 entschieden habe, habe ich keinen RAG-Ansatz implementiert.

# 7. Was hast Du ausprobiert und verworfen?
Ich habe zuerst versucht, die gesamte Vertragsanalyse in einem einzigen Schritt durchzuführen, indem ich das Modell direkt mit dem gesamten Vertrag gefüttert habe. Mein Programm tritt sofort mit einem "CUDA Out of Memory" Fehler auf. Als ich recherchiert habe, habe ich gesehen, dass LLMs Schwierigkeiten haben, lange Dokumente zu verarbeiten, insbesondere wenn sie komplexe Strukturen und viele Informationen enthalten. Darum habe ich versucht, den Vertrag nach 15.000 Zeichen abzuschneiden. Das hat den Fehler behoben und alles hat funktioniert. Die Precision war 85%, aber die Recall war nicht so gut, und zwar nur 31%. Höchstwahrscheinlich waren wichtige Informationen in den abgeschnittenen Teilen des Vertrags enthalten. Darum habe ich mich für einen Chunking Ansatz entschieden, bei dem ich den Vertrag in 15.000 Zeichen aufteile und jedes Chunk einzeln analysiere. Das hat lange gedauert, ungefähr 4x so lange wie die vorherige Version, aber die Recall hat sich deutlich verbessert, von 31% auf 76%, während die Precision ein bisschen gesunken ist, von 85% auf 76%.

# 8. Wo macht Dein System Fehler — Extraktion, Retrieval oder Regelanwendung?
Mein System macht hauptsächlich bei der Extraktion einen Fehler. Durch den Vergleich des gechunkten Ansatzes mit dem unchunked Ansatz habe ich die Senkung bei der Precision von 85% auf 76% gesehen. Das deutet darauf hin, dass das Modell mehr False Positives und True Positives generiert hat. Es kann sein, dass das Modell zwischen den Chunks den Kontext verloren hat, was zu ungenaueren Extraktionen geführt hat. 

# 9. Wenn Du eine Woche mehr Zeit hättest — was würdest Du als Nächstes angehen?
Wenn ich mehr Zeit und Ressourcen hätte, würde ich versuchen, Pfad 2 oder Pfad 3 zu implementieren, um die Vorteile von RAG zu nutzen. Mein Chunking-Ansatz hat mir gezeigt, dass das Lesen des gesamten Vertrags den Recall zwar verbessert, aber extrem viel Zeit kostet und die Precision verschlechtert. Mit einem RAG-Ansatz könnte ich die Informationen effizienter extrahieren, indem ich vorab relevante Abschnitte des Vertrags identifiziere und nur diese Abschnitte an das Modell weitergebe.
Außerdem würde ich verschiedene Chunk Größen und Overlaps ausprobieren, um zu sehen, ob ich die Balance zwischen Precision und Recall noch weiter optimieren kann.