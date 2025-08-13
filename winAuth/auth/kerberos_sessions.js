import session from "express-session";
import express from "express";
import { sso } from "node-expose-sspi";
import path from 'path';
import { fileURLToPath } from 'url';

// 🔧 Отримуємо __dirname в ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

app.use(session({
    name: 'cra_session',
    secret: "secret",
    resave: false,
    saveUninitialized: false,
    cookie: {maxAge: 20000}
}));

app.use('/api/{*splat}', sso.auth({useSession: true}));

// app.get("/login", (req, res) => {
//     const user = getUser(req);
//     res.send(`Ви увійшли як: ${user.name}`);
// });

// 📂 Папка для статичних файлів
// app.use(express.static(path.join(__dirname, 'public')));

// 🌐 Маршрут для головної сторінки
app.get('/{*splat}', (req, res) => {
    // if (!req.sso || !req.sso.user){
    //     return(res.status(401).send('asffdsfsdsdgsdg'))
    // }
    console.log(req.sso?.user?.domain+'\\'+req.sso?.user?.name);
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(3000, () => console.log("Сервер запущено"));

// npm install -P node-expose-sspi express
