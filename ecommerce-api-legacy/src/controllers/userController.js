// Caso de uso de exclusão de usuário.
const { MESSAGES } = require('../config/constants');
const { validateUserId } = require('./validators');

class UserController {
    constructor({ users, logger }) {
        this.users = users;
        this.logger = logger;
    }

    async deleteUser(rawId) {
        const userId = validateUserId(rawId);
        const removed = await this.users.deleteWithDependents(userId);

        this.logger.info('user.deleted', { userId, removed });

        return MESSAGES.USER_DELETED;
    }
}

module.exports = UserController;
