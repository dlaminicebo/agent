# streamlit_app.py
import os
import streamlit as st
from dotenv import load_dotenv
import openai
from tavily import TavilyClient

# 1) Load .env into os.environ
load_dotenv()

# 2) Pull keys from environment variables
openai.api_key      = os.getenv("OPENAI_API_KEY")
tavily_client       = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# ----- LLM Function -----
def generate_questions(topic):
    prompt = f"""
    Generate 5-6 in-depth research questions about the topic: "{topic}".
    Cover causes, effects, data, solutions, and controversies.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or gpt-4 if available
            messages=[{"role": "user", "content": prompt}]
        )
        content = response['choices'][0]['message']['content']
        questions = content.strip().split("\n")
        return [q.strip("- ").strip() for q in questions if q.strip()]
    except Exception as e:
        st.error(f"Error with OpenAI: {e}")
        return []

# ----- Web Search Function -----
def search_web(question):
    try:
        results = tavily_client.search(query=question, max_results=5)
        return results.get("results", [])
    except Exception as e:
        st.error(f"Web search error: {e}")
        return []

# ----- Report Generator -----
def generate_report(topic, qna):
    report = f"# Research Report: {topic}\n\n"
    report += f"## Introduction\nThis report explores the topic \"{topic}\" through a series of structured research questions and answers.\n\n"
    for q, answers in qna.items():
        report += f"## {q}\n"
        for a in answers:
            title = a.get("title")
            content = a.get("content")
            url = a.get("url")
            report += f"- **{title}**: {content}\n  [Read More]({url})\n"
        report += "\n"
    report += "## Conclusion\nThis report compiles recent online resources and data to provide a well-rounded view of the topic."
    return report

# ----- Streamlit App -----
st.title("🌐 Web Research Agent (ReAct Pattern)")

topic = st.text_input("Enter a research topic:")

if st.button("Generate Report"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Generating research questions..."):
            questions = generate_questions(topic)
            st.success("Questions generated!")

        qna = {}
        with st.spinner("Searching the web for answers..."):
            for q in questions:
                st.write(f"🔍 {q}")
                results = search_web(q)
                qna[q] = results

        with st.spinner("Compiling report..."):
            report_md = generate_report(topic, qna)

        # Display the report
        st.markdown("---")
        st.markdown(report_md)

        # Download button
        st.download_button(
            label="📥 Download Report as Markdown",
            data=report_md,
            file_name=f"{topic.replace(' ', '_')}_report.md",
            mime="text/markdown"
        )
