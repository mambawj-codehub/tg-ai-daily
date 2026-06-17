# tg-ai-daily 设计规格书

一个 Python 工具，拉取配置的 Telegram 频道过去 24 小时的消息，通过 OpenAI API 生成按主题分类的中文日报摘要。

## 架构

**模块化 CLI** — 单入口 `main.py` 编排独立模块，线性流水线执行。

### 目录结构

```
tg-ai-daily/
├── main.py                       # CLI 入口
├── config/
│   └── channels.yaml             # 频道配置列表
├── src/
│   ├── __init__.py
│   ├── fetcher.py                # Telethon — 拉取 24h 消息
│   ├── dedup.py                  # 消息 ID + 内容哈希去重
│   ├── filter.py                 # 广告/推广过滤
│   ├── summarizer.py             # OpenAI 中文日报摘要
│   └── storage.py                # JSON / Markdown 读写
├── data/
│   ├── raw/                      # tg_raw_YYYY-MM-DD.json（gitignore）
│   └── summaries/                # tg_summary_YYYY-MM-DD.md
├── tests/
│   ├── test_dedup.py
│   ├── test_filter.py
│   ├── test_storage.py
│   └── test_summarizer.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### 模块职责

| 模块 | 输入 | 输出 | 职责 |
|---|---|---|---|
| `main.py` | CLI 参数 | — | 编排全流程 |
| `fetcher.py` | `channels.yaml` | `List[dict]` 消息列表 | 连接 Telegram，遍历频道拉取最近 24h 消息 |
| `dedup.py` | `List[dict]` | `List[dict]` | 先按消息 ID 去重，再按内容 MD5 哈希去重 |
| `filter.py` | `List[dict]` | `List[dict]` | 过滤含推广链接和营销话术的消息 |
| `summarizer.py` | `List[dict]` | `str`（Markdown） | 调用 OpenAI，按主题分类生成中文日报 |
| `storage.py` | 数据 + 路径 | — | 保存原始 JSON 和摘要 MD，按日期命名 |

## 数据流

```
channels.yaml → fetcher → dedup → filter → storage(raw JSON)
                                                  ↓
                                          summarizer → storage(summary MD)
```

线性、顺序、单线程执行，每一步的输出作为下一步的输入。

### `config/channels.yaml` 结构

```yaml
channels:
  - username: "@ai_news_cn"
    label: "AI 新闻"
  - username: "https://t.me/crypto_insider"
    label: "加密内参"
```

字段说明：
- `username`（必填）：Telegram 频道用户名或 URL
- `label`（必填）：中文标签，用于摘要中展示

### 内部消息数据结构

```python
{
    "msg_id": 12345,              # Telegram 原始消息 ID
    "channel": "@ai_news_cn",     # 来源频道
    "label": "AI 新闻",           # 配置文件中的中文标签
    "date": "2026-06-08T14:30:00",
    "text": "GPT-5 今日发布...",
    "link": "https://t.me/ai_news_cn/12345",  # 原文永久链接
    "content_hash": "a1b2c3..."               # 内容 MD5，用于去重
}
```

## 关键决策

### 分类方式
消息按**主题/领域**分类（如：AI 技术、行业新闻、工具推荐、观点讨论），不按频道来源分类。

### 去重策略
1. 先按 Telegram `msg_id` 在单个频道内去重
2. 再按 `content_hash`（消息文本 MD5）跨频道去重，过滤掉不同频道转发的相同内容

### 广告/推广过滤
满足以下**任一**条件的消息会被过滤：
- 包含推广链接（常见短链接域名、affiliate 模式）
- 包含营销关键词（如"限时优惠""立即购买""扫码加入"）

被过滤的消息同时从原始数据存储和摘要中排除。

### 配置字段
`channels.yaml` 中每个频道只需 `username` 和 `label` 两个字段。优先级通过 YAML 中的排列顺序隐式表达。临时关闭某频道只需注释掉对应行。

### 摘要格式（标准版）
```markdown
# TG 日报 — 2026-06-08

## AI 技术
该分类下关键消息的 2-3 句综述段落。
- 某条消息要点。来源：[AI 新闻](https://t.me/...)

## 行业新闻
...
```

每个分类板块包含：
- 分类标题
- 2-3 句综述段落
- 逐条消息要点及原文链接

## 错误处理

| 场景 | 处理方式 |
|---|---|
| 网络超时 / Telegram 不可达 | 重试 3 次，指数退避（2s/4s/8s），最终失败则跳过该频道，继续处理其余 |
| 频道不存在或无权限 | 打印 `[WARN] 频道 @xxx 无法访问，已跳过`，继续 |
| OpenAI API 调用失败 | 重试 2 次，最终失败则报错退出，已保存的 raw JSON 保留不丢 |
| `channels.yaml` 格式错误 | 启动时校验，格式不对直接报错并提示 |
| `channels.yaml` 不存在 | 报错：`请复制 config/channels.example.yaml 为 channels.yaml 并填写频道` |
| 某频道最近 24h 无新消息 | 静默跳过 |

## 测试策略

个人工具，非公共库。测试集中在纯数据转换模块：

- `dedup.py`：用已知的消息 ID 冲突和哈希重复数据做单元测试
- `filter.py`：用广告/非广告消息样本做单元测试
- `storage.py`：测试 JSON/MD 读写和按日期命名的逻辑
- `summarizer.py`：通过 mock OpenAI client 测试 prompt 构建和响应解析
- `fetcher.py`：仅手动验证（需要真实 Telegram 凭证）

测试文件放在 `tests/` 目录下，使用 `pytest`。

## 环境与配置

### `.env`（gitignore，不提交）
```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，用于代理
OPENAI_MODEL=gpt-4o-mini
TG_API_ID=12345678
TG_API_HASH=abcdef...
```

### `.env.example`（提交到 git，含占位值）

### `.gitignore`
```
.env
*.session
data/raw/
__pycache__/
```

### 运行命令
```bash
# 安装依赖
pip install -r requirements.txt

# 首次运行 — 会提示 Telegram 登录（生成 session 文件）
python main.py

# 日常运行
python main.py
```

默认使用 `gpt-4o-mini`（便宜、快速、摘要够用）。可通过 `.env` 切换模型。
