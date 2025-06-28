from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
from textblob import TextBlob

extract = URLExtract()

def analyze_sentiment(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    # Compute sentiment polarity
    df['sentiment_score'] = df['message'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)

    # Categorize sentiment
    df['sentiment'] = df['sentiment_score'].apply(
        lambda score: "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"
    )

    # Get sentiment distribution
    sentiment_counts = df['sentiment'].value_counts()

    # Find most positive and most negative messages
    most_positive = df[df['sentiment'] == "Positive"].sort_values(by="sentiment_score", ascending=False).head(1)
    most_negative = df[df['sentiment'] == "Negative"].sort_values(by="sentiment_score").head(1)

    return sentiment_counts, most_positive, most_negative

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    num_messages = df.shape[0]
    words = [word for message in df['message'] for word in str(message).split()]
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    links = [url for message in df['message'] for url in extract.find_urls(str(message))]

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df_percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    df_percent.columns = ['name', 'percent']
    return x, df_percent

def create_wordcloud(selected_user, df):
    try:
        with open('stop_hinglish.txt', 'r') as f:
            stop_words = f.read()
    except FileNotFoundError:
        stop_words = ""

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')].copy()
    temp['message'] = temp['message'].apply(lambda msg: " ".join([word for word in str(msg).lower().split() if word not in stop_words]))

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    try:
        with open('stop_hinglish.txt', 'r') as f:
            stop_words = f.read()
    except FileNotFoundError:
        stop_words = ""

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')].copy()
    words = [word for message in temp['message'] for word in str(message).lower().split() if word not in stop_words]
    return pd.DataFrame(Counter(words).most_common(20))

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    emojis = [c for message in df['message'] for c in str(message) if c in emoji.EMOJI_DATA]
    return pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline.apply(lambda row: f"{row['month']}-{row['year']}", axis=1)
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    return df.groupby('only_date').count()['message'].reset_index()

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    return df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
