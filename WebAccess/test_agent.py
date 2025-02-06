import openai
from openai import OpenAI
import os

from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# For Agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_core.tools import Tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.document_loaders.pdf import BasePDFLoader
from langchain.agents import AgentExecutor, AgentType, initialize_agent, load_tools
from langchain.chains.transform import TransformChain
from langchain.chains.sequential import SequentialChain
from langchain.chains.base import Chain

#LLM設定
load_dotenv()
apikey = os.getenv("OPENAI_API_KEY")
LLM = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=apikey)

#1st: センシングデータから現在の情報を分析
analyze_template = """
以下は土壌の現在のセンサー情報です。

湿度: {humidity}%
気温: {temperature}°C
リン: {phosphorus}ppm
窒素: {nitrogen}ppm
カリウム: {potassium}ppm
地表画像の状態: {image_description}
"""

analyze_prompt = PromptTemplate(template=analyze_template, input_variables=["humidity", "temperature", "phosphorus", "nitrogen", "potassium", "image_description"])

analyze_chain = analyze_prompt | LLM | StrOutputParser(output_key = "status")

#2nd: 外部情報取得エージェント作成
def URLLoader(text: str):
    urls = ["https://www.maff.go.jp/j/press/nousan/kankyo/240930.html"]

    loader = UnstructuredURLLoader(urls=urls)

    data = loader.load()

    return data

report_template = """
現在の状況から必要があると判断したらURLの情報を取得し、{tex}の後に追記する形で教えてください。

###現在の状況
{text}
"""

report_prompt = PromptTemplate(template= report_template, input_variables=["text"])

url_tool = Tool(
    name="URL_Loader",
    func=URLLoader,
    description="現在の状況を元に、URLの情報を参照する必要があれば取得して要約する。"
)

tools = [url_tool]

agent = initialize_agent(tools=tools, llm=LLM, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent_executer = agent.invoke({"input": "current_status"})
print(agent_executer)
#agent.run(report_prompt.format_prompt(word=word))


"""
#2nd-1: 中間ラッパーを作成
def rename_output(inputs: dict) -> dict:
    return {'report': inputs['output']}

output_chain = SequentialChain(
    chains= agent,
    input_variables=['output'],
    output_variables=['report']
)
"""

#3rd: 分析結果と情報収集結果を元に提案を行う
suggest_template = """

### 現在の状況
{input}

### 取得した情報
{output}

"""

suggest_prompt = PromptTemplate(template=suggest_template, input_variables=["input", "output"])
suggest_chain = suggest_prompt | LLM | StrOutputParser()

#4th: chainを繋いでタスクを実行する
sequential_chain = analyze_chain | agent

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