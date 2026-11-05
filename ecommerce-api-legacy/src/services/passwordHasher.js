// Hashing lento e salgado com scrypt (stdlib), substituindo o badCrypto (F-05).
const crypto = require('crypto');
const { promisify } = require('util');

const scrypt = promisify(crypto.scrypt);

const SCHEME = 'scrypt';
const SALT_BYTES = 16;
const KEY_LENGTH = 64;

async function hash(password) {
    const salt = crypto.randomBytes(SALT_BYTES).toString('hex');
    const key = await scrypt(password, salt, KEY_LENGTH);
    return `${SCHEME}$${salt}$${key.toString('hex')}`;
}

async function verify(password, stored) {
    const [scheme, salt, key] = String(stored || '').split('$');
    if (scheme !== SCHEME || !salt || !key) return false;
    const expected = Buffer.from(key, 'hex');
    const candidate = await scrypt(password, salt, KEY_LENGTH);
    return candidate.length === expected.length && crypto.timingSafeEqual(candidate, expected);
}

module.exports = { hash, verify };
