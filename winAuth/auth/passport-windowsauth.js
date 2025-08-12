import express from "express";
import passport from "passport";
import WindowsStrategy from "passport-windowsauth";
import session from "express-session";

const app = express();

// Налаштування стратегії Windows Authentication
passport.use(new WindowsStrategy(
    { integrated: true }, // Дозволяє SSO
    (profile, done) => done(null, profile)
));

app.use(session({
    secret: "secret",
    resave: false,
    saveUninitialized: true
}));
app.use(passport.initialize());
app.use(passport.session());

// Маршрут для автентифікації
app.get("/login", passport.authenticate("WindowsAuthentication"), (req, res) => {
    res.send(`Привіт, ${req.user.displayName}`);
});

app.listen(3000, () => console.log("Сервер запущено"));

// npm install -P passport-windowsauth passport express-session