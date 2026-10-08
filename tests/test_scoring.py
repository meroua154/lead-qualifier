from src.schemas import Lead, Priority
from src.scoring import score_lead


def test_lead_complet_est_high():
    lead = Lead(type="location", city="Paris", budget=1200,
                property_type="T2", move_in_date="novembre")
    score, priority = score_lead(lead)
    assert score == 90
    assert priority == Priority.HIGH


def test_lead_vide_est_low():
    score, priority = score_lead(Lead())
    assert score == 0
    assert priority == Priority.LOW


def test_budget_incoherent_penalise():
    # 350 000 € en "location" : incohérent
    lead = Lead(type="location", city="Lyon", budget=350_000)
    score, _ = score_lead(lead)
    assert score == 25 + 20 + 10 - 15


def test_urgence_bonus():
    a, _ = score_lead(Lead(move_in_date="novembre"))
    b, _ = score_lead(Lead(move_in_date="ASAP"))
    assert b == a + 5