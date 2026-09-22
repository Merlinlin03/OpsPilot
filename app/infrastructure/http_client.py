import asyncio

from httpx import AsyncClient

# 定义变量
http_client : AsyncClient | None = None

# 初始化的方法
def init_http_client():
    global http_client
    http_client = AsyncClient(timeout=10.0)

def get_http_client()->AsyncClient:
    global http_client

    return http_client

# 关闭方法
async def close_http_client():
    await http_client.aclose()


if __name__ == '__main__':
    # 调用测试方法
    async def main():
        # 创建httpclient对象
        init_http_client()
        # 预留外部 HTTP 调用能力；当前 OpsPilot demo 使用本地 mock provider。
        response = await http_client.get(
            url="http://127.0.0.1:18081/users/u1001/orders")
        print(response.json())

    # 调用测试方法
    asyncio.run(main())
