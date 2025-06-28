import streamlit as st
import pandas as pd
import plotly.express as px
import helper
import preprocessor


st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")


light_theme_css = """
    <style>
        body { background-color: #f8f9fa; color: #212529; }
        .stApp { background-color: #ffffff; }
        .css-18e3th9 { background-color: #ffffff; }
        .css-1d391kg { background-color: #ffffff; }
        .css-1vbkxwb { color: #212529; }
        .stTabs [role="tablist"] { background-color: #e9ecef; }
    </style>
"""
st.markdown(light_theme_css, unsafe_allow_html=True)


st.sidebar.image("logo.png", width=200)
st.sidebar.title("WhatsApp Chat Analyzer 📊")

uploaded_file = st.sidebar.file_uploader("Upload your chat file", type=["txt"])

if uploaded_file is not None:
   
    data = uploaded_file.getvalue().decode("utf-8")
    df = preprocessor.preprocess(data)


    user_list = df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Select User", user_list)

 
    tabs = st.tabs(["Overview", "Activity Insights", "Message Analysis", "Emoji & Sentiment"])
    
    with tabs[0]:  # Overview
        st.title("Chat Analysis Dashboard 🏆")
        num_messages, words, media, links = helper.fetch_stats(selected_user, df)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Messages", num_messages)
        col2.metric("Total Words", words)
        col3.metric("Media Shared", media)
        col4.metric("Links Shared", links)
    
    with tabs[1]:  # Activity Insights
        st.subheader("📅 Monthly Activity")
        timeline = helper.monthly_timeline(selected_user, df)
        fig = px.line(timeline, x="time", y="message", title="Messages Per Month", markers=True)
        st.plotly_chart(fig)
        
        st.subheader("📆 Daily Activity")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig = px.line(daily_timeline, x="only_date", y="message", title="Messages Per Day", markers=True)
        st.plotly_chart(fig)
        
        st.subheader("📊 Weekly Activity")
        week_activity = helper.week_activity_map(selected_user, df)
        fig = px.bar(week_activity, x=week_activity.index, y=week_activity.values, title="Messages by Day of the Week")
        st.plotly_chart(fig)
        
        st.subheader("📊 Monthly Activity")
        month_activity = helper.month_activity_map(selected_user, df)
        fig = px.bar(month_activity, x=month_activity.index, y=month_activity.values, title="Messages by Month")
        st.plotly_chart(fig)
        
        st.subheader("🔥 Activity Heatmap")
        heatmap = helper.activity_heatmap(selected_user, df)
        st.dataframe(heatmap.style.background_gradient(cmap='Blues'))
    
    with tabs[2]:  # Message Analysis
        st.subheader("💙 Most Active Users")
        user_counts, user_percent = helper.most_busy_users(df)
        col1, col2 = st.columns(2)
        col1.bar_chart(user_counts)
        col2.dataframe(user_percent)
        
        st.subheader("☁️ Word Cloud")
        wordcloud = helper.create_wordcloud(selected_user, df)
        st.image(wordcloud.to_array())
        
        st.subheader("📢 Most Common Words")
        common_words = helper.most_common_words(selected_user, df)
        fig = px.bar(common_words, x=0, y=1, labels={'x': 'Word', 'y': 'Count'}, title="Most Common Words")
        st.plotly_chart(fig)
    
    with tabs[3]:  # Emoji & Sentiment Analysis
        st.subheader("😃 Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        if not emoji_df.empty:
            emoji_df.columns = ['Emoji', 'Count']
            fig = px.bar(emoji_df, x="Emoji", y="Count", title="Emoji Frequency")
            st.plotly_chart(fig)
        else:
            st.write("No emojis found!")
        
        st.subheader("📈 Sentiment Analysis")
        sentiment_counts, most_positive, most_negative = helper.analyze_sentiment(selected_user, df)
        fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title="Sentiment Distribution")
        st.plotly_chart(fig)
        
        st.subheader("🌟 Most Positive Message")
        st.write(most_positive[['user', 'message']])
        
        st.subheader("💀 Most Negative Message")
        st.write(most_negative[['user', 'message']])
