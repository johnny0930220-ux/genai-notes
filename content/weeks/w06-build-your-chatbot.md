---
week: 6
title: 打造自己的對話機器人
slides: 06 打造自己的對話機器人
summary: 用 system prompt 給 LLM 人設，再用 AISuite 寫程式，打造自己的對話機器人。
keywords: [system prompt, Prompt Engineering, AISuite, Groq, 幻覺, 負責任使用 AI]
related: [w04, w07]
---

## 課堂重點

> 最重要的 AI 使用技巧：一定要讀它寫了什麼。

### 在自己電腦跑模型

LM Studio 和 Ollama 都能在自己電腦上跑開源模型。挑機器時要看 GPU 的 VRAM；Mac 用 unified memory，記憶體多大，基本上就有多少 VRAM 可用。以 4-bit 量化的 200 億參數模型來說，模型本身約 10GB，再加 1～2GB 比較保險。（p.3–10）

另外兩點：記憶體頻寬會影響生成速度；同樣大小的模型，MoE 架構跑得比較快。不想自己跑的話，Groq 有免費 API，Ollama Cloud 可以跑超大型開源模型。（p.11–13）

### 負責任使用 AI

Karpathy 認為幻覺是 LLM 最偉大的特點。老師補充，某種程度上人的幻覺更嚴重：AI 會的，我們就以為自己也會了。（p.15–17）

使用者要負的責任包括：內容有沒有侵權、文獻對不對、品質符不符合需求。資安也要注意：就算對話不拿去訓練，存在雲端的原始對話仍可能因為帳號被盜或系統漏洞外洩，所以個資和機密不要拿去問。完全在本機執行，就能避開這一層風險。（p.22–24）

關於中國的模型，老師認為審查不一定是最大的問題，反而是訓練資料中簡體中文比例可能更高，長期使用會在不知不覺中影響想法和價值觀。另外有研究指出，加上「思考」的模型在劫持思維鏈（H-CoT）攻擊下，拒絕回答犯罪問題的比例會大幅下降。（p.27–30）

> AI 生成的都是「幻覺」。沒有寫錯，不代表寫對了我們的意思。要先讀懂，才能教 AI 用你的方法做事。

### System prompt：給 LLM 一個人設

對話中有三個角色：`system`、`user`、`assistant`。`system` 就是 LLM 的人設，使用者通常看不到。（p.36–37）

老師最有名的例子是「員瑛式思考」機器人：不管使用者遇到什麼事，都用第一人稱、社群貼文的口吻說明為什麼這超幸運，最後以「完全是 Lucky Vicky 呀！」結尾。（p.39–43）

想做可以一直聊下去的版本，prompt 就會變長，例如分成「人生哲學」和「歷史」兩部分，並規定像朋友聊天、200 字以內、不要條列。做法和 W04 的必殺技一樣：先和 AI 討論、請 AI 收集資料，最後請 AI 用 Markdown 寫成完整的 system prompt。（p.44–48）

收集資料時，AI 給的書名可能不對，要自己查證修正。老師提醒：不要覺得 AI 說的一定對，也不要笑它不知道你知道的事，你們是夥伴。（p.47）

### 更多人設範例

- **小編助理**：幫忙寫社群貼文，寫出來真的很像業配文，內容大致正確，但仍有需要修改的地方。（p.51–57）
- **AI 選系諮商師**：只推薦應用數學系的「業配 AI」。第一版 ChatGPT 會自曝身分，要修改 prompt。（p.58–64）
- **股票分析**：有論文用 ChatGPT 做情緒分析來預測股價，prompt 其實不複雜，但老師也反問：你真的相信這樣的機器人嗎？（p.49–50）

### 用 AISuite 寫程式

AISuite 是吳恩達老師推出的套件，可以用統一的寫法呼叫不同供應商的模型，切換模型只要改一個字串。API 金鑰放在 Colab 的密鑰裡，用 `userdata.get` 讀入。（p.66–74）

```python
import aisuite as ai
client = ai.Client()
messages = [
    {"role": "system", "content": "人設"},
    {"role": "user", "content": "使用者輸入"},
]
response = client.chat.completions.create(model="openai:gpt-4o", messages=messages)
reply = response.choices[0].message.content
```

對話歷史就是一串 `role` 和 `content` 的清單，每次都整串送進去，模型才「記得」前面說過什麼。（p.75–79）

## 重要名詞

- **system prompt**：設定 LLM 人設和規則的指令，在對話中扮演 `system` 角色。
- **AISuite**：用同一套寫法呼叫多家 LLM 的 Python 套件。
- **Groq**：提供 LPU 晶片和免費 API 的 AI 公司，主要加速模型的推論階段。
- **MoE**：混合專家架構，同樣大小的模型跑得比較快。
- **量化**：用較少位元存模型參數，例如 4-bit，可以大幅降低記憶體需求。

## 本週作業

投影片沒有寫出作業題目。課堂實作是用 AISuite 打造有人設的對話機器人，範例程式在 `yenlung.me/AI04`。（p.72）

## 和其他週的關係

本週把 [W04 LLM 只是在猜下一個字？](w04-next-token.md) 的 prompt 必殺技用在 system prompt 上。對話機器人只靠對話歷史記事情，[W07 讓 AI 看懂你的世界](w07-rag-and-llm-wiki.md) 會用 RAG 讓它查得到外部資料。

## 延伸思考

- system prompt 寫得越長越好嗎？什麼情況下會開始互相衝突？
- 對話歷史每次都整串送出，對話很長時要怎麼辦？
