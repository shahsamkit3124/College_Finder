import streamlit as st
import pandas as pd

# ═══════════════════════════════════════════════════════
# 1 ▸  Page config
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="CONCEPT SIMPLIFIED | JEE College Predictor",
    layout="wide",
    page_icon="🎓",
)

# ═══════════════════════════════════════════════════════
# 2 ▸  Global CSS  (adaptive colours)
# ═══════════════════════════════════════════════════════
st.markdown(
    """
    <style>
    /* ---------- colour palette ---------- */
    :root{
        --brand-red:   #D32F2F;
        --blue-text:   #13326B;  /* corporate deep-blue */
        --bg-light:    #F6F7FA;
        --bg-dark:     #0D1526;
        --text-dark:   var(--blue-text);
        --text-light:  #EAF0FF;
    }
    @media (prefers-color-scheme: dark){
        :root{
            --page-bg:   var(--bg-dark);
            --text-col:  var(--text-light);
            --badge-bg:  transparent;
            --badge-brd: #EAF0FF;
        }
    }
    @media (prefers-color-scheme: light){
        :root{
            --page-bg:   var(--bg-light);
            --text-col:  var(--text-dark);
            --badge-bg:  transparent;
            --badge-brd: var(--blue-text);
        }
    }

    html, body, div, section { color:var(--text-col); }
    body{ background:var(--page-bg); }

    #MainMenu{visibility:hidden;} footer, header{visibility:hidden;}

    /* hero */
    .hero-title{font:800 2.4rem/1 var(--brand-red); margin:0;}
    .hero-sub  {font:600 1.35rem/1.2 var(--text-col); margin:.25rem 0 .8rem;}

    .divider{height:2px;background:var(--brand-red);margin:1.6rem 0 2.3rem;}

    /* card */
    .card{
        background:#ffffff; border-radius:14px;
        max-width:880px; margin:0 auto; padding:2.1rem 2.5rem;
        box-shadow:0 4px 16px rgba(0,0,0,.07); color:var(--blue-text);
    }
    .card h3{font-size:1.68rem;margin-bottom:.9rem;color:var(--blue-text);}

    /* steps */
    .step{display:flex;margin:.65rem 0;}
    .badge{
        min-width:30px;height:30px;border-radius:50%;
        background:var(--badge-bg); border:2px solid var(--badge-brd);
        color:var(--badge-brd); font-weight:700;
        display:flex;align-items:center;justify-content:center;
        font-size:.85rem;margin-right:.6rem;
    }
    .step-text{line-height:1.4rem;}

    /* Streamlit widget backgrounds */
    .stSelectbox>div>div, .stTextInput>div>input{
        background:#ffffff; color:var(--blue-text);
    }

    /* primary button (Submit) */
    .stButton>button{
        background:var(--brand-red); color:#fff; font-weight:600;
        border:none; border-radius:10px; padding:.6rem 1.4rem;font-size:1.05rem;
    }
    .stButton>button:hover{background:#b71c1c;}

    /* table */
    .cs-table { color:var(--text-col); font-size:.88rem; }
    .cs-table th{background:#ECEFF4;color:var(--blue-text);}

    /* mobile tweaks */
    @media(max-width:480px){
        .hero-title{font-size:2.1rem;}
        .hero-sub  {font-size:1.15rem;}
        .card{padding:1.6rem 1.45rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════
# 3 ▸  Hero banner
# ═══════════════════════════════════════════════════════
st.markdown(
    """
    <div style="text-align:center">
        <div class="hero-title">CONCEPT SIMPLIFIED 🎓</div>
        <div class="hero-sub">JEE Mains &amp; Advanced College Predictor&nbsp;2025</div>
    </div>
    <div class="divider"></div>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════
# 4 ▸  Load counselling data
# ═══════════════════════════════════════════════════════
@st.cache_data
def load_data():
    path = "JOSSA 2025 - COUNSELLING.xlsx"
    return (
        pd.read_excel(path, sheet_name="JEE MAINS ROUND 1 PREDICTOR"),
        pd.read_excel(path, sheet_name="JEE Advanced ROUND 1 PREDICTOR"),
    )
mains_df, adv_df = load_data()

# ═══════════════════════════════════════════════════════
# 5 ▸  Instruction card
# ═══════════════════════════════════════════════════════
st.markdown(
    """
    <div class="card">
      <h3>How to use this Predictor</h3>

      <div class="step"><div class="badge">1</div><div class="step-text">
           <strong>Select Exam</strong> (JEE&nbsp;Mains or Advanced).</div></div>

      <div class="step"><div class="badge">2</div><div class="step-text">
           Pick <strong>Seat&nbsp;Type – Category</strong> (OPEN, EWS, OBC-NCL, SC…).</div></div>

      <div class="step"><div class="badge">3</div><div class="step-text">
           Optionally adjust <strong>Quota · Gender · Branches · Institutes</strong>.</div></div>

      <div class="step"><div class="badge">4</div><div class="step-text">
           Enter your <strong>Category Rank</strong> for that Seat&nbsp;Type (not overall CRL).</div></div>

      <div class="step"><div class="badge">5</div><div class="step-text">
           Click <strong>Submit</strong> to view colleges whose <strong>Closing Ranks</strong>
           meet / beat your rank.</div></div>

      <div class="step"><div class="badge">6</div><div class="step-text">
           Results sorted by Closing Rank (lower ⇒ better). Use <em>All</em> to widen filters.</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### &nbsp;")  # small vertical spacer

# ═══════════════════════════════════════════════════════
# 6 ▸  Predictor form
# ═══════════════════════════════════════════════════════
PH = "-- Select --"
exam = st.selectbox("Select Exam", [PH, "JEE Mains", "JEE Advanced"])

if exam != PH:
    df_opt = mains_df if exam == "JEE Mains" else adv_df
    left, right = st.columns(2)

    # LEFT column
    with left:
        inst_opts = ["All"] + sorted(df_opt["Institute"].dropna().unique())
        inst_sel  = st.multiselect("Select Institute(s)", inst_opts, default=["All"])

        quota = st.selectbox("Select Quota", ["All"] + sorted(df_opt["Quota"].dropna().unique()), index=0)

        seat_opts = ["-- Select Seat Type --"] + sorted(df_opt["Seat Type"].dropna().unique())
        seat_type = st.selectbox("Select Seat Type – Category (Required)", seat_opts)

    # RIGHT column
    with right:
        gender = st.selectbox("Select Gender", ["All"] + sorted(df_opt["Gender"].dropna().unique()), index=0)

        branch_opts = sorted(df_opt["Academic Program Name"].dropna().unique())
        branch_sel  = st.multiselect("Select Branch(es)", ["All"] + branch_opts, default=["All"])

        rank_text   = st.text_input("Enter Your Category Rank", help="Positive integer rank for selected Seat Type")

    st.markdown("---")

    if st.button("Submit"):
        errors = []
        if seat_type == "-- Select Seat Type --":
            errors.append("• Choose a Seat Type – Category.")
        if not rank_text.isdigit() or int(rank_text) <= 0:
            errors.append("• Enter a positive integer Category Rank.")

        if errors:
            st.error("\n".join(errors))
            st.stop()

        rank_val = int(rank_text)
        df = mains_df if exam == "JEE Mains" else adv_df

        df["Closing Rank"] = pd.to_numeric(df["Closing Rank"], errors="coerce")
        df["Opening Rank"] = pd.to_numeric(df["Opening Rank"], errors="coerce")

        mask = (df["Seat Type"] == seat_type) & (df["Closing Rank"].fillna(float("-inf")) >= rank_val)
        if quota != "All": mask &= df["Quota"] == quota
        if gender != "All": mask &= df["Gender"] == gender
        if inst_sel != ["All"]: mask &= df["Institute"].isin(inst_sel)
        if branch_sel != ["All"]: mask &= df["Academic Program Name"].isin(branch_sel)

        res = df[mask]
        if res.empty:
            st.warning("No colleges match your filters and rank.")
        else:
            cols = ["Institute","Academic Program Name","Quota","Seat Type","Gender","Opening Rank","Closing Rank"]
            table = res[cols].sort_values("Closing Rank").reset_index(drop=True)
            for c in ["Opening Rank","Closing Rank"]:
                table[c] = table[c].fillna(0).astype(int)

            st.markdown(f"### Colleges for Category Rank {rank_val}  ({seat_type}, {quota}, {gender})")
            st.write(table.to_html(index=False, classes="cs-table", escape=False), unsafe_allow_html=True)
else:
    st.info("Select an exam to display further options.")
