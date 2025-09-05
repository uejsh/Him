import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import openai

# ---- SET YOUR API KEY ----
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Vision + Execution Tracker with AI Insight Summaries")

# --- Initialize session state ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Task", "Insights Count", "Insight Value", "Products Shipped", "Weight",
        "Score", "Vision Score", "Execution Score", "Vision-to-Execution Ratio", "Timestamp"
    ])
if "reflections" not in st.session_state:
    st.session_state.reflections = []
if "ai_insights" not in st.session_state:
    st.session_state.ai_insights = []

# --- Input Section ---
st.header("Log a Session")
task = st.text_input("Task Name / Description")
insights_count = st.number_input("Number of Insights", min_value=0, step=1)
insight_value = st.number_input("Value per Insight", min_value=0.0, step=0.1)
products_shipped = st.number_input("Products Shipped (pages/functions/etc)", min_value=0, step=1)
weight = st.number_input("Weight per Product", min_value=0.0, step=0.1)

if st.button("Add Session"):
    vision_score = insights_count * insight_value
    execution_score = products_shipped * weight
    total_score = vision_score + execution_score
    ratio = vision_score / execution_score if execution_score != 0 else None
    timestamp = datetime.now()
    new_row = {
        "Task": task,
        "Insights Count": insights_count,
        "Insight Value": insight_value,
        "Products Shipped": products_shipped,
        "Weight": weight,
        "Score": total_score,
        "Vision Score": vision_score,
        "Execution Score": execution_score,
        "Vision-to-Execution Ratio": ratio,
        "Timestamp": timestamp
    }
    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
    st.success(f"Session added! Total Score: {total_score}, Ratio: {ratio}")

# --- Session Log ---
st.header("Session Log")
st.dataframe(st.session_state.data)

# --- Daily Summary ---
if not st.session_state.data.empty:
    total_vision = st.session_state.data["Vision Score"].sum()
    total_execution = st.session_state.data["Execution Score"].sum()
    total_score = st.session_state.data["Score"].sum()
    avg_ratio = st.session_state.data["Vision-to-Execution Ratio"].dropna().mean()
    st.subheader("Daily Summary")
    st.write(f"Total Vision Score: {total_vision}")
    st.write(f"Total Execution Score: {total_execution}")
    st.write(f"Total Weighted Productivity Score: {total_score}")
    st.write(f"Average Vision-to-Execution Ratio: {avg_ratio:.2f}")

    # --- Charts ---
    vision_chart = alt.Chart(st.session_state.data).mark_bar(color='blue').encode(
        x=alt.X('Task', sort=None),
        y='Vision Score',
        tooltip=['Task', 'Vision Score']
    ).properties(title='Vision Score per Task')
    
    execution_chart = alt.Chart(st.session_state.data).mark_bar(color='green').encode(
        x=alt.X('Task', sort=None),
        y='Execution Score',
        tooltip=['Task', 'Execution Score']
    ).properties(title='Execution Score per Task')
    
    st.altair_chart(vision_chart, use_container_width=True)
    st.altair_chart(execution_chart, use_container_width=True)

# --- 10-Hour Daily Progress ---
st.header("10-Hour Daily Progress")
max_hours = 10
progress_fraction = min(total_score / max_hours, 1.0) if 'total_score' in locals() else 0
st.session_state.progress_fraction = progress_fraction
completed_hours = int(progress_fraction * max_hours)
hour_display = ["🟩" if i < completed_hours else "⬜" for i in range(max_hours)]
st.write("Hourly Progress:", "".join(hour_display))
st.progress(progress_fraction)
st.write(f"Progress toward 10-hour goal: {progress_fraction*100:.1f}%")

# --- End-of-Day Reflection ---
st.header("End-of-Day Reflection")
if progress_fraction >= 1.0:
    st.subheader("Congratulations! You've completed your 10-hour goal.")
    reflection = st.text_area("Write your reflection for today (lessons, patterns, improvements):")
    if st.button("Save Reflection"):
        if reflection.strip() != "":
            st.session_state.reflections.append({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Reflection": reflection
            })
            st.success("Reflection saved!")
        else:
            st.warning("Please write something before saving.")

    if st.session_state.reflections:
        st.subheader("Previous Reflections")
        for r in st.session_state.reflections[::-1]:
            st.markdown(f"**{r['Date']}**: {r['Reflection']}")
else:
    st.info("Complete your 10-hour goal to unlock the daily reflection session.")

# --- AI-Powered Insight Logging ---
st.header("Log Your Insights for AI Feedback")

new_insights = st.text_area("Enter your insights (one per line)")

if st.button("Submit Insights"):
    if new_insights.strip() != "":
        insights_list = [line.strip() for line in new_insights.split("\n") if line.strip()]
        st.session_state.ai_insights.extend(insights_list)

        prompt = "Here are the insights I logged today:\n"
        for i, insight in enumerate(insights_list, 1):
            prompt += f"{i}. {insight}\n"
        prompt += "\nPlease do three things: 1) Summarize these insights concisely, 2) Provide a direct, encouraging comment with no fluff, 3) Suggest new insights or patterns I may have missed."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a direct, encouraging, and insightful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.7
            )
            ai_output = response.choices[0].message.content.strip()
            st.subheader("AI Summary, Comment & New Insights")
            st.markdown(ai_output)
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
    else:
        st.warning("Please enter at least one insight before submitting.")

# --- Display all logged insights ---
if st.session_state.ai_insights:
    st.subheader("All Logged Insights")
    for idx, insight in enumerate(st.session_state.ai_insights[::-1], 1):
        st.markdown(f"{idx}. {insight}")
