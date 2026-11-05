// Constantes de negócio e mensagens do contrato público da API (F-16).
module.exports = Object.freeze({
    APPROVED_CARD_PREFIX: '4',

    PAYMENT_STATUS: Object.freeze({
        PAID: 'PAID',
        DENIED: 'DENIED',
    }),

    ADMIN_TOKEN_HEADER: 'X-Admin-Token',

    UNKNOWN_STUDENT: 'Unknown',

    // Textos devolvidos ao cliente — preservam o contrato original.
    MESSAGES: Object.freeze({
        BAD_REQUEST: 'Bad Request',
        COURSE_NOT_FOUND: 'Curso não encontrado',
        PAYMENT_DECLINED: 'Pagamento recusado',
        CHECKOUT_SUCCESS: 'Sucesso',
        USER_DELETED: 'Usuário deletado, junto com suas matrículas e pagamentos.',
        ADMIN_FORBIDDEN: 'Acesso administrativo negado',
        INTERNAL_ERROR: 'Erro interno do servidor',
    }),
});
