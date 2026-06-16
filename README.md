# tg-ai-daily

Telegram 频道日报生成工具 — 拉取配置的频道过去 24 小时消息，通过 OpenAI 生成按主题分类的中文日报。

## 功能

- 📡 通过 Telethon 拉取 Telegram 频道消息
- 🔄 按消息 ID + 内容哈希双重去重
- 🚫 自动过滤广告和推广内容
- 🤖 调用 OpenAI API 生成中文日报摘要
- 📂 原始消息 JSON + 日报 Markdown 按日期存储

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env，填入你的 TG_API_ID, TG_API_HASH, OPENAI_API_KEY
```

### 3. 配置频道
编辑 `config/channels.yaml`，添加要监控的频道。

示例：
```yaml
channels:
  - username: "@ai_news_cn"
    label: "AI 新闻"
  - username: "https://t.me/tech_daily"
    label: "科技日报"
```

### 4. 运行
```bash
python main.py              # 拉取最近 24h
python main.py --hours 48   # 拉取最近 48h
```

首次运行会提示登录 Telegram（需要手机号验证码），之后会缓存 session 无需重复登录。

## 目录结构

```
tg-ai-daily/
├── main.py                 # CLI 入口
├── config/channels.yaml    # 频道配置
├── src/                    # 源代码
│   ├── fetcher.py          # 消息拉取
│   ├── dedup.py            # 去重
│   ├── filter.py           # 广告过滤
│   ├── summarizer.py       # OpenAI 摘要
│   └── storage.py          # 读写存储
├── data/raw/               # 原始消息 JSON
├── data/summaries/         # 日报 Markdown
└── tests/                  # 单元测试
```

## 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `TG_API_ID` | ✅ | Telegram API ID（my.telegram.org） |
| `TG_API_HASH` | ✅ | Telegram API Hash |
| `OPENAI_API_KEY` | ✅ | OpenAI API Key |
| `OPENAI_BASE_URL` | ❌ | API 代理地址（默认官方） |
| `OPENAI_MODEL` | ❌ | 模型名（默认 gpt-4o-mini） |

## License

MIT
