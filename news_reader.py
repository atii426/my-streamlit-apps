import streamlit as st
import feedparser
import re
import trafilatura
import requests
from datetime import datetime

# --- ここまであなたのニュースコード（CATEGORIES辞書など） ---

# 天気表示用関数
def show_weather():
    cities = {
        "東京 (Tokyo)": "Tokyo",
        "大阪 (Osaka)": "Osaka",
        "札幌 (Sapporo)": "Sapporo",
        "福岡 (Fukuoka)": "Fukuoka",
        "名古屋 (Nagoya)": "Nagoya",
        "京都 (Kyoto)": "Kyoto",
        "仙台 (Sendai)": "Sendai",
        "広島 (Hiroshima)": "Hiroshima",
        "高松 (Takamatsu)": "Takamatsu"
    }

    st.subheader("🌤 天気予報")
    city_name = st.selectbox("都市を選択してください", list(cities.keys()))
    city_query = cities[city_name]

    API_KEY = "e58c5125dd084212ab081525250807"

    if st.button("天気を取得"):
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city_query}&days=7&lang=ja"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            location = data["location"]["name"]
            st.markdown(f"### {location}の7日間の天気予報")
            forecast_days = data["forecast"]["forecastday"]
            for day in forecast_days:
                date = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%m/%d (%a)")
                condition = day["day"]["condition"]["text"]
                icon_url = "https:" + day["day"]["condition"]["icon"]
                max_temp = day["day"]["maxtemp_c"]
                min_temp = day["day"]["mintemp_c"]
                st.markdown(f"#### {date}")
                st.image(icon_url, width=64)
                st.write(f"天気: {condition}")
                st.write(f"最高気温: {max_temp}℃  最低気温: {min_temp}℃")
                st.markdown("---")
        else:
            st.error("天気情報の取得に失敗しました。")

# --- ページ設定、ニュース表示は元のまま ---

st.set_page_config(page_title="今日のニュースまとめ", layout="wide")
st.title("📰 今日のニュースまとめ")
st.markdown("Yahooニュースをカテゴリごとに表示し、要約と画像をつけて紹介します。")

# --- 天気を見るボタン ---
if st.button("🌤 天気を見る"):
    show_weather()

# --- 既存のニュースタブ表示コード（省略せず入れてください） ---
tabs = st.tabs(list(CATEGORIES.keys()))
for i, (category, rss_url) in enumerate(CATEGORIES.items()):
    with tabs[i]:
        st.subheader(f"📂 {category}カテゴリのニュース")
        entries = fetch_news(rss_url)
        # (ニュース表示のコードをここに入れる)

st.markdown("---")
st.info("このニュースリーダーは、Streamlitで構築されています。")