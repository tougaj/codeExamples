// 📦 Імпорт бібліотек
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

// 🔧 Отримуємо __dirname в ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 🚀 Створюємо застосунок
const app = express();
const PORT = 3000;

// 📂 Папка для статичних файлів
app.use(express.static(path.join(__dirname, 'public')));

// 🌐 Маршрут для головної сторінки
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ▶️ Запуск сервера
app.listen(PORT, () => {
  console.log(`✅ Сервер запущено: http://localhost:${PORT}`);
});
