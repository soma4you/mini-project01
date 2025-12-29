# holiday_song_bot_openai_quiz.py
from dotenv import load_dotenv
import os
import streamlit as st
import requests
from openai import OpenAI

# 환경변수 불러오기
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

HOLIDAY_INFO = {
    "3.1절": (
        "1919년 3월 1일, 독립선언서를 낭독하며 대한독립 만세를 외친 날입니다. "
        "이 운동은 전국적으로 확산되어 일제에 대한 민족적 저항을 상징하게 되었습니다. "
        "3.1운동은 대한민국 임시정부 수립에도 큰 영향을 미친 역사적 사건입니다."
    ),
    "제헌절": (
        "1948년 7월 17일, 대한민국 헌법이 제정·공포된 것을 기념하는 날입니다. "
        "이 헌법은 대한민국 정부 수립의 근간이 되는 중요한 역할을 했습니다. "
        "제헌절은 국가의 민주주의와 법치주의의 출발점을 되새기는 의미를 지닙니다."
    ),
    "광복절": (
        "1945년 8월 15일, 일본의 식민 지배에서 벗어나 광복을 맞이한 날입니다. "
        "이 날은 우리 민족이 주권을 되찾은 역사적 전환점입니다. "
        "광복의 기쁨과 함께 분단의 현실이 시작된 복합적인 의미를 담고 있습니다."
    ),
    "개천절": (
        "기원전 2333년, 10월 3일, 단군이 우리 민족 최초의 국가 고조선을 세운 것을 기념하는 날입니다. "
        "하늘이 열린 뜻을 기리는 의미에서 ‘개천절’이라 부릅니다. "
        "민족의 시원을 기념하며 공동체 정신을 되새기는 날입니다."
    ),
    "한글날": (
        "1446년, 10월 9일, 세종대왕이 훈민정음을 반포한 것을 기념하는 날입니다. "
        "한글은 백성을 위해 창제된 과학적이고 독창적인 문자로 평가받고 있습니다. "
        "이 날은 우리의 언어와 문화적 자긍심을 되새기는 중요한 의미를 지닙니다."
    )
}

def search_song_videos(holiday: str, max_results: int = 10) -> list:
    """국경일 관련 노래 영상을 여러 개 검색(재생 불가 영상 제외)"""
    query = holiday + " 노래"
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

def generate_quiz(holiday: str, info: str):
    """OpenAI API를 활용하여 국경일 퀴즈 생성"""
    prompt = f"""
    당신은 한국 국경일 학습용 퀴즈 제작자입니다.
    국경일: {holiday}
    설명: {info}

    위 정보를 바탕으로 3개의 객관식 퀴즈를 만들어주세요.
    질문은 <문제 1>, <문제 2>, <문제 3>으로 하세요.
    
    질문: ...
    
    보기:
    1. ...\n 2. ...\n 3. ...\n 4. ...

    *****
    정답: ...
    *****
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def holiday() :
    # Streamlit UI
    st.title("즐거운 공휴일")
    st.write("'국경일'을 선택하면 의미 설명, 관련 노래 영상, 그리고 OpenAI가 만든 퀴즈를 즐길 수 있습니다 🎶📝")

    # 인물 사진 매핑 (로컬 파일 경로) 
    HOLIDAY_IMAGES = {
        "3.1절": "images_holiday/t유관순.jpg", # 유관순 열사 
        "제헌절": "images_holiday/j제헌절.jpg", # 제헌절 이미지 
        "광복절": "images_holiday/광복절 위인.jpg", # 광복절 이미지
        "개천절": "images_holiday/단군신화.jpg", # 단군 (상징 이미지) 
        "한글날": "images_holiday/세종대왕.jpg" # 세종대왕
    }   

    # 버튼 UI
    for holiday in HOLIDAY_INFO.keys():
        if st.button(holiday):
            st.subheader(f"{holiday}의 의미")
            st.info(HOLIDAY_INFO[holiday])

            # 인물 사진 표시 (퀴즈 위에) 
            if holiday in HOLIDAY_IMAGES: 
                st.subheader("관련 그림 / 사진 자료 📷")
                st.image(HOLIDAY_IMAGES[holiday], caption=f"{holiday} 관련 인물", width=300)

            # 영상 표시
            video_links = search_song_videos(holiday, max_results=3)
            if video_links:
                st.success(f"{holiday}을 기념하는 노래들을 들어보세요 🎵")
                for link in video_links:
                    st.video(link)
            else:
                st.error("관련 영상을 찾을 수 없습니다.")
                
            # 퀴즈 생성
            st.subheader("퀴즈 🎯")
            quiz_text = generate_quiz(holiday, HOLIDAY_INFO[holiday])
            st.write(quiz_text)

