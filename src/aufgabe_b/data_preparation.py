# pip install datasets
from datasets import load_dataset
import json, random
ds = load_dataset("theatticusproject/cuad-qa",
 split="train", trust_remote_code=True)
# Eindeutige Verträge sammeln (im Datensatz mehrfach pro Frage vorhanden)
seen = {}
for row in ds:
 title = row["title"]
 if title not in seen:
    seen[title] = row["context"]
random.seed(42)
selected = random.sample(list(seen.items()), 50)
with open("aufgabe_b_contracts.jsonl", "w", encoding="utf-8") as f:
 for i, (title, text) in enumerate(selected):
    f.write(json.dumps({"id": f"contract_{i:03d}",
                        "title": title,
                        "text": text}) + "\n")