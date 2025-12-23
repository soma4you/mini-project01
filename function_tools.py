import random

tools_ = [
  {
    "type": "function",
    "function": {
      "name": "draw_tarot_cards",
      "description": "22장의 타로 숫자(0~21)) 아이디 3개를 반환합니다.",
      "strict": True,
      "parameters": {
        "type": "object",
        "properties": {
          "card_ids": {
            "type": "string",
            "description": "random 정수 3개 (0 ~ 21) (예: 7, 4, 20)"
          }
        },
        "required": [
          "card_ids"
        ],
        "additionalProperties": False
      }
    }
  }
]
def draw_tarot_cards(card_ids: str):
    print("카드 ID ----------> ", card_ids)
    card_ids = card_ids.split(',')
    return random.sample(card_ids, 3)