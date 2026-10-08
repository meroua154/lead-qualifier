import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from src.schemas import QualifiedLead

load_dotenv()


def send_to_n8n(qualified: QualifiedLead, test_mode: bool = False) -> tuple[bool, str]:
    """Envoie le lead qualifié au webhook n8n. Retourne (succès, message)."""
    url = os.environ["N8N_WEBHOOK_URL"]
    if test_mode:
        url = url.replace("/webhook/", "/webhook-test/")

    payload = qualified.model_dump(mode="json")
    payload["created_at"] = datetime.now().isoformat(timespec="seconds")

    try:
        r = requests.post(url, json=payload, timeout=10)
    except requests.RequestException as e:
        return False, f"n8n injoignable : {e}"

    if r.status_code == 200:
        return True, "Lead envoyé à n8n ✅"
    if r.status_code == 404:
        hint = ("Clique sur 'Execute workflow' dans n8n puis réessaie."
                if test_mode else
                "Le workflow n'est pas publié/actif dans n8n.")
        return False, f"Webhook introuvable (404). {hint}"
    return False, f"Erreur n8n {r.status_code} : {r.text[:200]}"