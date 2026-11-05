// Único ponto que traduz erro em resposta HTTP (F-13). Mantém o corpo em
// texto puro usado pela API original para os erros de 4xx.
const { MESSAGES } = require('../config/constants');
const { AppError } = require('../errors');

function createErrorHandler(logger) {
    return function errorHandler(err, req, res, next) {
        if (res.headersSent) return next(err);

        if (err instanceof AppError) {
            logger.warn('request.rejected', {
                method: req.method,
                path: req.path,
                status: err.status,
                reason: err.message,
            });
            return res.status(err.status).send(err.message);
        }

        logger.error('request.failed', {
            method: req.method,
            path: req.path,
            error: err.message,
            stack: err.stack,
        });
        return res.status(500).send(MESSAGES.INTERNAL_ERROR);
    };
}

module.exports = createErrorHandler;
