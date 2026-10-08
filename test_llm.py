import time
from src.llm import extract_lead

msgs = [
    "Bonjour, je cherche un T2 à Paris, budget 1200€, dispo en novembre",
    "Salut je veux acheter une maison pas loin de Lyon, 350 000 euros, 3 chambres",
    "Bonjour, vous avez des appartements ?",
]
for m in msgs:
    print(m, "\n ->", extract_lead(m), "\n")
    time.sleep(2)