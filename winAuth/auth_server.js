// server.mjs
import express from "express";
import passport from "passport";
import WindowsStrategy from "passport-windowsauth";
import session from "express-session";
import { getUser } from "node-expose-sspi";
import ntlm from "express-ntlm";

// 🔧 Обери метод автентифікації: "passport", "sspi" або "ntlm"
const AUTH_METHOD = "passport";

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
        saveUninitialized: true
    }));
    app.use(passport.initialize());
    app.use(passport.session());

    app.get("/login", passport.authenticate("WindowsAuthentication"), (req, res) => {
        res.send(`🔐 Passport-WindowsAuth: Привіт, ${req.user.displayName}`);
    });

} else if (AUTH_METHOD === "sspi") {
    // node-expose-sspi
    app.get("/login", (req, res) => {
        const user = getUser(req);
        res.send(`🪟 SSPI: Ви увійшли як ${user.name}`);
    });

} else if (AUTH_METHOD === "ntlm") {
    // express-ntlm
    app.use(ntlm({
        domain: "MYDOMAIN"
    }));

    app.get("/login", (req, res) => {
        res.send(`🔑 NTLM: Ви увійшли як ${req.ntlm.UserName}`);
    });
} else {
    app.get("/login", (_, res) => res.status(500).send("❌ Невідомий метод автентифікації"));
}

app.listen(3000, () => {
    console.log(`Сервер запущено. Метод автентифікації: ${AUTH_METHOD}`);
});

// npm install express passport passport-windowsauth express-session node-expose-sspi express-ntlm
