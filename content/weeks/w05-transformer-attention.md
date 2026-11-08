---
week: 5
title: AI 怎麼記得前面說過什麼？
slides: 05 AI 怎麼記得前面說過什麼？
summary: 拆解 RNN 和 Transformer 的記憶方式：QKV 注意力、位置編碼和讓網路更穩的設計。
keywords: [RNN, transformer, self-attention, position encoding, layer normalization, Vibe Coding]
related: [w04, w07]
---

## 課堂重點

> Transformer 的注意力機制，說穿了就是矩陣乘一乘，再加一個 softmax。

### RNN 神經元其實很普通

RNN 層和全連結層很像，差別是**上一次的輸出 $h_{t-1}$ 會再傳回來**，和這次的輸入 $x_t$ 一起決定輸出。拆開來看，RNN 神經元就是一般的神經元，只是多了一組處理「記憶」的權重。（p.3–8）

### 線性代數 101

矩陣的規則是「先列後行」，矩陣乘法 $C=AB$ 的 $c_{ij}$ 是 A 第 i 列和 B 第 j 行的內積。（p.10–12）

最重要的技巧：向量 $x$ 乘上矩陣 $A$，結果是用 $x$ 的分量對 $A$ 的列向量做線性組合。Google 特別喜歡列向量，所以 Transformer 論文裡的矩陣都乘在後面。（p.13–14）

### QKV 注意力機制

2017 年 Google 發表〈Attention is All you Need〉，原本想取代 RNN，標題也看得出野心。（p.16）

概念是：有一段資訊 $x_1, \dots, x_T$，現在進來一個問題 $q$，要從資訊裡組出最適合的代表向量 $h$。每個 $x_t$ 有自己的 key $k_t$ 和 value $v_t$：（p.17–26）

1. 用 $q$ 和每個 $k_t$ 做內積，得到注意力強度 $e_t$。
2. 經過 softmax 得到權重 $\alpha_t$。
3. $h = \alpha_1 v_1 + \alpha_2 v_2 + \cdots + \alpha_T v_T$。

**Self-attention** 就是每個字輪流當 $q$。Q、K、V 都是輸入 $X$ 乘上學來的矩陣，可以一次算完：$Q = XW^Q$、$K = XW^K$、$V = XW^V$。（p.27–35）

### 為什麼要除以 $\sqrt{d_k}$

softmax 是「贏者通吃」，分數差一點，機率就差很多，權重會被放大得不合理。解法是把所有分數除以一個夠大的數，拉回 0 附近。原論文寫 $\sqrt{d_k}$，老師說其實放一個適當的數就可以，也能當成超參數調。（p.31–33）

注意力也不只一種，可以同時用好幾組 $W^Q, W^K, W^V$，這就是 multi-head attention。Decoder 的輸入還沒生成的部分會被 mask 住。（p.36–40）

### Position encoding：補上順序

RNN 是真的一個字一個字讀，Transformer 為了平行計算一次做完，所以**不知道字的先後順序**。解法是在每個字的 embedding 加上位置向量。（p.42）

老師用進位系統來解釋：十進位的個位數變化最快，越高位變化越慢。原論文用 sin 和 cos 做出一個「連續、有週期、數值不大」的奇幻進位系統，低位數頻率快、高位數頻率慢。sin 和 cos 一組，剛好是單位圓上的一點，可以想成快慢不同的時鐘。（p.43–50）

### 讓 Transformer 更穩

Transformer 用了兩個讓深層網路更穩定的技術（p.52–65）：

- **Residual 連結**（ResNet 的設計）：輸出從 $\ell(z)$ 變成 $z + \ell(z)$，每層只需要學「還沒學到的部分」，loss 曲面也更平順。
- **Normalization**：原版用 layer normalization，Llama 等新模型改用 RMSNorm，Meta 最近還提出用 Dynamic Tanh 取代 normalization。

Transformer 不只處理文字，圖像、聲音、時間序列都可以。文字生圖時，也是用注意力機制把文字的意思「混入」生成過程。（p.66–67）

## 重要名詞

- **RNN**：遞歸神經網路，每一步都帶著上一步的輸出當記憶。
- **Q、K、V**：query、key、value，分別代表「問題」「索引」「內容」的特徵向量。
- **self-attention**：每個字都當一次 query，從整段文字組出自己的新表示。
- **multi-head attention**：同時用好幾組注意力，各自關注不同的關係。
- **position encoding**：加在 embedding 上的位置資訊，讓 Transformer 知道字的順序。
- **residual 連結**：把輸入直接加到輸出，讓網路可以疊得很深。
- **layer normalization**：把一層的輸出調整成平均 0、標準差 1，再乘上學來的參數。

## 本週作業

和 AI 討論出 Vibe Coding 程式規格書，做一個互動網頁（p.69–85）：

1. 先和 AI 討論，產生這個 App 的「規格書」。可以跟 AI 說「先不要寫程式，問我一些問題，幫我把需求釐清」。
2. 用規格書產生一個 `index.html`，圖片放在 `assets` 資料夾。
3. 上傳到 GitHub，用 GitHub Pages 讓全世界看到，網址是 `https://帳號.github.io/repo名稱/`。

## 和其他週的關係

本週把 [W04 LLM 只是在猜下一個字？](w04-next-token.md) 裡帶過的 Transformer 完整拆開。KV 的概念在 [W07 讓 AI 看懂你的世界](w07-rag-and-llm-wiki.md) 的 KV-Cache 會再出現；這週的 GitHub Pages 流程，也是這個筆記網站的發布方式。

## 延伸思考

- 位置編碼為什麼用「加」的，而不是接在 embedding 後面？
- 文字生圖時，Q 來自圖、K 和 V 來自文字，反過來可以嗎？
