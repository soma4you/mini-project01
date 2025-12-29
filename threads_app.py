
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ===== 설정 =====
access_token = os.getenv("THREADS_ACCESS_TOKEN")
threads_user_id = os.getenv("THREADS_USER_ID")
image_url = "https://logowik.com/content/uploads/images/instagram-threads2913.logowik.com.webp"     #이미지 URL
text_content = "안녕하세요. 글쓰기 테스트 입니다!"

# 1. Threads API: 이미지 + 텍스트 담는 "미디어 컨테이너" 생성
create_url = f"https://graph.threads.net/v1.0/{threads_user_id}/threads"
create_params = {
    "media_type": "IMAGE",
    "image_url": image_url,
    "text": text_content,
    "access_token": access_token
}

print(create_params, create_url)
response_create = requests.post(create_url, params=create_params)
print("Create Response Status:", response_create.status_code)
print("Create Response JSON:", response_create.json())

if response_create.status_code != 200:
    print("미디어 컨테이너 생성 실패:", response_create.text)
    exit(1)

media_container_id = response_create.json().get("id")
print("Media Container ID:", media_container_id)

# 2. 생성된 컨테이너로 "게시" 요청
publish_url = f"https://graph.threads.net/v1.0/{threads_user_id}/threads_publish"
publish_params = {
    "creation_id": media_container_id,
    "access_token": access_token
}

response_publish = requests.post(publish_url, params=publish_params)
print("Publish Response Status:", response_publish.status_code)
print("Publish Response JSON:", response_publish.json())
