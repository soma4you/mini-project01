from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from openai import BaseModel

"""
프로젝트에서 사용하는 상수값과 데이터 모델을 정의 -
전체 코드의 일정한 데이터 구조를 유지하며 및 특정 설정값을 관리한다.
"""

class Models(str, Enum):
    GPT4 = "gpt-4"
    GPT4o = "gpt-4o"

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class PromptUnit(BaseModel):
    title: str
    prompt: List[ChatMessage]
    response: Optional[Union[Any, List, Dict]]
