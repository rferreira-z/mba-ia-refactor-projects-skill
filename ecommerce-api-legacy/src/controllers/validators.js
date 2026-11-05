// Validação centralizada de entrada (F-12). Os nomes dos campos do payload
// (`usr`, `eml`, `pwd`, `c_id`, `card`) fazem parte do contrato público e são
// preservados; apenas os nomes internos passam a ser descritivos (F-17).
const { MESSAGES } = require('../config/constants');
const { ValidationError } = require('../errors');

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CARD_PATTERN = /^\d{12,19}$/;

function isNonEmptyString(value) {
    return typeof value === 'string' && value.trim().length > 0;
}

function isPresent(value) {
    return value !== undefined && value !== null && value !== '';
}

function toInteger(value) {
    const parsed = Number(value);
    return Number.isInteger(parsed) ? parsed : null;
}

function validateCheckoutPayload(body) {
    const payload = body && typeof body === 'object' && !Array.isArray(body) ? body : {};
    const { usr: name, eml: email, pwd: password, c_id: rawCourseId, card: rawCard } = payload;

    if (!isNonEmptyString(name) || !isNonEmptyString(email) || !isPresent(rawCourseId) || !isPresent(rawCard)) {
        throw new ValidationError(MESSAGES.BAD_REQUEST);
    }

    if (!EMAIL_PATTERN.test(email.trim())) {
        throw new ValidationError(MESSAGES.BAD_REQUEST);
    }

    const courseId = toInteger(rawCourseId);
    if (courseId === null) {
        throw new ValidationError(MESSAGES.BAD_REQUEST);
    }

    const cardNumber = String(rawCard).replace(/[\s-]/g, '');
    if (!CARD_PATTERN.test(cardNumber)) {
        throw new ValidationError(MESSAGES.BAD_REQUEST);
    }

    return {
        name: name.trim(),
        email: email.trim(),
        password: isNonEmptyString(password) ? password : null,
        courseId,
        cardNumber,
    };
}

function validateUserId(rawId) {
    const userId = toInteger(rawId);
    if (userId === null || userId < 1) {
        throw new ValidationError(MESSAGES.BAD_REQUEST);
    }
    return userId;
}

module.exports = { validateCheckoutPayload, validateUserId };
