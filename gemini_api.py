import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import os

# 讀取 API KEY（假設你已經設在 .env 或環境變數中）

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)


def student_learning_evaluation(
    question: dict, student_anwser: str, temperature: int, max_output_tokens: int
):

    prompt = f"""你是一位耐心且鼓勵學生的國中老師。根據題目資料與學生作答情況，請生成「學生學習狀況評估」的內容（請獨立一段文字輸出）。

                內容須包含：
                1. 分析學生對相關知識點的理解現況。
                2. 說明學生可能存在的常見誤解或遇到的學習困難。
                3. 根據題目所屬科目（國文、英文、數學、自然、社會），給出對應學科常見學習難點的具體建議。
                題目資料：{question}
                學生答案：{student_answer}
                """
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": temperature,  # 溫度，0~2.0 越低越穩定
            "top_p": 0.95,  # (可選) Nucleus sampling
            "max_output_tokens": max_output_tokens,  # (可選) 最長輸出長度
        },
    )
    evaluation_json = {"學生學習狀況評估": None}

    evaluation_response = model.generate_content(prompt).text

    evaluation_json["學生學習狀況評估"] = evaluation_response

    return evaluation_json


def solution_guidance(
    question: dict, student_anwser: str, temperature: int, max_output_tokens: int
):

    prompt = f"""你是一位耐心且引導式的國中老師。根據題目資料與學生作答情況，請生成「題目詳解與教學建議」的內容（請合併為一段文字，不要條列）。

                    內容須包含：
                    1. 詳細解釋題目的核心概念。
                    2. 說明正確答案的理由。
                    3. 根據此題的難度與學生常見迷思，提出具體可行的學習建議，建議內容可以包含：
                    - 推薦回顧哪些教材章節
                    - 適合的練習方式
                    - 補強資源
                    - 本題型容易出現的理解誤區提醒

                    題目資料：{question}
                    學生答案：{student_answer}"""
    guidance_json = {"題目詳解與教學建議": None}
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": temperature,  # 溫度，0~2.0 越低越穩定
            "top_p": 0.95,  # (可選) Nucleus sampling
            "max_output_tokens": max_output_tokens,  # (可選) 最長輸出長度
        },
    )

    guidance_response = model.generate_content(prompt).text

    guidance_json["題目詳解與教學建議"] = guidance_response

    return guidance_json


#####輸入範例

question = {
    "grade": "7A",
    "subject": "數學",
    "publisher": "翰林",
    "chapter": "1-1正數與負數",
    "topic": "正數與負數",
    "knowledge_point": ["正負數的定義", "數線表示"],
    "difficulty": "easy",
    "question": "下列關於正數與負數的敘述，何者正確？",
    "options": {
        "A": "$0$ 是正數。",
        "B": "$0$ 是負數。",
        "C": "$0$ 既不是正數也不是負數。",
        "D": "$0$ 是最小的正數。",
    },
    "answer": "C",
    "explanation": "$0$ 既不是正數也不是負數，它是正負數的分界點。",
}

student_answer = "B"
temperature = 1
max_output_token = 512


json_path = "南一_自然_.json"

with open(json_path, "r", encoding="utf_8") as f:

    data = json.load(f)

student_answer = "B"
temperature = 1
max_output_token = 512


# for question in data:

#     print(
#         student_learning_evaluation(
#             question, student_answer, temperature, max_output_token
#         )
#     )

#     print(solution_guidance(question, student_answer, temperature, max_output_token))

#####使用name__main__來測試功能

if __name__ == "__main__":

    question = {
        "grade": "7A",
        "subject": "國文",
        "publisher": "翰林",
        "chapter": "夏夜",
        "topic": "詩歌賞析",
        "knowledge_point": [
            "意象",
            "譬喻",
            "擬人",
            "詩歌主旨"
        ],
        "difficulty": "normal",
        "question": "楊喚的《夏夜》一詩中，詩人透過哪些意象的描寫，營造出夏夜寧靜而充滿生機的氛圍？下列選項何者說明最為恰當？",
        "options": {
            "A": "「小河」的流動與「螢火蟲」的閃爍，象徵時間的快速流逝。",
            "B": "「小蟲」的歌唱與「青蛙」的鼓噪，展現夏夜的熱鬧喧囂。",
            "C": "「星星」的眨眼與「月亮」的微笑，運用擬人手法，使夏夜充滿童趣與生命力。",
            "D": "「夜風」的輕拂與「花草」的搖曳，暗示夏夜的涼爽與寂寥。"
        },
        "answer": "C",
        "explanation": "《夏夜》一詩中，「星星」的眨眼和「月亮」的微笑，是詩人運用擬人法，將無生命的星月賦予人的動作與情感，使夏夜的景象更為生動活潑，充滿童趣與生命力，營造出寧靜而富有生機的氛圍。選項A的「時間快速流逝」與詩意不符；選項B的「熱鬧喧囂」與詩中寧靜的氛圍不符；選項D的「寂寥」與詩中充滿生命力的氛圍不符。"
    }
        

    student_answer = "D"
    temperature = 1
    max_output_token = 256
    print(student_learning_evaluation(question, student_answer, temperature, max_output_token))

    print(solution_guidance(question, student_answer, temperature, max_output_token))    