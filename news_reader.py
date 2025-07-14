import streamlit as st
import feedparser
from newspaper import Article
import re

# -----------------------------
# RSSカテゴリ辞書
# -----------------------------
CATEGORIES = {
    "トップ": "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
    "国内": "https://news.yahoo.co.jp/rss/topics/domestic.xml",
    "国際": "https://news.yahoo.co.jp/rss/topics/world.xml",
    "経済": "https://news.yahoo.co.jp/rss/topics/business.xml",
    "IT・科学": "https://news.yahoo.co.jp/rss/topics/it.xml",
    "スポーツ": "https://news.yahoo.co.jp/rss/topics/sports.xml",
    "エンタメ": "https://news.yahoo.co.jp/rss/topics/entertainment.xml",
    "地域": "https://news.yahoo.co.jp/rss/topics/local.xml",
    "主要": "https://news.yahoo.co.jp/rss/topics/main.xml",
}

# -----------------------------
# 要約（簡易）関数
# -----------------------------
def simple_summary(text, max_sentences=3):
    """
    与えられたテキストを簡易的に要約します。
    """
    sentences = re.split(r'(?<=[。！？])\s*', text)
    return " ".join(sentences[:max_sentences])

# -----------------------------
# ニュース取得
# -----------------------------
@st.cache_data(ttl=1800) # 30分キャッシュ
def fetch_news(rss_url):
    """
    指定されたRSSフィードからニュースを取得します。
    """
    try:
        feed = feedparser.parse(rss_url)
        # bozoが1の場合はパースエラーがあることを示す
        if feed.bozo:
            print(f"RSSフィードのパースエラー: {feed.bozo_exception}")
            return []
        return feed.entries[:10] # 最新の10件を取得
    except Exception as e:
        print(f"ニュースの取得中にエラーが発生しました: {e}")
        return []

# -----------------------------
# ページ設定
# -----------------------------
st.set_page_config(page_title="今日のニュースまとめ", layout="wide")
st.title("📰 今日のニュースまとめ")
st.markdown("Yahooニュースをカテゴリごとに表示し、要約と画像をつけて紹介します。")

# -----------------------------
# タブ
# -----------------------------
tabs = st.tabs(list(CATEGORIES.keys()))

for i, (category, rss_url) in enumerate(CATEGORIES.items()):
    with tabs[i]:
        st.subheader(f"📂 {category}カテゴリのニュース")
        entries = fetch_news(rss_url)

        if not entries:
            st.warning("⚠️ ニュースの取得に失敗しました。RSSフィードを確認してください。")
            continue

        for entry in entries:
            try:
                # newspaper3kで記事の詳細を解析
                article = Article(entry.link, language='ja')
                article.download()
                article.parse()
                summary = simple_summary(article.text)
                image_url = article.top_image
            except Exception as e:
                # 記事の解析に失敗した場合のフォールバック
                print(f"記事の解析に失敗しました ({entry.link}): {e}")
                summary = "⚠️ 要約できませんでした。記事リンクから直接お読みください。"
                image_url = "" # 画像も取得できない場合は空にする

            with st.expander(entry.title):
                cols = st.columns([1, 3])
                with cols[0]:
                    if image_url:
                        st.image(image_url, use_container_width=True, caption="記事画像")
                    else:
                        st.markdown("（画像なし）")
                with cols[1]:
                    st.markdown(f"🔗 [記事を読む]({entry.link})", unsafe_allow_html=True)
                    st.markdown("📝 **要約**")
                    st.write(summary)

st.markdown("---")
st.info("このニュースリーダーは、Streamlitで構築されています。")