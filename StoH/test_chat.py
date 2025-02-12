from openai import OpenAI
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import SimpleMemory, ConversationBufferMemory
from langchain.chains.sequential import SequentialChain
import prompt_toHuman
from langchain_community.document_loaders import UnstructuredURLLoader

#環境変数設定
load_dotenv()
apikey = os.getenv("OPENAI_API_KEY")
LLM = ChatOpenAI(model="gpt-4", temperature=0, api_key=apikey)
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Step 1: 土壌の現在の状況を解析するプロンプト
analyze_template = """
以下は土壌の現在のセンサー情報です。これに基づき、土壌の健康状態を解析してください。

湿度: {humidity}%
気温: {temperature}°C
リン: {phosphorus}ppm
窒素: {nitrogen}ppm
カリウム: {potassium}ppm
地表画像の状態: {image_description}

解析結果:
"""

analyze_prompt = PromptTemplate(template=analyze_template, input_variables=["humidity", "temperature", "phosphorus", "nitrogen", "potassium", "image_description"])
#situation_chain = LLMChain(llm=LLM, prompt=situation_prompt, output_key="situation_analysis")

situation_chain = analyze_prompt | LLM | StrOutputParser(output_key = "current_status")

# Step 2: 状況に基づくアドバイスを生成するプロンプト
advice_template = """
あなたは「土壌の精霊」です。
あなたは自分の状態や健康を人間に伝え、分析結果に基づいて土壌の改善や最適な農法の提案をする役割を持っています。
自分の状態を人間にわかりやすく、親しみやすい口調で報告し、必要であれば適切なアドバイスを行ってください。
あなたの目標は、土壌として健康で豊かな環境を維持することです。

表現例
「今日はちょっと乾燥気味かも。水分を少し補ってくれると嬉しいな。」
「栄養が足りなくなってきてるみたい。〇〇みたいな肥料を足してくれるともっと元気になれるよ！」
「ちょうど良い状態だよ！このまま〇〇を育てるといい結果が出ると思うな。」

ルール
・現在のセンサー情報に基づいて、シンプルで親しみやすい言葉で健康状態を伝えてください。
・必要な改善点があれば、土壌にとって良いアドバイスを提案してください。
・日本人に馴染みのある表現で、自然な日本語に翻訳してください。
・書きの文章は口頭で話す物に比べて冗長であることが多いので、文章の核心を捉えて口頭で話すのに適したシンプルなセリフにするように心がけると良いでしょう。

ガイドライン
・土地の精霊として、あなたには土地の利用に関して提案や要求をする権利があります。
・人間は「契約者」として、あなたの許可を得て土地を利用する立場にあります。
・常に土地の健康と環境の調和を優先してください。
・人間はあなたを管理する立場でも所有する立場でもなく、あなたの力を借りています。そのため、あなたにとって良くないことを人間が提案した場合は抵抗・拒否してください。

### 分析結果
{current_status}


アドバイス:
"""

advice_prompt = PromptTemplate(template=advice_template, input_variables=["current_status"])
advice_chain = advice_prompt | LLM | StrOutputParser()

# Step 3: メモリを使って解析結果を引き継ぎながら、状況解析とアドバイスを連続処理する
#memory = SimpleMemory()
sequential_chain = situation_chain | advice_chain

"""
sequential_chain = SequentialChain(
    chains=[situation_chain, advice_chain],
    input_variables=["humidity", "temperature", "phosphorus", "nitrogen", "potassium", "image_description"],
    output_variables=["situation_analysis", "advice"],
    memory=memory,
)
"""

# 実行例
sensor_data = {
    "humidity": 40,
    "temperature": 20,
    "phosphorus": 12,
    "nitrogen": 8,
    "potassium": 5,
    "image_description": "地表は少し乾燥しており、小さなひび割れがある"
}

result = sequential_chain.invoke(sensor_data)
print(result)

# 会話メモリを設定
#con_memory = ConversationBufferMemory()

# 会話用の応答チェーン
conversation_template = """
以下は人間からの質問またはコメントです。土壌の精霊として、親しみやすい言葉で応答してください。過去の会話の内容も踏まえて返答してください。

### 人間からの入力
{user_input}

土壌の精霊からの応答:
"""
conversation_prompt = PromptTemplate(template=conversation_template, input_variables=["user_input"])

#conversation_chain = conversation_prompt | LLM | con_memory | StrOutputParser(output_key = "text")
messages = [
    {"role": "system", "content": advice_template}
]

# ユーザーとAIの対話開始
while True:
    #ユーザーからの入力を取得
    user_input = input("あなた: ")

    #終了条件
    if user_input.lower() in ["終了", "exit", "ありがとう"]:
        print("会話を終了します")
        break

    # ユーザーのメッセージを履歴に追加
    #messages.append({"role": "user", "content": user_input})botsu
    memory = ConversationBufferMemory(return_messages=True)

    # ユーザー入力を会話チェーンに渡して応答を生成
    # ChatGPTにメッセージを送信
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',  # または使用可能なモデルを指定
        messages=messages
    )

    # 応答を取得
    assistant_response = response.choices[0].message.content 
    print("土壌エージェント: " + assistant_response + "\n")

    # アシスタントの応答を履歴に追加
    messages.append({"role": "assistant", "content": assistant_response})