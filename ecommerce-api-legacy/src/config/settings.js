// Configuração lida do ambiente. Nenhum segredo literal mora aqui (F-04, F-10).
const DEV_DEFAULTS = {
    port: 3000,
    databaseFile: ':memory:',
    logLevel: 'info',
};

const settings = Object.freeze({
    env: process.env.NODE_ENV || 'development',
    port: Number(process.env.PORT || DEV_DEFAULTS.port),
    databaseFile: process.env.DATABASE_FILE || DEV_DEFAULTS.databaseFile,
    logLevel: process.env.LOG_LEVEL || DEV_DEFAULTS.logLevel,
    // Sem valor padrão: ausente significa "rotas administrativas bloqueadas".
    adminToken: process.env.ADMIN_TOKEN || '',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
});

function assertProductionSettings(current = settings) {
    if (current.env !== 'production') return;
    const missing = ['adminToken', 'paymentGatewayKey'].filter((key) => !current[key]);
    if (missing.length > 0) {
        throw new Error(`Configuração obrigatória ausente em produção: ${missing.join(', ')}`);
    }
}

module.exports = { settings, assertProductionSettings };
