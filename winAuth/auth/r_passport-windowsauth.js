const express = require("express");
const passport = require("passport");
const WindowsStrategy = require("passport-windowsauth");

const app = express();

// Налаштування стратегії Windows Authentication
passport.use(new WindowsStrategy({
    integrated: true // Дозволяє SSO
}, (profile, done) => {
    return done(null, profile);
}));

app.use(require("express-session")({ secret: "secret", resave: false, saveUninitialized: true }));
app.use(passport.initialize());
app.use(passport.session());

// Маршрут для автентифікації
app.get('/login', passport.authenticate('WindowsAuthentication'), (req, res) => {
    res.send(`Привіт, ${req.user.displayName}`);
});

app.listen(3000, () => console.log("Сервер запущено"));

// npm install passport-windowsauth passport express-session