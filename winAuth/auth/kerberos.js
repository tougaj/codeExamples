import express from "express";
import { getUser } from "node-expose-sspi";

const app = express();

app.get("/login", (req, res) => {
    const user = getUser(req);
    res.send(`Ви увійшли як: ${user.name}`);
});

app.listen(3000, () => console.log("Сервер запущено"));

// npm install -P node-expose-sspi express
