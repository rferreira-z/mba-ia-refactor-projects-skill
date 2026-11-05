// Composition root: o único lugar onde dependências concretas são criadas e
// ligadas (F-07). Não contém rota nem regra de negócio.
const express = require('express');

const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const ReportModel = require('./models/reportModel');

const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');

const checkoutRoutes = require('./views/checkoutRoutes');
const reportRoutes = require('./views/reportRoutes');
const userRoutes = require('./views/userRoutes');

const createErrorHandler = require('./middlewares/errorHandler');
const requireAdminToken = require('./middlewares/requireAdminToken');

const { PaymentGateway } = require('./services/paymentGateway');
const passwordHasher = require('./services/passwordHasher');

function createApp({ settings, db, logger }) {
    const app = express();
    app.use(express.json());

    const users = new UserModel(db);
    const courses = new CourseModel(db);
    const enrollments = new EnrollmentModel(db);
    const payments = new PaymentModel(db);
    const auditLogs = new AuditLogModel(db);
    const reports = new ReportModel(db);

    const paymentGateway = new PaymentGateway({ settings, logger });

    const checkoutController = new CheckoutController({
        db,
        users,
        courses,
        enrollments,
        payments,
        auditLogs,
        paymentGateway,
        passwordHasher,
        logger,
    });
    const reportController = new ReportController({ reports });
    const userController = new UserController({ users, logger });

    const adminGuard = requireAdminToken(settings);

    app.use(checkoutRoutes(checkoutController));
    app.use(reportRoutes(reportController, adminGuard));
    app.use(userRoutes(userController, adminGuard));

    app.use(createErrorHandler(logger));

    return app;
}

module.exports = createApp;
