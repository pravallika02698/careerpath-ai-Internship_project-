# CareerPath AI

CareerPath AI is an AI-powered career guidance platform developed to help students, fresh graduates, and job seekers make informed career decisions. The application uses Artificial Intelligence (AI) and Natural Language Processing (NLP) to analyze resumes and provide personalized career recommendations. It evaluates resumes, predicts suitable job roles, recommends companies, identifies skill gaps, estimates salary ranges, generates learning roadmaps, and assists users with interview preparation.

---

# Problem Statement

Many students and fresh graduates face difficulties while starting their careers because they lack proper guidance and personalized recommendations. Some of the common challenges include:

- Not knowing whether their resume is ATS (Applicant Tracking System) friendly.
- Difficulty in identifying job roles that match their skills and qualifications.
- Lack of awareness about companies suitable for their profile.
- Inability to identify missing technical and soft skills.
- Uncertainty about expected salary for different job roles.
- Limited resources for interview preparation.

CareerPath AI addresses these challenges by using Artificial Intelligence and Natural Language Processing to automate resume analysis and provide intelligent career guidance.

---

# Project Objectives

The main objectives of this project are:

- Analyze resumes automatically.
- Extract candidate information from resumes.
- Predict suitable job roles.
- Recommend companies based on user skills.
- Identify missing skills required for target careers.
- Generate personalized learning roadmaps.
- Provide interview preparation support.
- Estimate salary ranges for recommended job roles.

---

# Key Features

### Resume Upload

Users can upload their resumes in PDF format for analysis.

### Resume Parsing

The application extracts important information such as name, education, skills, experience, certifications, and projects using Natural Language Processing.

### ATS Score Analysis

The system calculates the ATS compatibility score and provides suggestions to improve the resume.

### Job Role Prediction

Based on the extracted skills and qualifications, the application predicts suitable job roles.

### Company Recommendation

The system recommends companies that match the user's skills and preferred job roles.

### Skill Gap Analysis

The application compares existing skills with industry requirements and identifies missing skills that need improvement.

### Salary Prediction

CareerPath AI estimates the expected salary range based on the candidate's skills, experience, and selected job role.

### Learning Roadmap

The system generates a personalized roadmap to help users learn the required skills for their desired career.

### Interview Preparation

The application generates technical and HR interview questions to help users prepare for job interviews.

### AI Career Chatbot

An AI-powered chatbot provides career guidance and answers user queries related to jobs, skills, and career growth.

---

# Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend Development |
| Streamlit | Web Application Development |
| PDFPlumber | Resume Text Extraction |
| spaCy NER | Resume Parsing |
| Scikit-Learn | TF-IDF and Similarity Matching |
| Plotly | Interactive Data Visualization |
| JSON | Job and Company Database |

---

# System Workflow

```
Resume Upload
      │
      ▼
PDF Text Extraction
      │
      ▼
Resume Parsing (spaCy NER)
      │
      ▼
Resume Analysis Engine
      │
 ┌────┼────┬─────┬─────┐
 ▼    ▼    ▼     ▼     ▼
ATS  Job  Company Skill Salary
Score Role Match  Gap   Prediction
      │
      ▼
Roadmap Generator
      │
      ▼
Interview Question Generator
      │
      ▼
AI Career Chatbot
```

---

# Benefits

CareerPath AI provides several benefits to students, fresh graduates, and job seekers:

- Improves resume quality through ATS analysis.
- Provides personalized career recommendations.
- Helps users identify missing skills.
- Recommends suitable companies for job applications.
- Generates customized learning roadmaps.
- Assists in interview preparation.
- Estimates expected salary ranges.
- Saves time by automating resume analysis.

---

# Future Enhancements

The project can be enhanced with the following features:

- LinkedIn profile integration.
- Real-time job portal integration.
- AI-powered resume builder.
- Mock interview simulator.
- Resume ranking based on job descriptions.
- Email notifications for job opportunities.
- Multi-language resume analysis.
- Cloud deployment with secure user authentication.

---

# Conclusion

CareerPath AI is an intelligent career guidance system that combines Artificial Intelligence and Natural Language Processing to simplify the career planning process. It helps users analyze their resumes, identify suitable job opportunities, improve their skills, estimate salary expectations, and prepare for interviews. By providing personalized recommendations and actionable insights, CareerPath AI bridges the gap between academic qualifications and industry requirements, enabling users to make informed career decisions and enhance their employability.
