// Boots the ORIGINAL AppManager on a free port (src/app.js hardcodes 3000, which is busy on this machine)
const root = process.argv[2];
const express = require(root + '/node_modules/express');
const AppManager = require(root + '/src/AppManager');
const app = express(); app.use(express.json());
const m = new AppManager(); m.initDb(); m.setupRoutes(app);
app.listen(3102, () => console.log('baseline on 3102'));
