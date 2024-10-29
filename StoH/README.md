# demo_chat.py 実行手順書

この手順書では、`demo_chat.py`を実行するための手順を説明します。このスクリプトは、土壌エージェントとの対話を行うためのものです。

## 前提条件

- プロジェクトの基本設定が完了していること。
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

3. **`demo_chat.py`を実行します。**
    ```sh
    python StoH/demo_chat.py
    ```

4. **対話を開始します。**
   - スクリプトが実行されると、「土地との対話を開始します。終了するには「終了」と入力してください。」というメッセージが表示されます。
   - ユーザーはプロンプトに従って入力を行い、土壌エージェントとの対話を楽しむことができます。

5. **対話を終了するには、「終了」と入力します。**
   - 終了条件を満たすと、「対話を終了します。」というメッセージが表示され、スクリプトが終了します。

## プログラムの解説

`demo_chat.py`は、土壌エージェントとの対話を行うためのスクリプトです。以下に、主要な部分を解説します。

### 1. 必要なライブラリのインポート

```python
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import prompt_toHuman
```

- `openai`ライブラリを使用して、OpenAIのAPIにアクセスします。
- `dotenv`ライブラリを使用して、環境変数を読み込みます。
- `prompt_toHuman`は、システムプロンプトを定義するためのモジュールです。

### 2. 環境変数の読み込み

```python
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
```

- `.env`ファイルから環境変数を読み込み、OpenAIのAPIキーを取得します。
- `OpenAI`クライアントを初期化します。

### 3. システムプロンプトの定義

```python
system_prompt = prompt_toHuman.systemprompt
```

- `prompt_toHuman`からシステムプロンプトを取得します。このプロンプトは、エージェントの動作を定義するために使用されます。

### 4. 対話履歴の初期化

```python
messages = [
    {"role": "system", "content": system_prompt}
]
```

- 対話履歴を保持するリストを初期化します。最初のメッセージはシステムプロンプトです。

### 5. ユーザーとの対話ループ

```python
while True:
    user_input = input("あなた: ")

    if user_input == "終了":
        print("対話を終了します。")
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages
    )

    assistant_response = response.choices[0].message.content 
    print("土地: " + assistant_response + "\n")

    messages.append({"role": "assistant", "content": assistant_response})
```

- 無限ループを使用して、ユーザーからの入力を受け取ります。
- ユーザーが「終了」と入力すると、対話を終了します。
- ユーザーのメッセージを履歴に追加し、OpenAIのAPIに送信します。
- APIからの応答を取得し、表示します。アシスタントの応答も履歴に追加します。

### 6. プロンプト生成関数

```python
def generate_prompt_toH(humidity=float, temperature=float, potassium=float, phosphorus=float, nitrogen=float, image_description=str):
    return f"""
        現在の私の状態はこちらです。
        - **湿度**: {humidity}%
        - **気温**: {temperature}°C
        - **元素分析**: リン: {phosphorus}ppm, 窒素: {nitrogen}ppm, カリウム: {potassium}ppm
        - **地表画像**: {image_description}
        この情報を基に、アドバイスをお願いします。
    """
```

- この関数は、土壌の状態に関する情報をフォーマットして返します。湿度、気温、元素分析、地表画像の情報を含みます。

## 注意事項

- OpenAIのAPIキーが正しく設定されていない場合、スクリプトは正常に動作しません。必ず`.env`ファイルを確認してください。
- スクリプトの実行中にエラーが発生した場合は、必要なパッケージが正しくインストールされているか確認してください。

この手順書に従って、`demo_chat.py`を実行してください。