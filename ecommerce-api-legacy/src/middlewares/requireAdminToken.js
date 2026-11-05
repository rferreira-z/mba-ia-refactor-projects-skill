// Guarda das rotas administrativa e destrutiva (F-03). Sem ADMIN_TOKEN
// configurado o acesso é negado — o padrão seguro é bloquear.
const crypto = require('crypto');
const { ADMIN_TOKEN_HEADER, MESSAGES } = require('../config/constants');
const { ForbiddenError } = require('../errors');

function safeEquals(provided, expected) {
    const a = Buffer.from(String(provided));
    const b = Buffer.from(String(expected));
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function requireAdminToken(settings) {
    return function adminGuard(req, res, next) {
        const provided = req.get(ADMIN_TOKEN_HEADER) || '';
        if (!settings.adminToken || !safeEquals(provided, settings.adminToken)) {
            return next(new ForbiddenError(MESSAGES.ADMIN_FORBIDDEN));
        }
        return next();
    };
}

module.exports = requireAdminToken;
