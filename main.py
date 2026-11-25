import sys

from myllm import LearnAgent
from agents.simpleagent import SimpleAgent
from agents.reactagent import ReactAgent
from agents.plan_solve import PlanAndSolve
from agents.reflectagent import ReflectAgent
from config import Config

from memory.memory_config import MemoryConfig
from memory.memory_manager import MemoryManager
from memory.memory_tool import MemoryTool
from messages import Messages
from tools import TOOL_DEFINITION, TOOL_REGISTRY, Tool

# 修复 Windows 终端中文乱码
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

memory_tool = MemoryTool(MemoryManager(MemoryConfig()), user_id="local-user")

for method in (
    memory_tool.save_memory,
    memory_tool.read_memory,
    memory_tool.forget_memory,
    memory_tool.delete_memory,
):
    tool = Tool(method)
    TOOL_REGISTRY[tool.name] = tool.function
    TOOL_DEFINITION.append(tool.to_definition())


def build_agent(name: str, llmclient):
    agents = {
        "simple": SimpleAgent,
        "react": ReactAgent,
        "plan": PlanAndSolve,
        "reflect": ReflectAgent,
    }
    return agents[name](llmclient)


if __name__ == "__main__":
    try:
        config = Config.from_env()
        llmclient = LearnAgent(
            model=config.model_name,
            api_key=config.model_api_key.get_secret_value(),
            base_url=config.base_url,
        )

        # 默认用 ReactAgent（支持多轮工具调用）
        agent = ReactAgent(llmclient)

        # 短期记忆：维护全局历史消息列表
        history: list[Messages] = []

        print("个人助手已启动，输入 exit / quit 退出。")
        print("=" * 40)

        while True:
            user_input = input("\n你: ").strip()
            if user_input.lower() in ("exit", "quit"):
                print("再见！")
                break
            if not user_input:
                continue

            # 调用 agent，传入历史，返回后把本轮对话追加进历史
            reply = agent.run(user_input, history=history)
            reply = reply or "（模型没有返回内容）"

            history.append(Messages(role="user", content=user_input))
            history.append(Messages(role="assistant", content=reply))

            print("\n助手:", reply)

    except Exception as e:
        print("运行出错:", e)
