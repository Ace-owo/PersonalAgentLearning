 #.env → Config.from_env() → main.py 把配置交给 LearnAgent
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, SecretStr

class Config(BaseModel):
    '''BaseModel 是 Pydantic 提供的基类。继承它以后，
    `Config` 就能根据字段的类型和规则检查输入。
    `hide_input_in_errors=True` 让打印出来的校验错误显示哪项有问题、
    问题是什么，同时隐藏出错时传入的原始值。'''

    '''field是给字段加规则的函数。
    str 规定这个字段要接收字符串。
    Field(min_length=1) 进一步规定字符串至少有一个字符，
    所以 "" 会校验失败'''
    model_config = ConfigDict(hide_input_in_errors = True)
    model_name: str = Field(min_length=1)
    model_api_key: SecretStr = Field(min_length=1) # 密钥类型
    base_url: str = Field(min_length=1)

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv(Path(__file__).with_name(".env"))
        return cls.model_validate({
            "model_name" : os.getenv("MODEL_NAME"),
            "model_api_key" : os.getenv("MODEL_API_KEY"),
            "base_url" : os.getenv("BASE_URL"),
        })