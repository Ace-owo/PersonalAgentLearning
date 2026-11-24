from myllm import LearnAgent
from agents.simpleagent import SimpleAgent
from agents.reactagent import ReactAgent
from agents.plan_solve import PlanAndSolve
from agents.reflectagent import ReflectAgent
from config import Config

if __name__ == "__main__":
    try:
        config = Config.from_env()
        llmclient = LearnAgent(
            model = config.model_name,
            api_key = config.model_api_key.get_secret_value(),
            base_url = config.base_url,
        )
        agent = ReflectAgent(llmclient)
        result = agent.run("你认为人生的意义是什么")
        if result:
            print("模型完成响应")
            print(result)

    except Exception as e:
        print(e)