// server.js

const express = require("express");
const app = express();
const PORT = 3000;

// 假資料：stores 商家 & products 餐點
const stores = [
  { id: 1, name: "速食店" },
  { id: 2, name: "日式料理" },
];

const products = [
  { id: 1, name: "炸雞", price: 100, storeId: 1 },
  { id: 2, name: "壽司", price: 200, storeId: 2 },
];

// 搜尋 API
app.get("/api/search", (req, res) => {
  const keyword = req.query.keyword?.toLowerCase() || "";

  const matchedStores = stores.filter((s) =>
    s.name.toLowerCase().includes(keyword)
  );
  const matchedProducts = products.filter((p) =>
    p.name.toLowerCase().includes(keyword)
  );
  if (!isNaN(maxCalories)) {
    matchedProducts = matchedProducts.filter(
      (p) => p.calories <= maxCalories
    );
  }

  res.json({
    stores: matchedStores,
    products: matchedProducts,
  });
});

// 啟動伺服器
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
