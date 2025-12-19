import os
from openai import OpenAI
from dotenv import load_dotenv
import time
import prompt
import tarot_data
import streamlit as st
import random

load_dotenv()
client = OpenAI()

def stream_print(text: str, flush=True, sleep: float = 0.01):
    
    if not flush : 
        print(text)
        return
    
    for line in text:
        for s in line:
            print(s, flush=True, end = "")
            time.sleep(sleep)
    print()
        
 # 오프닝 문구
def openning_hook():
    stream_print(prompt.OPENNING_HOOK)
    stream_print("-" * 50)
        

openning_hook()

MENU = ["연애운", "금전/재물운", "관계문제", "기타"]
def select_menuFn():
    stream_print(":::::::::::::::: 메뉴 선택")
    for i, m in enumerate(MENU):
        stream_print(f"{i+1}. {m}")
    stream_print(":" * 30)
    user_input = input("\n\n사용자 >>> ")
    
    return user_input
    
while True:
    user_input = select_menuFn()
    
    menu_no = int(user_input)
    
    if menu_no == 0: # 종료
        break
    elif menu_no == 1:
        user_input = input(f"[{MENU[menu_no-1]}] 현재의 상황을 알려주세요.\n\n사용자 >>> ")
    elif menu_no == 2:
        user_input = input(f"[{MENU[menu_no-1]}] 현재의 상황을 알려주세요.\n\n사용자 >>> ")
    elif menu_no == 3:
        user_input = input(f"[{MENU[menu_no-1]}] 어떤 관게 문제로 힘들어하시나요?\n\n사용자 >>> ")
    elif menu_no == 4:
        user_input = input(f"[{MENU[menu_no-1]}] 당신의 고민은 무엇인가요?.\n\n사용자 >>> ")
    
    
    print("\n\n")
    print("Assistant>>> ")
    select_menu = f"[사용자의 고민은 '{MENU[menu_no-1]}]' 이며, 현재의 상황은 '{user_input}'입니다.\n\n>>> "
    
    stream_print("당신의 고민을 카드에 반영해 3장의 카드를 신중히 고르고 있습니다.")
    import time # 잠시 멈추는 효과를 위해 time 모듈 사용

    for i in range(1, 101):
        print(f'\r{i}% 진행률', end=' ', flush=True) # \r로 줄 처음으로, flush=True로 즉시 출력
        time.sleep(0.1) # 0.1초 대기
    print("\n\n")
    
    
    selected_card = ""
    cards = random.sample(tarot_data.TAROT_CARDS, 3)
    for i, card in enumerate(cards):
        # print(card)
        selected = f"{card['name']} / " if i != 2 else f"{card['name']}"
        selected_card += selected
    
    # 사용자의 고민 + 카드 3개 선택 (강제)
    user_prompt = f"저의 고민은 '{MENU[menu_no-1]}'입니다.\n현재 상황은 '{user_input}'입니다. 뽑은 카드는 '{selected_card}' 입니다 "
    stream_print(user_prompt)
    
    stream = client.responses.create(
        model = "gpt-4.1",
        instructions = prompt.prompt_01,
        input = user_prompt,
        stream = True,
    )

    print("\n\n")
    print("Assistant>>> ")
    # 응답 데이터
    # ResponseTextDeltaEvent(content_index=0, delta=' 설', item_id='msg_0c36b97224711e1c006943e7ac696081a1b4c9adcb13901676', logprobs=[], output_index=0, sequence_number=52, type='response.output_text.delta', obfuscation='DjT4JeHzscts9M')
    for event in stream:
        if hasattr(event, 'delta'):
            print(event.delta, end="", flush=True)
    print("\n\n")
    break