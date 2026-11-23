from myllm import LearnAgent
from agent import Agent
from config import Config

if __name__ == "__main__":
    try:
        config = Config.from_env()
        llmclient = LearnAgent(
            model = config.model_name,
            api_key = config.model_api_key.get_secret_value(),
            base_url = config.base_url,
        )
        agent = Agent(llmclient)
        result = agent.run("gpt是什么，使用搜索工具")
        if result:
            print("模型完成响应")
            print(result)

    except Exception as e:
        print(e)