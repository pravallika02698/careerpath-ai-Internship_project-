"""
CareerPath AI - Rule-Based Chatbot Module

A conversational chatbot that uses keyword-based intent detection
to answer user queries about their resume analysis results.
"""

import os
import sys

# Add parent directory to path for config imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ─── Intent Definitions ──────────────────────────────────
# Each intent maps keyword patterns to a handler function name
INTENTS = {
    "company": {
        "keywords": ["company", "companies", "where", "hire", "hiring", "employer", "work at"],
        "handler": "_handle_company_query",
    },
    "skill_gap": {
        "keywords": ["skill", "missing", "gap", "learn", "lacking", "need to learn", "weak"],
        "handler": "_handle_skill_gap_query",
    },
    "ats": {
        "keywords": ["ats", "score", "improve", "optimization", "optimize", "resume score"],
        "handler": "_handle_ats_query",
    },
    "role": {
        "keywords": ["role", "job", "career", "suitable", "position", "designation", "fit"],
        "handler": "_handle_role_query",
    },
    "salary": {
        "keywords": ["salary", "pay", "earn", "package", "compensation", "ctc", "income", "money"],
        "handler": "_handle_salary_query",
    },
    "interview": {
        "keywords": ["interview", "question", "prepare", "preparation", "practice"],
        "handler": "_handle_interview_query",
    },
    "roadmap": {
        "keywords": ["roadmap", "plan", "path", "timeline", "schedule", "month"],
        "handler": "_handle_roadmap_query",
    },
    "resume": {
        "keywords": ["resume", "format", "section", "layout", "structure", "breakdown"],
        "handler": "_handle_resume_query",
    },
}


# ─── Greeting & Fallback Responses ───────────────────────
GREETING_KEYWORDS = ["hi", "hello", "hey", "help", "start", "menu", "options", "what can you do"]

GREETING_RESPONSE = """👋 Hello! I'm your CareerPath AI assistant. I can help you with:

🏢 **Company Recommendations** — Ask about companies that match your profile
🎯 **Skill Gap Analysis** — Find out what skills you need to learn
📊 **ATS Score** — Get tips to improve your resume score
💼 **Job Roles** — Discover suitable career paths
💰 **Salary Insights** — Estimate your expected salary range
🎤 **Interview Prep** — Get practice questions for your skills
🗺️ **Learning Roadmap** — Get a month-by-month learning plan
📄 **Resume Breakdown** — See your resume score details

Just type your question naturally, and I'll help you out! 😊"""

FALLBACK_RESPONSE = """🤔 I'm not sure I understood that. Here are some things you can ask me:

• "What companies should I target?"
• "What skills am I missing?"
• "How can I improve my ATS score?"
• "What roles are suitable for me?"
• "What's my expected salary?"
• "Help me prepare for interviews"
• "Show me a learning roadmap"
• "Break down my resume score"

Try asking one of these, or type **'help'** for the full menu! 💡"""


# ─── Intent Handlers ─────────────────────────────────────

def _handle_company_query(resume_data):
    """Generate response for company-related queries.

    Args:
        resume_data (dict): Full resume analysis data.

    Returns:
        str: Formatted response about recommended companies.
    """
    companies = resume_data.get("recommended_companies", [])

    if not companies:
        return ("🏢 I don't have company recommendations available yet. "
                "Make sure your resume has been fully analyzed!")

    response = "🏢 **Top Company Recommendations for You:**\n\n"

    for i, company in enumerate(companies[:8], 1):
        if isinstance(company, dict):
            name = company.get("name", company.get("company", "Unknown"))
            reason = company.get("reason", company.get("match_reason", ""))
            match = company.get("match_score", "")
            response += f"**{i}. {name}**"
            if match:
                response += f" — Match: {match}%"
            response += "\n"
            if reason:
                response += f"   _{reason}_\n"
        else:
            response += f"**{i}. {company}**\n"

    response += "\n💡 _Tip: Tailor your resume for each company's specific requirements!_"
    return response


def _handle_skill_gap_query(resume_data):
    """Generate response for skill gap queries.

    Args:
        resume_data (dict): Full resume analysis data.

    Returns:
        str: Formatted response about missing skills.
    """
    skill_gap = resume_data.get("skill_gap", {})

    if not skill_gap:
        return ("🎯 Skill gap analysis isn't available yet. "
                "Please ensure your resume has been analyzed with a target role!")

    matching = skill_gap.get("matching_skills", [])
    missing = skill_gap.get("missing_skills", [])
    match_pct = skill_gap.get("match_percentage", 0)
    target = skill_gap.get("target_role", "your target role")

    response = f"🎯 **Skill Gap Analysis for {target}:**\n\n"
    response += f"📊 **Match Score:** {match_pct}%\n\n"

    if matching:
        response += f"✅ **Skills You Already Have ({len(matching)}):**\n"
        response += ", ".join(f"`{s}`" for s in matching[:10])
        response += "\n\n"

    if missing:
        critical = [s for s in missing if s.get("priority") == "Critical"]
        important = [s for s in missing if s.get("priority") == "Important"]
        nice = [s for s in missing if s.get("priority") == "Nice-to-have"]

        if critical:
            response += f"🔴 **Critical Skills to Learn ({len(critical)}):**\n"
            for s in critical:
                response += f"  • {s.get('skill', 'Unknown')}\n"
            response += "\n"

        if important:
            response += f"🟡 **Important Skills ({len(important)}):**\n"
            for s in important:
                response += f"  • {s.get('skill', 'Unknown')}\n"
            response += "\n"

        if nice:
            response += f"🟢 **Nice-to-Have ({len(nice)}):**\n"
            for s in nice[:5]:
                response += f"  • {s.get('skill', 'Unknown')}\n"
            response += "\n"

    response += "💡 _Focus on the Critical skills first to maximize your job readiness!_"
    return response


def _handle_ats_query(resume_data):
    """Generate response for ATS score queries.

    Args:
        resume_data (dict): Full resume analysis data.

    Returns:
        str: Formatted response about ATS score and improvement tips.
    """
    ats_data = resume_data.get("ats_score", {})

    if not ats_data:
        return ("📊 ATS score data isn't available yet. "
                "Make sure your resume has been analyzed!")

    overall = ats_data.get("overall_score", ats_data.get("score", 0))
    breakdown = ats_data.get("breakdown", ats_data.get("details", {}))
    suggestions = ats_data.get("suggestions", ats_data.get("improvements", []))

    response = f"📊 **Your ATS Compatibility Score: {overall}/100**\n\n"

    if breakdown:
        response += "📋 **Score Breakdown:**\n"
        for category, score in breakdown.items():
            category_display = category.replace("_", " ").title()
            if isinstance(score, (int, float)):
                bar_filled = int(score / 10)
                bar_empty = 10 - bar_filled
                bar = "█" * bar_filled + "░" * bar_empty
                response += f"  {category_display}: {bar} {score}%\n"
            else:
                response += f"  {category_display}: {score}\n"
        response += "\n"

    if suggestions:
        response += "💡 **Tips to Improve Your Score:**\n"
        for i, tip in enumerate(suggestions[:5], 1):
            if isinstance(tip, dict):
                response += f"  {i}. {tip.get('suggestion', tip.get('tip', str(tip)))}\n"
            else:
                response += f"  {i}. {tip}\n"
        response += "\n"
    else:
        response += "💡 **Quick Tips:**\n"
        response += "  1. Use industry-standard keywords throughout your resume\n"
        response += "  2. Include a clear 'Skills' section with relevant technologies\n"
        response += "  3. Quantify achievements with numbers and metrics\n"
        response += "  4. Use a clean, ATS-friendly format (avoid tables/graphics)\n"
        response += "  5. Tailor your resume for each job application\n"

    return response


def _handle_role_query(resume_data):
    """Generate response for job role queries.

    Args:
        resume_data (dict): Full resume analysis data.

    Returns:
        str: Formatted response about predicted job roles.
    """
    predictions = resume_data.get("predicted_roles", resume_data.get("role_predictions", []))

    if not predictions:
        return ("💼 Job role predictions aren't available yet. "
                "Please ensure your resume has been analyzed!")

    response = "💼 **Suitable Career Roles for You:**\n\n"

    for i, role in enumerate(predictions[:5], 1):
        if isinstance(role, dict):
            name = role.get("role", role.get("title", "Unknown"))
            confidence = role.get("confidence", role.get("match", ""))
            response += f"**{i}. {name}**"
            if confidence:
                response += f" — Confidence: {confidence}%"
            response += "\n"
        else:
            response += f"**{i}. {role}**\n"

    response += "\n💡 _These roles are based on your skills, experience, and education profile._"
    return response


def _handle_salary_query(resume_data):
    """Generate response for salary-related queries.

    Args:
        resume_data (dict): Full resume analysis data.

    Returns:
        str: Formatted response about salary predictions.
    """
    salary = resume_data.get("salary_prediction", {})

    if not salary:
        return ("💰 Salary prediction isn't available yet. "
                "Make sure your resume has been fully analyzed!")

    role = salary.get("role", "your role")
    exp_level = salary.get("experience_level", "unknown")
    base = salary.get("base_range", {})
    adjusted = salary.get("adjusted_range", {})
    unit = salary.get("unit", "LPA")
    factors = salary.get("factors", [])

    response = f"💰 **Salary Prediction for {role}:**\n\n"
    response += f"📊 **Experience Level:** {exp_level.capitalize()}\n\n"

    if base.get("min") and base.get("max"):
        response += f"📌 **Base Range:** ₹{base['min']} - ₹{base['max']} {unit}\n"

    if adjusted.get("min") and adjusted.get("max"):
        response += f"✨ **Adjusted Range:** ₹{adjusted['min']} - ₹{adjusted['max']} {unit}\n\n"

    if factors:
        response += "📋 **Factors Considered:**\n"
        for factor in factors:
            name = factor.get("name", "Unknown")
            impact = factor.get("impact", "N/A")
            response += f"  • {name}: {impact}\n"
        response += "\n"

    response += "💡 _Salary figures are estimates based on industry data and your profile._"
    return response


def _handle_interview_query(resume_data):
    """Generate response for interview preparation queries.

    Args:
        resume_data (dict): Full resume analysis data.

    Returns:
        str: Formatted response about interview preparation.
    """
    interview = resume_data.get("interview_questions", {})

    if not interview:
        return ("🎤 Interview questions aren't available yet. "
                "Make sure your resume has been analyzed!")

    total = interview.get("total_questions", 0)
    covered = interview.get("skills_covered", 0)
    questions = interview.get("questions", [])

    response = f"🎤 **Interview Preparation Guide:**\n\n"
    response += f"📊 **Total Questions:** {total} across {covered} skills\n\n"

    # Show a preview of questions for the first few skills
    for skill_qs in questions[:3]:
        skill = skill_qs.get("skill", "Unknown")
        beginner = skill_qs.get("beginner", [])
        intermediate = skill_qs.get("intermediate", [])
        advanced = skill_qs.get("advanced", [])

        response += f"**📚 {skill}** ({len(beginner) + len(intermediate) + len(advanced)} questions)\n"

        if beginner:
            response += f"  🟢 Beginner: _{beginner[0]}_\n"
        if intermediate:
            response += f"  🟡 Intermediate: _{intermediate[0]}_\n"
        if advanced:
            response += f"  🔴 Advanced: _{advanced[0]}_\n"
        response += "\n"

    if len(questions) > 3:
        response += f"_...and {len(questions) - 3} more skills covered!_\n\n"

    response += "💡 _Practice these questions to ace your interviews! Start with beginner-level and work your way up._"
    return response


def _handle_roadmap_query(resume_data):
    """Generate response for learning roadmap queries.

    Args:
        resume_data (dict): Full resume analysis data.

    Returns:
        str: Formatted response about the learning roadmap.
    """
    roadmap_data = resume_data.get("learning_roadmap", {})

    if not roadmap_data:
        return ("🗺️ Learning roadmap isn't available yet. "
                "Make sure your skill gap analysis has been completed!")

    total_months = roadmap_data.get("total_months", 0)
    roadmap = roadmap_data.get("roadmap", [])

    response = f"🗺️ **Your Personalized Learning Roadmap:**\n\n"
    response += f"⏱️ **Total Duration:** {total_months} months\n\n"

    for month_data in roadmap[:6]:
        month = month_data.get("month", "?")
        skills = month_data.get("skills", [])

        response += f"**📅 Month {month}:**\n"
        for skill in skills:
            name = skill.get("name", "Unknown")
            priority = skill.get("priority", "")
            courses = skill.get("courses", [])

            priority_emoji = {"Critical": "🔴", "Important": "🟡", "Nice-to-have": "🟢"}.get(priority, "⚪")
            response += f"  {priority_emoji} **{name}** ({priority})\n"

            if courses:
                top_course = courses[0]
                response += f"     📖 _{top_course.get('name', 'Course')}_ on {top_course.get('platform', 'Online')}\n"

        response += "\n"

    if len(roadmap) > 6:
        response += f"_...and {len(roadmap) - 6} more months of learning!_\n\n"

    response += "💡 _Consistency is key! Focus on 1-2 skills per month for the best results._"
    return response


def _handle_resume_query(resume_data):
    """Generate response for resume score breakdown queries.

    Args:
        resume_data (dict): Full resume analysis data.

    Returns:
        str: Formatted response about resume scoring.
    """
    resume_score = resume_data.get("resume_score", {})

    if not resume_score:
        return ("📄 Resume score breakdown isn't available yet. "
                "Make sure your resume has been analyzed!")

    overall = resume_score.get("overall_score", resume_score.get("total", 0))
    breakdown = resume_score.get("breakdown", resume_score.get("details", {}))

    response = f"📄 **Resume Score Breakdown:**\n\n"
    response += f"🏆 **Overall Score: {overall}/100**\n\n"

    if breakdown:
        response += "📋 **Category Scores:**\n"
        for category, score in breakdown.items():
            category_display = category.replace("_", " ").title()
            if isinstance(score, (int, float)):
                max_score = 30  # Default max
                bar_filled = min(int(score / 3), 10)
                bar_empty = 10 - bar_filled
                bar = "█" * bar_filled + "░" * bar_empty
                response += f"  {category_display}: {bar} {score}\n"
            else:
                response += f"  {category_display}: {score}\n"
        response += "\n"

    # General tips
    response += "💡 **General Resume Tips:**\n"
    response += "  • Keep your resume to 1-2 pages\n"
    response += "  • Use action verbs to describe achievements\n"
    response += "  • Include relevant keywords from job descriptions\n"
    response += "  • Quantify your accomplishments with numbers\n"
    response += "  • Proofread for grammar and spelling errors\n"

    return response


# ─── Core Chatbot Functions ──────────────────────────────

def _detect_intent(message):
    """Detect the user's intent from their message using keyword matching.

    Performs case-insensitive keyword matching against defined intent patterns.
    Returns the best matching intent based on keyword hit count.

    Args:
        message (str): The user's message.

    Returns:
        str or None: The detected intent key, or None for unknown.
    """
    message_lower = message.strip().lower()

    # Check for greeting first
    if any(kw in message_lower for kw in GREETING_KEYWORDS):
        return "greeting"

    # Score each intent by number of keyword matches
    best_intent = None
    best_score = 0

    for intent_name, intent_data in INTENTS.items():
        score = 0
        for keyword in intent_data["keywords"]:
            if keyword in message_lower:
                score += 1
        if score > best_score:
            best_score = score
            best_intent = intent_name

    return best_intent if best_score > 0 else None


def get_response(user_message, resume_data):
    """Process a user message and generate a contextual response.

    Uses keyword-based intent detection to understand the user's query
    and generates a formatted response using the resume analysis data.

    Args:
        user_message (str): The user's chat message.
        resume_data (dict): Dictionary containing all resume analysis results.
            Expected keys include: recommended_companies, skill_gap, ats_score,
            predicted_roles, salary_prediction, interview_questions,
            learning_roadmap, resume_score.

    Returns:
        str: A formatted, conversational response string.
    """
    if not user_message or not user_message.strip():
        return "❓ It looks like you sent an empty message. Try asking me something!"

    if not resume_data or not isinstance(resume_data, dict):
        return ("⚠️ I don't have any resume analysis data to work with yet. "
                "Please upload and analyze your resume first!")

    # Detect intent
    intent = _detect_intent(user_message)

    # Route to appropriate handler
    if intent == "greeting":
        return GREETING_RESPONSE

    # Map intent to handler
    handler_map = {
        "company": _handle_company_query,
        "skill_gap": _handle_skill_gap_query,
        "ats": _handle_ats_query,
        "role": _handle_role_query,
        "salary": _handle_salary_query,
        "interview": _handle_interview_query,
        "roadmap": _handle_roadmap_query,
        "resume": _handle_resume_query,
    }

    handler = handler_map.get(intent)

    if handler:
        try:
            return handler(resume_data)
        except Exception as e:
            return f"⚠️ Oops! Something went wrong while processing your query: {str(e)}\nPlease try again!"

    # Fallback for unrecognized queries
    return FALLBACK_RESPONSE
