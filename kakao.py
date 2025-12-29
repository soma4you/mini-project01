import streamlit as st 
from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import json

# ===== 환경 변수 =====
load_dotenv()
def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)

client = get_client()

# ===== 설정 =====
MAX_CHARS = 80000
MAX_FILE_CHARS = 1_000_000
MIN_CHARS_PER_SPEAKER = 10
MAX_SELECT = 4
IMAGE_DIR = "images_kakao"

# ===== 이미지 목록 =====
AVAILABLE_ANIMALS = [
    os.path.splitext(f)[0]
    for f in os.listdir(IMAGE_DIR)
    if f.lower().endswith((".png", ".jpg", ".jpeg"))
]




# ===== 텍스트 분할 =====
def split_text_by_lines(text, max_chars):
    lines = text.splitlines()
    chunks, current = [], ""

    for line in lines:
        if len(current) + len(line) > max_chars:
            chunks.append(current)
            current = line + "\n"
        else:
            current += line + "\n"

    if current:
        chunks.append(current)
    return chunks


# ===== 화자 추출 =====
def extract_speakers(text):
    speaker_map = {}

    # 줄 앞 공백 허용 + [이름] 구조 강제
    pattern = re.compile(r"^\s*\[([^\]]+?)\]")

    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            speaker = match.group(1).strip()
            speaker_map.setdefault(speaker, 0)
            speaker_map[speaker] += 1

    return speaker_map

# ===== 동물 이미지 매칭 ======
def find_image(animal_key):
    for ext in (".png", ".jpg", ".jpeg"):
        path = os.path.join(IMAGE_DIR, animal_key + ext)
        if os.path.exists(path):
            return path
    return None

# ===== UI =====
def kakao():
    st.markdown("## 카카오톡 대화 분석기")
    st.write("카카오톡 대화 내용을 활용한 대화분석기입니다.")

    uploaded_file = st.file_uploader("TXT 파일 업로드", type=["txt"])
    if uploaded_file is None:
        st.write("카카오톡 '대화 내보내기'기능으로 TXT 파일 생성 후 업로드해주세요.")
        st.divider()
        st.text("TXT 파일의 화자 구분은 [      ]입니다. (예: [홍길동] : 나는 행복해.)")
        st.write("따라서 형태가 다른 파일도 서식을 유지한다면 분석이 가능합니다.")
        st.divider()
        st.write("*3MB이상의 텍스트 파일은 분석이 어려울 수 있습니다.")
        st.write("*사용자 개인정보를 수집하지 않습니다.")

        st.stop()
# =====TXT파싱=====
    text = uploaded_file.read().decode("utf-8")

    if len(text) > MAX_FILE_CHARS:
        st.error("파일이 너무 큽니다.")
        st.stop()

    # ===== 화자 추출 및 필터 =====
    speaker_map = extract_speakers(text)
    
    st.write("정확한 결과 도출을 위해 화자 수를 제한합니다.")
    st.write("아래에서 분석할 화자를 선택해주세요.")    
    filtered_speakers = {
        name: content
        for name, content in speaker_map.items()
        if content >= MIN_CHARS_PER_SPEAKER
    }

    if not filtered_speakers:
        st.error("분석 가능한 화자가 없습니다.")
        st.stop()

    # ===== 화자 선택 =====
    st.markdown("### 분석할 화자 선택 (최대 4명)")

    selected_speakers = st.multiselect(
        "화자를 선택하세요",
        options=filtered_speakers,  # 추출된 화자 리스트
        max_selections=4
    )

    if st.button("선택한 화자 분석 시작"):
        if not selected_speakers:
            st.warning("분석할 화자를 최소 1명 이상 선택하세요.")
            st.stop()

        # ===== 텍스트 분할 =====
        text_chunks = (
            split_text_by_lines(text, MAX_CHARS)
            if len(text) > MAX_CHARS
            else [text]
        )

        # ===== 1차 분석 (체크리스트 방식) =====
        analysis_results = []

        for chunk in text_chunks:
            prompt = f"""
다음은 여러 화자가 참여한 전체 대화의 일부입니다.

아래 **분석 대상 화자 체크리스트**에 포함된 화자에 대해서만 분석하세요.
체크리스트에 없는 화자는 절대 분석 결과에 포함하지 마세요.

분석 대상 화자 체크리스트:
{chr(10).join([f"- {s}" for s in selected_speakers])}

분석 규칙:
- 모든 체크리스트 화자를 빠짐없이 분석할 것
- 각 화자별로 성향, 대화 스타일, 다른 화자와의 관계를 각각 5문장 이내로 작성
- 추측이 아닌 대화 맥락 기반으로 서술
- 대화가 중간에 끊겨서 분석이 어려운 경우 정해진 정보 안에서 의미를 창조하지 말 것.
- 답변의 형식은 반드시 아래 제시하는 예시의 형식을 유지할 것
답변 예시:
[화자 : ,
성향 : ,
대화 스타일 : ,
다른 화자와의 관계 : ]

대화문:
{chunk}
    """
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 전문 성격 분석가입니다."},
                    {"role": "user", "content": prompt}
                ]
            )
            analysis_results.append(resp.choices[0].message.content)

        merged_analysis = "\n".join(analysis_results)

        # ===== 최종 종합 =====
        final_prompt = f"""
아래 분석 결과는 긴 대화를 여러 부분으로 나누어 분석한 결과입니다.
종합된 내용에 대해 반드시 답변 형식과 규칙을 지켜 설명하세요.

답변 형식 :
1. 아무개
- 성향 :
- 스타일 :
종합 분석 

답변 규칙 : 
 - 반드시 아래 화자 체크리스트에 포함된 화자를 빠짐없이 모두 설명
 - 체크리스트에 없는 화자에 대한 개별분석은 절대 출력하지 않을 것. 
 - 번호와 화자명은 글자 크기를 키우고 볼드처리
 - 성향과 스타일에 대해 각각 5줄 이상으로 분석
 - 종합분석은 10줄 이상으로 화자들 간의 종합적인 관계와 태도를 서술
 - 각 화자에게 부정적이거나 불쾌할 수 있는 내용은 배제
 - 화자의 이름뒤에는 무조건 존칭을 붙여서 답변
 - 중복되는 내용이 쓰이지 않도록 할 것
 - 분석 결과에 적혀 있는 모든 내용을 종합적으로 활용

화자 체크리스트:
{', '.join(selected_speakers)}

분석 결과:
{merged_analysis}
    """

        final_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 전문 성격 분석가입니다."},
                {"role": "user", "content": final_prompt}
            ]
        )

        final_result = final_resp.choices[0].message.content
        st.markdown("### 최종 분석 결과")
        st.write(final_result)

# ===== 동물 추천 (이미지 제한) =====
        animal_prompt = f"""
동물 목록:
{', '.join(AVAILABLE_ANIMALS)}

**출력은 JSON 형식만 포함해야 하며, JSON 외 다른 텍스트(설명, 문장 등)가 1자라도 포함되면 잘못된 출력으로 간주합니다. **
**본 프롬프트에서 요구하는 JSON 배열 형식만 출력하세요. 반드시 다른 설명 문장은 절대 포함하지 마세요.**

 배열 형식 : 
[
  {{
    "name": "아무개",
    "animal_key": "호랑이",
    "animal_label": "용맹한 호랑이",
    "reason": ""
  }}
]

 - "name" 조건
 1. 반드시 화자의 이름을 그대로 사용할 것
 2. 위의 분석에 나온 화자는 반드시 모두 분석할 것
 3. 화자의 이름 뒤에 반드시 존칭을 붙일 것

- "animal_key" 조건
 1. 반드시 위의 동물 목록 안에서만 추천할 것
 2. 이 목록외의 동물은 추천하지 말고 정확히 일치하는 동물이 없더라도 가장 유사한 점을 찾아 추천할 것
 
- "animal_label"
 1. 00한 000의 형식으로 추천할 것
 2. 동물 앞에 들어가는 형용사는 화자간 성향과 스타일에 맞춰 표현할 것
 3. 반드시 화자간 같은 동물을 추천하더라도 형용사 중복을 피할 것
 4. 너무 일반적인 형용사는 사용하지 말 것 (ex. 귀여운, 착한 등)

- "reason"
 1. 위의 animal_label을 추천한 이유에 대해 5줄 이내로 간략히 설명할 것
 2. 그 동물의 특징을 먼저 서술하고 이를 화자의 특징과 연결지어 설명할 것

분석 대상 화자:
{', '.join(selected_speakers)}

분석 결과:
{final_result}
        """

        animal_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 성격 분석 및 브랜딩 전문가입니다."},
            {"role": "user", "content": animal_prompt}
        ]
        )

        animal_text = animal_resp.choices[0].message.content.strip()

        # ===== JSON 파싱 =====
        profiles = json.loads(animal_text)

        # ===== 카드 UI =====
        st.markdown("## 🐾 화자별 동물 카드")

        for p in profiles:
            with st.container(border=True):
                st.subheader(p["name"])

                image_path = find_image(p["animal_key"])
                if image_path:
                    st.image(image_path, width=250)

                st.markdown(f"**추천 동물:** {p['animal_label']}")
                st.write(p["reason"])
            