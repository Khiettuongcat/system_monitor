// main.js
const { app, BrowserWindow } = require('electron');
const path = require('node:path')

require("electron-reload")(path.join(__dirname), {
  electron: require(`${__dirname}/node_modules/electron`)
});

function createWindow() {
  const win = new BrowserWindow({
    width: 1300,
    height: 800,
    icon: path.join(__dirname, "img", "logo.png"),
    autoHideMenuBar: true,
    webPreferences: {
      // preload: path.join(__dirname, 'src', 'js', 'index.js'), // ⚡ load preload
      contextIsolation: true,  // ⚡ nên bật
      nodeIntegration: false   // ⚡ tắt // ⚡ tắt contextIsolation để dùng trực tiếp ipcRenderer
    }
  });
  win.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
