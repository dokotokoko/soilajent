import base64
import io
import random
import time
import os
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for
from langchain_openai.chat_models.base import ChatOpenAI

# demo_o3.py 内のクラス・関数をインポート
from demo_o3 import Environment, actions, select_action

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # セッション等を利用する場合の秘密鍵

# シミュレーション状態管理クラス
class SimulationManager:
    def __init__(self, num_turns=10):
        self.num_turns = num_turns
        self.current_turn = 0
        # 初期状態：湿度50, 温度20, 生物多様性指数30
        self.env = Environment(humidity=50, temperature=20, biodiversity_index=30)
        self.biodiversity_history = [self.env.biodiversity_index]
        self.humidity_history = [self.env.humidity]
        self.temperature_history = [self.env.temperature]
        self.turn_history = [0]

    def is_finished(self):
        return self.current_turn >= self.num_turns

    def get_current_state(self):
        return self.env.get_state()

    def agent_suggest_action(self):
        # 現在の状態に基づきエージェントが提案する行動を取得
        suggestion = select_action(self.env, actions)
        return suggestion

    def advance_turn(self, action: str):
        adjustments = actions[action]
        self.env.apply_action(action, adjustments)
        self.current_turn += 1
        self.biodiversity_history.append(self.env.biodiversity_index)
        self.humidity_history.append(self.env.humidity)
        self.temperature_history.append(self.env.temperature)
        self.turn_history.append(self.current_turn)

# グローバル変数でシミュレーション状態を保持（シンプルな例のため）
sim_manager = None

def generate_plot(sim_manager: SimulationManager):
    plt.figure(figsize=(10, 5))
    plt.plot(sim_manager.turn_history, sim_manager.biodiversity_history, marker='o', label='Biodiversity Index')
    plt.plot(sim_manager.turn_history, sim_manager.humidity_history, marker='x', label='Humidity')
    plt.plot(sim_manager.turn_history, sim_manager.temperature_history, marker='s', label='Temperature')
    plt.xlabel('Turn')
    plt.ylabel('Value')
    plt.title('環境パラメータの推移')
    plt.legend()
    plt.grid(True)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return image_base64

@app.route('/')
def index():
    # シミュレーション開始前のページ
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global sim_manager
    sim_manager = SimulationManager(num_turns=10)
    return redirect(url_for('simulate'))

@app.route('/simulate', methods=['GET', 'POST'])
def simulate():
    global sim_manager
    if sim_manager is None:
        return redirect(url_for('index'))
    if request.method == 'POST':
        # ユーザーが選択した行動をフォームより取得
        selected_action = request.form.get('action')
        if selected_action:
            sim_manager.advance_turn(selected_action)
        # シミュレーション終了チェック
        if sim_manager.is_finished():
            return redirect(url_for('result'))
        else:
            return redirect(url_for('simulate'))
    else:
        current_state = sim_manager.get_current_state()
        # 各ターンごとにエージェントの提案を取得
        agent_suggestion = sim_manager.agent_suggest_action()
        return render_template(
            'simulate.html',
            turn=sim_manager.current_turn + 1,
            state=current_state,
            actions=list(actions.keys()),
            agent_suggestion=agent_suggestion
        )

@app.route('/result')
def result():
    global sim_manager
    if sim_manager is None:
        return redirect(url_for('index'))
    # matplotlib によるプロットを画像化して埋め込み
    plot_image = generate_plot(sim_manager)
    return render_template('result.html', plot_image=plot_image)

# ----- 人間とのチャット（コミュニケーション）機能 -----  
# 単純なシングルユーザー用のチャット履歴をグローバル変数で保持
chat_history = []

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    global chat_history
    if request.method == 'POST':
        user_message = request.form.get('user_message')
        if user_message:
            # ユーザーからのメッセージを履歴に記録
            chat_history.append({"role": "user", "content": user_message})
            # システムの初期プロンプトとこれまでの対話履歴を含むプロンプトを構築
            prompt = "以下はユーザーと環境改善エージェントの対話です。エージェントは環境に関する専門的なアドバイスを提供します。\n"
            for msg in chat_history:
                prompt += f"{msg['role']}: {msg['content']}\n"
            # チャットモデルによるエージェントの応答を取得
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.7,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            response = llm.invoke(prompt)
            assistant_reply = response.content
            chat_history.append({"role": "assistant", "content": assistant_reply})
        return redirect(url_for('chat'))
    return render_template('chat.html', chat_history=chat_history)

if __name__ == '__main__':
    app.run(debug=True)