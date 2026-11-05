// Hierarquia de erros de domínio. Controllers e middlewares lançam; o
// errorHandler é o único lugar que traduz para HTTP (F-13).
class AppError extends Error {
    constructor(message, status = 400) {
        super(message);
        this.name = new.target.name;
        this.status = status;
    }
}

class ValidationError extends AppError {
    constructor(message) {
        super(message, 400);
    }
}

class PaymentDeclinedError extends AppError {
    constructor(message) {
        super(message, 400);
    }
}

class ForbiddenError extends AppError {
    constructor(message) {
        super(message, 403);
    }
}

class NotFoundError extends AppError {
    constructor(message) {
        super(message, 404);
    }
}

module.exports = { AppError, ValidationError, PaymentDeclinedError, ForbiddenError, NotFoundError };
