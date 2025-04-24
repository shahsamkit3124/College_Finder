import streamlit as st
import pandas as pd

# -------------------------
# Global CSS for modern look
# -------------------------
st.markdown("""
<style>
/* Center content and give some breathing room */
.css-18ni7ap {padding:2rem;}
  
/* Survey step box */
.step-box {
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

/* Big button styles */
.stButton>button {
  background-color: #ff4b4b;
  color: white;
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  font-size: 1rem;
}
.stButton>button:hover {
  background-color: #e84343;
}

/* Card styles */
.card-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin: 2rem 0;
}
.card {
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  width: 240px;
  transition: transform 0.3s ease;
}
.card:hover {
  transform: translateY(-8px);
}
.card-header {
  background: linear-gradient(135deg, #6e8efb, #a777e3);
  border-radius: 10px 10px 0 0;
  padding: 0.75rem;
  color: #fff;
  font-weight: bold;
  text-align: center;
}
.card-body {
  padding: 1rem;
  text-align: center;
}
.card-body p {
  margin: 0.5rem 0;
  color: #333;
}
.card-body .score {
  font-size: 1.3rem;
  font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Helper functions
# -------------------------
def safe_float(val):
    try: return float(val)
    except: return 0.0

def build_profile(state):
    return {
        'Grades (Academics)':             state.grades_pct       / 100.0,
        'Standardized Tests (SAT/ACT)':   state.sat_score        / 1600.0,
        'Personal Statement/Essay':       state.essay_rating     /   5.0,
        'Letters of Recommendation (LORs)': 
            (min(state.lor_count,3)/3.0) if state.lor_yes_no=="Yes" else 0.0,
        'Extracurricular Activities': 
            (min(state.eca_count,5)/5.0) if state.eca_yes_no=="Yes" else 0.0,
        'Interview':                      state.interview_rating /   5.0,
        'Subject Tests/APs':              state.aptitude_rating  /  10.0,
    }

def compute_fit_scores(df, profile):
    meta = {'QS Rank','University Name','Country','SUM'}
    crit = [c for c in df.columns if c not in meta]
    rows = []
    for _,r in df.iterrows():
        ws = tw = 0.0
        for col,val in profile.items():
            w = safe_float(r.get(col))
            if w > 0:
                ws += val * w
                tw += w
        fit = ws/tw if tw > 0 else 0.0
        rows.append({
            'QS Rank':       safe_float(r['QS Rank']),
            'University':    r['University Name'],
            'Country':       r['Country'],
            'Fit Score (%)': round(fit*100,2)
        })
    return (
        pd.DataFrame(rows)
          .sort_values(['Fit Score (%)','QS Rank'], ascending=[False,True])
          .reset_index(drop=True)
    )

# -------------------------
# Load data once
# -------------------------
@st.cache_data
def load_universities():
    return pd.read_excel("College Finder UG.xlsx", sheet_name="College Finder")
df = load_universities()

# -------------------------
# Multi-view logic
# -------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'survey'

# Survey page
if st.session_state.page == 'survey':
    st.title("🎓 College Predictor – UG Admissions")
    st.markdown("Answer each question to see your top 18 fit–universities.")

    # init session state defaults
    for k, default in {
        'step':1,
        'grades_pct':0.0, 'sat_score':0,
        'essay_rating':1,
        'lor_yes_no':"No",'lor_count':0,
        'eca_yes_no':"No",'eca_count':0,
        'interview_rating':1,'aptitude_rating':1,'english_test':"No"
    }.items():
        if k not in st.session_state:
            st.session_state[k] = default

    def nxt(): st.session_state.step += 1
    def prv(): st.session_state.step -= 1

    step = st.session_state.step
    st.markdown(f"<div class='step-box'><strong>Step {step}/9</strong></div>", unsafe_allow_html=True)

    # One-by-one questions
    if step == 1:
        st.session_state.grades_pct = st.number_input(
            "📊 Grades (Avg of 10th & 12th) [%]", 0.0, 100.0, st.session_state.grades_pct)
    elif step == 2:
        st.session_state.sat_score = st.number_input(
            "📈 SAT/ACT Score (out of 1600)", 0, 1600, st.session_state.sat_score)
    elif step == 3:
        st.session_state.essay_rating = st.slider(
            "✍️ Essay Efficiency (1–5)", 1, 5, st.session_state.essay_rating)
    elif step == 4:
        st.session_state.lor_yes_no = st.selectbox(
            "🖋️ Do you have Letters of Recommendation?", ["No","Yes"],
            index=["No","Yes"].index(st.session_state.lor_yes_no))
        if st.session_state.lor_yes_no == "Yes":
            st.session_state.lor_count = st.number_input(
                "↳ How many LORs? (max 3)", 0, 3, st.session_state.lor_count)
    elif step == 5:
        st.session_state.eca_yes_no = st.selectbox(
            "🏅 Do you have Extracurricular Activities?", ["No","Yes"],
            index=["No","Yes"].index(st.session_state.eca_yes_no))
        if st.session_state.eca_yes_no == "Yes":
            st.session_state.eca_count = st.number_input(
                "↳ How many activities? (max 5)", 0, 5, st.session_state.eca_count)
    elif step == 6:
        st.session_state.interview_rating = st.slider(
            "🤝 Interview Skill (1–5)", 1, 5, st.session_state.interview_rating)
    elif step == 7:
        st.session_state.aptitude_rating = st.slider(
            "🧠 Aptitude / Subject Tests (1–10)", 1, 10, st.session_state.aptitude_rating)
    elif step == 8:
        st.session_state.english_test = st.selectbox(
            "📚 Have you taken IELTS/TOEFL?", ["No","Yes"],
            index=["No","Yes"].index(st.session_state.english_test))
    else:  # step == 9: review
        st.markdown("**Review your answers:**")
        st.write(f"- Grades: {st.session_state.grades_pct}%")
        st.write(f"- SAT/ACT: {st.session_state.sat_score}/1600")
        st.write(f"- Essay Efficiency: {st.session_state.essay_rating}/5")
        st.write(f"- LORs: {st.session_state.lor_yes_no} ({st.session_state.lor_count})")
        st.write(f"- Activities: {st.session_state.eca_yes_no} ({st.session_state.eca_count})")
        st.write(f"- Interview: {st.session_state.interview_rating}/5")
        st.write(f"- Aptitude: {st.session_state.aptitude_rating}/10")
        st.write(f"- IELTS/TOEFL: {st.session_state.english_test}")

    # Navigation
    cols = st.columns([1,2,1])
    with cols[0]:
        if step > 1:
            st.button("⬅️ Previous", on_click=prv)
    with cols[2]:
        if step < 9:
            st.button("Next ➡️", on_click=nxt)
        else:
            if st.session_state.english_test == "No":
                st.error("⚠️ IELTS/TOEFL is mandatory.")
            else:
                if st.button("🔍 Find My Colleges"):
                    st.session_state.profile = build_profile(st.session_state)
                    st.session_state.page = 'results'

# Results page
else:
    st.title("🏆 Your Top-18 College Matches")

    profile = st.session_state.profile
    results18 = compute_fit_scores(df, profile).head(18)

    categories = [
        ("🎯 Ambitious Universities", results18.iloc[:6],  "#E74C3C"),
        ("🏹 Target Universities",    results18.iloc[6:12],"#E67E22"),
        ("🛡️ Safe Universities",      results18.iloc[12:18],"#27AE60"),
    ]

    for header, group, color in categories:
        st.markdown(f"## {header}")
        for i in range(0, 6, 3):
            cols = st.columns(3, gap="large")
            for col, (_, uni) in zip(cols, group.iloc[i:i+3].iterrows()):
                col.markdown(f"""
                  <div class='card'>
                    <div class='card-header'>{uni['University']}</div>
                    <div class='card-body'>
                      <p>{uni['Country']}</p>
                      <p class='score' style='color:{color};'>{uni['Fit Score (%)']}%</p>
                    </div>
                  </div>
                """, unsafe_allow_html=True)

    st.button("🔄 Back to Survey", on_click=lambda: st.session_state.update(page='survey'))
