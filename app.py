import os
import json
import hashlib
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# ------------------- LOAD ENV -------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# fallback for Streamlit Cloud
if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    except:
        pass

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ------------------- IMPORTS -------------------
from utils.pdf_parser import extract_text_from_pdf

# ------------------- LLM CALL -------------------
def call_llm(prompt, text):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        top_p=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

# ------------------- CACHE -------------------
def get_cache_key(text):
    return hashlib.md5(text.encode()).hexdigest()

if "cache" not in st.session_state:
    st.session_state.cache = {}

# ------------------- UI -------------------
st.set_page_config(page_title="Resume Risk Analyzer", layout="wide")

st.title("🧠 Resume Risk Analyzer")
st.markdown("Upload your resume and get realistic interview-risk analysis of your key claims.")

uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])

# ------------------- MAIN -------------------
if uploaded_file:

    resume_text = extract_text_from_pdf(uploaded_file)

    # ---------- LOAD PROMPTS ----------
    with open("prompts/extract_prompt.txt", "r", encoding="utf-8") as f:
        extract_prompt = f.read()

    with open("prompts/confusion_prompt.txt", "r", encoding="utf-8") as f:
        confusion_prompt = f.read()

    st.markdown("---")
    st.subheader("🔍 Extracting Important Claims")

    # ---------- STEP 1: EXTRACT CLAIMS ----------
    cache_key = get_cache_key("extract_" + resume_text)

    if cache_key in st.session_state.cache:
        claims_result = st.session_state.cache[cache_key]
    else:
        claims_result = call_llm(extract_prompt, resume_text)
        st.session_state.cache[cache_key] = claims_result

    try:
        start = claims_result.find("[")
        end = claims_result.rfind("]") + 1
        claims = json.loads(claims_result[start:end])
    except:
        st.error("❌ Failed to extract claims")
        st.text(claims_result)
        st.stop()

    # ---------- HANDLE TOO FEW CLAIMS ----------
    if len(claims) < 4:
        st.warning("⚠ Few claims detected, retrying...")

        relaxed_prompt = extract_prompt + "\nInclude more technical lines, even if moderately important."

        claims_result = call_llm(relaxed_prompt, resume_text)

        start = claims_result.find("[")
        end = claims_result.rfind("]") + 1
        claims = json.loads(claims_result[start:end])

    # ---------- LIMIT UI ----------
    claims = claims[:8]

    st.markdown("---")
    st.subheader("📌 Evaluating Claims")

    total_claims = 0
    total_points = 0

    # ---------- STEP 2: EVALUATE ----------
    for claim in claims:

        cache_key = get_cache_key("eval_" + claim)

        if cache_key in st.session_state.cache:
            result = st.session_state.cache[cache_key]
        else:
            result = call_llm(confusion_prompt, claim)
            st.session_state.cache[cache_key] = result

        try:
            start = result.find("{")
            end = result.rfind("}") + 1
            data = json.loads(result[start:end])
        except:
            st.warning("⚠ Invalid response")
            st.text(result)
            continue

        # ---------- FIXED RISK HANDLING ----------
        risk = data.get("risk_level", "Medium")
        risk = str(risk).strip().lower()

        if risk == "low":
            risk = "Low"
        elif risk == "medium":
            risk = "Medium"
        elif risk == "high":
            risk = "High"
        else:
            risk = "Medium"   # fallback

        reason = data.get("reason", "")
        questions = data.get("interviewer_questions", [])
        improvement = data.get("improvement_suggestion", "")

        total_claims += 1

        st.markdown("---")
        st.markdown(f"### 📌 Claim {total_claims}")
        st.write(claim)

        # ---------- RISK DISPLAY ----------
        if risk == "Low":
            total_points += 3
            st.success("🟢 LOW RISK")

        elif risk == "Medium":
            total_points += 2
            st.warning("🟡 MEDIUM RISK")

        elif risk == "High":
            total_points += 1
            st.error("🔴 HIGH RISK")

        # ---------- WHY ----------
        if reason:
            st.markdown("**📝 Why this may be questioned:**")
            st.write(reason)

        # ---------- QUESTIONS ----------
        if questions:
            with st.expander("🎤 Possible Interview Questions"):
                for q in questions:
                    st.write(f"- {q}")

        # ---------- IMPROVEMENT ----------
        if improvement:
            st.markdown("**✨ Suggested Improvement:**")
            st.info(improvement)

    # ---------- SCORE ----------
    if total_claims > 0:
        max_points = total_claims * 3
        score = int((total_points / max_points) * 100)

        st.markdown("---")
        st.subheader("📊 Overall Resume Strength")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.progress(score)

        with col2:
            st.metric("Confidence Score", f"{score}/100")

        if score >= 85:
            st.success("🚀 Excellent resume strength. Very interview-ready.")
        elif score >= 70:
            st.info("👍 Strong resume with minor improvements needed.")
        else:
            st.warning("⚠ Resume needs strengthening in key claim areas.")