"""
CareerPath AI - Main Streamlit Application
AI-powered Resume Analyzer and Career Guidance System
"""

import os
import sys
import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ─── Path Setup ───────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import PAGE_CONFIG, THEME, JOB_ROLES_DB_PATH
from modules.pdf_extractor import extract_text_from_pdf
from modules.resume_parser import parse_resume
from modules.resume_scorer import score_resume
from modules.ats_analyzer import analyze_ats
from modules.job_predictor import predict_job_roles
from modules.company_recommender import recommend_companies
from modules.skill_gap_analyzer import analyze_skill_gap
from modules.roadmap_generator import generate_roadmap
from modules.interview_generator import generate_interview_questions
from modules.salary_predictor import predict_salary
from modules.chatbot import get_response

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(**PAGE_CONFIG)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

    /* ── Global Reset ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #E8E8F0;
    }

    .stApp {
        background: linear-gradient(135deg, #0A0A14 0%, #0F0F1A 40%, #13131F 100%);
        min-height: 100vh;
    }

    /* ── Hide Streamlit Branding ── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D0D1A 0%, #111122 100%);
        border-right: 1px solid rgba(108, 99, 255, 0.2);
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #6C63FF;
        font-family: 'Outfit', sans-serif;
    }

    /* ── File Uploader ── */
    [data-testid="stFileUploader"] {
        background: rgba(108, 99, 255, 0.05);
        border: 2px dashed rgba(108, 99, 255, 0.4);
        border-radius: 16px;
        padding: 1rem;
        transition: all 0.3s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(108, 99, 255, 0.8);
        background: rgba(108, 99, 255, 0.08);
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(26, 26, 46, 0.8);
        border-radius: 14px;
        padding: 6px;
        gap: 4px;
        border: 1px solid rgba(108, 99, 255, 0.2);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #9090B0;
        border-radius: 10px;
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
        font-size: 0.85rem;
        padding: 8px 14px;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6C63FF, #43E97B) !important;
        color: white !important;
        font-weight: 600 !important;
    }

    /* ── Metric Cards ── */
    [data-testid="stMetric"] {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 16px;
        padding: 1rem 1.25rem;
        backdrop-filter: blur(10px);
    }

    [data-testid="stMetricLabel"] { color: #9090B0 !important; font-size: 0.8rem !important; }
    [data-testid="stMetricValue"] { color: #6C63FF !important; font-family: 'Outfit', sans-serif; font-weight: 700 !important; }

    /* ── Buttons ── */
    .stButton button {
        background: linear-gradient(135deg, #6C63FF 0%, #43E97B 100%);
        border: none;
        border-radius: 12px;
        color: white;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(108, 99, 255, 0.3);
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(108, 99, 255, 0.5);
    }

    /* ── Selectbox & Slider ── */
    [data-testid="stSelectbox"] > div > div,
    .stSlider > div > div > div {
        background: rgba(26, 26, 46, 0.9) !important;
        border-color: rgba(108, 99, 255, 0.3) !important;
        border-radius: 10px !important;
        color: #E8E8F0 !important;
    }

    /* ── Text Input ── */
    .stTextInput input, .stTextArea textarea {
        background: rgba(26, 26, 46, 0.9) !important;
        border: 1px solid rgba(108, 99, 255, 0.3) !important;
        border-radius: 10px !important;
        color: #E8E8F0 !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(26, 26, 46, 0.6) !important;
        border: 1px solid rgba(108, 99, 255, 0.2) !important;
        border-radius: 10px !important;
        color: #B0B0C8 !important;
        font-family: 'Outfit', sans-serif;
    }

    /* ── Progress Bar ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6C63FF, #43E97B) !important;
        border-radius: 10px !important;
    }

    /* ── Divider ── */
    hr { border-color: rgba(108, 99, 255, 0.2) !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0F0F1A; }
    ::-webkit-scrollbar-thumb { background: #6C63FF; border-radius: 3px; }

    /* ── Plotly Charts BG ── */
    .js-plotly-plot .plotly { background: transparent !important; }
    </style>
    """, unsafe_allow_html=True)


# ─── HTML Component Helpers ───────────────────────────────────────────────────

def header_html():
    return """
    <div style="
        background: linear-gradient(135deg, rgba(108,99,255,0.15) 0%, rgba(67,233,123,0.08) 100%);
        border: 1px solid rgba(108,99,255,0.3);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute; top: -40px; right: -40px;
            width: 200px; height: 200px;
            background: radial-gradient(circle, rgba(108,99,255,0.2) 0%, transparent 70%);
            border-radius: 50%;
        "></div>
        <div style="
            position: absolute; bottom: -30px; left: 30%;
            width: 150px; height: 150px;
            background: radial-gradient(circle, rgba(67,233,123,0.15) 0%, transparent 70%);
            border-radius: 50%;
        "></div>
        <h1 style="
            font-family: 'Outfit', sans-serif;
            font-size: 2.4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6C63FF 0%, #43E97B 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 0 0.4rem 0;
        ">🚀 CareerPath AI</h1>
        <p style="color: #9090B0; font-size: 1.05rem; margin: 0; font-family: 'Inter', sans-serif;">
            AI-Powered Resume Analyzer &amp; Career Guidance System
        </p>
    </div>
    """

def glass_card(content, border_color="#6C63FF", padding="1.5rem"):
    return f"""
    <div style="
        background: rgba(26,26,46,0.7);
        border: 1px solid rgba({_hex_to_rgb(border_color)}, 0.25);
        border-radius: 16px;
        padding: {padding};
        backdrop-filter: blur(12px);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    ">{content}</div>
    """

def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"{r},{g},{b}"

def score_badge(score, label):
    if score >= 75:
        color, emoji = "#43E97B", "🟢"
    elif score >= 50:
        color, emoji = "#FFB347", "🟡"
    else:
        color, emoji = "#FF6584", "🔴"
    return f"""
    <div style="text-align:center;">
        <div style="font-size:0.8rem; color:#9090B0; margin-bottom:4px; font-family:'Outfit',sans-serif;">{label}</div>
        <div style="font-size:2.2rem; font-weight:800; color:{color}; font-family:'Outfit',sans-serif;">
            {emoji} {score:.0f}
        </div>
        <div style="font-size:0.75rem; color:{color}; opacity:0.8;">/100</div>
    </div>
    """

def skill_tag(skill, color="#6C63FF", bg_opacity="0.15"):
    r, g, b = _hex_to_rgb(color).split(",")
    return f"""<span style="
        display:inline-block;
        background: rgba({r},{g},{b},{bg_opacity});
        border: 1px solid rgba({r},{g},{b},0.4);
        color: {color};
        border-radius: 8px;
        padding: 3px 10px;
        font-size: 0.78rem;
        margin: 3px 3px 3px 0;
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
    ">{skill}</span>"""

def priority_tag(skill, priority):
    colors = {"Critical": "#FF6584", "Important": "#FFB347", "Nice-to-have": "#43E97B"}
    color = colors.get(priority, "#9090B0")
    return skill_tag(f"{skill} ({priority})", color)

def info_card(icon, label, value):
    return f"""
    <div style="
        background: rgba(26,26,46,0.7);
        border: 1px solid rgba(108,99,255,0.2);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.7rem;
    ">
        <span style="font-size:1.4rem;">{icon}</span>
        <div>
            <div style="font-size:0.72rem; color:#9090B0; font-family:'Outfit',sans-serif;">{label}</div>
            <div style="font-size:0.95rem; color:#E8E8F0; font-weight:600; font-family:'Inter',sans-serif; word-break:break-all;">{value or '—'}</div>
        </div>
    </div>
    """

def section_header(title, icon=""):
    return f"""
    <div style="margin: 1.5rem 0 1rem 0;">
        <h3 style="
            font-family: 'Outfit', sans-serif;
            font-size: 1.15rem;
            font-weight: 700;
            color: #E8E8F0;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 8px;
        ">{icon} {title}
        <span style="
            display:inline-block;
            height:2px;
            flex:1;
            background: linear-gradient(90deg, rgba(108,99,255,0.5), transparent);
            margin-left: 10px;
            border-radius: 2px;
        "></span>
        </h3>
    </div>
    """

def company_card(company, index):
    name = company.get("name", "Unknown")
    full_name = company.get("full_name", name)
    match = company.get("match_percentage", 0)
    domains = company.get("domains", [])
    url = company.get("career_url", "#")
    req_skills = company.get("required_skills", [])
    matched_skills = company.get("matched_skills", [])
    missing = company.get("missing_skills", [])

    if match >= 70:
        badge_color = "#43E97B"
    elif match >= 45:
        badge_color = "#FFB347"
    else:
        badge_color = "#FF6584"

    domains_html = " ".join([f'<span style="background:rgba(108,99,255,0.15);color:#6C63FF;border-radius:6px;padding:2px 8px;font-size:0.72rem;">{d}</span>' for d in domains[:3]])

    matched_html = " ".join([skill_tag(s, "#43E97B") for s in req_skills[:5]])
    missing_html = " ".join([skill_tag(s, "#FF6584") for s in missing[:3]])

    return f"""
    <div style="
        background: rgba(26,26,46,0.8);
        border: 1px solid rgba(108,99,255,0.18);
        border-left: 4px solid {badge_color};
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
    ">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
            <div>
                <div style="font-family:'Outfit',sans-serif; font-weight:700; font-size:1rem; color:#E8E8F0;">
                    #{index} {full_name}
                </div>
                <div style="margin-top:4px;">{domains_html}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:1.8rem; font-weight:800; color:{badge_color}; font-family:'Outfit',sans-serif; line-height:1;">{match:.0f}%</div>
                <div style="font-size:0.7rem; color:#9090B0;">Match Score</div>
            </div>
        </div>
        <div style="margin-top:0.8rem;">
            <div style="font-size:0.75rem; color:#9090B0; margin-bottom:4px;">✅ Key Skills</div>
            <div>{matched_html}</div>
        </div>
        {f'<div style="margin-top:0.5rem;"><div style="font-size:0.75rem; color:#9090B0; margin-bottom:4px;">❌ Missing Skills</div><div>{missing_html}</div></div>' if missing else ''}
        <div style="margin-top:0.8rem;">
            <a href="{url}" target="_blank" style="
                color:#6C63FF; font-size:0.8rem; text-decoration:none;
                border:1px solid rgba(108,99,255,0.3); border-radius:8px;
                padding:4px 12px; font-family:'Outfit',sans-serif;
            ">🔗 View Careers</a>
        </div>
    </div>
    """


# ─── Plotly Chart Helpers ─────────────────────────────────────────────────────

def make_gauge(value, title, color="#6C63FF"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": "/100", "font": {"size": 28, "color": "#E8E8F0", "family": "Outfit"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#555570", "tickwidth": 1, "tickfont": {"color": "#9090B0", "size": 10}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(26,26,46,0.5)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(255,101,132,0.15)"},
                {"range": [40, 70], "color": "rgba(255,179,71,0.12)"},
                {"range": [70, 100], "color": "rgba(67,233,123,0.12)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.85,
                "value": value
            }
        },
        title={"text": title, "font": {"size": 14, "color": "#9090B0", "family": "Outfit"}}
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E8E8F0",
    )
    return fig


def make_radar(breakdown, title):
    categories = [k.replace("_", " ").title() for k in breakdown.keys()]
    values = list(breakdown.values())
    max_vals = {"Skills": 30, "Projects": 25, "Certifications": 20, "Education": 15, "Format": 10}

    normalized = []
    for cat, val in zip(categories, values):
        max_v = max_vals.get(cat, 25)
        normalized.append(min(100, (val / max_v) * 100))

    categories.append(categories[0])
    normalized.append(normalized[0])

    fig = go.Figure(go.Scatterpolar(
        r=normalized,
        theta=categories,
        fill='toself',
        fillcolor='rgba(108,99,255,0.15)',
        line=dict(color='#6C63FF', width=2),
        marker=dict(color='#6C63FF', size=6),
        name='Score',
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#9090B0", size=9), gridcolor="rgba(108,99,255,0.15)"),
            angularaxis=dict(tickfont=dict(color="#B0B0C8", size=11, family="Outfit"), gridcolor="rgba(108,99,255,0.1)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        height=320,
        margin=dict(l=40, r=40, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        title=dict(text=title, font=dict(color="#9090B0", size=13, family="Outfit"), x=0.5),
    )
    return fig


def make_bar_chart(breakdown):
    labels = [k.replace("_", " ").title() for k in breakdown.keys()]
    values = list(breakdown.values())
    max_vals = [30, 25, 20, 15, 10]
    pcts = [min(100, (v / m) * 100) if m > 0 else 0 for v, m in zip(values, max_vals)]
    colors = ["#FF6584" if p < 40 else "#FFB347" if p < 70 else "#43E97B" for p in pcts]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        marker_line_width=0,
        text=[f"{v:.1f}" for v in values],
        textposition="outside",
        textfont=dict(color="#E8E8F0", size=12, family="Outfit"),
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#9090B0", size=11), gridcolor="rgba(108,99,255,0.08)"),
        yaxis=dict(tickfont=dict(color="#9090B0", size=9), gridcolor="rgba(108,99,255,0.08)"),
        showlegend=False,
    )
    return fig


def make_job_bar(roles):
    names = [r.get("title", "?") for r in roles[:8]]
    scores = [r.get("match_percentage", 0) for r in roles[:8]]
    colors = ["#43E97B" if s >= 70 else "#FFB347" if s >= 45 else "#FF6584" for s in scores]

    fig = go.Figure(go.Bar(
        y=names[::-1],
        x=scores[::-1],
        orientation='h',
        marker_color=colors[::-1],
        marker_line_width=0,
        text=[f"{s:.0f}%" for s in scores[::-1]],
        textposition="outside",
        textfont=dict(color="#E8E8F0", size=11, family="Outfit"),
    ))
    fig.update_layout(
        height=340,
        margin=dict(l=10, r=60, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 115], tickfont=dict(color="#9090B0", size=9), gridcolor="rgba(108,99,255,0.1)"),
        yaxis=dict(tickfont=dict(color="#B0B0C8", size=11, family="Outfit"), gridcolor="rgba(0,0,0,0)"),
    )
    return fig


# ─── Load Job Roles List ──────────────────────────────────────────────────────

@st.cache_data
def load_job_role_titles():
    try:
        with open(JOB_ROLES_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        roles = data.get("roles", []) if isinstance(data, dict) else data
        return [r.get("title", "") for r in roles if r.get("title")]
    except Exception:
        return ["Data Scientist", "Software Engineer", "ML Engineer", "Frontend Developer", "Backend Developer"]


# ─── Run Analysis ─────────────────────────────────────────────────────────────

def run_full_analysis(uploaded_file, target_role, experience_years):
    """Run the full pipeline and cache results in session_state."""
    with st.spinner("⚡ Extracting text from PDF..."):
        raw_text = extract_text_from_pdf(uploaded_file)

    with st.spinner("🔍 Parsing resume sections..."):
        parsed = parse_resume(raw_text)

    with st.spinner("📊 Calculating scores..."):
        resume_score = score_resume(parsed)
        ats_result = analyze_ats(parsed, target_role)

    with st.spinner("🎯 Predicting job roles..."):
        predicted_roles = predict_job_roles(parsed)

    with st.spinner("🏢 Matching companies..."):
        companies = recommend_companies(parsed)

    with st.spinner("🧠 Analyzing skill gap..."):
        skill_gap = analyze_skill_gap(parsed.get("skills", []), target_role) if target_role else {}

    with st.spinner("🗺️ Generating learning roadmap..."):
        roadmap = generate_roadmap(skill_gap.get("missing_skills", [])) if skill_gap else {"roadmap": [], "total_months": 0}

    with st.spinner("🎤 Generating interview questions..."):
        interview_qs = generate_interview_questions(parsed.get("skills", [])[:6])

    with st.spinner("💰 Predicting salary range..."):
        role_titles = [r.get("title", "") for r in predicted_roles]
        edu_list = parsed.get("education", [])
        edu_level = edu_list[0] if edu_list else "Bachelors"
        salary = predict_salary(
            role_titles,
            len(parsed.get("skills", [])),
            edu_level,
            len(parsed.get("certifications", [])),
            experience_years,
        )

    # Enrich company records with matched/missing skill sets for display
    user_skills_lower = {s.lower() for s in parsed.get("skills", [])}
    for c in companies:
        req = c.get("required_skills", [])
        c["matched_skills"] = [s for s in req if s.lower() in user_skills_lower]
        c["missing_skills"] = [s for s in req if s.lower() not in user_skills_lower]

    st.session_state.update({
        "parsed": parsed,
        "resume_score": resume_score,
        "ats_result": ats_result,
        "predicted_roles": predicted_roles,
        "companies": companies,
        "skill_gap": skill_gap,
        "roadmap": roadmap,
        "interview_qs": interview_qs,
        "salary": salary,
        "target_role": target_role,
        "experience_years": experience_years,
        "analyzed": True,
        "chat_history": [],
    })


# ─── Tab Renderers ────────────────────────────────────────────────────────────

def render_dashboard():
    parsed       = st.session_state.parsed
    resume_score = st.session_state.resume_score
    ats_result   = st.session_state.ats_result
    salary       = st.session_state.salary

    total   = resume_score.get("total_score", 0)
    ats     = ats_result.get("ats_score", 0)
    name    = parsed.get("name", "Candidate")
    skills  = parsed.get("skills", [])
    certs   = parsed.get("certifications", [])
    projs   = parsed.get("projects", [])
    sects   = parsed.get("sections", {})
    words   = len(parsed.get("raw_text", "").split())

    st.markdown(section_header("📊 Score Overview", ""), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(make_gauge(total, "Resume Score", "#6C63FF"), use_container_width=True)
    with col2:
        st.plotly_chart(make_gauge(ats, "ATS Score", "#43E97B"), use_container_width=True)

    st.markdown(section_header("📋 Profile Snapshot", ""), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("👤 Name", name[:18] + "..." if len(name) > 18 else name or "N/A")
    with c2: st.metric("🛠️ Skills", len(skills))
    with c3: st.metric("📜 Certifications", len(certs))
    with c4: st.metric("📂 Projects", len(projs))

    c5, c6, c7, c8 = st.columns(4)
    with c5: st.metric("📝 Word Count", words)
    with c6: st.metric("📑 Sections", len(sects))
    with c7:
        sal_min = salary.get("adjusted_range", {}).get("min", 0)
        sal_max = salary.get("adjusted_range", {}).get("max", 0)
        st.metric("💰 Salary Est.", f"{sal_min:.1f}-{sal_max:.1f} LPA")
    with c8:
        exp_level = salary.get("experience_level", "fresher").capitalize()
        st.metric("🏆 Level", exp_level)

    st.markdown(section_header("📈 Score Breakdown", ""), unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.plotly_chart(make_radar(resume_score.get("breakdown", {}), "Resume Quality Radar"), use_container_width=True)
    with col_b:
        st.plotly_chart(make_bar_chart(resume_score.get("breakdown", {})), use_container_width=True)

    st.markdown(section_header("💡 Improvement Suggestions", ""), unsafe_allow_html=True)
    suggestions = resume_score.get("suggestions", [])
    problems    = ats_result.get("problems", [])
    col_s, col_p = st.columns(2)
    with col_s:
        st.markdown("**Resume Suggestions**")
        for s in suggestions[:5]:
            st.markdown(f"> {s}")
    with col_p:
        st.markdown("**ATS Issues**")
        for p in problems[:5]:
            icon = p.get("icon", "❌")
            msg  = p.get("message", "")
            st.markdown(f"> {icon} {msg}")


def render_profile():
    parsed = st.session_state.parsed
    st.markdown(section_header("👤 Contact Details", ""), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(info_card("👤", "Full Name", parsed.get("name", "")), unsafe_allow_html=True)
        st.markdown(info_card("📧", "Email Address", parsed.get("email", "")), unsafe_allow_html=True)
    with col2:
        st.markdown(info_card("📱", "Phone Number", parsed.get("phone", "")), unsafe_allow_html=True)
        st.markdown(info_card("🔗", "LinkedIn", parsed.get("linkedin", "")), unsafe_allow_html=True)

    st.markdown(section_header("🛠️ Extracted Skills", ""), unsafe_allow_html=True)
    skills = parsed.get("skills", [])
    if skills:
        skills_html = " ".join(skill_tag(s) for s in sorted(skills))
        st.markdown(f'<div style="line-height:2.2;">{skills_html}</div>', unsafe_allow_html=True)
    else:
        st.info("No skills were detected. Ensure your resume has a clear Skills section.")

    col_e, col_c = st.columns(2)
    with col_e:
        st.markdown(section_header("🎓 Education", ""), unsafe_allow_html=True)
        edu = parsed.get("education", [])
        if edu:
            for e in edu:
                st.markdown(f'<div style="background:rgba(26,26,46,0.7);border:1px solid rgba(108,99,255,0.2);border-radius:10px;padding:0.6rem 1rem;margin-bottom:0.4rem;color:#E8E8F0;font-family:Inter,sans-serif;">'
                            f'🎓 {e}</div>', unsafe_allow_html=True)
        else:
            st.info("No education entries detected.")

    with col_c:
        st.markdown(section_header("📜 Certifications", ""), unsafe_allow_html=True)
        certs = parsed.get("certifications", [])
        if certs:
            for c in certs:
                st.markdown(f'<div style="background:rgba(26,26,46,0.7);border:1px solid rgba(67,233,123,0.2);border-radius:10px;padding:0.6rem 1rem;margin-bottom:0.4rem;color:#E8E8F0;font-family:Inter,sans-serif;">'
                            f'📜 {c}</div>', unsafe_allow_html=True)
        else:
            st.info("No certifications detected.")

    st.markdown(section_header("📂 Projects", ""), unsafe_allow_html=True)
    projects = parsed.get("projects", [])
    if projects:
        for p in projects:
            with st.expander(f"📁 {p[:80]}..." if len(p) > 80 else f"📁 {p}"):
                st.write(p)
    else:
        st.info("No projects were detected.")

    st.markdown(section_header("💼 Experience", ""), unsafe_allow_html=True)
    experience = parsed.get("experience", [])
    if experience:
        for line in experience[:20]:
            st.markdown(f'<div style="color:#B0B0C8;font-size:0.88rem;padding:4px 0;border-bottom:1px solid rgba(108,99,255,0.1);">• {line}</div>',
                        unsafe_allow_html=True)
    else:
        st.info("No experience entries detected.")


def render_career():
    predicted_roles = st.session_state.predicted_roles
    companies       = st.session_state.companies
    salary          = st.session_state.salary
    parsed          = st.session_state.parsed

    st.markdown(section_header("🎯 Predicted Job Roles", ""), unsafe_allow_html=True)
    if predicted_roles:
        col_chart, col_list = st.columns([1.2, 1])
        with col_chart:
            st.plotly_chart(make_job_bar(predicted_roles), use_container_width=True)
        with col_list:
            for i, role in enumerate(predicted_roles[:5], 1):
                title  = role.get("title", "Unknown")
                match  = role.get("match_percentage", 0)
                cat    = role.get("category", "")
                desc   = role.get("description", "")
                badge_color = "#43E97B" if match >= 70 else "#FFB347" if match >= 45 else "#FF6584"
                st.markdown(f"""
                <div style="background:rgba(26,26,46,0.8);border:1px solid rgba(108,99,255,0.18);border-left:3px solid {badge_color};border-radius:12px;padding:0.9rem 1rem;margin-bottom:0.6rem;">
                    <div style="font-family:Outfit,sans-serif;font-weight:700;font-size:0.95rem;color:#E8E8F0;">#{i} {title}</div>
                    <div style="display:flex;gap:8px;margin-top:4px;align-items:center;">
                        <span style="color:{badge_color};font-size:0.85rem;font-weight:700;">{match:.0f}% match</span>
                        <span style="color:#6090A0;font-size:0.75rem;">{cat}</span>
                    </div>
                    <div style="color:#9090B0;font-size:0.78rem;margin-top:4px;line-height:1.4;">{desc[:100]}...</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Upload a resume to see job role predictions.")

    st.markdown(section_header("🏢 Company Recommendations", ""), unsafe_allow_html=True)
    st.caption("Companies matched using TF-IDF cosine similarity on your skill profile")
    if companies:
        num_per_row = 2
        for i in range(0, min(len(companies), 12), num_per_row):
            cols = st.columns(num_per_row)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(companies):
                    with col:
                        st.markdown(company_card(companies[idx], idx + 1), unsafe_allow_html=True)
    else:
        st.info("No company matches found.")

    st.markdown(section_header("💰 Salary Prediction", ""), unsafe_allow_html=True)
    if salary:
        adj_min = salary.get("adjusted_range", {}).get("min", 0)
        adj_max = salary.get("adjusted_range", {}).get("max", 0)
        base_min = salary.get("base_range", {}).get("min", 0)
        base_max = salary.get("base_range", {}).get("max", 0)

        cols = st.columns(3)
        with cols[0]: st.metric("🎯 Role", salary.get("role", "N/A")[:24])
        with cols[1]: st.metric("📊 Base Range", f"{base_min:.1f} – {base_max:.1f} LPA")
        with cols[2]: st.metric("💰 Adjusted Range", f"{adj_min:.1f} – {adj_max:.1f} LPA", delta=f"+{((adj_max - base_max) / base_max * 100) if base_max else 0:.0f}% adjustments")

        st.markdown("**💡 Adjustment Factors Applied:**")
        for factor in salary.get("factors", []):
            st.markdown(f"- **{factor.get('name', '')}**: {factor.get('impact', '')}")


def render_skillgap():
    skill_gap = st.session_state.skill_gap
    roadmap   = st.session_state.roadmap

    if not skill_gap or skill_gap.get("error"):
        st.warning("⚠️ Select a target role in the sidebar to see your skill gap analysis.")
        return

    target_role    = skill_gap.get("target_role", "Target Role")
    matching       = skill_gap.get("matching_skills", [])
    missing        = skill_gap.get("missing_skills", [])
    match_pct      = skill_gap.get("match_percentage", 0)

    st.markdown(section_header(f"🎯 Skill Gap Analysis: {target_role}", ""), unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]: st.metric("✅ Skills You Have", len(matching))
    with cols[1]: st.metric("❌ Missing Skills", len(missing))
    with cols[2]: st.metric("📊 Match Score", f"{match_pct:.0f}%")

    st.progress(int(match_pct) / 100)

    if matching:
        st.markdown("**✅ Matching Skills**")
        html = " ".join(skill_tag(s, "#43E97B") for s in sorted(matching))
        st.markdown(f'<div style="line-height:2.2;">{html}</div>', unsafe_allow_html=True)

    if missing:
        st.markdown("**❌ Skills to Acquire**")
        critical   = [m for m in missing if m.get("priority") == "Critical"]
        important  = [m for m in missing if m.get("priority") == "Important"]
        nicetohave = [m for m in missing if m.get("priority") == "Nice-to-have"]

        for label, group, color in [("🔴 Critical", critical, "#FF6584"),
                                     ("🟡 Important", important, "#FFB347"),
                                     ("🟢 Nice-to-have", nicetohave, "#43E97B")]:
            if group:
                st.markdown(f"*{label}*")
                html = " ".join(skill_tag(m.get("skill", ""), color) for m in group)
                st.markdown(f'<div style="line-height:2.2;">{html}</div>', unsafe_allow_html=True)

    st.markdown(section_header("🗺️ Learning Roadmap", ""), unsafe_allow_html=True)
    rm = roadmap.get("roadmap", [])
    if rm:
        st.caption(f"📅 Estimated {roadmap.get('total_months', 0)}-month learning plan")
        for month_entry in rm:
            month_num  = month_entry.get("month", 1)
            month_skills = month_entry.get("skills", [])
            with st.expander(f"📅 Month {month_num} — {', '.join(s.get('name','') for s in month_skills)}", expanded=month_num <= 2):
                for skill_info in month_skills:
                    sname    = skill_info.get("name", "")
                    priority = skill_info.get("priority", "")
                    courses  = skill_info.get("courses", [])

                    p_colors = {"Critical": "#FF6584", "Important": "#FFB347", "Nice-to-have": "#43E97B"}
                    p_color  = p_colors.get(priority, "#9090B0")

                    st.markdown(f'<div style="font-family:Outfit,sans-serif;font-weight:700;color:#E8E8F0;font-size:0.95rem;margin-bottom:4px;">'
                                f'🎯 {sname} <span style="color:{p_color};font-size:0.78rem;">({priority})</span></div>', unsafe_allow_html=True)

                    for course in courses[:2]:
                        platform = course.get("platform", "Online")
                        cname    = course.get("name", "")
                        curl     = course.get("url", "#")
                        ctype    = course.get("type", "Course")
                        st.markdown(f'&nbsp;&nbsp;&nbsp;📚 <a href="{curl}" target="_blank" style="color:#6C63FF;text-decoration:none;">{cname}</a> '
                                    f'<span style="color:#9090B0;font-size:0.75rem;">— {platform} ({ctype})</span>', unsafe_allow_html=True)
                    st.markdown("---")
    else:
        st.success("🎉 No missing skills detected! You're ready for your target role.")


def render_interview():
    interview_qs = st.session_state.interview_qs
    parsed       = st.session_state.parsed

    st.markdown(section_header("🎤 Interview Preparation", ""), unsafe_allow_html=True)
    all_skills = parsed.get("skills", [])

    if not interview_qs or not interview_qs.get("questions"):
        st.info("No interview questions generated. Make sure your resume has extractable skills.")
        return

    st.caption(f"📊 {interview_qs.get('total_questions', 0)} questions across {interview_qs.get('skills_covered', 0)} skills")

    skill_selector = st.selectbox(
        "🔍 Select a skill to practice:",
        options=[q.get("skill", "") for q in interview_qs.get("questions", [])],
        key="interview_skill_select"
    )

    selected_q = next((q for q in interview_qs.get("questions", []) if q.get("skill") == skill_selector), None)
    if selected_q:
        levels = [("🟢 Beginner", "beginner", "#43E97B"),
                  ("🟡 Intermediate", "intermediate", "#FFB347"),
                  ("🔴 Advanced", "advanced", "#FF6584")]
        for level_label, level_key, level_color in levels:
            questions = selected_q.get(level_key, [])
            if questions:
                with st.expander(f"{level_label} Questions ({len(questions)})", expanded=(level_key == "beginner")):
                    for i, q in enumerate(questions, 1):
                        st.markdown(f"""
                        <div style="background:rgba(26,26,46,0.7);border-left:3px solid {level_color};border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.5rem;color:#D0D0E8;font-size:0.9rem;font-family:Inter,sans-serif;">
                            <strong style="color:{level_color};">Q{i}.</strong> {q}
                        </div>
                        """, unsafe_allow_html=True)


def render_chatbot():
    parsed          = st.session_state.parsed
    resume_score    = st.session_state.resume_score
    ats_result      = st.session_state.ats_result
    predicted_roles = st.session_state.predicted_roles
    companies       = st.session_state.companies
    skill_gap       = st.session_state.skill_gap
    salary          = st.session_state.salary
    roadmap         = st.session_state.roadmap
    interview_qs    = st.session_state.interview_qs

    resume_data = {
        **parsed,
        "resume_score": resume_score,
        "ats_result": ats_result,
        "predicted_roles": predicted_roles,
        "recommended_companies": companies,
        "skill_gap": skill_gap,
        "salary": salary,
        "roadmap": roadmap,
        "interview_questions": interview_qs,
    }

    st.markdown(section_header("🤖 AI Career Chatbot", ""), unsafe_allow_html=True)
    st.caption("Ask me anything about your resume analysis, career path, skills, salary, or interview prep!")

    chat_container = st.container()
    with chat_container:
        history = st.session_state.get("chat_history", [])
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:10px;">
                    <div style="background:linear-gradient(135deg,#6C63FF,#5a52d5);color:white;border-radius:16px 16px 4px 16px;padding:10px 16px;max-width:75%;font-family:Inter,sans-serif;font-size:0.9rem;line-height:1.5;">
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-start;margin-bottom:10px;">
                    <div style="background:rgba(26,26,46,0.9);border:1px solid rgba(108,99,255,0.2);color:#D0D0E8;border-radius:16px 16px 16px 4px;padding:10px 16px;max-width:80%;font-family:Inter,sans-serif;font-size:0.88rem;line-height:1.6;">
                        🤖 {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        col_in, col_btn = st.columns([5, 1])
        with col_in:
            user_input = st.text_input("", placeholder="e.g. What companies should I apply to?", label_visibility="collapsed", key="chat_input")
        with col_btn:
            send = st.form_submit_button("Send 🚀")

    if send and user_input.strip():
        response = get_response(user_input.strip(), resume_data)
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "bot", "content": response})
        st.rerun()

    st.markdown("**💡 Quick Prompts:**")
    quick_prompts = [
        "What companies should I target?",
        "What skills am I missing?",
        "What's my expected salary?",
        "Show me interview questions",
        "How can I improve my ATS score?",
        "What roles are suitable for me?",
    ]
    cols = st.columns(3)
    for i, prompt in enumerate(quick_prompts):
        with cols[i % 3]:
            if st.button(prompt, key=f"qp_{i}"):
                response = get_response(prompt, resume_data)
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.session_state.chat_history.append({"role": "bot", "content": response})
                st.rerun()


def get_project_files():
    project_files = {}
    exclude_dirs = {'.git', '__pycache__', 'venv', '.agents', '.gemini'}
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(('.py', '.json', '.txt', '.md')) and not file.startswith('.'):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, BASE_DIR).replace('\\', '/')
                project_files[rel_path] = abs_path
    return project_files


def render_code_viewer():
    st.markdown(section_header("💻 Codebase Explorer", ""), unsafe_allow_html=True)
    st.caption("Explore the file structure, statistics, and full source code of CareerPath AI.")

    files = get_project_files()
    sorted_files = sorted(list(files.keys()))

    # Group files by directory for a structured explorer
    categories = {}
    for f in sorted_files:
        parts = f.split('/')
        if len(parts) > 1:
            cat = parts[0]
        else:
            cat = "Root Directory"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(f)

    # Let the user select category first, then file
    cat_list = list(categories.keys())
    if "Root Directory" in cat_list:
        cat_list.remove("Root Directory")
        cat_list.insert(0, "Root Directory")

    col_nav, col_code = st.columns([1, 2.5])

    with col_nav:
        st.markdown("##### 📁 Navigation")
        selected_cat = st.selectbox("Select Directory / Layer:", cat_list)
        
        file_options = categories[selected_cat]
        selected_file = st.selectbox(
            "Select File:",
            options=file_options,
            format_func=lambda x: os.path.basename(x)
        )
        
        # Read the file
        file_path = files[selected_file]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
        except Exception as e:
            code_content = f"Error reading file: {e}"

        # File Stats Card
        num_lines = len(code_content.splitlines())
        file_size_kb = len(code_content.encode('utf-8')) / 1024.0
        num_funcs = sum(1 for line in code_content.splitlines() if line.strip().startswith("def "))
        num_classes = sum(1 for line in code_content.splitlines() if line.strip().startswith("class "))
        
        st.markdown(f"""
        <div style="background:rgba(26,26,46,0.8);border:1px solid rgba(108,99,255,0.2);border-radius:12px;padding:1rem;margin-top:1rem;">
            <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#6C63FF;font-size:0.9rem;margin-bottom:8px;">📊 File Insights</div>
            <div style="font-size:0.8rem;color:#9090B0;margin-bottom:4px;">Path: <code style="color:#E8E8F0;">{selected_file}</code></div>
            <div style="font-size:0.8rem;color:#9090B0;margin-bottom:4px;">Size: <strong style="color:#E8E8F0;">{file_size_kb:.2f} KB</strong></div>
            <div style="font-size:0.8rem;color:#9090B0;margin-bottom:4px;">Lines: <strong style="color:#E8E8F0;">{num_lines}</strong></div>
            {f'<div style="font-size:0.8rem;color:#9090B0;margin-bottom:4px;">Functions: <strong style="color:#43E97B;">{num_funcs}</strong></div>' if num_funcs > 0 else ''}
            {f'<div style="font-size:0.8rem;color:#9090B0;margin-bottom:4px;">Classes: <strong style="color:#FFB347;">{num_classes}</strong></div>' if num_classes > 0 else ''}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Search Code
        st.markdown("##### 🔍 Search Codebase")
        search_query = st.text_input("Find text in files:", placeholder="e.g. TF-IDF")
        if search_query:
            matches = []
            for rel_path, abs_path in files.items():
                try:
                    with open(abs_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        if search_query.lower() in line.lower():
                            matches.append((rel_path, idx, line.strip()))
                except:
                    pass
            if matches:
                st.success(f"Found {len(matches)} match(es):")
                for match_file, line_num, line_text in matches[:8]:
                    st.markdown(f"**{os.path.basename(match_file)}** (L{line_num}): `{line_text[:40]}...`")
                if len(matches) > 8:
                    st.caption(f"... and {len(matches)-8} more matches.")
            else:
                st.info("No matches found.")

    with col_code:
        st.markdown(f"##### 📄 Code: `{selected_file}`")
        
        lang = "python"
        if selected_file.endswith(".json"):
            lang = "json"
        elif selected_file.endswith(".md"):
            lang = "markdown"
        elif selected_file.endswith(".txt"):
            lang = "text"
            
        st.code(code_content, language=lang, line_numbers=True)


# ─── Main App ─────────────────────────────────────────────────────────────────

def main():
    inject_css()
    st.markdown(header_html(), unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0 0.5rem 0;">
            <div style="font-family:'Outfit',sans-serif;font-size:1.5rem;font-weight:800;
                background:linear-gradient(135deg,#6C63FF,#43E97B);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                🚀 CareerPath AI
            </div>
            <div style="color:#9090B0;font-size:0.78rem;margin-top:2px;">Resume Analyzer</div>
        </div>
        <hr style="border-color:rgba(108,99,255,0.2);margin:0.5rem 0 1rem;">
        """, unsafe_allow_html=True)

        st.markdown("**📄 Upload Resume**")
        uploaded_file = st.file_uploader(
            "Upload your PDF resume",
            type=["pdf"],
            label_visibility="collapsed",
            key="resume_uploader"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🎯 Target Job Role**")
        role_titles = load_job_role_titles()
        target_role = st.selectbox(
            "Select target role",
            options=[""] + role_titles,
            format_func=lambda x: "Select a role..." if x == "" else x,
            label_visibility="collapsed",
            key="target_role_select"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**📅 Years of Experience**")
        experience_years = st.slider(
            "Years of experience",
            min_value=0, max_value=20, value=0, step=1,
            label_visibility="collapsed",
            key="exp_slider"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("⚡ Analyze Resume", use_container_width=True, key="analyze_btn")

        if analyze_btn and uploaded_file:
            uploaded_file.seek(0)
            run_full_analysis(uploaded_file, target_role, experience_years)
            st.success("✅ Analysis complete!")
        elif analyze_btn and not uploaded_file:
            st.error("⚠️ Please upload a PDF resume first.")

        if st.session_state.get("analyzed"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**📊 Quick Stats**")
            parsed = st.session_state.parsed
            resume_score = st.session_state.resume_score
            ats_result = st.session_state.ats_result
            st.markdown(f"""
            <div style="background:rgba(26,26,46,0.7);border:1px solid rgba(108,99,255,0.2);border-radius:12px;padding:0.8rem 1rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="color:#9090B0;font-size:0.8rem;">Resume Score</span>
                    <span style="color:#6C63FF;font-weight:700;font-size:0.85rem;">{resume_score.get('total_score',0):.0f}/100</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="color:#9090B0;font-size:0.8rem;">ATS Score</span>
                    <span style="color:#43E97B;font-weight:700;font-size:0.85rem;">{ats_result.get('ats_score',0):.0f}/100</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:#9090B0;font-size:0.8rem;">Skills Found</span>
                    <span style="color:#FFB347;font-weight:700;font-size:0.85rem;">{len(parsed.get('skills',[]))}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(108,99,255,0.2);margin:1rem 0;'>", unsafe_allow_html=True)
        st.checkbox("💻 Code Explorer Mode", value=False, key="show_code_explorer")

    # ── Main Content ─────────────────────────────────────────────────────────
    if st.session_state.get("show_code_explorer"):
        render_code_viewer()
    elif not st.session_state.get("analyzed"):
        # Welcome / Landing State
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;">
            <div style="font-size:5rem;margin-bottom:1rem;">📄</div>
            <h2 style="font-family:'Outfit',sans-serif;font-weight:700;color:#E8E8F0;margin-bottom:0.5rem;">
                Upload Your Resume to Get Started
            </h2>
            <p style="color:#9090B0;font-size:1rem;max-width:500px;margin:0 auto 2rem auto;">
                Get AI-powered insights including resume score, ATS compatibility, job role predictions,
                company matches, skill gap analysis, and more.
            </p>
        </div>
        """, unsafe_allow_html=True)

        f1, f2, f3 = st.columns(3)
        features = [
            ("📊", "Resume & ATS Score", "Get scored on skills, education, projects, certifications, and ATS compatibility."),
            ("🎯", "Job Role Predictions", "Discover top matching roles using TF-IDF cosine similarity on your skill profile."),
            ("🏢", "Company Matcher", "Find companies like TCS, Infosys, Wipro & Accenture with match percentages."),
            ("🧠", "Skill Gap Analysis", "Identify Critical, Important, and Nice-to-have skills you need to acquire."),
            ("🗺️", "Learning Roadmap", "Get a month-by-month plan with real course recommendations."),
            ("🤖", "Career Chatbot", "Chat with an AI assistant about your career based on your resume analysis."),
        ]
        for col, (icon, title, desc) in zip([f1, f2, f3] * 2, features):
            with col:
                st.markdown(f"""
                <div style="background:rgba(26,26,46,0.7);border:1px solid rgba(108,99,255,0.18);border-radius:16px;padding:1.3rem;margin-bottom:1rem;text-align:center;">
                    <div style="font-size:2rem;margin-bottom:0.5rem;">{icon}</div>
                    <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#E8E8F0;font-size:0.95rem;margin-bottom:0.4rem;">{title}</div>
                    <div style="color:#9090B0;font-size:0.8rem;line-height:1.5;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Dashboard",
            "👤 Profile Details",
            "🏢 Career & Companies",
            "🧠 Skill Gap & Roadmap",
            "🎤 Interview Prep",
            "🤖 AI Chatbot",
        ])
        with tab1: render_dashboard()
        with tab2: render_profile()
        with tab3: render_career()
        with tab4: render_skillgap()
        with tab5: render_interview()
        with tab6: render_chatbot()


if __name__ == "__main__":
    main()
