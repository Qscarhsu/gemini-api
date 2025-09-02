# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from google import genai
import cohere

# 載入環境變數
load_dotenv()

# ====== 初始化 API Client ======
# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai_client = genai.Client(api_key=GEMINI_API_KEY)

# Cohere
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(api_key=COHERE_API_KEY)

# ====== 函式：用 Gemini 生成學生學習評估 ======
def generate_student_feedback(question: str, student_answer: str) -> str:
    prompt = f"""
    你是一個老師，以下有一個題目與學生的答案，請撰寫一段「學生學習狀況評估」。
    - 題目: {question}
    - 學生答案: {student_answer}
    """
    response = genai_client.models.generate_content(
        model="gemini-2.0-flash",  # 可換成 gemini-2.5-pro
        contents=prompt,
        config={
            "temperature": 0.7,
            "max_output_tokens": 256,
        }
    )
    return response.text.strip()

# ====== 函式：用 Cohere 進行評分 ======
def evaluate_with_cohere(correct_explanation: str, generated_feedback: str) -> float:
    """
    利用 Cohere 的 command-r-plus 做 semantic 判斷，
    給出 generated_feedback 與 correct_explanation 的相似性分數。
    """

    judge_prompt = f"""
    你是一個答案評分系統，請根據以下規則評估「Gemini 生成的學生學習評估」是否涵蓋正確詳解：
    - 如果完全吻合，給分 5。
    - 如果部分正確，給分 3。
    - 如果大部分錯誤，給分 1。
    - 如果完全無關，給分 0。

    正確詳解：
    {correct_explanation}

    Gemini 生成的學生學習評估：
    {generated_feedback}

    請只輸出一個數字分數（0–5）。
    """

    response = co.chat(
        model="command-r-plus",
        message=judge_prompt
    )

    try:
        score = float(response.text.strip())
    except:
        score = -1  # parsing 失敗
    return score


# ====== 範例執行 ======
if __name__ == "__main__":
    # 題目 + 答案 + 詳解
    question = "楊喚的《夏夜》詩中，如何透過意象營造氛圍？"
    student_answer = "應該是青蛙的叫聲很吵，所以表現夏夜很熱鬧。"
    correct_explanation = "詩中透過星星、月亮、螢火蟲、小蟲的描寫，營造寧靜卻充滿生機的氛圍。"

    # 1. Gemini 生成學生學習評估
    feedback = generate_student_feedback(question, student_answer)
    print("Gemini 生成回饋：", feedback)

    # 2. Cohere 評分
    score = evaluate_with_cohere(correct_explanation, feedback)
    print("Cohere 評分：", score)
