// View: apenas declara o endpoint, repassa o corpo ao controller e serializa.
const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');

function checkoutRoutes(controller) {
    const router = express.Router();

    router.post(
        '/api/checkout',
        asyncHandler(async (req, res) => {
            const result = await controller.checkout(req.body);
            res.status(200).json(result);
        }),
    );

    return router;
}

module.exports = checkoutRoutes;
