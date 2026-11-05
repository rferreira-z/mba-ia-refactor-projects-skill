// Persistência de cursos.
class CourseModel {
    constructor(db) {
        this.db = db;
    }

    findActiveById(courseId) {
        return this.db.get('SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1', [courseId]);
    }
}

module.exports = CourseModel;
