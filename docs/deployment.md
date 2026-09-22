# OpsPilot 部署

OpsPilot 为面向 App 用户的客服聊天应用。FastAPI 同时提供静态前端和聊天 API，需要可访问的模型服务及 MySQL；GitHub Pages 无法运行本项目后端。

## Docker Compose

1. 在服务器安装 Docker Engine 和 Compose 插件，克隆仓库。
2. 复制 `.env.example` 为 `.env`，配置模型名称、模型接口地址、API 密钥和两组不同的随机数据库密码。Compose 中的数据库密码使用字母和数字，避免 URL 转义问题。
3. 执行 `docker compose up -d --build`。首次启动会等待 MySQL 就绪，并创建缺失的会话表，不删除已有表。
4. 在服务器执行 `curl http://127.0.0.1:18082/` 验证页面，再验证一次聊天请求。
5. 配置域名及 HTTPS 反向代理，将请求转发至 `127.0.0.1:18082`。默认配置不直接暴露数据库或应用端口。

对外演示应在反向代理或托管平台启用访问控制及请求限速。聊天接口会消耗模型额度，目前应用没有账户鉴权或额度限制；不能把公开演示地址视为生产级服务。

常用命令：

```sh
docker compose logs --tail=100 web
docker compose ps
docker compose down
```

不要执行 `docker compose down -v`，除非确实要删除数据库数据。数据保存在 `mysql_data` 持久化卷中。

## 本地启动

使用 Python 3.12+，安装 `requirements.txt` 并在 `.env` 配置自己的 MySQL 连接和模型凭据。数据库本身需预先创建。

```sh
python -m app.init_db
python main.py
```

页面默认在 `http://127.0.0.1:18082/`。只在同一 Wi-Fi 使用时，可监听 `0.0.0.0` 并通过电脑的局域网 IP 访问；这不等于公网部署。

## 临时外网演示（无需云服务器）

安装官方 Cloudflare `cloudflared`，保持 MySQL 和本机服务运行。打开两个终端：

```powershell
cd D:\shangguigu\Vibecoding_finetune\OpsPilot
.\.venv\Scripts\python.exe -m uvicorn app.api.app:app --host 127.0.0.1 --port 18082
```

另一个终端运行：

```powershell
cloudflared tunnel --url http://127.0.0.1:18082 --protocol http2
```

输出中的 `https://...trycloudflare.com` 是临时外网入口，可通过手机移动网络测试。重启通道会生成新地址，电脑关机、休眠或进程退出后无法访问。按 Ctrl+C 关闭对应终端进程。只将链接发给需要演示的人，聊天调用会消耗你配置的模型额度。

官方说明：https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/

## 上传边界

`.env`、虚拟环境、IDE 设置、本地技能、开发记录、日志、私钥、测试数据库及旧练习目录不进入 Git。`.env.example` 只有占位值。真实模型密钥只配置在部署环境，禁止写进前端文件、Dockerfile 或构建参数。

订单、知识资料和工单动作为本地模拟，未接入真实支付或人工客服系统。模型负责意图识别、闲聊和知识回复，部分业务话术由流程模板生成。
