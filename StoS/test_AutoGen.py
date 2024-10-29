import os
from dotenv import load_dotenv

from autogen import ConversableAgent
import prompt_toSoil

#環境設定
load_dotenv()
apikey = os.getenv("OPENAI_API_KEY")

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

result = agent1.initiate_chat(agent2, message="最近調子どう？", max_turns=5)