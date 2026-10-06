import streamlit as st
import pandas as pd
from pathlib import Path

from components.ui import inject_css, sidebar
from components.chatbot import render_chatbot
from utils.scoring import analyze_presentation
from utils.helpers import load_history, save_session, estimate_speech_time

st.set_page_config(
    page_title="AI Presentation Coach",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard"
if "presentation" not in st.session_state:
    st.session_state.presentation = ""
if "analysis" not in st.session_state:
    st.session_state.analysis = None

page = sidebar()

if page == "🏠 Dashboard":
    st.markdown('<div class="hero"><h1>🎤 AI-Powered Presentation Coach</h1><p>Practice smarter. Speak clearer. Present with confidence.</p></div>', unsafe_allow_html=True)

    hist = load_history()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Practice Sessions", len(hist))
    c2.metric("Average Score", f"{hist['overall'].mean():.1f}/100" if not hist.empty else "—")
    c3.metric("Best Score", f"{hist['overall'].max():.1f}/100" if not hist.empty else "—")
    c4.metric("Words Practiced", f"{hist['words'].sum():,}" if not hist.empty else "0")

    st.markdown("### 🚀 Start your practice")
    a, b = st.columns(2)
    with a:
        st.markdown("#### 📝 Presentation Coach")
        st.write("Enter your presentation script and receive instant AI-style feedback on structure, clarity, relevance, engagement and completeness.")
        if st.button("Start Presentation Practice", use_container_width=True):
            st.session_state.page = "🎤 Presentation Coach"
            st.rerun()
    with b:
        st.markdown("#### 💬 Intelligent Assistant")
        st.write("Ask questions such as “How can I improve my introduction?” or “How do I reduce nervousness?”")
        if st.button("Open AI Assistant", use_container_width=True):
            st.session_state.page = "💬 AI Assistant"
            st.rerun()

    st.markdown("### ✨ What the coach evaluates")
    cols = st.columns(5)
    for col, title, desc in zip(
        cols,
        ["Structure", "Clarity", "Relevance", "Engagement", "Completeness"],
        ["Flow & organization", "Simple communication", "Topic alignment", "Audience connection", "Coverage & ending"]
    ):
        col.markdown(f"**{title}**")
        col.caption(desc)

elif page == "🎤 Presentation Coach":
    st.title("🎤 Presentation Coach")
    st.caption("Paste a practice script below. The coach analyzes it instantly.")

    with st.form("practice_form"):
        topic = st.text_input("Presentation topic", placeholder="e.g., AI in Healthcare")
        audience = st.selectbox("Audience", ["Students", "Faculty", "Professionals", "General Audience"])
        target_minutes = st.slider("Target duration (minutes)", 1, 30, 5)
        script = st.text_area(
            "Your presentation script",
            height=300,
            placeholder="Start with your introduction, explain your key points, examples, conclusion..."
        )
        submitted = st.form_submit_button("🔍 Analyze Presentation", use_container_width=True)

    if submitted:
        if len(script.split()) < 15:
            st.warning("Please enter at least 15 words so the coach can provide meaningful feedback.")
        else:
            result = analyze_presentation(script, topic)
            result["target_minutes"] = target_minutes
            result["estimated_minutes"] = estimate_speech_time(script)
            st.session_state.presentation = script
            st.session_state.analysis = result
            save_session(topic or "Untitled", audience, result)
            st.success("Analysis completed!")

    result = st.session_state.analysis
    if result:
        st.markdown("---")
        st.subheader("📊 Your Presentation Score")
        cols = st.columns(5)
        metrics = [
            ("Overall", result["overall"]),
            ("Structure", result["structure"]),
            ("Clarity", result["clarity"]),
            ("Relevance", result["relevance"]),
            ("Engagement", result["engagement"]),
        ]
        for col, (label, value) in zip(cols, metrics):
            col.metric(label, f"{value:.0f}/100")

        st.progress(min(result["overall"]/100, 1.0))
        st.caption(f"Estimated speaking time: {result['estimated_minutes']:.1f} min | Target: {result['target_minutes']} min")

        left, right = st.columns(2)
        with left:
            st.subheader("✅ Strengths")
            for item in result["strengths"]:
                st.success(item)
        with right:
            st.subheader("🎯 Improve next")
            for item in result["improvements"]:
                st.warning(item)

        st.subheader("🔑 Topic & Structure Feedback")
        st.write(result["feedback"])
        if result["missing"]:
            st.info("Consider adding: " + ", ".join(result["missing"]))

elif page == "💬 AI Assistant":
    render_chatbot()

elif page == "📈 Analytics":
    st.title("📈 Practice Analytics")
    hist = load_history()
    if hist.empty:
        st.info("No practice sessions yet. Complete a presentation analysis first.")
    else:
        st.dataframe(hist, use_container_width=True, hide_index=True)
        st.subheader("Score Trend")
        chart = hist.set_index("session")[["overall", "structure", "clarity", "relevance", "engagement"]]
        st.line_chart(chart)
        st.subheader("Latest Session")
        st.write(hist.iloc[-1].to_dict())

elif page == "ℹ️ About":
    st.title("ℹ️ About the Project")
    st.markdown("""
### AI-Powered Presentation Coach
This application combines presentation analytics with an intelligent conversational assistant.

**Core workflow**
1. Choose a topic and audience.
2. Enter your presentation script.
3. Analyze the script.
4. Review scores and actionable feedback.
5. Ask the assistant for personalized guidance.
6. Track improvement over multiple practice sessions.

**Technology**
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- Requests
- Python-dotenv
- Matplotlib
""")
