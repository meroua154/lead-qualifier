import streamlit as st
from src.n8n_client import send_to_n8n

from src.llm import extract_lead
from src.scoring import score_lead
from src.schemas import QualifiedLead, Priority

st.set_page_config(page_title="ImmoLead AI", page_icon="🏠", layout="centered")
st.title("🏠 ImmoLead AI")
st.caption("Qualification automatique de leads immobiliers")

EXAMPLES = {
    "Location Paris": "Bonjour, je cherche un T2 à Paris, budget 1200€, dispo en novembre",
    "Achat Lyon": "Salut je veux acheter une maison pas loin de Lyon, 350 000 euros, 3 chambres",
    "Message vague": "Bonjour, vous avez des appartements ?",
}

ACTIONS = {
    Priority.HIGH: ("🔥 Contacter rapidement le prospect", st.success),
    Priority.MEDIUM: ("📞 Rappeler sous 48h", st.warning),
    Priority.LOW: ("📧 Envoyer un mail pour compléter les informations", st.info),
}

choice = st.selectbox("Exemple de message", ["(écrire le mien)"] + list(EXAMPLES))
default = EXAMPLES.get(choice, "")
message = st.text_area("Message du prospect", value=default, height=120)

if st.button("Qualifier le lead", type="primary", disabled=not message.strip()):
    try:
        with st.spinner("Analyse du message..."):
            lead = extract_lead(message)
            score, priority = score_lead(lead)
        st.session_state["result"] = QualifiedLead(
            lead=lead, score=score, priority=priority, raw_message=message
        )
    except Exception as e:
        st.session_state.pop("result", None)
        st.error(f"Erreur pendant l'analyse : {e}")

result = st.session_state.get("result")
if result:
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Score", f"{result.score}/100")
    col2.metric("Priorité", result.priority.value)

    label, box = ACTIONS[result.priority]
    box(label)

    st.subheader("Données extraites")
    st.json(result.lead.model_dump(mode="json"))
    st.divider()
    test_mode = st.checkbox("Mode test n8n (webhook-test)", value=True)
    if st.button("📤 Envoyer vers n8n"):
        ok, msg = send_to_n8n(result, test_mode=test_mode)
        (st.success if ok else st.error)(msg)