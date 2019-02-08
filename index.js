const electron = require('electron');
const { app, BrowserWindow, Menu } = electron;


const path = require('path');
const url = require('url');
const fs = require('fs');

const appName = app.getName();

// Get app directory
// on OSX it's /Users/Yourname/Library/Application Support/AppName
const getAppPath = path.join(app.getPath('appData'), appName);


let mainWindow;

let subpy;
let appUrl = 'http://127.0.0.1:5000/';

app.on('window-all-closed', function () {
  app.quit();
});

app.on('quit', function () {
  subpy.kill('SIGINT');
});

if (fs.existsSync(path.join(__dirname, 'app'))) {
  var executablePath = path.join(__dirname, 'app');

  const { execFile } = require('child_process');
  const child = execFile(executablePath, (error, stdout, stderr) => {
    if (error) {
      throw error;
    }
    console.log(stdout);
  });
}

else {
  subpy = require('child_process').spawn('python3', [path.join(__dirname, 'app.py')]);
}





app.on('ready', function () {


  mainWindow = new BrowserWindow({ width: 1200, height: 700 });
  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'index.html'),
    protocol: 'file:',
    slashes: true
  }));

  var openWindow = function () {


    mainWindow.setMenu(null);
    //mainWindow.webContents.openDevTools();    

    mainWindow.loadURL(appUrl);


    mainWindow.on('closed', function () {
      mainWindow = null;
      subpy.kill('SIGINT');

    });
  };

  var startUp = function () {
    require('request-promise')(appUrl).then(function () {
      openWindow();
    }).catch(function (err) {
      //console.log(err);

      setTimeout(startUp, 500);
    });
  }

  startUp();


  var server = require.main.require(path.join(__dirname, "express_app.js"));

});



