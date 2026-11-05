// Caso de uso do checkout. Orquestra models e services, não conhece req/res
// e não monta status HTTP — lança erros de domínio (F-06).
const { MESSAGES } = require('../config/constants');
const { NotFoundError, PaymentDeclinedError, ValidationError } = require('../errors');
const { validateCheckoutPayload } = require('./validators');

class CheckoutController {
    constructor({ db, users, courses, enrollments, payments, auditLogs, paymentGateway, passwordHasher, logger }) {
        this.db = db;
        this.users = users;
        this.courses = courses;
        this.enrollments = enrollments;
        this.payments = payments;
        this.auditLogs = auditLogs;
        this.paymentGateway = paymentGateway;
        this.passwordHasher = passwordHasher;
        this.logger = logger;
    }

    async checkout(body) {
        const input = validateCheckoutPayload(body);

        const course = await this.courses.findActiveById(input.courseId);
        if (!course) {
            throw new NotFoundError(MESSAGES.COURSE_NOT_FOUND);
        }

        const userId = await this.resolveUserId(input);

        const charge = this.paymentGateway.charge({ cardNumber: input.cardNumber, amount: course.price });
        if (!charge.approved) {
            throw new PaymentDeclinedError(MESSAGES.PAYMENT_DECLINED);
        }

        // Matrícula, pagamento e auditoria são uma única unidade atômica (F-08).
        const enrollmentId = await this.db.transaction(async () => {
            const createdId = await this.enrollments.create(userId, course.id);
            await this.payments.create(createdId, course.price, charge.status);
            await this.auditLogs.create(`Checkout curso ${course.id} por ${userId}`);
            return createdId;
        });

        this.logger.info('checkout.completed', { userId, courseId: course.id, enrollmentId });

        return { msg: MESSAGES.CHECKOUT_SUCCESS, enrollment_id: enrollmentId };
    }

    // Mantém o cadastro implícito do fluxo original: um e-mail desconhecido
    // vira um novo usuário, agora com senha obrigatória e hash salgado (F-05).
    async resolveUserId({ name, email, password }) {
        const existing = await this.users.findByEmail(email);
        if (existing) return existing.id;

        if (!password) {
            throw new ValidationError(MESSAGES.BAD_REQUEST);
        }

        const passwordHash = await this.passwordHasher.hash(password);
        return this.users.create({ name, email, passwordHash });
    }
}

module.exports = CheckoutController;
