# -*- coding: utf-8 -*-
# file: drikn_song_bot_explain.py
from dotenv import load_dotenv
import os
import streamlit as st
import requests

# 환경변수 불러오기
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

DRINK_INFO = {
    "'월요일'": "'월래 마십니다.'",
    "'화요일'": "'화가 나서 마십니다.'",
    "'수요일'": "'수금해서 마십니다.'",
    "'목요일'": "'목말라서 마십니다.'",
    "'금요일'": "'금방 먹고 또 먹습니다.'"
}

def search_song_videos(drink: str, max_results: int = 30) -> list:
    """음주 관련 노래 영상을 검색"""
    query = drink + " 술 노래"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    resp = requests.get(YOUTUBE_SEARCH_URL, params=params)
    resp.raise_for_status()
    data = resp.json()

    video_links = []
    if "items" in data and len(data["items"]) > 0:
        for item in data["items"]:
            video_id = item["id"]["videoId"]
            video_links.append(f"https://www.youtube.com/watch?v={video_id}")
    return video_links

# Streamlit UI
st.title("'음주 노래 챗봇'")
st.write("'요일을 선택하세요'")

# 버튼 UI
for drink in DRINK_INFO.keys():
    if st.button(drink):
        st.subheader(f"{drink}의 의미")
        st.info(DRINK_INFO[drink])

        video_links = search_song_videos(drink, max_results=2)
        if video_links:
            st.success(f"'{drink} 노래를 들어보세요 🎵'")
            for link in video_links:
                st.video(link)
        else:
            st.error("관련 영상을 찾을 수 없습니다.")

print("API_KEY:", YOUTUBE_API_KEY)