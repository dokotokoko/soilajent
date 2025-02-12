# Soil Agent System

このプロジェクトは、自律型土壌エージェントシステムの開発プロジェクトです。以下の手順に従って、デモやテストを実行できます。

# !!注意!!
2025年2月12日16:48時点で、動かしているディレクトリは `Agent`のみ
他は以前のプロトタイプで没
- StoH
- StoR
- StoS
- VoiceChat
- WebAccess


# プロジェクト基本設定手順書

この手順書では、プロジェクトの基本設定を行うための手順を説明します。Pythonのバージョンは3.9.0を推奨しますが、他のバージョンでも大きな影響はありません。

## セットアップ手順

### Windowsの場合

1. リポジトリをクローンします。
    ```sh
    git clone https://github.com/your-repo/your-project.git
    cd your-project
    ```

2. `pyenv-win`をインストールします。
    ```sh
    choco install pyenv-win
    ```

3. Python 3.9.0をインストールし、グローバルに設定します。
    ```sh
    pyenv install 3.9.0
    pyenv global 3.9.0
    python -V
    # Python 3.9.0
    ```

4. 仮想環境を作成し、アクティベートします。
    ```sh
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```

5. 必要なパッケージをインストールします。
    ```sh
    pip install -r requirements.txt
    ```

### MacOS/Linuxの場合

1. リポジトリをクローンします。
    ```sh
    git clone https://github.com/your-repo/your-project.git
    cd your-project
    ```

2. `pyenv`をインストールします。
    ```sh
    curl https://pyenv.run | bash
    ```

3. 必要な環境変数を設定します。
    ```sh
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    ```

4. Python 3.9.0をインストールし、グローバルに設定します。
    ```sh
    pyenv install 3.9.0
    pyenv global 3.9.0
    python -V
    # Python 3.9.0
    ```

5. 仮想環境を作成し、アクティベートします。
    ```sh
    python -m venv .venv
    source .venv/bin/activate
    ```

6. 必要なパッケージをインストールします。
    ```sh
    pip install -r requirements.txt
    ```

## 注意事項

- Windows環境でのセットアップ手順を記載していますが、MacOSやLinuxでも動作します。適宜コマンドを変更してください。
- `pyenv-win`のインストールにはChocolatey或いはpipが必要です。事前にインストールしておいてください。
- 仮想環境をアクティベートする際、PowerShellの実行ポリシーが制限されている場合があります。その場合は、以下のコマンドを実行してポリシーを変更してください。
    ```sh
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```

この手順書に従って、プロジェクトの基本設定を行ってください。
※このREADME.mdはAIによって作成されました。