import os
import random
import time
import matplotlib.pyplot as plt
from openai import OpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain_openai.chat_models.base import ChatOpenAI
from dotenv import load_dotenv
from typing import Dict
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from prompt.custom_prompt import ACTION_PROMPT, CHAT_PROMPT

# ----- 環境クラス定義 -----
class Environment:
    def __init__(self, humidity: float, temperature: float, bd_score: float):
        self.humidity = humidity #湿度
        self.temperature = temperature #地中の温度
        #self.ph = ph #ph値
        #self.ec = ec #電気伝導度
        self.bd_score = bd_score

    def get_state(self) -> Dict[str, float]:
        """現在の環境状態を返す"""
        return {
            "humidity": self.humidity,
            "temperature": self.temperature,
            #"ph": self.ph,
            #"ec": self.ec,
            "bd_score": self.bd_score
        }
    
    def apply_action(self, action: str, adjustment: Dict[str, float]):
        """行動に応じて環境パラメータを更新する"""
        print(f"\n[行動実行] 選択された行動: {action}")

        self.humidity += adjustment.get("humidity", 0)
        self.temperature += adjustment.get("temperature", 0)
        self.bd_score += adjustment.get("bd_score", 0)

        # 環境にはランダムなばらつき（雑音）を加える
        self.humidity += random.uniform(-1, 1)
        self.temperature += random.uniform(-0.5, 0.5)
        self.bd_score += random.uniform(-0.5, 0.5)

        # 値を現実的な範囲にクランプ
        self.humidity = max(0, min(100, self.humidity))
        self.temperature = max(-50, min(50, self.temperature))
        self.bd_score = max(0, self.bd_score)

        print(f"[状態更新] 新しい環境状態: {self.get_state()}")

# ----- 行動選択エージェントクラス定義 -----
class ActionAgent:
    def __init__(self, LLM, custom_prompt):
        self.LLM = LLM
        self.custom_prompt = custom_prompt
    
    # ----- 行動選択肢とその環境への効果（調整値） -----
    actions = {
        "森林の再生を促進する（人間に依頼）": {"humidity": 0, "temperature": 0, "bd_score": 15},
        "生物が移動しやすい緑の回廊を設置": {"humidity": 0, "temperature": 0, "bd_score": 15},
        "人工的な湿地を作り、多様な水生生物を呼び込む（人間に依頼）": {"humidity": 3, "temperature": 0, "bd_score": 15},
        "果樹や花の植栽": {"humidity": 0, "temperature": 0, "bd_score": 12},
        "水辺環境を整え、両生類・魚類の生息地を守る（人間に依頼）": {"humidity": 2, "temperature": 0, "bd_score": 12},
        "小規模な池やビオトープを作り、雨水を貯留して水生生物の生息地とする": {"humidity": 2, "temperature": 0, "bd_score": 12},
        "在来種の植栽": {"humidity": 0, "temperature": 0, "bd_score": 10},
        "草原の維持・再生": {"humidity": 0, "temperature": 0, "bd_score": 10},
        "昆虫の生息場所を確保する": {"humidity": 0, "temperature": 0, "bd_score": 10},
        "ミツバチ・チョウなどの花粉媒介者のための花を植える": {"humidity": 0, "temperature": 0, "bd_score": 10},
        "外来種の駆除": {"humidity": 0, "temperature": 0, "bd_score": 10},
        "堆肥や有機物の投入": {"humidity": 0, "temperature": 0, "bd_score": 10},
        "湧水・湿地の保全": {"humidity": 2, "temperature": 0, "bd_score": 10},
        "都市部での屋上緑化・壁面緑化": {"humidity": 0, "temperature": 0, "bd_score": 9},
        "川の連続性を確保し、魚類の移動を妨げるダムや障害物を減らす": {"humidity": 0, "temperature": 0, "bd_score": 9},
        "多様な植物層を形成する": {"humidity": 0, "temperature": 0, "bd_score": 8},
        "植生遷移の段階的保護": {"humidity": 0, "temperature": 0, "bd_score": 8},
        "腐葉土を作り、土壌の栄養を補充（人間に依頼）": {"humidity": 0, "temperature": 0, "bd_score": 8}
    }

    # ----- エージェントによる行動選択関数 -----
    def select_action(self, environment: Environment) -> str:
        """
        現在の状態と利用可能な行動の一覧から、LLMに最適な行動を選ばせる
        """
        #現在の環境の取得
        state = environment.get_state()

        # プロンプト生成：状態と各行動の効果を明示
        prompt = self.custom_prompt
        prompt += f"【現在の状態】\n{state}\n\n"
        prompt += "【利用可能な行動】\n"
        for action, effects in self.actions.items():
            prompt += f"- {action}: {effects}\n"
        prompt += "\nこの環境状態において、最も適切な行動を【利用可能な行動】の中から1つ選んでください。"

        print("\n[エージェントの思考過程]")

        # LangChain を利用して LLM により行動を決定する
        response = self.LLM.invoke(prompt)
        response_text = response.content

        for action in self.actions.keys():
            if action.lower() in response_text.lower():
                selected_action = action
                print(f"[LLM選択] 選ばれた行動: {selected_action}")
                return selected_action

# ----- チャットエージェントクラス定義 -----
class ChatAgent:
    def __init__(self, LLM, custom_prompt):
        self.agent = LLM
        self.custom_prompt = custom_prompt  

    def chat_executor(self, human_request):
        while True:

            print("AIエージェント: " + human_request)
            #ユーザーからの入力を取得
            user_input = input("あなた: ")
            agent_input = [HumanMessage(content=user_input)]

            #終了条件
            if user_input.lower() in ["終了", "exit", "ありがとう"]:
                print("会話を終了します")
                break

            # ユーザーのメッセージを履歴に追加
            messages = [{"role": "user", "content": user_input}]

            # ユーザー入力を会話チェーンに渡して応答を生成
            # ChatGPTにメッセージを送信
            response = self.agent.invoke(agent_input)

            print("\n[AIからのメッセージ]")
            # 応答を取得
            print("\nAIエージェント: " + response.content + "\n")

            # アシスタントの応答を履歴に追加
            messages.append({"role": "assistant", "content": response})

    def generate_human_request(self, selected_action):
        """
        依頼文を生成する関数。
        ここでは例として、土壌の状態改善のための依頼文を作成していますが、
        必要に応じて内容を拡充してください。
        """
        prompt = "{selected_action}を人間に実行するようにお願いしてください。友人に連絡するようにラフな感じで大丈夫です。"
        request_message = self.agent.invoke(prompt)
        return request_message.content

def main(num_turns: int=10):
    #LLMの初期設定
    load_dotenv
    api_key = os.getenv("OPENAI_API_KEY")
    LLM = ChatOpenAI(
        model="gpt-4o",
        api_key=api_key,
        temperature=0.7
    )

    #エージェントの作成
    agent = ActionAgent(LLM=LLM, custom_prompt=ACTION_PROMPT)
    chat_agent = ChatAgent(LLM=LLM, custom_prompt=CHAT_PROMPT)

    #環境の作成
    env_state = Environment(humidity=50, temperature=20, bd_score=30)

    # 各パラメータの履歴を記録（可視化用）
    biodiversity_history = [env_state.bd_score]
    humidity_history = [env_state.humidity]
    temperature_history = [env_state.temperature]
    turn_history = [0]

    for turn in range(1, num_turns + 1):
        print(f"\n==== ターン {turn} ====")
        current_state = env_state.get_state()
        print(f"[状態取得] 現在の環境状態: {current_state}")
        
        # エージェントによる行動選択
        selected_action = agent.select_action(env_state)

        if selected_action is None:
            agent.actions["AIは行動を選択しませんでした。（人間に依頼）"] = {"humidity": 0, "temperature": 0, "bd_score": 0}
            selected_action = "AIは行動を選択しませんでした。（人間に依頼）"
            print(selected_action)
        else:
            print(selected_action)

        # 選択した行動の効果（調整値）を取得し、環境状態を更新
        adjustments = agent.actions[selected_action]
        env_state.apply_action(selected_action, {
            "humidity": adjustments.get("humidity", 0),
            "temperature": adjustments.get("temperature", 0),
            "bd_score": adjustments.get("bd_score", 0)
        })

        # ここでは action_choice が文字列のリストで与えられている前提です。
        if "人間に依頼" in selected_action:
            # 条件に応じた依頼文を生成・表示
            human_request = chat_agent.generate_human_request(selected_action)
            #print("AIエージェント: " + human_request + "\n")
            
            # 依頼文表示後にユーザーとの会話システムを起動
            chat_agent.chat_executor(human_request)

        # 履歴の更新
        biodiversity_history.append(env_state.bd_score)
        humidity_history.append(env_state.humidity)
        temperature_history.append(env_state.temperature)
        turn_history.append(turn)

        time.sleep(1)  # ターン間のウェイト（シミュレーション感を付与）

        user_input = input("終了しますか？:")

        #終了条件
        if user_input.lower() in ["終了", "exit", "ありがとう"]:
            print("会話を終了します")
            break
        else:
            continue

    # ----- 状態変化の可視化（グラフ表示） -----
    plt.figure(figsize=(10, 5))
    plt.plot(turn_history, biodiversity_history, marker='o', label='Biodiversity Index')
    plt.plot(turn_history, humidity_history, marker='x', label='Humidity')
    plt.plot(turn_history, temperature_history, marker='s', label='Temperature')
    plt.xlabel('Turn')
    plt.ylabel('Value')
    plt.title('Environment Parameter Evolution Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

# ----- メイン処理 -----
if __name__ == "__main__":
    main(num_turns=10)