import streamlit as st
import requests
from datetime import datetime, timedelta
import random

# ---------------------------
# Basic Theming (HCL blues)
# ---------------------------
HCL_PRIMARY = "#004C97"  # deep blue
HCL_ACCENT = "#00A1E0"   # cyan-blue
HCL_BG = "#F5F8FC"

st.set_page_config(page_title="HCL Healthcare Assistant", page_icon="💙", layout="centered")
st.markdown(
    f"""
    <style>
        .app-container {{
            background: {HCL_BG};
            padding: 1rem 1.25rem 2rem 1.25rem;
            border-radius: 1rem;
        }}
        .chip-row {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin: 0.5rem 0 1rem 0;
        }}
        .hcl-chip > button {{
            background: white !important;
            border: 1px solid {HCL_ACCENT} !important;
            color: {HCL_PRIMARY} !important;
            border-radius: 999px !important;
            padding: 0.25rem 0.9rem !important;
        }}
        .hcl-chip-specialty > button {{
            background: white !important;
            border: 1px solid {HCL_PRIMARY} !important;
            color: {HCL_PRIMARY} !important;
            border-radius: 999px !important;
            padding: 0.2rem 0.8rem !important;
            font-size: 0.95rem !important;
        }}
        .title {{
            color: {HCL_PRIMARY};
        }}
        .card {{
            background: white;
            border: 1px solid #E6EDF7;
            border-radius: 12px;
            padding: 1rem;
        }}
        .ok-badge {{
            display: inline-block; 
            padding: .25rem .5rem; 
            border-radius: 999px; 
            background: #E6FAF0; 
            color: #117A3A; 
            border: 1px solid #BCEBD1;
            font-weight: 600;
        }}
        .warn-badge {{
            display: inline-block; 
            padding: .25rem .5rem; 
            border-radius: 999px; 
            background: #FFF6E5; 
            color: #8A5500; 
            border: 1px solid #FFE1B3;
            font-weight: 600;
        }}
        .link-like a {{
            text-decoration: none !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Utilities
# ---------------------------
@st.cache_data(show_spinner=False, ttl=3600)
def wiki_summary(query: str, fallback: str = "") -> str:
    """
    Fetch a short, neutral summary using Wikipedia REST API (free; no key).
    Returns first extract sentence(s) or fallback if none.
    """
    if not query:
        return fallback
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(query)}"
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                txt = data.get("extract") or ""
                # Trim to ~500 chars for brevity
                if len(txt) > 500:
                    txt = txt[:497].rsplit(" ", 1)[0] + "..."
                return txt.strip() or fallback
    except Exception:
        pass
    return fallback

def next_slot_str(hours_ahead_min=3, hours_ahead_max=48):
    """
    Create a simple mock appointment slot within the next 3–48 hours.
    """
    delta = random.randint(hours_ahead_min, hours_ahead_max)
    slot = datetime.now() + timedelta(hours=delta)
    return slot.strftime("%A, %d %b %Y at %I:%M %p")

def basic_precautions(symptom: str):
    """
    Very lightweight keyword-based precautions. Not medical advice.
    """
    s = symptom.lower()
    tips = []
    if any(k in s for k in ["fever", "temperature", "flu"]):
        tips += ["Hydrate well", "Rest adequately", "Monitor temperature", "Use OTC antipyretics if advised"]
    if any(k in s for k in ["cough", "cold", "sore throat"]):
        tips += ["Warm fluids & steam inhalation", "Avoid irritants/smoke", "Salt-water gargle", "Consider lozenges"]
    if any(k in s for k in ["chest pain", "pressure", "tightness", "breath"]):
        tips += ["Seek urgent medical evaluation", "Avoid exertion", "Stay with someone until evaluated"]
    if any(k in s for k in ["headache", "migraine"]):
        tips += ["Hydrate", "Dim lights & rest", "Limit screen time", "OTC analgesics only if appropriate"]
    if any(k in s for k in ["rash", "itch", "hives"]):
        tips += ["Avoid scratching", "Mild hypoallergenic moisturizer", "Note triggers (new foods, detergents)"]
    if not tips:
        tips = ["Hydrate and rest", "Monitor symptoms", "Avoid known triggers", "Consult a clinician if it persists/worsens"]
    # Deduplicate while preserving order
    seen = set(); dedup = []
    for t in tips:
        if t not in seen:
            seen.add(t); dedup.append(t)
    return dedup[:6]

def health_tip_mix(topic: str):
    """
    Combine a brief web-derived summary with pragmatic rule-based tips.
    """
    base = wiki_summary(topic, fallback="")
    rules = []
    t = (topic or "").lower()

    if "sleep" in t:
        rules += ["Aim 7–9 hours nightly", "Keep a consistent bedtime/wake time", "Limit caffeine after noon", "No screens 60 min before bed"]
    if any(k in t for k in ["weight", "bmi", "obesity"]):
        rules += ["Prioritize whole foods & protein", "250–500 kcal daily deficit for gradual loss", "Walk 8–10k steps/day", "2–3 strength sessions/week"]
    if any(k in t for k in ["diabetes", "glucose", "a1c"]):
        rules += ["Track fasting & post-meal readings", "Plate method: half veg, quarter lean protein, quarter whole grains", "Daily activity ≥30 mins"]
    if any(k in t for k in ["cholesterol", "lipid"]):
        rules += ["Increase soluble fiber (oats, legumes)", "Cut trans fats; prefer unsaturated fats", "Discuss statins if LDL remains high"]
    if any(k in t for k in ["bp", "blood pressure", "hypertension"]):
        rules += ["Reduce sodium (<2g/day)", "DASH-style diet", "Regular aerobic activity", "Limit alcohol; manage stress"]

    # Default general wellness
    if not rules:
        rules = ["Stay active daily", "Balanced diet (more plants, fewer ultra-processed foods)", "Sleep 7–9 hours", "Don’t ignore persistent symptoms"]

    return base, rules[:6]

# ---------------------------
# State
# ---------------------------
if "mode" not in st.session_state:
    st.session_state.mode = None
if "specialty" not in st.session_state:
    st.session_state.specialty = None

# ---------------------------
# Header & Greeting
# ---------------------------
st.markdown('<div class="app-container">', unsafe_allow_html=True)

st.markdown(
    f"""
    <h2 class="title">Hello dear user! Welcome to HCL Healthcare, making corporate India better. How can I help you today in your healthcare journey?</h2>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Main Chips Row
# ---------------------------
st.write("")
chip_cols = st.columns(4, gap="small")

with chip_cols[0]:
    if st.button("📅 Book Appointment", key="chip_book", use_container_width=True):
        st.session_state.mode = "book"
        st.session_state.specialty = None
with chip_cols[1]:
    if st.button("🩺 Symptom Check", key="chip_symptom", use_container_width=True):
        st.session_state.mode = "symptom"
with chip_cols[2]:
    if st.button("💊 Order Medicines", key="chip_meds", use_container_width=True):
        st.session_state.mode = "meds"
with chip_cols[3]:
    if st.button("💡 Health Tips", key="chip_tips", use_container_width=True):
        st.session_state.mode = "tips"

st.write("")

# ---------------------------
# Mode: Book Appointment
# ---------------------------
if st.session_state.mode == "book":
    st.markdown("### Book Appointment")
    st.markdown("**Please choose a speciality:**")

    spec_cols = st.columns(4, gap="small")
    specs = [("Cardiologist", "❤️"), ("Dermatologist", "🧴"), ("Neurologist", "🧠"), ("Physician", "🩺")]
    for i, (spec, emoji) in enumerate(specs):
        with spec_cols[i]:
            if st.button(f"{emoji} {spec}", key=f"spec_{spec}", use_container_width=True):
                st.session_state.specialty = spec

    if st.session_state.specialty:
        slot = next_slot_str()
        st.markdown(
            f"""
            <div class="card">
                <div class="ok-badge">Appointment booked</div>
                <p style="margin:.5rem 0 0 0;">Speciality: <b>{st.session_state.specialty}</b><br/>
                Slot: <b>{slot}</b></p>
                <p style="margin:.5rem 0 0 0;">You’ll receive a confirmation on your registered email/phone.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------
# Mode: Symptom Check
# ---------------------------
elif st.session_state.mode == "symptom":
    st.markdown("### Symptom Check")
    symptom = st.text_input("Type your symptom (e.g., fever, chest pain, rash, headache):", key="sym_input")
    if st.button("Check Symptom", key="sym_go"):
        if not symptom.strip():
            st.warning("Please enter a symptom.")
        else:
            summary = wiki_summary(symptom, fallback="No quick reference found. Consider consulting a clinician.")
            st.markdown("#### Quick Reference (from the web)")
            st.markdown(f"> {summary}")

            st.markdown("#### Suggested Precautions *(general guidance; not a diagnosis)*")
            tips = basic_precautions(symptom)
            st.markdown("- " + "\n- ".join(tips))

            # Show a web search link to "see web browser for typed symptom"
            st.markdown(
                f'<p class="link-like">🔎 <a href="https://www.google.com/search?q={requests.utils.quote(symptom)}" target="_blank">Search more about “{symptom}” on the web</a></p>',
                unsafe_allow_html=True
            )

            # Display the Book Appointment chip
            st.markdown("#### Would you like to book an appointment?")
            app_cols = st.columns(4, gap="small")
            with app_cols[0]:
                if st.button("📅 Book Appointment", key="sym_book", use_container_width=True):
                    st.session_state.mode = "book"
                    st.experimental_rerun()

# ---------------------------
# Mode: Order Medicines
# ---------------------------
elif st.session_state.mode == "meds":
    st.markdown("### Order Medicines")
    st.info("We’ll direct you to our medical partner.")
    st.link_button("Go to Tata 1mg", "https://www.1mg.com/", use_container_width=True)

# ---------------------------
# Mode: Health Tips
# ---------------------------
elif st.session_state.mode == "tips":
    st.markdown("### Health Tips")
    topic = st.text_input("Tell me your focus area (e.g., sleep, diabetes, cholesterol, weight loss):", key="tips_topic")
    if st.button("Get Tips", key="tips_go"):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            web, rules = health_tip_mix(topic)
            if web:
                st.markdown("#### From the web (neutral summary)")
                st.markdown(f"> {web}")
            st.markdown("#### Personalized, Practical Tips")
            st.markdown("- " + "\n- ".join(rules))

            # Helpful links
            st.markdown(
                f'<p class="link-like">🔎 <a href="https://www.google.com/search?q={requests.utils.quote(topic + " health tips")}" target="_blank">More tips on the web</a></p>',
                unsafe_allow_html=True
            )

# ---------------------------
# Footer: Medical Disclaimer
# ---------------------------
st.write("---")
st.caption("⚠️ This assistant provides general information and convenience only. It is not a medical diagnosis. For urgent or persistent symptoms, consult a qualified clinician immediately.")

st.markdown('</div>', unsafe_allow_html=True)
