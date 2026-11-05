// Express 4 não captura promises rejeitadas: este wrapper encaminha qualquer
// rejeição para o errorHandler central (F-13, F-15).
module.exports = (handler) => (req, res, next) => Promise.resolve(handler(req, res, next)).catch(next);
