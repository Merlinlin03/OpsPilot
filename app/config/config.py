from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取当前文件路径   # 获取上两层路径
ENV_DIR = Path(__file__).resolve().parents[2]
# 拼接最终目录 + 文件名称
ENV_FILE = ENV_DIR / '.env'

class Settings(BaseSettings):

    # 加载配置文件（环境变量）
    # 执行SettingsConfigDict之后，使用变量接受，
    #  变量名称固定的 model_config
    model_config = SettingsConfigDict(
        # .env文件路径
        env_file=ENV_FILE,
        # 编码方式
        env_file_encoding='utf-8',
        # .env的key数量和类属性不对应
        extra='ignore'
    )

    # 创建和配置文件（环境变量）相同名称属性
    LLM_MODEL:str
    llm_api_key: str
    llm_base_url: str
    database_url: str
    ops_api_base_url: str = "mock://opspilot"
    app_host: str
    app_port: int

settings = Settings()

if __name__ == '__main__':
    print(settings.LLM_MODEL)
