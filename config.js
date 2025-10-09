// 配置前端 API 基底位址（統一指向 Render 後端）。
// 本機以 8000 埠預覽時，若未設定此值，前端會回退到 http://localhost:3000；
// 為避免連線被拒絕（本機未啟動後端），改為固定使用雲端 Render 服務。
window.API_BASE = 'https://homeletter2-0-backend.onrender.com';