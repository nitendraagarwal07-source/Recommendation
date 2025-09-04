import streamlit as st
import requests
from datetime import datetime, timedelta
import random

# =========================
# THEME — Light Blue HCL vibes
# =========================
CLR_PRIMARY = "#1F6FE3"   # HCL-ish blue (buttons/icons)
CLR_PRIMARY_LIGHT = "#EAF2FF"
CLR_ACCENT = "#7BB3FF"    # softer blue accents
CLR_BG = "#F6FAFF"        # background wash
CLR_BORDER = "#DCE9FF"
CLR_TEXT = "#0F2B46"
CLR_SUCCESS_BG = "#E8F8F1"
CLR_SUCCESS_TXT = "#16794D"
CLR_WARN_BG = "#FFF6E5"
CLR_WARN_TXT = "#8A5500"

st.set_page_config(
    page_title="HCL Healthcare Assistant",
    page_icon="🏥",
    layout="centered",
)

# ---------- Global Styles ----------
st.markdown(
    f"""
    <style>
        html, body, [data-testid="stAppViewContainer"] {{
            background: linear-gradient(180deg, {CLR_BG} 0%, #FFFFFF 80%);
            color: {CLR_TEXT};
        }}
        .hcl-shell {{
            max-width: 980px;
            margin: 0 auto;
        }}

        /* Banner */
        .hcl-banner {{
            background: linear-gradient(135deg, {CLR_PRIMARY_LIGHT} 0%, #FFFFFF 100%);
            border: 1px solid {CLR_BORDER};
            border-radius: 16px;
            padding: 18px 20px;
            display: flex;
            gap: 14px;
            align-items: center;
            margin-bottom: 10px;
        }}
        .hcl-badge {{
            background: #FFFFFF;
            border: 1px solid {CLR_BORDER};
            color: {CLR_PRIMARY};
            font-weight: 700;
            border-radius: 999px;
            padding: 6px 12px;
            font-size: 12px;
        }}
        .hcl-title {{
            margin: 0;
            color: {CLR_TEXT};
            font-size: 22px;
            line-height: 1.35;
        }}
        .hcl-sub {{
            margin: 4px 0 0 0;
            color: #33536E;
            font-size: 14px;
        }}

        /* Symbol strip */
        .hcl-symbols {{
            display: flex;
            gap: 10px;
            font-size: 20px;
            opacity: .95;
        }}
        .pulse {{
            animation: pulse 3s ease-in-out infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: translateY(0px); opacity: .85; }}
            50% {{ transform: translateY(-3px); opacity: 1; }}
            100% {{ transform: translateY(0px); opacity: .85; }}
        }}

        /* Cards */
        .hcl-card {{
            background: #FFFFFF;
            border: 1px solid {CLR_BORDER};
            border-radius: 14px;
            padding: 16px 16px;
            box-shadow: 0 1px 0 rgba(0,0,0,0.02);
        }}

        /* Section titles */
        .hcl-section-title {{
            font-size: 18px;
            font-weight: 700;
            color: {CLR_TEXT};
            margin: 4px 0 8px 0;
        }}

        /* Status badges */
        .ok-badge {{
            display: inline-block;
            padding: .3rem .6rem;
            border-radius: 999px;
            background: {CLR_SUCCESS_BG};
            color: {CLR_SUCCESS_TXT};
            border: 1px solid #BCEBD1;
            font-weight: 700;
            font-size: 12px;
        }}
        .warn-badge {{
            display: inline-block;
            padding: .3rem .6rem;
            border-radius: 999px;
            background: {CLR_WARN_BG};
            color: {CLR_WARN_TXT};
            border: 1px solid #FFE1B3;
            font-weight: 700;
            font-size: 12px;
        }}

        /* Buttons → make them pill & blue */
        button[kind="secondary"], div[data-testid="stButton"] > button {{
            border-radius: 999px !important;
            border: 1px solid {CLR_ACCENT} !important;
            color: {CLR_TEXT} !important;
            background-color: #FFFFFF !important;
        }}
        .stButton>button:hover {{
            border-color: {CLR_PRIMARY} !important;
            box-shadow: 0 0 0 3px {CLR_PRIMARY_LIGHT};
        }}
        /* Primary feeling for top chips */
        .hcl-top-btn .stButton>button {{
            background: {CLR_PRIMARY} !important;
            color: #FFFFFF !important;
            border: 1px solid {CLR_PRIMARY} !important;
        }}
        .hcl-top-btn .stButton>button:hover {{
            box-shadow: 0 0 0 3px {CLR_ACCENT};
        }}

        /* Links */
        .link-like a {{
            text-decoration: none !important;
            color: {CLR_PRIMARY} !important;
            font-weight: 600;
        }}
        .link-like a:hover {{
            text-decoration: underline !important;
        }}

        /* Inputs */
        input, textarea {{
            border-radius: 10px !important;
            border-color: {CLR_BORDER} !important;
        }}

        /* Footer */
        .hcl-foot {{
            color: #506B81;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# HELPERS (unchanged logic)
# =========================
@st.cache_data(show_spinner=False, ttl=3600)
def wiki_summary(query: str, fallback: str = "") -> str:
    """Free, keyless Wikipedia summary (short)."""
    if not query:
        return fallback
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(query)}"
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                txt = data.get("extract") or ""
                if len(txt) > 500:
                    txt = txt[:497].rsplit(" ", 1)[0] + "..."
                return txt.strip() or fallback
    except Exception:
        pass
    return fallback

def next_slot_str(hours_ahead_min=3, hours_ahead_max=48):
    """Mock appointment slot text."""
    delta = random.randint(hours_ahead_min, hours_ahead_max)
    slot = datetime.now() + timedelta(hours=delta)
    return slot.strftime("%A, %d %b %Y at %I:%M %p")

def basic_precautions(symptom: str):
    """Keyword-based general precautions."""
    s = (symptom or "").lower()
    tips = []
    if any(k in s for k in ["fever", "temperature", "flu"]):
        tips += ["Hydrate well", "Rest adequately", "Monitor temperature", "Use OTC antipyretics if advised"]
    if any(k in s for k in ["cough", "cold", "sore throat"]):
        tips += ["Warm fluids & steam inhalation", "Avoid irritants/smoke", "Salt-water gargle", "Consider lozenges"]
    if any(k in s for k in ["chest pain", "pressure", "tightness", "breath"]):
        tips += ["Seek urgent medical evaluation", "Avoid exertion", "Stay with someone until evaluated"]
    if any(k in s for k in ["headache", "migraine"]):
        tips += ["Hydrate", "Dim lights & rest", "Limit screen time", "OTC analgesics if appropriate"]
    if any(k in s for k in ["rash", "itch", "hives"]):
        tips += ["Avoid scratching", "Mild hypoallergenic moisturizer", "Note triggers (new foods, detergents)"]
    if not tips:
        tips = ["Hydrate and rest", "Monitor symptoms", "Avoid known triggers", "Consult a clinician if it persists/worsens"]

    seen = set(); dedup = []
    for t in tips:
        if t not in seen:
            seen.add(t); dedup.append(t)
    return dedup[:6]

def health_tip_mix(topic: str):
    """Combine web snippet with pragmatic rules."""
    base = wiki_summary(topic, fallback="")
    rules = []
    t = (topic or "").lower()

    if "sleep" in t:
        rules += ["Aim 7–9 hours nightly", "Consistent sleep/wake time", "Limit caffeine after noon", "No screens 60 min before bed"]
    if any(k in t for k in ["weight", "bmi", "obesity"]):
        rules += ["Whole foods & protein focus", "250–500 kcal daily deficit", "8–10k steps/day", "2–3 strength sessions/week"]
    if any(k in t for k in ["diabetes", "glucose", "a1c"]):
        rules += ["Track fasting/post-meal readings", "Plate method", "Daily activity ≥30 mins"]
    if any(k in t for k in ["cholesterol", "lipid"]):
        rules += ["More soluble fiber", "Cut trans fats; prefer unsaturated", "Discuss statins if LDL remains high"]
    if any(k in t for k in ["bp", "blood pressure", "hypertension"]):
        rules += ["Reduce sodium (<2g/day)", "DASH-style diet", "Regular aerobic activity", "Limit alcohol; manage stress"]

    if not rules:
        rules = ["Move daily", "Balanced diet (more plants)", "Sleep 7–9 hours", "Don’t ignore persistent symptoms"]

    return base, rules[:6]

# =========================
# STATE
# =========================
if "mode" not in st.session_state:
    st.session_state.mode = None
if "specialty" not in st.session_state:
    st.session_state.specialty = None

# =========================
# HEADER / HERO
# =========================
st.markdown('<div class="hcl-shell">', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="hcl-banner">
        <div class="hcl-symbols">
            <span class="pulse">🏥</span>
            <span class="pulse">🫀</span>
            <span class="pulse">🧬</span>
            <span class="pulse">💊</span>
        </div>
        <div>
            <div class="hcl-badge">HCL HEALTHCARE</div>
            <p class="hcl-title">Hello dear user! Welcome to HCL Healthcare, making corporate India better. How can I help you today in your healthcare journey?</p>
            <p class="hcl-sub">Smart assistance for appointments, symptoms, medicines, and personalized health tips.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# TOP CHIPS (same features)
# =========================
with st.container():
    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        st.markdown('<div class="hcl-top-btn">', unsafe_allow_html=True)
        if st.button("📅 Book Appointment", key="chip_book", use_container_width=True):
            st.session_state.mode = "book"
            st.session_state.specialty = None
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="hcl-top-btn">', unsafe_allow_html=True)
        if st.button("🩺 Symptom Check", key="chip_symptom", use_container_width=True):
            st.session_state.mode = "symptom"
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="hcl-top-btn">', unsafe_allow_html=True)
        if st.button("💊 Order Medicines", key="chip_meds", use_container_width=True):
            st.session_state.mode = "meds"
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="hcl-top-btn">', unsafe_allow_html=True)
        if st.button("💡 Health Tips", key="chip_tips", use_container_width=True):
            st.session_state.mode = "tips"
        st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# =========================
# MODE SCREENS (logic unchanged)
# =========================

# --- Book Appointment ---
if st.session_state.mode == "book":
    st.markdown('<div class="hcl-card">', unsafe_allow_html=True)
    st.markdown('<div class="hcl-section-title">🗓️ Book Appointment</div>', unsafe_allow_html=True)
    st.write("Please choose a speciality:")

    spec_cols = st.columns(4, gap="small")
    specs = [("Cardiologist", "🫀"), ("Dermatologist", "🩹"), ("Neurologist", "🧠"), ("Physician", "🩺")]
    for i, (spec, emoji) in enumerate(specs):
        with spec_cols[i]:
            if st.button(f"{emoji} {spec}", key=f"spec_{spec}", use_container_width=True):
                st.session_state.specialty = spec

    if st.session_state.specialty:
        slot = next_slot_str()
        st.markdown(
            f"""
            <div style="margin-top:10px;">
              <span class="ok-badge">Appointment booked</span>
              <p style="margin:.6rem 0 0 0;">Speciality: <b>{st.session_state.specialty}</b><br/>
              Slot: <b>{slot}</b></p>
              <p style="margin:.25rem 0 0 0;">You’ll receive a confirmation on your registered email/phone.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# --- Symptom Check ---
elif st.session_state.mode == "symptom":
    st.markdown('<div class="hcl-card">', unsafe_allow_html=True)
    st.markdown('<div class="hcl-section-title">🩺 Symptom Check</div>', unsafe_allow_html=True)
    symptom = st.text_input("Type your symptom (e.g., fever, chest pain, rash, headache):", key="sym_input", placeholder="e.g., high fever and cough")
    if st.button("Check Symptom", key="sym_go", use_container_width=True):
        if not symptom.strip():
            st.warning("Please enter a symptom.")
        else:
            summary = wiki_summary(symptom, fallback="No quick reference found. Consider consulting a clinician.")
            st.markdown("**Quick Reference (from the web)**")
            st.markdown(f"> {summary}")

            st.markdown("**Suggested Precautions *(general guidance; not a diagnosis)***")
            tips = basic_precautions(symptom)
            st.markdown("- " + "\n- ".join(tips))

            st.markdown(
                f'<p class="link-like">🔎 <a href="https://www.google.com/search?q={requests.utils.quote(symptom)}" target="_blank">Search more about “{symptom}” on the web</a></p>',
                unsafe_allow_html=True
            )

            st.markdown("---")
            st.markdown("**Would you like to book an appointment?**")
            app_cols = st.columns(4, gap="small")
            with app_cols[0]:
                if st.button("📅 Book Appointment", key="sym_book", use_container_width=True):
                    st.session_state.mode = "book"
                    st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- Order Medicines ---
elif st.session_state.mode == "meds":
    st.markdown('<div class="hcl-card">', unsafe_allow_html=True)
    st.markdown('<div class="hcl-section-title">💊 Order Medicines</div>', unsafe_allow_html=True)
    st.info("We’ll direct you to our medical partner.")
    st.link_button("Go to Tata 1mg", "https://www.1mg.com/", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Health Tips ---
elif st.session_state.mode == "tips":
    st.markdown('<div class="hcl-card">', unsafe_allow_html=True)
    st.markdown('<div class="hcl-section-title">💡 Health Tips</div>', unsafe_allow_html=True)
    topic = st.text_input("Tell me your focus area (e.g., sleep, diabetes, cholesterol, weight loss):", key="tips_topic", placeholder="e.g., improving sleep")
    if st.button("Get Tips", key="tips_go", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            web, rules = health_tip_mix(topic)
            if web:
                st.markdown("**From the web (neutral summary)**")
                st.markdown(f"> {web}")
            st.markdown("**Personalized, Practical Tips**")
            st.markdown("- " + "\n- ".join(rules))
            st.markdown(
                f'<p class="link-like">🔎 <a href="https://www.google.com/search?q={requests.utils.quote(topic + " health tips")}" target="_blank">More tips on the web</a></p>',
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.write("")
st.markdown(
    f"""
    <div class="hcl-card hcl-foot">
        ⚠️ <b>Medical Disclaimer:</b> This assistant provides general information and convenience only. It is not a medical diagnosis. 
        For urgent or persistent symptoms, consult a qualified clinician immediately.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)
