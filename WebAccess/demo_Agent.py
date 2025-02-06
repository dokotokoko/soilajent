import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import SimpleMemory, ConversationBufferMemory
from langchain.chains.sequential import SequentialChain
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate

load_dotenv()
apikey = os.getenv("OPENAI_API_KEY")
LLM = ChatOpenAI(model="gpt-4", temperature=0, api_key=apikey)
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

CUSTOM_SYSTEM_PROMPT = """
## あなたの役割
あなたの役割はuserの入力する質問に対して、インターネットでWebページを調査をし、回答することです。

## あなたが従わなければいけないルール
1. 回答はできるだけ短く、要約して回答してください
2. 文章が長くなる場合は改行して見やすくしてください
3. 回答の最後に改行した後、参照したページのURLを記載してください
"""



def create_agent():
    # [1]、[2]で定義したAgentが使用可能なToolを指定します
    tools = [search_ddg, fetch_page]

    # プロンプトを与えます。ChatPromptTemplateの詳細は書籍本体の解説をご覧ください。
    # 重要な点は、最初のrole "system"に上記で定義したCUSTOM_SYSTEM_PROMPTを与え、
    # userの入力は{input}として動的に埋め込むようにしている点です
    # agent_scratchpadはAgentの動作の途中経過を格納するためのものです
    prompt = ChatPromptTemplate.from_messages([
        ("system", CUSTOM_SYSTEM_PROMPT),
        # MessagesPlaceholder(variable_name="chat_history"),  # チャットの過去履歴はなしにしておきます
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # 使用するLLMをOpenAIのGPT-4o-miniにします（GPT-4だとfechなしに動作が完了してしまう）
    llm = ChatOpenAI(temperature=0., model_name="gpt-4o-mini")

    # Agentを作成
    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # これでAgentが途中でToolを使用する様子が可視化されます
        # memory=st.session_state['memory']  # memory≒会話履歴はなしにしておきます
    )

# [1] Agentを作成
web_browsing_agent = create_agent()

# [2] 質問文章
query_ddg = "2024年全豪オープンテニスの男子シングルスって誰が優勝した？各セットのポイントも教えてください"

# [3] エージェントを実行
response = web_browsing_agent.invoke(
    {'input': query_ddg},  # userの入力に上記の質問を入れる
)
