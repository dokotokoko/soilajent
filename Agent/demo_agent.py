import os
import random
import matplotlib.pyplot as plt
from openai import OpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain_openai.chat_models.base import ChatOpenAI
from dotenv import load_dotenv

# 環境変数の読み込み（OpenAI APIキーが必要）
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 環境のパラメータ（初期状態）
class Environment():
    def __init__(self, humidity, temperature, ph, bd_score):
        self.humidity = humidity
        self.temperature = temperature
        self.ph = ph
        self.bd_score = bd_score

    # 環境の状態を取得する関数
    def get_environment_state(self):
        state = (f"現在の環境の状態:\n"
                 f"- 湿度: {self.humidity}\n"
                 f"- 温度: {self.temperature}\n"
                 f"- 土壌pH: {self.ph}\n"
                 f"- 生物多様性指数: {self.bd_score}")
        return state

class Agent():
    # LLMの設定（OpenAIのGPTを使用）
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=OPENAI_API_KEY
    ) 

    # 行動の選択肢リスト
    action_list = {
        "水をあげる",
        "肥料を撒く",
        "日光を増やす",
        "植生を増やす"
    }

    #環境を作成
    environment = Environment(humidity=30, temperature=25, ph=6.5, bd_score=0.7)

    # エージェントが行動を選択する関数
    def choose_action(environment, action_list, llm):
        prompt = (f"環境の状態: 湿度={environment.humidity}%, 温度={environment.temerature}°C, "
                f"土壌pH={environment.ph}, 生物多様性指数={environment.bd_score}\n"
                "この環境を改善するための最適な行動を1つ選んでください。")
        action = llm(prompt)
        return action

    # 行動を実行し環境を更新する関数
    @Tool
    def apply_action(action):
        if "水をあげる" in action:
            environment.humidity = min(environment.humidity+ 20, 100)
        elif "肥料を撒く" in action:
            environment["soil_ph"] = max(environment["soil_ph"] - 0.2, 5.5)
        elif "日光を増やす" in action:
            environment["temperature"] = min(environment["temperature"] + 2, 35)
        elif "植生を増やす" in action:
            environment["biodiversity_index"] = min(environment["biodiversity_index"] + 0.1, 1.0)
        return environment

    # LangChainのエージェントを作成
    memory = ConversationBufferMemory(memory_key="chat_history")
    tools = [environment_tool]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )

    # シミュレーションを実行
    def run_simulation(turns=5):
        history = []
        for t in range(turns):
            print(f"\n=== ターン {t+1} ===")
            print(get_environment_state())
            action = choose_action()
            print(f"エージェントの行動: {action}")
            updated_state = apply_action(action)
            history.append(updated_state.copy())
        return history

    # 実行
    env_history = run_simulation()

    # 環境変化を可視化
    def plot_environment(history):
        turns = range(len(history))
        humidity = [h["humidity"] for h in history]
        temperature = [h["temperature"] for h in history]
        biodiversity = [h["biodiversity_index"] for h in history]

        plt.figure(figsize=(8, 5))
        plt.plot(turns, humidity, label="湿度", marker="o")
        plt.plot(turns, temperature, label="温度 (°C)", marker="s")
        plt.plot(turns, biodiversity, label="生物多様性指数", marker="^")
        plt.xlabel("ターン数")
        plt.ylabel("値")
        plt.title("環境の変化")
        plt.legend()
        plt.show()

    # グラフを表示
    plot_environment(env_history)
