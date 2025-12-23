# # tarot_app.py
# import os
# import time
# import random  # ✅ 추가
# import streamlit as st
# from openai import OpenAI
# import prompt  # 프롬프트 모듈
# import tarot_data  # ✅ 추가 (tarot_data.py의 TAROT_CARDS 사용)
# from function_tools import get_current_time, draw_tarot_cards, tools_
# import json

# st.set_page_config(layout="centered")

# client = OpenAI()

# MODEL = "gpt-4.1-mini"
# TEMPERATURE = 1

# # messages 세션 초기화
# def reset():
#     if "reset" in st.session_state and st.session_state.reset:
#         # messages 세션 상태 키 목록 가져오기
#         del_key_list = ["messages"]
#         keys = list(st.session_state.keys())
#         for key in keys:
#             if key in del_key_list:
#                 del st.session_state[key]
#         st.session_state.reset = False
#     return st.session_state.reset
        

# # OpenAI API 호출
# def get_ai_response(messages, stream = False, tools = None):
#     response = client.chat.completions.create(
#         model = MODEL,
#         messages = messages,
#         temperature = TEMPERATURE,
#         stream = stream,
#         tools = tools,
#     )
    
#     return response


# # def reset_chat():
# #     """
# #     모든 세션 상태를 제거하고 최초 상태로 복귀
# #     """
# #     keys_to_keep = []  # 유지할 키가 있으면 여기에
# #     if st.session_state.phase == "reset": 
# #         for key in list(st.session_state.keys()):
# #             if key not in keys_to_keep:
# #                 del st.session_state[key]
# #         st.rerun()
    
# # 기존 메시지 출력 (이미 완료된 대화는 markdown으로)
# def chat_print_message():
#     for message in st.session_state.messages:
#         if message["role"] in ("user", "assistant"):
#             with st.chat_message(message["role"]):
#                 st.markdown(message["content"])
                
#         elif message["role"] in "function":
#             st.markdown(message["content"])
#             # 이미지가 있으면 출력 (이 부분이 있어야 대화 중에도 안 사라짐)
#             if "image_ids" in message:
#                 card_ids = message["image_ids"].split(',')
#                 cols = st.columns(3) 
#                 for i, col in enumerate(cols):
#                     card = tarot_data.TAROT_CARDS[int(card_ids[i])]
#                     col.image(card["image_url"], use_container_width=True)
#                     col.markdown(f"**{i}. {card['name']}**  \n{card['keywords']}", text_alignment="center")

# def openning_hook():
#     # 오프닝 멘트는 한 번만 실행
#     if st.session_state.phase == "start": # reset, start -> reading
#         st.session_state.phase = "reading"
        
#         with st.chat_message("assistant"):
#             stream = get_ai_response(st.session_state.messages, stream=True)
#             response = st.write_stream(stream)
#         st.session_state.messages.append({"role": "assistant", "content": response})

        
# def run():
    
#     # 세션 초기화 ----------------------------------
#     if "reset" not in st.session_state or st.session_state.reset == False:
#         st.session_state.reset = True
        
#         # if "messages" not in st.session_state:
#         st.session_state.messages = [{"role": "system", "content": prompt.streamlit_prompt_01}] # 사전 프롬프트 세팅
    
#         # 진행 단계 표시 (start -> reading)
#         # if "phase" not in st.session_state: 
#         st.session_state.phase = "start"
        
#         # 입력창 활성/바활성
#         # if "input_disabled" not in st.session_state:
#         st.session_state.input_disabled = False
#     # ---------------------------------------------
    
#     chat_print_message()
#     openning_hook()

#     # 3. 새로운 사용자 입력 처리
#     if user_input := st.chat_input("질문을 입력하세요",  disabled = st.session_state.input_disabled):
        
#         # 사용자 응답 처리
#         with st.chat_message("user"):
#             st.markdown(user_input)
#         st.session_state.messages.append({"role": "user", "content": user_input})
        
#         # if not st.session_state.input_disabled: # 입력창 비활성화
#         #     st.session_state.input_disabled = True
#         #     st.rerun()
        
        
#         # 어시스턴트 응답에 대한 1차 처리(도구 사용)
#         ai_response = get_ai_response(st.session_state.messages, tools=tools_)
#         ai_message = ai_response.choices[0].message
        
#         # GPT가 함수 호출을 요청한 경우
#         tool_calls = ai_message.tool_calls
        
#         if tool_calls:
#             for tool_call in tool_calls:
#                 tool_name = tool_call.function.name
#                 tool_call_id = tool_call.id
#                 arguments = json.loads(tool_call.function.arguments)
                
#                 # 카로카드 id 3개 반환
#                 if tool_name == "draw_tarot_cards":
#                     card_ids = ""
                    
#                     # 연출 (뜸들이기)
#                     placeholder = st.empty()
#                     for i in range(0, 10):
#                         placeholder.markdown(f"에너지가 모이고 있어요{ '.' * i}")
#                         time.sleep(0.5)
                    
#                     card_ids = draw_tarot_cards(card_ids=arguments["card_ids"])
                    
#                     cols = st.columns(3)
#                     placeholders = [col.empty() for col in cols] # 각 컬럼에 내용을 담을 빈 공간(empty) 확보
#                     content_text = "사용자가 선택한 카드는 "
#                     for i, col in enumerate(placeholders):
                        
#                         # 연출(타로 카드 생성)
#                         progress = col.progress(0)
#                         for percent_complete in range(100):
#                             time.sleep(random.uniform(0, 0.05))
#                             progress.progress(percent_complete + 1)
#                         progress.empty()
                        
#                         # 카드 이미지 출력(뒷면)
#                         with col.container():
#                             card = tarot_data.TAROT_CARDS[int(card_ids[i])]
#                             st.image("assets/cards/back.jpg", use_container_width=True)
#                         content_text += f"{card['name'], }"
                    
#                     st.session_state.messages.append({
#                         "role": "function",
#                         "tool_call_id": tool_call_id,
#                         "name": tool_name,
#                         "content": content_text,
#                         "image_ids": ",".join(map(str,card_ids))
#                     })
                    
#                     # 연출 (한 번더 뜸들이기)
#                     placeholder.markdown("**잠시 숨을 고르고 리딩을 시작합니다.**", text_alignment="center")
#                     time.sleep(random.randint(5, 10))
                    
#                     # 실제 카드 이미지 출력(한 장씩 오픈)
#                     for i, col in enumerate(placeholders):
#                         card = tarot_data.TAROT_CARDS[int(card_ids[i])]
#                         with col.container():
#                             st.image(card["image_url"], use_container_width=True)            
#                             st.markdown(f"**{card['id']}. {card['name']}**  \n{card['keywords']}", text_alignment="center")
#                             time.sleep(1)

#         # 어시스턴트 응답에 대한 2차 처리
#         with st.chat_message("assistant"):
#             stream = get_ai_response(st.session_state.messages, stream=True)
#             response = st.write_stream(stream)
#         st.session_state.messages.append({"role": "assistant", "content": response})
            
#         # if st.session_state.input_disabled:
#         #     st.session_state.input_disabled = False
#         #     st.rerun()
            

# if __name__ == "__main__":
    
#     run()


# streamlit_app.py
import time
import random
import json

import streamlit as st
from openai import OpenAI

import prompt
import tarot_data
from function_tools import (
    draw_tarot_cards,
    tools_,
)

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(layout="centered")
st.title("👉 고민될 땐, 타로챗봇")

MODEL_MAIN = "gpt-4o-mini"
MODEL_STREAM = "gpt-4.1"
MODEL_OPENING = "gpt-4.1-nano-2025-04-14"

client = OpenAI()

# --------------------------------------------------
# OpenAI 호출
# --------------------------------------------------
def call_ai(messages, tools=None, stream=False, model=MODEL_MAIN):
    return client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        stream=stream,
    )

# --------------------------------------------------
# 세션 초기화
# --------------------------------------------------
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": prompt.streamlit_prompt_01}]
    st.session_state.setdefault("phase", "start")        # 상태: start => reading
    st.session_state.setdefault("input_disabled", False) # 채팅 입력창 활성/비활성

# --------------------------------------------------
# 채팅 메시지 렌더링
# --------------------------------------------------
def render_messages():
    for msg in st.session_state.messages:
        role = msg["role"]

        if role in ("user", "assistant"):
            with st.chat_message(role):
                st.markdown(msg["content"])

        elif role == "function":
            st.markdown(msg["content"])
            render_tarot_images(msg)

# --------------------------------------------------
# 카드 이미지 렌더링
# --------------------------------------------------
def render_tarot_images(message):
    if "image_ids" not in message:
        return

    card_ids = message["image_ids"].split(",")
    cols = st.columns(3)

    for i, col in enumerate(cols):
        card = tarot_data.TAROT_CARDS[int(card_ids[i])]
        col.image(card["image_url"], width="content")
        col.markdown(
            f"**{i}. {card['name']}**  \n{card['keywords']}",
            text_alignment="center",
        )

# --------------------------------------------------
# 오프닝 멘트
# --------------------------------------------------
def opening_hook():
    if st.session_state.phase != "start": # 시작때, 한 번 만!
        return

    st.session_state.phase = "reading"

    with st.chat_message("assistant"):
        stream = call_ai(
            st.session_state.messages,
            stream=True,
            model=MODEL_OPENING,
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})

# --------------------------------------------------
# Tool Dispatcher
# --------------------------------------------------
def handle_tool_calls(tool_calls):
    for call in tool_calls:
        name = call.function.name
        args = json.loads(call.function.arguments)

        # Tool 사용시
        if name == "draw_tarot_cards":
            handle_draw_tarot(call, args)

# --------------------------------------------------
# 카드 오픈 연출 처리
# --------------------------------------------------
def handle_draw_tarot(call, args):
    placeholder = st.empty()
    for i in range(10):
        placeholder.markdown(f"에너지가 모이고 있어요{'.' * i}", text_alignment="center")
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
            st.image("assets/cards/back.jpg", width="content")
            content += f"{card['name']} "

    st.session_state.messages.append({
        "role": "function",
        "tool_call_id": call.id,
        "name": call.function.name,
        "content": content,
        "image_ids": ",".join(map(str, card_ids)),
    })

    placeholder.markdown("### 잠시 숨을 고르고 리딩을 시작합니다.", text_alignment="center")
    time.sleep(random.randint(3, 5))

    # 실제 카드 오픈(앞면)
    for i, slot in enumerate(slots):
        with slot.container():
            card = tarot_data.TAROT_CARDS[int(card_ids[i])]
            st.image(card["image_url"], width="content")
            st.markdown(
                f"**{card['id']}. {card['name']}**  \n{card['keywords']}",
                text_alignment="center",
            )
            time.sleep(1)

# --------------------------------------------------
# 메인 루프
# --------------------------------------------------
def tarot_app():
    init_session()
    render_messages()
    opening_hook()

    if user_input := st.chat_input("질문을 입력하세요"):
        
        # user 입력 처리
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # tool 사용 유무
        response = call_ai(
            st.session_state.messages,
            tools=tools_,
        )
        response = response.choices[0].message

        if response.tool_calls:
            handle_tool_calls(response.tool_calls)

        # assistant 입력 처리
        with st.chat_message("assistant"):
            stream = call_ai(
                st.session_state.messages,
                stream=True,
                model=MODEL_STREAM,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --------------------------------------------------
if __name__ == "__main__":
    run()
