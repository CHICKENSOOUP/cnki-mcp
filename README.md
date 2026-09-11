# CNKI Scholar for ChatGPT / Codex

**语言：** [English](README.en.md) | [简体中文](README.md)

这是一个让 ChatGPT、Codex 等工具查询 CNKI（中国知网）论文信息的小服务。它可以搜索论文题录、读取摘要和关键词、查看论文详情与参考文献，并返回 JSON 或引用信息。

它只读取文献资料，不下载收费全文，不收集 CNKI 账号、密码或 Cookie，也不会尝试绕过验证码和访问限制。

## 能做什么

| 工具 | 用途 |
|---|---|
| `search_cnki` | 按主题、关键词、篇名、作者、摘要、全文或 DOI 搜索；可以按年份、文献类型和排序方式筛选 |
| `get_cnki_paper_detail` | 读取标题、作者、单位、摘要、关键词、DOI、来源、基金、被引/下载数等信息 |
| `get_cnki_references` | 读取一篇论文的参考文献 |

支持的文献类型包括期刊、硕士论文、博士论文、会议、报纸和年鉴。工具名称和参数保持不变，方便接入 MCP 客户端。

## 一键启动（Windows）

先安装并启动 [Docker Desktop](https://www.docker.com/products/docker-desktop/)，然后在项目根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

脚本会自动：

1. 检查 Docker 是否可用；
2. 构建镜像；
3. 在后台启动服务；
4. 等待 `http://127.0.0.1:8000/health` 返回成功。

启动成功后：

- 服务首页：<http://127.0.0.1:8000/>
- 健康检查：<http://127.0.0.1:8000/health>
- MCP 地址：<http://127.0.0.1:8000/mcp>

停止服务：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1 -Stop
```

查看日志：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1 -Logs
```

脚本不会覆盖已有的 `.env`，也不会打印其中的内容。

## 不用脚本时

如果已经安装 Docker，也可以直接运行：

```bash
docker compose up --build -d
curl http://127.0.0.1:8000/health
docker compose down
```

## 在 MCP 客户端中使用

开发配置已经写在根目录的 `mcp.json` 中，默认地址是：

```text
http://127.0.0.1:8000/mcp
```

启动服务后，把这个地址添加到支持 Remote MCP 的客户端，然后可以直接说：

```text
帮我在知网上搜索“大语言模型”相关论文，限定 2020 年以后，按被引排序。
```

也可以要求读取某篇论文的详情或参考文献。详情和参考文献 URL 必须来自 `https://kns.cnki.net/...`。

## 直接使用上游 `cnki` 命令

Docker 镜像会自动编译并安装上游 [`ExquisiteCore/CNKI-search`](https://github.com/ExquisiteCore/CNKI-search) 的 `cnki` 命令。它也可以单独运行：

```bash
cnki search "深度学习" --size=10
cnki search "大语言模型" --from=2020 --to=2025 --sort=cited --size=30
cnki search "知识图谱" --size=20 --format=citation
cnki detail "https://kns.cnki.net/kcms2/article/abstract?v=..." --with-refs --format=markdown
cnki refs "https://kns.cnki.net/kcms2/article/abstract?v=..."
```

上游命令支持 JSON、表格、引用和 Markdown 输出。详细参数见 [ExquisiteCore/CNKI-search](https://github.com/ExquisiteCore/CNKI-search)。

## 配置

普通本地使用不需要改配置。需要调整时，可以复制示例文件：

```powershell
Copy-Item .env.example .env
```

常用变量：

| 变量 | 默认值 | 用途 |
|---|---|---|
| `CNKI_TIMEOUT_SECONDS` | `90` | 单次请求最长等待时间 |
| `CNKI_MAX_RESULTS` | `100` | 单次最多返回多少条结果 |
| `CNKI_MAX_CONCURRENCY` | `2` | 同时向 CNKI 发起的请求数 |
| `PORT` | `8000` | 本地服务端口 |
| `PUBLISHER_NAME` | `CNKI Scholar contributors` | 页面上显示的维护者名称 |
| `SUPPORT_EMAIL` | 空 | 支持邮箱 |

`.env` 只应放在本机或服务器上，不要提交到 Git。示例文件不包含真实凭据。

## 公开部署

如果只在自己电脑上使用，到这里就够了。如果要让其他人访问，还需要：

1. 准备一个可以从公网访问的 HTTPS 域名；
2. 将域名反向代理到容器的 8000 端口；
3. 设置 `PUBLIC_BASE_URL`、`MCP_ALLOWED_HOSTS`、`PUBLISHER_NAME` 和 `SUPPORT_EMAIL`；
4. 运行 `python scripts/configure_plugin.py --base-url https://你的域名 --publisher "你的名称"` 生成插件配置。

反向代理示例见 [`deploy/Caddyfile.example`](deploy/Caddyfile.example)。完整的 OpenAI 提交材料在 `submission/` 目录中。

## 安全说明

- 只接受 `https://kns.cnki.net/...` 的论文详情链接；
- 不提供 PDF/CAJ 下载、付费墙绕过或验证码绕过；
- 不需要 CNKI 登录账号、校园网密码或机构 Cookie；
- 服务端不会把搜索结果写入数据库；
- 公开部署时请关闭详细请求日志，并给日志设置保留期限。

## 测试

适配层测试不需要连接 CNKI：

```bash
python -m unittest discover -s tests -v
```

当前测试集共 11 项。真实的 CNKI 搜索需要能访问 `kns.cnki.net` 的部署环境。

## 项目文件

```text
cnki-mcp/
├── cnki_chatgpt/              # MCP 服务代码
├── skills/                    # 文献检索 skill
├── scripts/start.ps1          # Windows 一键启动/停止脚本
├── scripts/configure_plugin.py  # 生成正式插件配置
├── submission/                # 发布材料
├── Dockerfile
├── docker-compose.yml
├── mcp.json
└── plugin.json
```

## 许可证

本项目使用 MIT License，版权归 `Chengxu Xie`（2026）所有。上游 `ExquisiteCore/CNKI-search` 也使用 MIT License，详见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。