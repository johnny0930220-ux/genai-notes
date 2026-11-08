# 生成式 AI 課程筆記

TAICA「生成式 AI：文字與圖像生成的原理與實務」的每週筆記網站。

- 網站：https://johnny0930220-ux.github.io/genai-notes/
- 給 AI 的規則：[AGENTS.md](AGENTS.md)

## 怎麼新增一週

1. 複製 `templates/week-template.md` 到 `content/weeks/`，改名成 `wNN-英文短名.md`。
2. 依 AGENTS.md 第 4 節的格式填寫。
3. 執行 `python3 build.py`，看到「✓ 已產生網站」就完成。
4. 把變更上傳到 GitHub，1～2 分鐘後網站會更新。

或者直接請 AI：「請讀 AGENTS.md，然後依附件投影片新增第 N 週筆記。」

## 檔案結構

- `content/`：筆記原稿（Markdown），要改內容就改這裡
- `templates/`：網頁外框和筆記範本
- `assets/`：樣式、互動功能
- `build.py`：檢查格式並產生網站，只用 Python 標準庫
- `index.html`、`keywords.html`、`about.html`、`notes/`：自動產生的網頁，不要手動改
