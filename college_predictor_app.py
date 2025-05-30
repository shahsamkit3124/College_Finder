import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────
# Page config MUST be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(page_title="YOCKET STUDY ABROAD | Study‑Abroad University Finder",
                   layout="wide", page_icon="🎓")

# ─────────────────────────────────────────────
# Hide Streamlit hamburger & footer
# ─────────────────────────────────────────────
hide_menu_style = """
    <style>
        #MainMenu, footer {visibility:hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Base styles & hero banner
# ─────────────────────────────────────────────
st.markdown("""
<style>
body{background:#f5f6f7;color:#212121;font-family:"Segoe UI",sans-serif;}

.hero-title{font-size:2.4rem;font-weight:800;color:#D32F2F;margin:0;}
.hero-sub {font-size:1.4rem;font-weight:600;margin-top:.3rem;}
.hero-divider{height:2px;background:#D32F2F;margin:1.6rem 0 2.4rem;}

.card{background:#fff;border-radius:14px;max-width:900px;margin:0 auto;
      padding:2.1rem 2.6rem;box-shadow:0 4px 16px rgba(0,0,0,.06);color:#000;}
.card h3{font-size:1.65rem;margin-bottom:.9rem;color:#000;}

.step{display:flex;margin:.65rem 0;}
.step-num{min-width:30px;height:30px;border-radius:50%;background:#e0e0e0;
          color:#000;font-weight:700;font-size:.85rem;
          display:flex;align-items:center;justify-content:center;margin-right:.6rem;}
.step-text{line-height:1.45rem;color:#000;}

@media(max-width:480px){
  .card{padding:1.5rem 1.2rem;}
  .hero-title{font-size:2rem;}
  .hero-sub{font-size:1.2rem;}
  label{font-size:.9rem;}
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center">
  <div class="hero-title">YOCKET STUDY ABROAD 🎓</div>
  <div class="hero-sub">Study‑Abroad University Finder 2025</div>
</div>
<div class="hero-divider"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Instruction card
# ─────────────────────────────────────────────
st.markdown("""
<div class="card">
  <h3>How to use this Finder</h3>
  <div class="step"><div class="step-num">1</div><div class="step-text">
        Choose one or more <strong>Countries</strong> (or <em>All</em>).</div></div>
  <div class="step"><div class="step-num">2</div><div class="step-text">
        Enter your <strong>Academic Percentages</strong> (Class 9‑12) and <strong>SAT/ACT</strong> score.</div></div>
  <div class="step"><div class="step-num">3</div><div class="step-text">
        Add <strong>AP test</strong> scores if any.</div></div>
  <div class="step"><div class="step-num">4</div><div class="step-text">
        Specify numbers of <strong>Co‑/Extra‑curriculars</strong>, <strong>Internships</strong>, and check extra boxes.</div></div>
  <div class="step"><div class="step-num">5</div><div class="step-text">
        Indicate <strong>Letters of Recommendation</strong> count.</div></div>
  <div class="step"><div class="step-num">6</div><div class="step-text">
        Click <strong>Find My Universities</strong> to see a gap analysis and personalised Ambitious‑Target‑Safe lists.</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("### &nbsp;")  # spacer

# ─────────────────────────────────────────────
# 1) Load & clean Excel (both sheets)
# ─────────────────────────────────────────────
EXCEL_PATH = "College Finder UG New.xlsx"
profile_df = pd.read_excel(EXCEL_PATH, sheet_name="College_Finder")
uni_df     = pd.read_excel(EXCEL_PATH, sheet_name="University")

profile_df["Country"] = profile_df["Country"].astype(str).str.strip()
profile_df = profile_df[profile_df["Country"].str.lower() != "nan"]
profile_df.rename(columns={
    "CC (Max 3)":         "CC",
    "EC (Max 3)":         "EC",
    "Internship (Max 2)": "Internship"
}, inplace=True)

# Force numeric for profile weights
keys = ["Class 9","Class 10","Class 11","Class 12","SAT","AP",
        "CC","EC","Internship","Community","Research","LOR"]
profile_df[keys] = profile_df[keys].apply(pd.to_numeric, errors="coerce").fillna(0)

# Clean university sheet numeric cols
uni_df.rename(columns=str.strip, inplace=True)
uni_df["Required Profile Score"] = pd.to_numeric(uni_df["Required Profile Score"], errors="coerce")

# ─────────────────────────────────────────────
# 3) Country selector
# ─────────────────────────────────────────────
countries = sorted(profile_df["Country"].unique())
sel = st.multiselect("🌐 Choose Countries", ["All"]+countries, default=["All"])
filtered_profile = profile_df if "All" in sel else profile_df[profile_df["Country"].isin(sel)]

# ─────────────────────────────────────────────
# 4) User inputs – left = academics | right = activities
# ─────────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.header("📘 Academic")
    class9  = st.number_input("Class 9 % (0–100)", 0,100)/100
    class10 = st.number_input("Class 10 % (0–100)",0,100)/100
    class11 = st.number_input("Class 11 % (0–100)",0,100)/100
    class12 = st.number_input("Class 12 % (0–100)",0,100)/100
    sat     = st.number_input("SAT/ACT (400–1600)",400,1600)/1600

    st.subheader("📘 AP Tests")
    num_ap    = st.number_input("APs (0–5)",0,5,step=1)
    ap_scores = [st.number_input(f"AP{i+1} (0–5)",0,5,step=1) for i in range(int(num_ap))]
    avg_ap    = sum(ap_scores)/(num_ap*5) if num_ap>0 else 0.0

with right:
    st.header("🏅 Activities & Extras")
    cc_cnt     = st.number_input("Co‑curricular (0–3)",0,3,step=1)
    ec_cnt     = st.number_input("Extra‑curricular (0–3)",0,3,step=1)
    intern_cnt = st.number_input("Internships (0–2)",0,2,step=1)
    community  = 1.0 if st.checkbox("Community Service") else 0.0
    research   = 1.0 if st.checkbox("Research Project") else 0.0

    st.header("📄 LORs")
    num_lor    = st.number_input("LORs (0–3)",0,3,step=1)
    lor_frac   = num_lor/3

# Build user_profile
auth_profile = {
    "Class 9":    class9,
    "Class 10":   class10,
    "Class 11":   class11,
    "Class 12":   class12,
    "SAT":        sat,
    "AP":         avg_ap,
    "CC":         cc_cnt/3,
    "EC":         ec_cnt/3,
    "Internship": intern_cnt/2,
    "Community":  community,
    "Research":   research,
    "LOR":        lor_frac
}

# ─────────────────────────────────────────────
# 5) Breakdown & University matching
# ─────────────────────────────────────────────
if st.button("🔍 Find My Universities"):
    acad_keys     = ["Class 9","Class 10","Class 11","Class 12","SAT","AP"]
    activity_keys = ["CC","EC","Internship","Community","Research"]

    def breakdown(row):
        raw_acad   = sum(auth_profile[k]*row[k] for k in acad_keys)
        raw_act    = sum(auth_profile[k]*row[k] for k in activity_keys)
        raw_lor    = auth_profile["LOR"] * row["LOR"]
        total_raw  = raw_acad + raw_act + raw_lor
        max_acad   = sum(row[k] for k in acad_keys)
        max_act    = sum(row[k] for k in activity_keys)
        max_lor    = row["LOR"]
        acad_pct = (raw_acad/max_acad*100) if max_acad>0 else 0
        act_pct  = (raw_act/ max_act *100) if max_act >0 else 0
        lor_pct  = (raw_lor/ max_lor *100) if max_lor>0 else 0
        return pd.Series({
            "Academic %":      round(acad_pct,1),
            "Activity %":      round(act_pct,1),
            "LOR %":           round(lor_pct,1),
            "Total Profile %": round(total_raw*100,1)
        })

    country_scores = filtered_profile.apply(breakdown, axis=1)
    country_scores.insert(0, "Country", filtered_profile["Country"].values)

    st.subheader("🌎 Country‑wise Profile Breakdown")
    st.dataframe(country_scores.sort_values("Total Profile %", ascending=False).reset_index(drop=True), use_container_width=True)

    # ---------- University matching ----------
    score_map = dict(zip(country_scores["Country"], country_scores["Total Profile %"]))
    uni_df_filtered = uni_df.copy()
    uni_df_filtered["Your Profile %"] = uni_df_filtered["Country"].map(score_map)
    uni_df_filtered = uni_df_filtered[uni_df_filtered["Your Profile %"].notna()]

    if uni_df_filtered.empty:
        st.warning("No universities available for the selected countries.")
        st.stop()

    uni_df_filtered["Gap %"] = (uni_df_filtered["Required Profile Score"] - uni_df_filtered["Your Profile %"]).round(1)

    # Full gap analysis table
    gap_view = uni_df_filtered[[
        "Country","University","QS Ranking","Required Profile Score","Your Profile %","Gap %"
    ]].sort_values("Gap %", ascending=False).reset_index(drop=True)

    st.subheader("🗺️ University Gap Analysis (positive gap = profile below requirement)")
    st.dataframe(gap_view, use_container_width=True)

    # ---------- Ambitious / Target / Safe lists ----------
    # Determine the university A (least positive gap > 0)
    pos_mask = gap_view["Gap %"] > 0
    if pos_mask.any():
        A_gap = gap_view[pos_mask]["Gap %"].min()
        A_idx = gap_view[(gap_view["Gap %"] == A_gap) & pos_mask].index[0]
    else:
        # No positive gaps – take the first zero / smallest absolute gap as A
        A_idx = gap_view["Gap %"].abs().idxmin()
        A_gap = gap_view.loc[A_idx, "Gap %"]

    # Build category slices (ensure bounds)
    ambitious_start = max(0, A_idx - 12)
    ambitious_list = gap_view.iloc[ambitious_start:A_idx]

    target_end = A_idx - 6  # includes A + 5 below
    target_list = gap_view.iloc[A_idx:target_end]

    safe_end = target_end + 6
    safe_list = gap_view.iloc[target_end:safe_end]

    # Tabs UI
    tabs = st.tabs(["🚀 Ambitious", "🎯 Target", "🛡️ Safe"])
    with tabs[0]:
        st.markdown("#### Universities that will stretch your profile")
        st.dataframe(ambitious_list.reset_index(drop=True), use_container_width=True)
    with tabs[1]:
        st.markdown("#### Best‑fit options (Target)")
        st.dataframe(target_list.reset_index(drop=True), use_container_width=True)
    with tabs[2]:
        st.markdown("#### Safer admits consistent with your profile")
        st.dataframe(safe_list.reset_index(drop=True), use_container_width=True)
else:
    st.info("Enter your profile details and click the button to see personalised recommendations.")

