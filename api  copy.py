import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# --- 1. 設定 Gemini API 金鑰 ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("錯誤：未找到 GEMINI_API_KEY 環境變數。")
    print("請確保你的 .env 檔案在程式碼相同目錄下，且內容為：GEMINI_API_KEY=\"你的API金鑰\"")
    exit()

genai.configure(api_key=api_key)
print("Gemini API 金鑰設定成功！")


## 2. 確認可用的模型並載入 `models/gemini-2.5-pro`

print("\n--- 檢查可用的 Gemini 模型 ---")
# 由於你明確指定了要使用的模型，這裡的檢查主要是確認該模型理論上是否存在
# 注意：即使模型名稱存在，你仍然可能因為權限或區域限制無法使用
target_model_name = 'gemini-2.5-pro' # 使用簡潔名稱

available_model_names = []
try:
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            available_model_names.append(m.name.replace('models/', '')) # 移除 'models/' 前綴以便比較
            # print(f"找到可用模型: {m.name}") # 可選：印出所有可用的完整模型名稱

except Exception as e:
    print(f"列出可用模型時發生錯誤：{e}")
    print("請檢查你的網路連線或 API 金鑰是否正確。")
    exit()

if target_model_name not in available_model_names:
    print(f"\n警告：'{target_model_name}' 模型不在目前可用模型列表中。")
    print("這表示你可能沒有權限訪問此模型，或者它在你的區域不可用。")
    print("請確保你已在 Google Cloud Vertex AI 啟用相關服務，並檢查你的 API 金鑰是否具有足夠的權限。")
    print("目前可用的模型有：", available_model_names)
    print("程式將嘗試繼續使用此模型，但可能會失敗。")

# 載入 Gemini 2.5 Pro 模型
# 注意：儘管上面警告，程式仍會嘗試載入你指定的模型
model = genai.GenerativeModel(target_model_name)
print(f"嘗試載入模型：'{target_model_name}'。")


## 3. 準備固定開頭與變動內容 (保持不變)

# 定義你的固定開頭
fixed_prefix = """
根據以下翰林9B自然科課綱單元，為每個單元產出5題優質的選擇題，選項請平均分配，其中A和D選項可以稍微多一點。
請嚴格依照以下的 JSON 格式輸出，最終結果應是一個 JSON 陣列，每個元素都是一個題目物件。
請確保所有的題目、選項和解釋都以繁體中文呈現。

題目範例格式：
{
    "grade": "9B",
    "subject": "自然",
    "publisher": "翰林",
    "chapter": "替換為當前章節編號，如 '1-1'",
    "topic": "替換為當前單元名稱，如 '電流的熱效應'",
    "knowledge_point": ["請列出相關的知識點，例如：'電流的熱效應應用'"],
    "difficulty": "normal",
    "question": "科學家能夠測定出岩石或化石的精確年齡（例如，幾億幾千萬年），主要是利用了下列哪一種技術？",
    "options": {
      "A": "地層切割關係",
      "B": "疊置定律",
      "C": "化石比對法",
      "D": "放射性同位素定年法"
    },
    "answer": "D",
    "explanation": "放射性同位素定年法是利用岩石中某些放射性元素（如鈾、碳-14）會以固定的速率衰變成穩定元素的特性。通過測量母元素和子元素的比例，就可以像時鐘一樣，精確計算出岩石形成的絕對年齡。"
}
"""

# 定義你的變動內容列表 (8A 自然科課綱單元)
course_units = [
      "1-1電流的熱效應",
      "1-2生活用電",
      "1-3電池",
      "1-4電流的化學效應",
      "2-1磁鐵與磁場",
      "2-2電流的磁效應",
      "2-3電流與磁場的交互作用",
      "2-4電磁感應",
      "3-1地球的大氣",
      "3-2天氣現象",
      "3-3氣團與鋒面",
      "3-4臺灣的災變天氣",
      "4-1海洋與大氣的互動",
      "4-2全球變遷",
      "4-3人與自然的互動",
      "5-1全球變遷的進行式－北極海海冰融化對於海平面的影響",
      "5-2全球變遷的過去式－從氣候變遷的角度看歷史發展",
      "5-3全球變遷的未來式－人類對氣候的影響與調適"
]


## 4. 使用迴圈結合固定開頭與變動內容 (保持不變)

print("\n--- 逐筆生成內容 ---")
all_generated_questions = []

for i, unit_name in enumerate(course_units):
    parts = unit_name.split(' ', 1)
    chapter_number = parts[0] if len(parts) > 0 else ""
    topic_name = parts[1] if len(parts) > 1 else unit_name

    dynamic_prompt = f"{fixed_prefix}\n\n為以下康軒8A自然科課綱單元產生題目：\n單元名稱: {unit_name}\n" \
                     f"請生成5道關於單元 '{topic_name}' 的題目，並將 'chapter' 設為 '{chapter_number}'，'topic' 設為 '{topic_name}'。" \
                     f"請嚴格按照上述 JSON 陣列格式輸出。"

    print(f"\n--- 處理第 {i+1} 筆單元：{unit_name} ---")
    print(f"部分提示詞預覽 (只顯示部分，完整提示詞很長)：\n{dynamic_prompt[:500]}...\n")

    try:
        response = model.generate_content(dynamic_prompt)

        try:
            json_string = response.text.strip()
            # 處理可能存在的 markdown 程式碼區塊標記
            if json_string.startswith("```json"):
                json_string = json_string.strip("```json").strip("```").strip()

            generated_questions = json.loads(json_string)

            if isinstance(generated_questions, list):
                all_generated_questions.extend(generated_questions)
                print(f"成功為單元 '{unit_name}' 生成並解析 {len(generated_questions)} 題。")
            else:
                print(f"警告：單元 '{unit_name}' 模型回應不是預期的 JSON 陣列格式。")
                print("原始回應：\n", response.text)

        except json.JSONDecodeError as json_e:
            print(f"解析單元 '{unit_name}' 的 JSON 回應時發生錯誤：{json_e}")
            print("原始回應：\n", response.text)

        if response.prompt_feedback and response.prompt_feedback.safety_ratings:
            print("安全性評估：")
            for rating in response.prompt_feedback.safety_ratings:
                print(f"  {rating.category.name}: {rating.probability.name}")

    except Exception as e:
        print(f"處理單元 '{unit_name}' 時發生錯誤：{e}")

print("\n所有單元處理完畢。")
print(f"\n總共生成並解析了 {len(all_generated_questions)} 題。")

output_filename = "generated_science_questions.json"
try:
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_generated_questions, f, ensure_ascii=False, indent=4)
    print(f"\n所有題目已保存到 {output_filename}")
except Exception as e:
    print(f"保存題目到檔案時發生錯誤：{e}")