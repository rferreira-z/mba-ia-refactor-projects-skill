// View de usuários. A exclusão é destrutiva, logo exige credencial admin.
const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');

function userRoutes(controller, adminGuard) {
    const router = express.Router();

    router.delete(
        '/api/users/:id',
        adminGuard,
        asyncHandler(async (req, res) => {
            const message = await controller.deleteUser(req.params.id);
            res.status(200).send(message);
        }),
    );

    return router;
}

module.exports = userRoutes;
