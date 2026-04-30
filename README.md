# 🧠 AI Resume Risk Analyzer

An AI-powered web application that analyzes resumes and identifies potential interview risks using Large Language Models (LLMs). It helps candidates improve their resume quality by highlighting weak claims and suggesting better versions.

---

## 🚀 Live Demo

👉 https://your-app.streamlit.app

---

## 📌 Features

* 🔍 Extracts key technical claims from uploaded resumes (PDF)
* 🤖 Uses Groq LLaMA 3.1 to evaluate interview risk
* 🎯 Classifies each claim into:

  * 🟢 Low Risk
  * 🟡 Medium Risk
  * 🔴 High Risk
* 💡 Provides improved versions of weak statements
* 🎤 Generates realistic interviewer questions
* 📊 Calculates overall resume strength score

---

## 🧠 How It Works

1. Upload your resume (PDF)
2. Extract text from the document
3. Identify important technical claims
4. Evaluate each claim using LLM
5. Display:

   * Risk level
   * Reason
   * Interview questions
   * Improvement suggestions

---

## 🏗️ Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python
* **LLM API**: Groq (LLaMA 3.1)
* **Deployment**: Streamlit Cloud
* **Libraries**:

  * python-dotenv
  * JSON processing

---

## 📁 Project Structure

resume-risk-analyzer/
│
├── app.py
├── requirements.txt
├── .env (not included)
│
├── prompts/
│   ├── extract_prompt.txt
│   └── confusion_prompt.txt
│
├── utils/
│   └── pdf_parser.py

---

## 🚀 Future Improvements

* Resume auto-rewrite feature
* Downloadable report (PDF)
* Better UI/UX design
* Multi-language support

---

## 👨‍💻 Author

Aasish
B.Tech CSE Student
