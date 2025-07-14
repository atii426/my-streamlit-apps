import streamlit as st
import feedparser
import re
import trafilatura # ★追加: trafilaturaをインポート

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
    if not text:
        return "⚠️ 要約できるテキストがありません。"
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
            article_text = ""
            image_url = ""
            try:
                # ★trafilaturaを使って記事の詳細を解析★
                downloaded = trafilatura.fetch_url(entry.link)
                if downloaded:
                    # 記事の本文を抽出
                    article_text = trafilatura.extract(downloaded, include_images=True, include_links=False)
                    # 画像URLはtrafilaturaでは直接取得しにくいので、RSSのenclosuresから試みる
                    if hasattr(entry, 'enclosures') and entry.enclosures:
                        for enc in entry.enclosures:
                            if 'image' in enc.type:
                                image_url = enc.href
                                break
                    # もしenclosuresになければ、記事本文から最初の画像を探す（簡易的）
                    if not image_url and article_text:
                        # ここはtrafilaturaの機能ではなく、簡易的な正規表現などになるため、
                        # 確実性はありません。必要であれば、より高度なHTMLパースが必要です。
                        # 例: <img src="(.*?)"
                        pass # 今回は省略し、enclosuresを優先

            except Exception as e:
                print(f"記事の解析に失敗しました ({entry.link}): {e}")
                article_text = "" # エラー時はテキストを空にする
                image_url = ""

            summary = simple_summary(article_text)
            if not summary or summary == "⚠️ 要約できるテキストがありません。":
                summary = "⚠️ 要約できませんでした。記事リンクから直接お読みください。"


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
