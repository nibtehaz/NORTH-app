const express = require('express');
const { dialog } = require('electron');
const app = express();
const port = 3000;
const { shell } = require('electron');
const path = require('path');
const fs = require('fs');

app.all('/filed', function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "X-Requested-With");
    next();
});


app.get('/filed', (req, res) => {
    const pathArray = dialog.showOpenDialog({ properties: ['openDirectory'] });

    res.send(pathArray);
});

app.all('/readjson', function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "X-Requested-With");
    next();
});


app.get('/readjson', (req, res) => {
    const pth = path.join(__dirname, 'tempdata', req.query.filepath);

    try {
        var jsonData = fs.readFileSync(pth, "utf8");
        jsonData = jsonData.replace(/\'/g, '"');
        var data = JSON.parse(jsonData);
        fs.unlinkSync(pth);
        res.send(data);
    }

    catch (err) {
        console.log(err);

        res.send({ "error": "error" });
    }

});

app.all('/gochrome', function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "X-Requested-With");
    next();
});


app.get('/gochrome', (req, res) => {


    shell.openExternal(req.query.siteurl, (d, e) => { res.send("done"); });

});


app.listen(port, () => console.log(`Started App`));

module.exports.server = 'True';