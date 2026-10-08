import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

# usage : python test_webhook.py [HIGH|MEDIUM|LOW]
priority = sys.argv[1] if len(sys.argv) > 1 else "HIGH"

# URL de test de n8n (/webhook-test/...) au lieu de /webhook/...
url = os.environ["N8N_WEBHOOK_URL"].replace("/webhook/", "/webhook-test/")

payload = {
    "lead": {
        "type": "location",
        "city": "Lille",
        "budget": 600,
        "property_type": "studio",
        "bedrooms": None,
        "move_in_date": "ASAP",
    },
    "score": 95 if priority == "HIGH" else 20,
    "priority": priority,
    "raw_message": "Je cherche un studio à Lille, 600€, ASAP",
}

r = requests.post(url, json=payload, timeout=10)
print(r.status_code, r.text)