import requests

API_URL_CHAT = "http://127.0.0.1:5000/chat"

print("\n=== AIエージェントの行動が決定しました ===")
print("AIが新しい行動を決定した場合、ここに表示されます。\n")

while(True):
    user_input = input("あなた： ")

    if user_input.lower() in ["exit", "終了", "またね"]:
        print("AI: ありがとう！また相談してください。")
        break

    #AIにメッセージを送信し、応答を受け取る
    response = requests.post(API_URL_CHAT, json={"message": user_input})
    print("AI: ", response.json()["response"])