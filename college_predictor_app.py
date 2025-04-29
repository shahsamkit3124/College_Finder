import streamlit as st
import pandas as pd

# --- Page Configuration: MUST be first Streamlit command ---
st.set_page_config(
    page_title="Concept Simplified: College Dashboard",
    layout='wide',
    initial_sidebar_state='expanded'
)

# --- Data Loading ---
@st.cache_data
def load_weights(path: str) -> pd.DataFrame:
    """
    Reads the country-specific admission weight table (rows 8–23, cols A–G).
    """
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
    """
    Reads the university list (rows 26+, cols A–C).
    """
    df = pd.read_excel(
        path,
        sheet_name="College Finder",
        header=None,
        skiprows=25,
        usecols="A:C"
    )
    df.columns = ["Country", "University", "QS World Rank"]
    df = df.dropna(subset=["University"])
    df["QS World Rank"] = pd.to_numeric(df["QS World Rank"], errors='coerce')
    return df.reset_index(drop=True)

# --- Load data ---
DATA_PATH = "College Finder UG.xlsx"
weights_df = load_weights(DATA_PATH)
unis_df     = load_universities(DATA_PATH)
all_df      = unis_df.merge(
    weights_df,
    left_on='Country',
    right_index=True,
    how='left'
)
country_list = weights_df.index.tolist()

# --- Fit Score Computation ---
def compute_fit_scores(df: pd.DataFrame, profile: dict) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        score = sum(profile[k] * r.get(k, 0) for k in profile)
        rows.append({
            'QS World Rank': r['QS World Rank'],
            'University':    r['University'],
            'Country':       r['Country'],
            'Fit Score (%)': round(score * 100, 2)
        })
    out = pd.DataFrame(rows)
    return out.sort_values(['Fit Score (%)','QS World Rank'], ascending=[False,True]).reset_index(drop=True)

# --- App UI ---
st.title("🎓 Concept Simplified: College Dashboard")
mode = st.sidebar.radio("Navigation", ["College Finder", "Top Universities"])

if mode == "Top Universities":
    st.header("📊 Top Universities & Admission Weights")
    # allow multiple with All option
    options = ["All"] + country_list
    selected_countries = st.multiselect(
        "Filter by country (multiple):", options, default=["All"]
    )
    pct_df = (weights_df * 100).round(0).astype(int).astype(str) + "%"

    # interpret selection
    if "All" in selected_countries or set(selected_countries) == set(country_list):
        st.subheader("Admission Weightage by Country")
        st.dataframe(pct_df, use_container_width=True)
        st.subheader("All QS Top Universities")
        st.dataframe(unis_df.sort_values("QS World Rank"), use_container_width=True)
    else:
        st.subheader("Admission Weightage for Selected Countries")
        st.dataframe(pct_df.loc[selected_countries], use_container_width=True)
        st.subheader("Top Universities in Selected Countries")
        sub = unis_df[unis_df.Country.isin(selected_countries)]
        st.dataframe(sub.sort_values("QS World Rank"), use_container_width=True)

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
        count = st.number_input("How many tests taken? (max 3)", 1, 3, 1)
        for i in range(count):
            val = st.number_input(f"Score for Test {i+1} [%]", 0.0, 100.0, key=f"apt{i}")
            apt_scores.append(val)
    avg_apt = sum(apt_scores) / len(apt_scores) if apt_scores else 0.0

    # Activities & Experience
    st.subheader("Activities & Experience")
    eca    = st.number_input("Extracurricular Activities (0–3)", 0, 3)
    cc     = st.number_input("Co-curricular Activities (0–3)", 0, 3)
    intern = st.checkbox("Completed an internship?")
    serv   = st.checkbox("Done community service?")
    res    = st.checkbox("Carried out research?")

    # Country Preference for Weighting
    st.subheader("Country Preference for Weighting")
    pref_options = ["All"] + country_list
    pref_countries = st.multiselect(
        "Select one or more countries for weighting:", pref_options, default=["All"]
    )

    if st.button("🔍 Find My Colleges"):
        acad = 0.65 * ((c10 + c12) / 2 / 100) + 0.25 * (sat / 1600) + 0.10 * (avg_apt / 100)
        eca_s = eca / 3
        cc_s  = cc  / 3
        int_s = 1.0 if intern else 0.0
        cs_s  = 1.0 if serv   else 0.0
        r_s   = 1.0 if res    else 0.0
        ps    = 0.10*eca_s + 0.20*cc_s + 0.25*int_s + 0.20*cs_s + 0.25*r_s
        lor   = 0.5*acad + 0.5*ps
        iv    = (eca_s + cc_s + int_s + cs_s + r_s) / 5
        profile = {
            "Grades (Academics)": acad,
            "Personal Statement/Essay": ps,
            "Letters of Recommendation (LORs)": lor,
            "Extracurricular Activities": eca_s,
            "Interview": iv
        }

        # determine df subset
        if "All" in pref_countries or set(pref_countries) == set(country_list):
            df = all_df
        else:
            df = all_df[all_df.Country.isin(pref_countries)]

        results = compute_fit_scores(df, profile)
        top18   = results.head(18)

        tiers = [
            ("🎯 Ambitious Universities", top18.iloc[:6],   "#E74C3C"),
            ("🏹 Target Universities",    top18.iloc[6:12], "#E67E22"),
            ("🛡️ Safe Universities",      top18.iloc[12:18],"#27AE60")
        ]
        for title, block, color in tiers:
            st.subheader(title)
            for i in range(0, len(block), 3):
                cols = st.columns(3)
                for col, (_, uni) in zip(cols, block.iloc[i:i+3].iterrows()):
                    col.markdown(f"""
                        <div style='border:1px solid #ddd; border-radius:8px; padding:1rem;'>
                          <strong>{uni['University']}</strong><br>
                          {uni['Country']}<br>
                          <span style='color:{color}; font-size:1.2em;'>{uni['Fit Score (%)']}%</span>
                        </div>
                    """, unsafe_allow_html=True)
        st.info("Use the sidebar to switch views or run again.")
