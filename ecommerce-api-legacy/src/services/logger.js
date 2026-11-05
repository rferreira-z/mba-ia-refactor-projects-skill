// Logger mínimo com níveis, sobre a stdlib — sem nova dependência (F-19).
const LEVELS = Object.freeze({ error: 0, warn: 1, info: 2, debug: 3 });

function createLogger({ level = 'info' } = {}) {
    const threshold = LEVELS[level] !== undefined ? LEVELS[level] : LEVELS.info;

    const emit = (name) => (message, context) => {
        if (LEVELS[name] > threshold) return;
        const entry = { level: name, time: new Date().toISOString(), message };
        if (context) entry.context = context;
        const line = JSON.stringify(entry);
        // Único ponto de escrita em stdout/stderr da aplicação.
        if (name === 'error') process.stderr.write(`${line}\n`);
        else process.stdout.write(`${line}\n`);
    };

    return {
        error: emit('error'),
        warn: emit('warn'),
        info: emit('info'),
        debug: emit('debug'),
    };
}

module.exports = createLogger;
