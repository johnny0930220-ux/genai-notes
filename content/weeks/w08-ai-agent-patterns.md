---
week: 8
title: 教 AI 做事的方法
slides: 08 教 AI 做事的方法
summary: AI Agent 就是教 AI 用我們做事的方法，吳恩達整理出四種設計模式。
keywords: [AI Agent, Reflection, Tool Use, Planning, Multiagent Collaboration, MCP, Vibe Coding, RAG]
related: [w01, w07, w09]
---

## 課堂重點

> AI Agent = AI Model + Harness。在 LLM 時代，就是教 AI 用「我們做事的方法」做事情。

### AI Agent 到底是什麼

經典教科書的定義是：能透過感測器感知環境、透過致動器對環境採取行動的實體。課堂的定義更白話：教 AI 用我們做事的方法做事。（p.3–5）

以前是下一個 prompt、LLM 一路寫到底，就像要人寫文章卻不能刪除、不能修改。人做事會邊寫邊試邊改，也會查規定、上網搜尋、按計算機。AI Agent 就是把這些本來你要做的事，交給 AI 自動完成。（p.8–13）

RAG 其實也是一種 AI Agent，因為是電腦自己去找相關資訊。（p.14）

### 吳恩達的四種設計模式

1. **Reflection**：第一個 LLM 寫初稿，第二個 LLM 當評論員給建議，第一個再修改，可以重複好幾輪。評論員也可以換成不同的模型。（p.19–21）
2. **Tool Use**：精確計算、實際資料、網路搜尋這些 LLM 不擅長的事，就叫工具來做。（p.22–23）
3. **Planning**：先請 LLM 想一想、打草稿，再正式回應。CoT（思維鏈）是有名的方法，DeepSeek-R1 會先在 `<think>` 標籤裡產生思考。（p.32–35）
4. **Multiagent Collaboration**：多個 Agent 一起工作，常常有一個像 PM 的 LLM 負責拆解任務、分配工作。（p.37–38）

### Tool Use 的實際流程

以飲料店機器人為例，使用者說「我想訂 20 杯麥茶」（p.24–29）：

1. 先告訴 LLM 有哪些工具，例如 `get_menu` 回傳菜單，`quote_order` 輸入品項和杯數、回傳單價和總金額。
2. LLM 判斷要呼叫 `quote_order("麥茶", 20)`。
3. 程式真的執行函式，回傳 JSON 格式的結果，例如單價 30、總金額 600。
4. 再請 LLM 根據 JSON 回答：「沒問題！20 杯麥茶一共 600 元。」

所以 LLM 參與了兩個階段：決定呼叫什麼工具，以及根據結果回答。工具也可以分享出去：Anthropic 的 **MCP** 規範單一 Agent 怎麼使用外部工具；Google 的 **A2A** 規範 Agent 之間怎麼溝通。（p.26、p.30–31）

### Vibe Coding 是什麼

這個詞是 Karpathy 在 2025 年 2 月創的。原文的重點是：忘了程式碼的存在、不檢查 AI 改了什麼、有錯就把錯誤訊息貼回去、完全不看也不改程式。（p.43–46）

所以 Vibe Coding **不等於** AI 輔助寫程式。它適合週末小專案、給自己用的小工具、和工程師討論用的原型；不適合要正式上線，或不檢查就可能出亂子的程式。（p.47–51）

### 進階觀點

Karpathy 在訪談中認為 AGI 還要十年，現在的 AI 還不像真正的人類實習生。投影片也整理了 LLM 訓練的三個階段：預訓練、後訓練和微調。Hinton 則認為 AI 已經用和人類相同的方式理解世界，將來會比我們聰明。（p.40–42、p.53–55）

## 重要名詞

- **Harness**：讓模型能真正動手做事的配備，例如工具、規則檔和工作環境。
- **Reflection**：讓 LLM 自我檢討、反覆修改的設計模式。
- **Tool Use**：讓 LLM 呼叫外部函式或服務的設計模式。
- **Planning**：先規劃步驟再執行的設計模式，CoT 是代表做法。
- **MCP**：Model Context Protocol，Anthropic 提出的 LLM 連接外部工具的標準。
- **A2A**：Agent-to-Agent，Google 提出的 Agent 之間溝通的協定。
- **JSON**：用文字描述「有欄位名稱的資料」的格式，電腦很喜歡。

## 本週作業

投影片沒有出作業。三個設計模式各有範例程式：Reflection 是 `yenlung.me/AI07a`、Tool Use 是 `yenlung.me/AI07b`、Planning 是 `yenlung.me/AI07c`。（p.19、p.22、p.32）

## 和其他週的關係

[W01 如何不焦慮地學 AI](w01-learn-ai-without-anxiety.md) 的課程地圖預告過 AI Agent，本週正式登場。[W07 讓 AI 看懂你的世界](w07-rag-and-llm-wiki.md) 的 RAG 在本週被重新定義成一種 AI Agent。本週是用 AISuite 自己手刻 Agent，下一週 [W09 換你當老闆](w09-agentic-work.md) 會改用現成的 Agent 產品。

## 延伸思考

- Reflection 的評論員如果和作者是同一個模型，會不會只是自己說服自己？
- 什麼樣的任務值得拆成多個 Agent，什麼樣的任務一個就夠？
