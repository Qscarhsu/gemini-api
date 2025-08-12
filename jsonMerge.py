import pandas as pd

file1 = r'自然題庫\\翰林_自然.json'
file2 = r'自然題庫\\翰林(自然).json'

def merge_json_files(file1, file2):
    
    df1 = pd.read_json(file1, encoding='utf-8')
    df2 = pd.read_json(file2, encoding='utf-8')

    df_merged = pd.concat([df1,df2], ignore_index=True)

    with open('翰林_自然_.json', 'w', encoding='utf-8') as f:
        df_merged.to_json(f, orient='records', force_ascii=False, indent=4)

        print("合併完成，已儲存為 '翰林_自然_.json'")
merge_json_files(file1, file2)