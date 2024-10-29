# test_AutoGen.py 実行手順書

この手順書では、`test_AutoGen.py`を実行するための手順を説明します。このスクリプトは、土壌エージェント同士の対話をシミュレートするためのものです。

## 前提条件

- プジェクトの基本設定が完了していること。
- 必要なパッケージがインストールされていること。
- `.env`ファイルにOpenAIのAPIキーが設定されていること。

## 実行手順

1. **プロジェクトディレクトリに移動します。**
    ```sh
    cd your-project
    ```

2. **仮想環境をアクティベートします。**

   - **Windowsの場合**
    ```sh
    .venv\Scripts\Activate.ps1
    ```

   - **MacOS/Linuxの場合**
    ```sh
    source .venv/bin/activate
    ```

3. **`test_AutoGen.py`を実行します。**
    ```sh
    python StoS/test_AutoGen.py
    ```

4. **結果を確認します。**
   - スクリプトが実行されると、土壌エージェント同士の対話がシミュレートされ、結果が表示されます。

## プログラムの解説

`test_AutoGen.py`は、2つの土壌エージェント（`agent1`と`agent2`）が対話を行うためのスクリプトです。以下に、主要な部分を解説します。

### 1. 環境設定

```python
import os
from dotenv import load_dotenv

from autogen import ConversableAgent
import prompt_toSoil

# 環境設定
load_dotenv()
apikey = os.getenv("OPENAI_API_KEY")
```

- `dotenv`ライブラリを使用して、`.env`ファイルから環境変数を読み込みます。
- OpenAIのAPIキーを取得します。

### 2. エージェントの設定

```python
agent1 = ConversableAgent(
    "Kou",
    system_message= prompt_toSoil.sytemprompt_for_1,
    llm_config= {"config_list": [{"model": "gpt-4", "api_key": apikey, "api_rate_limit": 60}]},
    is_termination_msg= lambda msg: "ばいばい" in msg["content"].lower(),
    human_input_mode= "TERMINATE",
)

agent2 = ConversableAgent(
    "KOKO",
    system_message= prompt_toSoil.sytemprompt_for_2,
    llm_config= {"config_list": [{"model": "gpt-4", "api_key": apikey, "api_rate_limit": 60}]},
    is_termination_msg= lambda msg: "ばいばい" in msg["content"].lower(),
    human_input_mode= "TERMINATE",
)
```

- `ConversableAgent`クラスを使用して、2つのエージェント（`Kou`と`KOKO`）を作成します。
- 各エージェントには、システムメッセージ、使用するモデル、APIキー、終了条件が設定されています。
- `is_termination_msg`は、エージェントが「ばいばい」と言った場合に対話を終了するための条件です。

### 3. 対話の開始

```python
result = agent1.initiate_chat(agent2, message="最近調子どう？", max_turns=5)
```

- `agent1`が`agent2`に対して「最近調子どう？」というメッセージを送信し、最大5ターンの対話を開始します。
- 結果は`result`に格納され、エージェント同士の対話の内容が含まれます。

## 注意事項

- OpenAIのAPIキーが正しく設定されていない場合、スクリプトは正常に動作しません。必ず`.env`ファイルを確認してください。
- スクリプトの実行中にエラーが発生した場合は、必要なパッケージが正しくインストールされているか確認してください。

この手順書に従って、`test_AutoGen.py`を実行してください。