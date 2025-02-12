from openai import OpenAI
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from prompt import CUSTOM_PROMPT

app = Flask(__name__)

load_dotenv
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

received_action = None #グローバル変数で最新のアクションを保持

@app.route("/receive_action", methods = ["POST"])
def receive_action():
    global received_action
    received_action = request.json  # 受信した行動データを保存

    action = received_action["action"]

    # メッセージを作成してユーザーに送信
    print("\n=== AIエージェントからの指示 ===")
    print(f"AI: {action} を実施してください。\n")

    return jsonify({"status": "success", "message": "行動を受信しました"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
 
    response = client.chat.completions.create(
        model="chatgpt-4o",
        messages=[
            {"role": "developer", "content": CUSTOM_PROMPT},
            {"role":"user", "content": user_message }
        ])
    
    return jsonify({"response": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(debug=True)