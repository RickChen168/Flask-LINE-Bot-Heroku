# Flask-LINE-Bot-Heroku

### 一. 自動部署 Heroku
首先我們先做一個最簡單的 Echo Bot (也就是你跟他說什麼，他都會回覆一模一樣的話給你) 點擊下面紫色的 Deploy to Heroku 按鈕

<a href="https://heroku.com/deploy?template=https://github.com/hsuanchi/Flask-LINE-Bot-Heroku/tree/main">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy">
</a>

點擊 Deploy to Heroku 按鈕後：

1. 會進入 Heroku 頁面
2. 輸入專案名稱，這邊將會成為未來網址的一部分像是 https://xxxxxxx.herokuapp.com/
3. 輸入在 LINE Developers 取得的 Access Token 和 CHANNEL_SECRET

<img src="https://github.com/hsuanchi/Flask-LINE-Bot-Heroku/blob/main/img/step1%20LINE-bot%20deploy_to_heroku.png" width="800px" height="auto">

然後等待 Heroku 建立部署，完成後會出現以下畫面，綠色勾勾就代表部署成功囉！

<img src="https://github.com/hsuanchi/Flask-LINE-Bot-Heroku/blob/main/img/step2%20LINE-bot%20deploy_to_heroku_success.png" width="800px" height="auto">

### 二. 更新 LINE webhook
將剛剛部署完後的 heroku 網址填入 LINE Developers 的 Webhook URL，就完成設定囉！

<img src="https://github.com/hsuanchi/Flask-LINE-Bot-Heroku/blob/main/img/step3%20LINE-bot%20depoly%20webhook%20settings.png" width="800px" height="auto">

### 三. 測試 LINE Bot 機器人
這時候我們密機器人，如果出現 echo 的狀態，就代表部署成功囉！

<img src="https://github.com/hsuanchi/Flask-LINE-Bot-Heroku/blob/main/img/step4%20LINE-bot%209527%20demo.png" width="200px" height="auto">

### 四. 如何客制成自己的 LINE-Bot
首先將這份 LINE-Bot template Fork 回自己的 GitHub 專案
1. 修改 Flask-LINE-Bot-Heroku/app.py/ 內的程式碼
2. 修改 README.md 內的路徑 (如下圖)，改成自己的專案位置
3. 點擊 Deploy to Heroku 按鈕完成部署

<img src="https://github.com/hsuanchi/Flask-LINE-Bot-Heroku/blob/main/img/custom%20readme-flask-line-bot.png" width="800px" height="auto">

本篇文章同步刊登於 [ [Flask – LINE Bot 教學] Heroku 一鍵自動部署 - Max行銷誌](https://www.maxlist.xyz/2020/11/30/flask-line-bot-deploy-heroku/)，如果有遇到任何問題，歡迎私訊或留言，我會盡快回覆您

### 五. 業務資訊上傳與追蹤功能

這個專案除了 Echo Bot，也內建了「業務上傳資訊、管理者用指令查詢追蹤」的功能，資料存放於 Google 試算表。

#### 5.1 建立 Google 試算表 + 服務帳戶

1. 開一個新的 Google 試算表，記下網址中的 ID（`https://docs.google.com/spreadsheets/d/<這一段就是ID>/edit`）。
2. 到 [Google Cloud Console](https://console.cloud.google.com/) 建立專案，啟用 **Google Sheets API**。
3. 建立一個「服務帳戶 (Service Account)」，下載 JSON 金鑰。
4. 把試算表「共用」給 JSON 金鑰裡的 `client_email`（給編輯權限）。
5. 把整份 JSON 金鑰內容（壓成一行）設定到 Heroku 環境變數 `GOOGLE_SERVICE_ACCOUNT_JSON`，試算表 ID 設定到 `GOOGLE_SHEET_ID`。

程式第一次寫入時會自動在試算表建立「業務紀錄」分頁與標題列，不需要手動建立欄位。

#### 5.2 建立 LIFF 上傳表單

1. 到 [LINE Developers Console](https://developers.line.biz/console/)，在你的 Messaging API Channel 底下新增一個 **LIFF App**。
2. Endpoint URL 填入 `https://你的heroku網址/liff/upload`，Scope 勾選 `profile`。
3. 建立完成後複製 **LIFF ID**，設定到 Heroku 環境變數 `LIFF_ID`。
4. （建議）把 Channel 的 **Channel ID**（在 Basic settings 頁面）設定到 `LINE_CHANNEL_ID`，程式會用它驗證上傳者身份，避免被冒用。

#### 5.3 登記業務人員與管理者身份

1. 讓業務先把官方帳號加為好友，並傳一則訊息給機器人；機器人會回覆他的 **LINE User ID**。
2. 把每位業務的 User ID 整理成 JSON，設定到 `SALES_USERS`，例如：
   ```json
   {"U1234...": "王小明", "U5678...": "陳小華"}
   ```
3. 把你（管理者）自己的 LINE User ID 設定到 `MANAGER_USER_IDS`（多人用逗號分隔），這是用來判斷誰可以用文字指令查詢資料。

#### 5.4 設定新紀錄的 Email 通知

業務每上傳一筆新紀錄，系統會寄一封 Email 通知管理者（不透過 LINE 推播）。設定以下 Heroku 環境變數：

- `SMTP_HOST`：SMTP 伺服器位址（例如用 Gmail 就是 `smtp.gmail.com`）
- `SMTP_PORT`：通常是 `587`（不設定則預設 587）
- `SMTP_USERNAME` / `SMTP_PASSWORD`：SMTP 登入帳密（Gmail 需要用「應用程式密碼」，不是登入密碼）
- `FROM_EMAIL`：寄件者信箱（不設定則預設用 `SMTP_USERNAME`）
- `MANAGER_EMAIL`：收件者信箱，多人用逗號分隔

若沒有設定 `SMTP_HOST` / `MANAGER_EMAIL`，機器人仍可正常運作，只是不會寄出通知信。

#### 5.5 使用方式

- **業務**：傳任意訊息給機器人，會收到「開啟上傳表單」按鈕，點擊後填寫客戶名稱、聯絡方式、商機金額、狀態、備註並送出；管理者會收到 Email 通知。
- **管理者**：直接傳文字指令給機器人查詢：
  - `說明`：列出所有指令
  - `最新`：查看最新 5 筆紀錄
  - `本週`：本週紀錄數與商機金額加總
  - `查詢 關鍵字`：依客戶名稱或業務姓名搜尋

若尚未設定 `GOOGLE_SERVICE_ACCOUNT_JSON` / `GOOGLE_SHEET_ID` / `LIFF_ID`，機器人仍可運作，但上傳與查詢功能會回覆尚未設定完成的提示。
