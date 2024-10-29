import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import prompt_toHuman

load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)
# システムプロンプトを定義
system_prompt = prompt_toHuman.systemprompt

# 対話履歴を保持するリストを初期化
messages = [
    {"role": "system", "content": system_prompt}
]

print("土地との対話を開始します。終了するには「終了」と入力してください。\n")

while True:
    # ユーザーからの入力を取得
    user_input = input("あなた: ")

    # 終了条件
    if user_input == "終了":
        print("対話を終了します。")
        break

    # ユーザーのメッセージを履歴に追加
    messages.append({"role": "user", "content": user_input})

    # ChatGPTにメッセージを送信
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',  # または使用可能なモデルを指定
        messages=messages
    )

    # 応答を取得
    assistant_response = response.choices[0].message.content 
    print("土地: " + assistant_response + "\n")

    # アシスタントの応答を履歴に追加
    messages.append({"role": "assistant", "content": assistant_response})

def generate_prompt_toH(humidity = float, temperature = float, potassium = float, phosphorus = float, nitrogen = float, image_description = str):
    return f"""
        現在の私の状態はこちらです。
        - **湿度**: {humidity}%
        - **気温**: {temperature}°C
        - **元素分析**: リン: {phosphorus}ppm, 窒素: {nitrogen}ppm, カリウム: {potassium}ppm
        - **地表画像**: {image_description}
        この情報を基に、アドバイスをお願いします。
    """