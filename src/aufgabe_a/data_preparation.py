# pip install datasets
from datasets import load_dataset
import json
ds = load_dataset("ag_news", split="test")
samples = ds.shuffle(seed=42).select(range(30))
with open("aufgabe_a_data.jsonl", "w", encoding="utf-8") as f:
 for i, s in enumerate(samples):
    f.write(json.dumps({"id": f"doc_{i:03d}",
    "text": s["text"]}) + "\n")