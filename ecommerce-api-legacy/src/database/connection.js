// Conexão SQLite com API promisificada e transações serializadas.
// Substitui a API callback-only aninhada nos handlers (F-14, F-15) e dá
// suporte às escritas atômicas exigidas por F-08.
const sqlite3 = require('sqlite3');
const { promisify } = require('util');

const SCHEMA_STATEMENTS = [
    'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)',
    'CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)',
    'CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)',
    'CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)',
    'CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)',
];

const SEED_USER = { name: 'Leonan', email: 'leonan@fullcycle.com.br', password: '123' };
const SEED_COURSES = [
    { title: 'Clean Architecture', price: 997.0, active: 1 },
    { title: 'Docker', price: 497.0, active: 1 },
];

function createConnection(settings) {
    const raw = new sqlite3.Database(settings.databaseFile);

    const get = promisify(raw.get.bind(raw));
    const all = promisify(raw.all.bind(raw));
    const exec = promisify(raw.exec.bind(raw));
    const close = promisify(raw.close.bind(raw));

    const run = (sql, params = []) =>
        new Promise((resolve, reject) => {
            raw.run(sql, params, function onDone(err) {
                if (err) reject(err);
                else resolve({ lastID: this.lastID, changes: this.changes });
            });
        });

    // Uma única conexão é compartilhada entre requisições, então as transações
    // são enfileiradas para que dois BEGIN nunca se sobreponham.
    let queue = Promise.resolve();

    const transaction = (work) => {
        const result = queue.then(async () => {
            await run('BEGIN IMMEDIATE');
            try {
                const value = await work();
                await run('COMMIT');
                return value;
            } catch (err) {
                await run('ROLLBACK').catch(() => {});
                throw err;
            }
        });
        queue = result.then(
            () => undefined,
            () => undefined,
        );
        return result;
    };

    return { get, all, run, exec, close, transaction };
}

async function initializeDatabase(db, { passwordHasher }) {
    for (const statement of SCHEMA_STATEMENTS) {
        await db.exec(statement);
    }

    const passwordHash = await passwordHasher.hash(SEED_USER.password);

    await db.transaction(async () => {
        await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
            SEED_USER.name,
            SEED_USER.email,
            passwordHash,
        ]);
        for (const course of SEED_COURSES) {
            await db.run('INSERT INTO courses (title, price, active) VALUES (?, ?, ?)', [
                course.title,
                course.price,
                course.active,
            ]);
        }
        await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
        await db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [1, 997.0, 'PAID']);
    });
}

module.exports = { createConnection, initializeDatabase };
