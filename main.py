from myllm import LearnAgent
from agent import Agent

if __name__ == "__main__":
    try:
        llmclient = LearnAgent()
        agent = Agent(llmclient)
        result = agent.run("请用一句话介绍自己")
        if result:
            print("模型完成响应")
            print(result)

    except Exception as e:
        print(e)