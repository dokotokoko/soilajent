import os
import random
import matplotlib.pyplot as plt
from langchain_openai.chat_models.base import ChatOpenAI
from dotenv import load_dotenv
import random
import time
import matplotlib.pyplot as plt
from typing import Dict


# 環境変数の読み込み（OpenAI APIキーが必要）
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ----- 環境クラス定義 -----
class Environment:
    def __init__(self, humidity: float, temperature: float, biodiversity_index: float):
        self.humidity = humidity
        self.temperature = temperature
        self.biodiversity_index = biodiversity_index

    def get_state(self) -> Dict[str, float]:
        """現在の環境状態を返す"""
        return {
            "humidity": self.humidity,
            "temperature": self.temperature,
            "biodiversity_index": self.biodiversity_index
        }

    def apply_action(self, action: str, adjustments: Dict[str, float]):
        """行動に応じて環境パラメータを更新する"""
        print(f"\n[行動実行] 選択された行動: {action}")
        self.humidity += adjustments.get("humidity", 0)
        self.temperature += adjustments.get("temperature", 0)
        self.biodiversity_index += adjustments.get("biodiversity_index", 0)
        # 環境にはランダムなばらつき（雑音）を加える
        self.humidity += random.uniform(-1, 1)
        self.temperature += random.uniform(-0.5, 0.5)
        self.biodiversity_index += random.uniform(-0.5, 0.5)
        # 値を現実的な範囲にクランプ
        self.humidity = max(0, min(100, self.humidity))
        self.temperature = max(-50, min(50, self.temperature))
        self.biodiversity_index = max(0, self.biodiversity_index)

        print(f"[状態更新] 新しい環境状態: {self.get_state()}")

# ----- 候補行動とその環境への効果（調整値） -----
actions = {
    "森林の再生を促進する": {"humidity": 0, "temperature": 0, "biodiversity_index": 15},
    "生物が移動しやすい緑の回廊を設置": {"humidity": 0, "temperature": 0, "biodiversity_index": 15},
    "人工的な湿地を作り、多様な水生生物を呼び込む": {"humidity": 3, "temperature": 0, "biodiversity_index": 15},
    "果樹や花の植栽": {"humidity": 0, "temperature": 0, "biodiversity_index": 12},
    "水辺環境を整え、両生類・魚類の生息地を守る": {"humidity": 2, "temperature": 0, "biodiversity_index": 12},
    "小規模な池やビオトープを作り、雨水を貯留して水生生物の生息地とする": {"humidity": 2, "temperature": 0, "biodiversity_index": 12},
    "在来種の植栽": {"humidity": 0, "temperature": 0, "biodiversity_index": 10},
    "草原の維持・再生": {"humidity": 0, "temperature": 0, "biodiversity_index": 10},
    "昆虫の生息場所を確保する": {"humidity": 0, "temperature": 0, "biodiversity_index": 10},
    "ミツバチ・チョウなどの花粉媒介者のための花を植える": {"humidity": 0, "temperature": 0, "biodiversity_index": 10},
    "外来種の駆除": {"humidity": 0, "temperature": 0, "biodiversity_index": 10},
    "堆肥や有機物の投入": {"humidity": 0, "temperature": 0, "biodiversity_index": 10},
    "湧水・湿地の保全": {"humidity": 2, "temperature": 0, "biodiversity_index": 10},
    "都市部での屋上緑化・壁面緑化": {"humidity": 0, "temperature": 0, "biodiversity_index": 9},
    "川の連続性を確保し、魚類の移動を妨げるダムや障害物を減らす": {"humidity": 0, "temperature": 0, "biodiversity_index": 9},
    "多様な植物層を形成する": {"humidity": 0, "temperature": 0, "biodiversity_index": 8},
    "植生遷移の段階的保護": {"humidity": 0, "temperature": 0, "biodiversity_index": 8},
    "腐葉土を作り、土壌の栄養を補充": {"humidity": 0, "temperature": 0, "biodiversity_index": 8}
}

# ----- カスタムプロンプト（エージェントの思考過程の設計） -----
custom_prompt = """
あなたは土地の状態を改善し、生物多様性を向上させるエージェントです。
以下は現在の環境状態です:
  湿度: {humidity}
  温度: {temperature}
  生物多様性指数: {biodiversity_index}

この状態から、生物多様性を最も改善できる行動を、次の候補から1つ選んでください:
{actions_list}

行動を選ぶ際は、環境への影響と長期的な改善を十分に考慮してください。
"""

# ----- エージェントによる行動選択関数 -----
def select_action(environment: Environment, actions: Dict[str, Dict[str, float]]) -> str:
    state = environment.get_state()
    # 候補行動のリストを文字列に整形
    actions_list = "\n".join([f"- {action}" for action in actions.keys()])
    # カスタムプロンプトへ現在の環境状態と候補行動を埋め込む
    prompt = custom_prompt.format(
        humidity=state["humidity"],
        temperature=state["temperature"],
        biodiversity_index=state["biodiversity_index"],
        actions_list=actions_list
    )
    print("\n[エージェントの思考過程]")
    print("以下のプロンプトに基づいて最適な行動を選択します:")
    print(prompt)

    # LangChain を利用して LLM により行動を決定する
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=OPENAI_API_KEY
    ) 
    response = llm.invoke(prompt)

    response_text = response.content

    # 応答中に候補行動の名前が含まれていればそれを選択する（実際の実装ではより堅牢な解析が必要）
    for action in actions.keys():
        if action.lower() in response_text.lower():
            selected_action = action
            break
    else:
        selected_action = random.choice(list(actions.keys()))
    print(f"[エージェント決定] LangChain agent により選択された行動: {selected_action}")
    return selected_action

# ----- シミュレーションループ -----
def simulation_loop(num_turns: int = 10):
    # 初期状態の設定
    env = Environment(humidity=50, temperature=20, biodiversity_index=30)
    
    # 各パラメータの履歴を記録（可視化用）
    biodiversity_history = [env.biodiversity_index]
    humidity_history = [env.humidity]
    temperature_history = [env.temperature]
    turn_history = [0]
    
    for turn in range(1, num_turns + 1):
        print(f"\n==== ターン {turn} ====")
        current_state = env.get_state()
        print(f"[状態取得] 現在の環境状態: {current_state}")
        
        # エージェントによる行動選択
        selected_action = select_action(env, actions)
        
        # ユーザーによる介入（エージェントの決定を上書き可能）
        user_input = input("エージェントの決定を上書きしますか？ (y/n): ").strip().lower()
        if user_input == "y":
            print("利用可能な行動一覧:")
            for idx, action in enumerate(actions.keys()):
                print(f"  {idx + 1}: {action}")
            user_choice = input("実行する行動番号を入力してください: ")
            try:
                choice_idx = int(user_choice) - 1
                selected_action = list(actions.keys())[choice_idx]
                print(f"[ユーザー介入] ユーザーにより選択された行動: {selected_action}")
            except (ValueError, IndexError):
                print("入力が不正です。エージェントの決定を採用します。")
        
        # 選択した行動の効果（調整値）を取得し、環境状態を更新
        adjustments = actions[selected_action]
        env.apply_action(selected_action, {
            "humidity": adjustments.get("humidity", 0),
            "temperature": adjustments.get("temperature", 0),
            "biodiversity_index": adjustments.get("biodiversity_index", 0)
        })
        
        # 履歴の更新
        biodiversity_history.append(env.biodiversity_index)
        humidity_history.append(env.humidity)
        temperature_history.append(env.temperature)
        turn_history.append(turn)
        
        time.sleep(1)  # ターン間のウェイト（シミュレーション感を付与）
    
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
    simulation_loop(num_turns=10)