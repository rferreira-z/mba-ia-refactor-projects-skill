// View do relatório financeiro, protegida pelo guard administrativo.
const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');

function reportRoutes(controller, adminGuard) {
    const router = express.Router();

    router.get(
        '/api/admin/financial-report',
        adminGuard,
        asyncHandler(async (req, res) => {
            const report = await controller.financialReport();
            res.status(200).json(report);
        }),
    );

    return router;
}

module.exports = reportRoutes;
