// Entry point — preserva `npm start` / `node src/app.js`.
const createApp = require('./createApp');
const { settings, assertProductionSettings } = require('./config/settings');
const { createConnection, initializeDatabase } = require('./database/connection');
const createLogger = require('./services/logger');
const passwordHasher = require('./services/passwordHasher');

async function main() {
    assertProductionSettings();

    const logger = createLogger({ level: settings.logLevel });
    const db = createConnection(settings);
    await initializeDatabase(db, { passwordHasher });

    const app = createApp({ settings, db, logger });

    app.listen(settings.port, () => {
        logger.info('server.started', { port: settings.port, env: settings.env });
    });
}

main().catch((err) => {
    process.stderr.write(`${JSON.stringify({ level: 'error', message: 'server.start_failed', error: err.message })}\n`);
    process.exit(1);
});
