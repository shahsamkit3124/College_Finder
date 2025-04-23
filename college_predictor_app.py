import streamlit as st
import pandas as pd

# -------------------------
# Helper functions
# -------------------------
def safe_float(val):
    """
    Try to convert val to float; return 0.0 on failure.
    """
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def build_profile(
    grades_pct: float,
    sat_score: float,
    essay_rating: int,
    lor_count: int,
    eca_count: int,
    interview_rating: int,
    aptitude_rating: int
) -> dict:
    """
    Normalize student inputs to a 0–1 scale.
    """
    return {
        'Grades (Academics)':            grades_pct / 100.0,
        'Standardized Tests (SAT/ACT)':  sat_score  / 1600.0,
        'Personal Statement/Essay':      essay_rating    / 10.0,
        'Letters of Recommendation (LORs)': min(lor_count, 5)  / 5.0,
        'Extracurricular Activities':    min(eca_count, 10)  / 10.0,
        'Interview':                     interview_rating  / 10.0,
        'Subject Tests/APs':             aptitude_rating   / 10.0,
    }

def compute_fit_scores(df: pd.DataFrame, profile: dict) -> pd.DataFrame:
    """
    For each university in df, compute a weighted average of the student's
    normalized inputs, using the university-specific weights.
    Tie‑break by QS Rank (lower is better).
    """
    metadata_cols = {'QS Rank', 'University Name', 'Country', 'SUM'}
    criteria_cols = [c for c in df.columns if c not in metadata_cols]

    results = []
    for _, row in df.iterrows():
        weighted_sum = 0.0
        total_weight = 0.0

        for col, input_score in profile.items():
            weight = safe_float(row.get(col))
            if weight > 0:
                weighted_sum += input_score * weight
                total_weight += weight

        fit_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0

        results.append({
            'QS Rank':        safe_float(row['QS Rank']),
            'University':     row['University Name'],
            'Country':        row['Country'],
            'Fit Score (%)':  round(fit_score * 100, 2)
        })

    # Sort by Fit Score desc, then QS Rank asc
    return (
        pd.DataFrame(results)
          .sort_values(
              by=['Fit Score (%)', 'QS Rank'],
              ascending=[False, True]
          )
          .reset_index(drop=True)
    )

# -------------------------
# Streamlit App
# -------------------------
st.set_page_config(page_title="College Predictor", layout="wide")
st.title("🎓 College Predictor - UG Admissions")
st.markdown("Fill in your profile details below to see your best-fit universities.")

@st.cache_data
def load_university_data():
    return pd.read_excel("College Finder UG.xlsx", sheet_name="College Finder")

df = load_university_data()

with st.form("profile_form"):
    grades_pct       = st.number_input("Grades (Average of Class 10 & 12) [%]", 0.0, 100.0, 85.0)
    sat_score        = st.number_input("SAT/ACT Score (out of 1600)", 0, 1600, 1300)
    essay_rating     = st.slider("Personal Statement/Essay (1–10)", 1, 10, 7)
    lor_yes_no       = st.selectbox("Do you have Letters of Recommendation?", ["No", "Yes"])
    lor_count        = st.number_input("If Yes, how many LORs? (max 5)", 0, 5, 2) if lor_yes_no == "Yes" else 0
    eca_yes_no       = st.selectbox("Do you have Extracurricular Activities?", ["No", "Yes"])
    eca_count        = st.number_input("If Yes, how many activities? (max 10)", 0, 10, 3) if eca_yes_no == "Yes" else 0
    interview_rating = st.slider("Interview Rating (1–10)", 1, 10, 7)
    aptitude_rating  = st.slider("Subject Tests/APs / Aptitude (1–10)", 1, 10, 8)
    english_test     = st.selectbox("Have you taken IELTS/TOEFL?", ["No", "Yes"])
    submit_btn       = st.form_submit_button("🔍 Find My Colleges")

if submit_btn:
    if english_test == "No":
        st.error("English Proficiency Test (IELTS/TOEFL) is mandatory.")
    else:
        profile    = build_profile(
            grades_pct, sat_score, essay_rating,
            lor_count, eca_count, interview_rating, aptitude_rating
        )
        results_df = compute_fit_scores(df, profile)

        st.success("✅ Here are your best-fit universities:")
        st.dataframe(results_df[['University', 'Country', 'Fit Score (%)']], use_container_width=True)

        st.markdown("### 📈 Top 5 Universities")
        st.bar_chart(results_df.head(5).set_index("University")["Fit Score (%)"])
