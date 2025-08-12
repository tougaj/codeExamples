import express from "express";
import ntlm from "express-ntlm";

const app = express();

app.use(ntlm({
    domain: "MYDOMAIN"
}));

app.get("/", (req, res) => {
    res.send(`Ви увійшли як: ${req.ntlm.UserName}`);
});

app.listen(3000, () => console.log("Сервер запущено"));

// npm -P install express-ntlm
