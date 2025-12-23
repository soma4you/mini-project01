import time
import random
import json

import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

import prompt
import tarot_data
from function_tools import (
    get_current_time,
    draw_tarot_cards,
    tools_,
)
   
# --------------------------------------------------
# 기본 설정
# --------------------------------------------------


client = OpenAI()
MODEL = "gpt-4.1-mini"
TEMPERATURE = 1


# --------------------------------------------------
# 유틸 함수
# --------------------------------------------------
def set_mystic_tarot_theme():
    st.markdown("""
        <style>
        .stApp {
            background: radial-gradient(circle at 50% 10%, #2b1055 0%, #000000 100%);
            color: #E6E6FA;
        }

        div[data-testid="stChatMessage"] {
            background-color: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 15px;
            padding: 15px;
            gap: 15px; /* 아이콘과 텍스트 사이 간격 */
        }
        
        div[data-testid="stChatMessage"] p, 
        div[data-testid="stChatMessage"] div {
            color: #E6E6FA !important;
        }

        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
def focus_chat_input():
    """chat_input textarea에 포커스"""
    components.html(
        """
        <script>
        setTimeout(() => {
            const el = window.parent.document
                .querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (el) el.focus();
        }, 500);
        </script>
        """,
        height=0,
    )

def extract_token_usage(response):
    """
    OpenAI 응답에서 토큰 사용량을 안전하게 추출
    """
    if hasattr(response, "usage") and response.usage:
        return {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
    return None

def add_token_usage(usage):
    if usage is None:
        return

    if "token_usage" not in st.session_state:
        st.session_state.token_usage = {
            "prompt": 0,
            "completion": 0,
            "total": 0,
        }

    st.session_state.token_usage["prompt"] += usage["prompt_tokens"]
    st.session_state.token_usage["completion"] += usage["completion_tokens"]
    st.session_state.token_usage["total"] += usage["total_tokens"]


def call_openai(messages, stream=False, tools=None):
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        stream=stream,
        tools=tools,
    )

# --------------------------------------------------
# 세션 관리
# --------------------------------------------------
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": prompt.streamlit_prompt_01}
        ]

    st.session_state.setdefault("phase", "start")
    st.session_state.setdefault("input_disabled", False)
            
# --------------------------------------------------
# 메시지 출력
# --------------------------------------------------
def render_messages():
    for msg in st.session_state.messages:
        role = msg["role"]

        if role in ("user", "assistant"):
            with st.chat_message(role):
                st.markdown(msg["content"])

        elif role == "function":
            st.markdown(msg["content"])

            if "image_ids" in msg:
                card_ids = msg["image_ids"].split(",")
                cols = st.columns(3)
                for i, col in enumerate(cols):
                    card = tarot_data.TAROT_CARDS[int(card_ids[i])]
                    col.image(card["image_url"], use_container_width=True)
                    col.markdown(
                        f"**{i}. {card['name']}**  \n{card['keywords']}",
                        text_alignment="center",
                    )

# --------------------------------------------------
# 오프닝
# --------------------------------------------------
def opening_message():
    if st.session_state.phase != "start":
        return

    st.session_state.phase = "reading"

    with st.chat_message("assistant"):
        stream = call_openai(st.session_state.messages, stream=True)
        response = st.write_stream(stream)
    
    add_token_usage(extract_token_usage(response))
    st.session_state.messages.append({"role": "assistant", "content": response})

# --------------------------------------------------
# Tool 처리
# --------------------------------------------------
def handle_tools(ai_message):
    for tool_call in ai_message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if name == "get_current_time":
            st.session_state.messages.append({
                "role": "function",
                "tool_call_id": tool_call.id,
                "name": name,
                "content": get_current_time(timezone=args["timezone"]),
            })

        elif name == "draw_tarot_cards":
            handle_tarot_draw(tool_call, args)

# --------------------------------------------------
# 카드 오픈 연출 처리
# --------------------------------------------------
def handle_tarot_draw(tool_call, args):
    placeholder = st.empty()
    for i in range(10):
        placeholder.markdown(f"### 에너지가 모이고 있어요{'.' * i}", text_alignment="center")
        time.sleep(0.5)

    # 타로 카드 아이디 3개 가져오기
    card_ids = draw_tarot_cards(card_ids=args["card_ids"])

    # 카드 정렬 후 배치
    cols = st.columns(3)
    slots = [col.empty() for col in cols]
    content = "사용자가 선택한 카드는 "

    for i, slot in enumerate(slots):
        progress = slot.progress(0)
        for p in range(100):
            time.sleep(random.uniform(0, 0.05))
            progress.progress(p + 1)
        progress.empty()

        # 카드 뒷면 출력
        with slot.container():
            card = tarot_data.TAROT_CARDS[int(card_ids[i])]
            st.image("assets/cards/back.jpg", use_container_width=True)
            content += f"{card['name']} "

    st.session_state.messages.append({
        "role": "function",
        "tool_call_id": tool_call.id,
        "name": tool_call.function.name,
        "content": content,
        "image_ids": ",".join(map(str, card_ids)),
    })

    placeholder.markdown("### 잠시 숨을 고르고 리딩을 시작합니다.*", text_alignment="center")
    time.sleep(random.randint(5, 10))

    # 실제 카드 오픈(앞면)
    for i, slot in enumerate(slots):
        with slot.container():
            card = tarot_data.TAROT_CARDS[int(card_ids[i])]
            st.image(card["image_url"], use_container_width=True)
            st.markdown(
                f"**{card['id']}. {card['name']}**  \n{card['keywords']}",
                text_alignment="center",
            )
            time.sleep(1)
        
# --------------------------------------------------
# 메인 루프
# --------------------------------------------------
def run():
    init_session()
    render_messages()
    opening_message()
    focus_chat_input()

    # user 입력 처리
    if user_input := st.chat_input(
        "질문을 입력하세요",
        disabled=st.session_state.input_disabled,
    ):
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        
        # 입력창 비활성화
        st.session_state.input_disabled = True
        st.rerun()

    # assistant 입력 처리
    if st.session_state.input_disabled:
        # 1차 : 도구 사용 유무 선택
        response = call_openai(
            st.session_state.messages,
            tools=tools_,
        )
        ai_message = response.choices[0].message
        
        add_token_usage(extract_token_usage(response))

        # 선택 결과에 따른 tool 사용
        if ai_message.tool_calls:
            handle_tools(ai_message)
            
        # 2차 : OpenAi API 응답 호출
        with st.chat_message("assistant"):
            stream = call_openai(
                st.session_state.messages,
                stream=True,
            )
            response = st.write_stream(stream)

        add_token_usage(extract_token_usage(response))
        
        st.session_state.messages.append({"role": "assistant", "content": response})

        # 입력창 활성화
        st.session_state.input_disabled = False
        st.rerun()

# --------------------------------------------------
if __name__ == "__main__":
    
    st.set_page_config(layout="centered")
    
    # 테마 적용 함수 실행
    set_mystic_tarot_theme()

    # 테스트용 화면
    st.title("🌙 타로 점성술 챗봇")
    st.sidebar.title("📊 토큰 사용량")
    with st.sidebar:
        if "token_usage" in st.session_state:
            st.write(st.session_state.token_usage)
            
    run()


