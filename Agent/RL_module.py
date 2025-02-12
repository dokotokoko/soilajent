import requests
import random

def send_action_to_chatbot(action):
    """
    強化学習AIの行動をAPIサーバーへ送信
    """
    API_URL = "http://127.0.0.1:5000/receive_action"

    action_data = {"action": action}  # actionのみ送信

    try:
        response = requests.post(API_URL, json=action_data)
        response.raise_for_status()
        print(f"✅ AIの行動をチャットボットに送信しました: {action}")
    except requests.exceptions.RequestException as e:
        print(f"⚠ AIの行動送信に失敗しました: {e}")