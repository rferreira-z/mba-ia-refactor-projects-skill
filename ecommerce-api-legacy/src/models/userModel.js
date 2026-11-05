// Persistência de usuários. Nunca seleciona a coluna `pass` para fora do
// model (F-02/PB-06) e nunca conhece HTTP.
class UserModel {
    constructor(db) {
        this.db = db;
    }

    findByEmail(email) {
        return this.db.get('SELECT id, name, email FROM users WHERE email = ?', [email]);
    }

    async create({ name, email, passwordHash }) {
        const { lastID } = await this.db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
            name,
            email,
            passwordHash,
        ]);
        return lastID;
    }

    // Remove o usuário e tudo que o referencia, de forma atômica (F-08).
    deleteWithDependents(userId) {
        return this.db.transaction(async () => {
            await this.db.run(
                'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
                [userId],
            );
            await this.db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
            const { changes } = await this.db.run('DELETE FROM users WHERE id = ?', [userId]);
            return changes;
        });
    }
}

module.exports = UserModel;
