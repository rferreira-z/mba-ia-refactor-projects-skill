// Fronteira com o gateway de pagamento. Nunca registra o PAN completo nem a
// chave do gateway (F-02); a regra de aprovação vive aqui, não na rota (F-06).
const { APPROVED_CARD_PREFIX, PAYMENT_STATUS } = require('../config/constants');

function maskCardNumber(cardNumber) {
    return `****${String(cardNumber).slice(-4)}`;
}

class PaymentGateway {
    constructor({ settings, logger }) {
        this.settings = settings;
        this.logger = logger;
    }

    charge({ cardNumber, amount }) {
        const status = cardNumber.startsWith(APPROVED_CARD_PREFIX)
            ? PAYMENT_STATUS.PAID
            : PAYMENT_STATUS.DENIED;

        this.logger.info('payment.charge', {
            card: maskCardNumber(cardNumber),
            amount,
            status,
            gatewayConfigured: Boolean(this.settings.paymentGatewayKey),
        });

        return { status, approved: status === PAYMENT_STATUS.PAID };
    }
}

module.exports = { PaymentGateway, maskCardNumber };
