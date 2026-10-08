from src.schemas import Lead, LeadType, Priority

URGENT_WORDS = ("asap", "urgent", "immédiat", "immediat", "dès que possible",
                "des que possible", "rapidement", "tout de suite")

# fourchettes de budget plausibles (cohérence)
BUDGET_RANGES = {
    LeadType.LOCATION: (300, 10_000),       # €/mois
    LeadType.ACHAT: (30_000, 5_000_000),    # €
}


def score_lead(lead: Lead) -> tuple[int, Priority]:
    score = 0

    if lead.budget:
        score += 25
    if lead.city:
        score += 20
    if lead.move_in_date:
        score += 20
        if any(w in lead.move_in_date.lower() for w in URGENT_WORDS):
            score += 5
    if lead.property_type:
        score += 15
    if lead.type:
        score += 10
    if lead.bedrooms is not None:
        score += 5

    # pénalité si le budget est incohérent avec le type de demande
    if lead.budget and lead.type:
        low, high = BUDGET_RANGES[lead.type]
        if not (low <= lead.budget <= high):
            score -= 15

    score = max(0, min(100, score))

    if score >= 70:
        priority = Priority.HIGH
    elif score >= 40:
        priority = Priority.MEDIUM
    else:
        priority = Priority.LOW

    return score, priority