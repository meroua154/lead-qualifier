import os
import re
import time

from dotenv import load_dotenv
from openai import OpenAI, APIStatusError, APIConnectionError
from pydantic import ValidationError

from src.schemas import Lead

load_dotenv()

client = OpenAI(
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.environ["LLM_BASE_URL"],
)
MODEL = os.environ["LLM_MODEL"]

SYSTEM = """Tu extrais des informations d'un message de prospect immobilier.
Réponds UNIQUEMENT avec un objet JSON contenant exactement ces clés :
type, city, budget, property_type, bedrooms, move_in_date.

Règles :
- type : "location" ou "achat". Déduis-le du contexte : un budget mensuel
  (ex. 500-5000€), "louer", "loyer" → "location" ; "acheter", "acquisition",
  un budget de plusieurs dizaines/centaines de milliers d'euros → "achat".
  Sinon null.
- city : ville mentionnée, sinon null
- budget : nombre en euros (sans symbole), sinon null
- property_type : "studio", "T2", "T3", "maison"... sinon null
- bedrooms : nombre de chambres si précisé, sinon null (ne le déduis pas)
- move_in_date : date ou délai tel qu'exprimé ("novembre", "ASAP"), sinon null

N'invente jamais une information absente du message."""


def extract_lead(message: str, retries: int = 3) -> Lead:
    last_error = None
    for attempt in range(retries):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": message + " /no_think"},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            content = r.choices[0].message.content or ""
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            return Lead.model_validate_json(content)

        except ValidationError as e:  # JSON cassé : on réessaie
            last_error = e
        except (APIStatusError, APIConnectionError) as e:
            status = getattr(e, "status_code", None)
            if status is not None and status not in (429, 500, 502, 503, 504):
                raise  # erreur de config (401, 404...) : inutile de réessayer
            last_error = e
            time.sleep(2 ** attempt)

    raise last_error