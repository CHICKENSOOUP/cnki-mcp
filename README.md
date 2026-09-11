# CNKI Scholar for ChatGPT / Codex

把开源的 [`ExquisiteCore/CNKI-search`](https://github.com/ExquisiteCore/CNKI-search) 改装成一个面向 ChatGPT / Codex 的 **只读 Remote MCP + portable plugin + literature-search skill**。

目标很明确：让模型真正查询 CNKI 文献元数据，而不是把普通网页搜索误当成“查过知网”。这个项目用于文献发现、撞题检查、硕博论文检索、摘要/关键词读取和参考文献追踪；它不下载收费全文、不绕过机构权限，也不破解验证码。

> **独立性说明：** CNKI Scholar 是一个独立的开源适配项目，不是 CNKI 官方产品，也不代表 CNKI 背书。

## 现在包含什么

```text
cnki-mcp/
├── plugin.json                      # 本地/开发 portable plugin manifest
├── mcp.json                         # 本地 MCP 配置
├── plugin.template.json             # 生产 URL 模板
├── mcp.template.json                # 生产 MCP URL 模板
├── skills/
│   └── cnki-literature-search/
│       └── SKILL.md                 # CNKI 文献检索与撞题判断工作流
├── cnki_chatgpt/
│   ├── server.py                    # Remote MCP + public policy/domain routes
│   ├── runner.py                    # 参数校验与 cnki CLI 调用
│   ├── config.py                    # 环境变量配置
│   └── policy.py                    # Privacy / Terms / Support 页面
├── submission/                      # OpenAI 公共发布准备材料
│   ├── LISTING.md
│   ├── STARTER_PROMPTS.md
│   ├── TEST_CASES.md                # 正好 5 个 positive + 3 个 negative
│   ├── ANNOTATIONS.md
│   ├── DATA_FLOW.md
│   ├── AUTH.md
│   ├── RELEASE_NOTES.md
│   └── REVIEW_CHECKLIST.md
├── scripts/configure_plugin.py      # 用真实 HTTPS 域名生成生产插件包
├── deploy/                          # 反代/部署说明
├── Dockerfile
└── docker-compose.yml
```

## MCP 工具

| 工具 | 能力 | 安全边界 |
|---|---|---|
| `search_cnki` | 主题/关键词/篇名/作者/摘要/全文索引/DOI；年份与文献类型过滤；相关度/时间/被引/下载排序 | 只读；单次结果数有上限 |
| `get_cnki_paper_detail` | 标题、作者、机构、摘要、关键词、DOI、来源、基金、被引/下载等元数据；可选参考文献 | 只接受 `https://kns.cnki.net/...` |
| `get_cnki_references` | 获取 CNKI 论文参考文献列表 | 只接受 `https://kns.cnki.net/...` |

三个工具都声明：`readOnlyHint=true`、`destructiveHint=false`、`idempotentHint=true`、`openWorldHint=true`。

## Skill 做了什么

`skills/cnki-literature-search/SKILL.md` 专门解决“这个题到底有没有人写过”这一类问题。它要求模型：

- 先做**精确篇名检索**，再做主题/关键词扩展；
- 对创新性判断同时考虑期刊、硕士、博士论文；
- 分开看“被引最高”和“最新发表”；
- 结果太少时一次只放宽一个检索维度；
- 把重合拆成“标题重合 / 对象重合 / 方法重合 / 贡献重合”；
- **绝不把一次零结果当成“没人研究过”的证明**；
- 只使用工具实际返回的题名、作者、年份、摘要等元数据，不编造。

例如：

```text
帮我判断《基于视障人群需求的生活性街道无障碍环境评价与优化》
这个题目是否已经有人做过。先查精确篇名，再扩大到主题和关键词；
期刊、硕士和博士都查，不要因为一次零结果就说没人做。
```

## 本地运行

```bash
docker compose up --build
```

然后：

```bash
curl http://127.0.0.1:8000/health
```

默认 MCP endpoint：

```text
http://127.0.0.1:8000/mcp
```

开发版根目录的 `mcp.json` 故意指向这个 localhost 地址。

## 生产部署

ChatGPT 公共插件需要一个稳定的公网 HTTPS MCP endpoint。因此生产环境先准备一个域名，比如：

```text
https://cnki-scholar.example.com
```

环境变量至少设置：

```env
PUBLIC_BASE_URL=https://cnki-scholar.example.com
MCP_ALLOWED_HOSTS=cnki-scholar.example.com,cnki-scholar.example.com:*
PUBLISHER_NAME=你的 OpenAI 已验证开发者或企业名称
SUPPORT_EMAIL=你的支持邮箱
```

MCP endpoint 会是：

```text
https://cnki-scholar.example.com/mcp
```

同时公开：

```text
/                 项目首页
/health           健康检查
/privacy          隐私政策
/terms            服务条款
/support          支持说明
/.well-known/openai-apps-challenge   OpenAI 域名验证
```

如果提交页面给出域名验证 token：

```env
OPENAI_APPS_CHALLENGE=粘贴提交页面给你的原始token
```

服务会原样返回该 token。

反向代理示例见 `deploy/Caddyfile.example`。

## 生成生产 portable plugin 包

不要把示例域名硬写进仓库。部署 HTTPS 后运行：

```bash
python scripts/configure_plugin.py \
  --base-url https://cnki-scholar.example.com \
  --publisher "你的已验证发布者名称"
```

会生成：

```text
dist-plugin/
├── plugin.json
├── mcp.json
└── skills/cnki-literature-search/SKILL.md
```

这里的 `mcp.json` 才会指向真实的公网 HTTPS `/mcp`。

## OpenAI 公共提交准备

`submission/` 已经把主要材料拆好了：

- 公共 listing 文案；
- starter prompts；
- **5 个 positive + 3 个 negative review test cases**；
- 每个 MCP tool 的 annotation 解释；
- anonymous read-only 的鉴权设计说明；
- 数据流/隐私边界；
- release notes；
- 一份逐项 review checklist。

正式提交前仍然需要你自己完成几件不可代替的事情：

1. 在 OpenAI Platform 使用真实的、已验证的个人或企业发布者身份；
2. 有一个真正可访问的 HTTPS 域名；
3. 提供你自己拥有版权的 logo/icon，不要拿 CNKI 官方 logo 冒充官方集成；
4. 在提交 portal 里执行 **Scan Tools**；
5. 真机跑一遍 5+3 review cases；
6. 按 portal 要求选择发布地区并完成政策声明。

细节见 `submission/REVIEW_CHECKLIST.md`。

## 为什么当前版本不做 OAuth

这是一个**公开文献元数据、只读**的 v0.2.0：没有用户账户，没有用户专属数据库，没有写操作，也不接收 CNKI 账号、校园网密码或机构 cookie。因此它保持 anonymous read-only，而不是为了“看起来更正式”硬塞一个登录系统。

如果未来要做“每个用户绑定自己的机构 CNKI 权限、私有收藏、下载历史”等用户专属功能，再重新设计权限边界，并按当时的 MCP/OpenAI 要求走 OAuth 2.1。

## 数据与隐私

工具请求只把完成当前检索所需的数据发给上游 CNKI：搜索词、筛选参数，或一个 `kns.cnki.net` 论文 URL。

应用代码本身没有保存搜索词/结果的数据库。生产反向代理和云平台仍可能生成常规访问/错误日志，因此部署者应避免记录 request body/原始搜索词，尽量脱敏，并设置有限保留周期。更完整说明见 `/privacy` 和 `submission/DATA_FLOW.md`。

## 安全设计

- 详情/参考文献 URL 必须是 `https://kns.cnki.net/...`，避免 SSRF/任意 URL 抓取；
- MCP HTTP 层启用 DNS rebinding 防护；
- 空查询、非法字段/文献类型/排序方式直接拒绝；
- 年份范围和最大结果数强校验；
- 默认最大并发 2，避免对 CNKI 激进抓取；
- 上游 CAPTCHA/反爬触发时明确报错，绝不尝试绕过；
- 不提供 PDF/CAJ 下载和付费墙绕过；
- Docker 构建固定 `ExquisiteCore/CNKI-search` revision，避免上游静默变更。

当前固定 revision：

```text
f7f423c9962c2cfcde8b31086bdb3e1099c46888
```

## 环境变量

| 变量 | 默认 | 用途 |
|---|---|---|
| `CNKI_BIN` | `/usr/local/bin/cnki` | 上游 CLI |
| `CNKI_TIMEOUT_SECONDS` | `90` | 单次调用总超时 |
| `CNKI_MAX_RESULTS` | `100` | 单次最大返回量 |
| `CNKI_MAX_CONCURRENCY` | `2` | 对 CNKI 最大并发 |
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8000` | 服务端口 |
| `MCP_ALLOWED_HOSTS` | localhost 集合 | DNS rebinding Host allowlist |
| `MCP_ALLOWED_ORIGINS` | localhost 集合 | 浏览器/Inspector Origin allowlist |
| `PUBLIC_BASE_URL` | 空 | 公网 HTTPS origin |
| `PUBLISHER_NAME` | `CNKI Scholar contributors` | 页面/部署标识 |
| `SUPPORT_EMAIL` | 空 | 支持/隐私联系邮箱 |
| `OPENAI_APPS_CHALLENGE` | 空 | OpenAI 域名验证 token |

## 测试

适配层测试无需连接 CNKI：

```bash
python -m unittest discover -s tests -v
```

另外建议部署后再做两类 live test：

```text
1. 用 MCP Inspector / OpenAI Scan Tools 检查三项工具 schema 和 annotations
2. 实际跑 search -> detail -> references，确认部署网络可以访问 kns.cnki.net
```

本项目不会伪造“联网测试通过”。如果构建环境无法访问 GitHub/CNKI，只能完成静态/适配层测试，真正 CNKI 联调必须在能联网的部署环境完成。

## License / third-party

本适配层 MIT。上游 `ExquisiteCore/CNKI-search` 也是 MIT；详见 `THIRD_PARTY_NOTICES.md`。CNKI 内容、商标、服务条款与数据库权利归其相应权利人所有。

## License

This project is released under the MIT License. Copyright (c) 2026 Chengxu Xie.

It uses the MIT-licensed open-source project [`ExquisiteCore/CNKI-search`](https://github.com/ExquisiteCore/CNKI-search) as an upstream command-line client. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for attribution. This repository is an unofficial community project and is not affiliated with, endorsed by, or sponsored by CNKI.
