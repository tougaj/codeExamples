const express = require("express");
const { getUser } = require("node-expose-sspi");

const app = express();

app.get("/login", (req, res) => {
    const user = getUser(req);
    res.send(`Ви увійшли як: ${user.name}`);
});

app.listen(3000, () => console.log("Сервер запущено"));

// npm install node-expose-sspi express
