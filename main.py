import os
import streamlit as st
from kakao import *
from holiday import *
from tarot_app import *

#  홈 버튼
def home_button() :
    if st.button("홈으로 돌아가기", key="home_btn"):
        st.session_state.view = "home"
        st.session_state.selected_tool = None
        st.rerun()


# 세션 상태 초기화
if "view" not in st.session_state:
    st.session_state.view = "home"

if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = None

# 홈 화면
if st.session_state.view == "home":
    st.title("일기일회조 미니 팀프로젝트")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### Chat2Animal")
        st.write("팀장 : 김동명님")
        st.write("조원 : 배수아님, 유미숙님")

    with col2:
        st.write("##### 고민될 떈, 타로챗봇")
        st.write("팀장 : 추승균님")
        st.write("조원 : 강현석님, 이다원님")
        
    with col3:
        st.write("##### 공휴일은 즐거워")
        st.write("팀장 : 이현숙님")
        
    # 세션 변경 버튼
    if st.button("시작하기", key="start_btn"):
        st.session_state.view = "tool"
        st.rerun()

    # 일기일회 이미지
    st.markdown(" ")
      # 불러올 이미지 파일명
    image_name = "일기일회1.png" 
    image_path = os.path.join(image_name)
    st.image(image_path, width=600)
    

# 툴 선택 화면

else:
    
   # 사이드바
    st.sidebar.title("주제 선택")

    st.session_state.selected_tool = st.sidebar.radio(
        "실행할 주제를 선택하세요",
        ("Chat2Animal", "고민될 땐, 타로챗봇", "공휴일은 즐거워"),
        key="tool_radio"
    )

    # 선택 결과 실행
    if st.session_state.selected_tool == "Chat2Animal":
        home_button()
        kakao()

    elif st.session_state.selected_tool == "고민될 땐, 타로챗봇":
        tarot_app()
        home_button()

    elif st.session_state.selected_tool == "공휴일은 즐거워":
        home_button()
        holiday()


