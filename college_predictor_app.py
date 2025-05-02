import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Concept Simplified: College Dashboard",
    layout='wide',
    initial_sidebar_state='expanded'
)

# --- Data Loading ---
@st.cache_data
def load_weights(path: str) -> pd.DataFrame:
    df = pd.read_excel(
        path,
        sheet_name="College Finder",
        header=None,
        skiprows=7,
        nrows=16,
        usecols="A:G"
    )
    df.columns = [
        "Country",
        "Grades (Academics)",
        "Personal Statement/Essay",
        "Letters of Recommendation (LORs)",
        "Extracurricular Activities",
        "Interview",
        "Total"
    ]
    df = df[df['Country'].notna() & (df['Country'] != 'Country')]
    return df.set_index('Country')

@st.cache_data
def load_universities(path: str) -> pd.DataFrame:
    df = pd.read_excel(
        path,
        sheet_name="College Finder",
        header=None,
        skiprows=25,
        usecols="A:D"
    )
    df.columns = ["Country","University","QS World Rank","Required Profile Score"]
    df = df.dropna(subset=["University"])
    df["QS World Rank"] = pd.to_numeric(df["QS World Rank"], errors='coerce')
    df["Required Profile Score"] = pd.to_numeric(df["Required Profile Score"], errors='coerce')
    return df.reset_index(drop=True)

# --- Load data ---
data_path   = "College Finder UG.xlsx"
weights_df  = load_weights(data_path)
unis_df     = load_universities(data_path)
all_df      = unis_df.merge(weights_df, left_on='Country', right_index=True, how='left')
country_list = weights_df.index.tolist()

# --- Fit Score Computation ---
def compute_fit_scores(df: pd.DataFrame, profile: dict) -> pd.DataFrame:
    records = []
    for _, r in df.iterrows():
        fit = sum(profile[k] * r.get(k, 0) for k in profile)
        records.append({
            'Country': r['Country'],
            'University': r['University'],
            'QS World Rank': r['QS World Rank'],
            'Required Profile Score': r['Required Profile Score'],
            'Your Fit Score (%)': round(fit * 100, 2),
            'Diff (%)': round(fit * 100 - r['Required Profile Score'], 2)
        })
    return pd.DataFrame(records)

# --- App UI ---
st.title("🎓 Concept Simplified: College Dashboard")
mode = st.sidebar.radio("Navigation", ["College Finder", "Top Universities"])

if mode == "Top Universities":
    st.header("📊 Top Universities & Admission Weights")
    opts = ["All"] + country_list
    selected = st.multiselect("Filter by country:", opts, default=["All"])
    pct_df = (weights_df * 100).round().astype(int).astype(str) + "%"

    if "All" in selected:
        st.subheader("Admission Weightage by Country")
        st.dataframe(pct_df, use_container_width=True)
        st.subheader("All Universities (QS & Required Score)")
        st.dataframe(all_df.sort_values('QS World Rank'), use_container_width=True)
    else:
        st.subheader("Weightage for Selected Countries")
        st.dataframe(pct_df.loc[selected], use_container_width=True)
        st.subheader("Universities in Selected Countries")
        sub = all_df[all_df.Country.isin(selected)]
        st.dataframe(sub.sort_values('QS World Rank'), use_container_width=True)

else:
    st.header("🔍 College Finder – Personalized Match")

    # Academic Profile
    st.subheader("Academic Profile")
    c10 = st.number_input("Class 10 Percentage [%]", 0.0, 100.0)
    c12 = st.number_input("Class 12 Percentage [%]", 0.0, 100.0)
    sat = st.number_input("SAT/ACT Score (out of 1600)", 0, 1600)

    # Subject Tests / AP Exams
    st.subheader("Subject Tests / AP Exams")
    took = st.selectbox("Attempted any Subject Tests/AP exams?", ["No", "Yes"])
    apt_scores = []
    if took == "Yes":
        count = st.slider("Number of tests taken (max 3)", 1, 3, 1)
        for i in range(count):
            apt_scores.append(
                st.number_input(f"Test {i+1} Score [%]", 0.0, 100.0, key=f"apt{i}")
            )
    avg_apt = sum(apt_scores) / len(apt_scores) if apt_scores else 0.0

    # Activities & Experience
    st.subheader("Activities & Experience")
    eca_cnt      = st.number_input("Extracurricular Activities (0–3)", 0, 3)
    cc_cnt       = st.number_input("Co-curricular Activities (0–3)", 0, 3)
    intern_cnt   = st.number_input("Internships completed (0–2)", 0, 2)
    service_done = st.checkbox("Completed Community Service?")
    research_done= st.checkbox("Completed Research Project?")

    # Country Preference for Weighting
    st.subheader("Country Preference for Weighting")
    pref = st.multiselect("Select countries for weighting:", ["All"] + country_list, default=["All"])

    if st.button("🔍 Find My Colleges"):
        # Calculate component scores
        acad = 0.65 * ((c10 + c12) / 2 / 100) + 0.25 * (sat / 1600) + 0.10 * (avg_apt / 100)
        eca  = eca_cnt / 3
        cc   = cc_cnt / 3
        intv = intern_cnt / 2
        cs   = 1.0 if service_done  else 0.0
        rs   = 1.0 if research_done else 0.0
        ps   = 0.10 * eca + 0.20 * cc + 0.25 * intv + 0.20 * cs + 0.25 * rs
        lor  = 0.5 * acad + 0.5 * ps
        iv   = (eca + cc + intv + cs + rs) / 5

        profile = {
            'Grades (Academics)': acad,
            'Personal Statement/Essay': ps,
            'Letters of Recommendation (LORs)': lor,
            'Extracurricular Activities': eca,
            'Interview': iv
        }

        # Tooltips for each component
        tips = {
            'Grades (Academics)': '65% boards + 25% SAT + 10% aptitude tests',
            'Personal Statement/Essay': 'ECA, co-curricular, internships, service, research split',
            'Letters of Recommendation (LORs)': '50% academics + 50% personal statement',
            'Extracurricular Activities': 'Max 3 activities normalized',
            'Interview': 'Based on your activities & research experiences'
        }

        # Display Profile Scores with ℹ️ tooltips (icon at end)
        profile_rows = [
            f"<tr>" +
            f"<td style='text-align:left;'>{k} <span title='{tips[k]}' style='cursor:help;'>ℹ️</span></td>" +
            f"<td>{round(v*100,2)}%</td>" +
            f"</tr>"
            for k, v in profile.items()
        ]
        profile_table = (
            "<table style='width:60%;border-collapse:collapse;'>" +
            "<tr><th>Component</th><th>Your Score</th></tr>" +
            "".join(profile_rows) +
            "</table>"
        )
        st.subheader("📝 Your Profile Scores")
        st.markdown(profile_table, unsafe_allow_html=True)

        # Subset and compute university results
        df = all_df if 'All' in pref else all_df[all_df.Country.isin(pref)]
        df_res = compute_fit_scores(df, profile)

        # Sort by Diff ascending and split into tiers
        sorted_df = df_res.sort_values('Diff (%)')
        amb = sorted_df.iloc[:6]
        tgt = sorted_df.iloc[6:12]
        saf = sorted_df.iloc[12:18]

        # Display tiers
        for title, block, color in [
            ('🎯 Ambitious Universities', amb, '#E74C3C'),
            ('🏹 Target Universities',    tgt, '#E67E22'),
            ('🛡️ Safe Universities',      saf, '#27AE60')
        ]:
            st.subheader(title)
            for i in range(0, len(block), 3):
                cols = st.columns(3)
                for col, (_, u) in zip(cols, block.iloc[i:i+3].iterrows()):
                    col.markdown(
                        f"""
                        <div style='border:1px solid #ddd; padding:1rem; border-radius:8px;'>
                          <strong>{u['University']}</strong><br>
                          {u['Country']} (QS {u['QS World Rank']})<br>
                          Req: {u['Required Profile Score']}%<br>
                          You: {u['Your Fit Score (%)']}%
                        </div>
                        """, unsafe_allow_html=True
                    )
        st.info("Use sidebar to switch views or rerun.")
