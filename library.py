import openai
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import UnstructuredURLLoader

# LLM設定
load_dotenv()

class URLSummarizer:
    """
    # 使用例
    if __name__ == "__main__":
        url = "https://www.maff.go.jp/j/tokei/kouhyou/noukou/gaiyou/index.html#1"
        summarizer = URLSummarizer(url)
        summary = summarizer.summarize()
        print(summary)
    """
    def __init__(self, url):
        self.url = url
        self.loader = UnstructuredURLLoader(urls=[self.url])
        self.data = self.load_data()
        self.model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key= os.getenv("OPENAI_API_KEY"))

    def load_data(self):
        return self.loader.load()

    def summarize(self):
        prompt = """
        以下の内容を日本語で要約してください

        {text}
        """
        prompt_template = PromptTemplate(template=prompt, input_variables=["text"])
        chain = prompt_template | self.model | StrOutputParser()

        # データがリストの場合、最初の要素を取得する
        if isinstance(self.data, list):
            self.data = self.data[0]  # 最初の要素を使用

        # データの長さを確認し、必要に応じて要約またはトリミングします
        if len(self.data) > 1000:  # 例えば、1000文字を超える場合
            self.data = self.data[:1000]  # 最初の1000文字だけを使用

        summary = chain.invoke({"text": self.data})  # dataを辞書形式で渡す
        return summary
