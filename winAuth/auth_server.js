// server.mjs
import express from "express";
import passport from "passport";
import WindowsStrategy from "passport-windowsauth";
import session from "express-session";
// import sspi from 'node-expose-sspi';
import { sso } from "node-expose-sspi";
import ntlm from "express-ntlm";
// const { sso } = sspi;
import path from 'path';
import { fileURLToPath } from 'url';

// 🔧 Отримуємо __dirname в ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 🔧 Обери метод автентифікації: "passport", "sspi" або "ntlm"
const AUTH_METHOD = "sspi";

const app = express();

if (AUTH_METHOD === "passport") {
    // Passport Windows Authentication
    passport.use(new WindowsStrategy(
        { integrated: true },
        (profile, done) => done(null, profile)
    ));

    app.use(session({
        secret: "secret",
        resave: false,
        saveUninitialized: false
    }));
    app.use(passport.initialize());
    app.use(passport.session());

    app.get("/", passport.authenticate("WindowsAuthentication"), (req, res) => {
        // res.send(`🔐 Passport-WindowsAuth: Привіт, ${req.user.displayName}`);
        res.send(`🔐 Passport-WindowsAuth: Привіт, ${req.user}`);
    });

} else if (AUTH_METHOD === "sspi") {
    // node-expose-sspi
    app.use(sso.auth());
    // app.all('/api/{*splat}', sso.auth());
    // app.all('/{*splat}', sso.auth(), (req, res, next) =>{
    //     if (!req.sso || !req.sso.user){
    //         return(res.status(401).send('asffdsfsdsdgsdg'))
    //     }
    //     next();
    // });

    // app.get("/login", (req, res) => {
    // app.all("/{*splat}", (req, res, next) => {
    // app.use((req, res, next) => {
    //     if (!req.sso || !req.sso.user){
    //         return(res.status(401).send('asffdsfsdsdgsdg'))
    //     }
    //     console.log(req.sso.user.domain+'\\'+req.sso.user.name);
    //     next();
    //     // res.json({sso: req.sso});
    //     // const user = getUser(req);
    //     // res.send(`🪟 SSPI: Ви увійшли як ${user.name}`);
    // });

} else if (AUTH_METHOD === "ntlm") {
    // express-ntlm
    app.use(ntlm({
        domain: "ztm"
    }));

    app.all("/{*splat}", (req, res) => {
        console.log(req.ntlm)
        res.send(`🔑 NTLM: Ви увійшли як ${req.ntlm}`);
    });
} else {
    app.get("/login", (_, res) => res.status(500).send("❌ Невідомий метод автентифікації"));
}

// 📂 Папка для статичних файлів
app.use(express.static(path.join(__dirname, 'public')));

// 🌐 Маршрут для головної сторінки
app.get('/', (req, res) => {
    if (!req.sso || !req.sso.user){
        return(res.status(401).send('asffdsfsdsdgsdg'))
    }
    console.log(req.sso.user.domain+'\\'+req.sso.user.name);
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(3000, () => {
    console.log(`Сервер запущено. Метод автентифікації: ${AUTH_METHOD}`);
});

// npm install express passport passport-windowsauth express-session node-expose-sspi express-ntlm
