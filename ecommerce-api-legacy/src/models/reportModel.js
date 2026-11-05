// Leitura do relatório financeiro em uma única consulta, no lugar das
// 1 + C + 2*M queries aninhadas da versão original (F-11).
const FINANCIAL_ROWS_SQL = `
    SELECT c.id                AS course_id,
           c.title             AS course_title,
           e.id                AS enrollment_id,
           u.name              AS student_name,
           p.amount            AS payment_amount,
           p.status            AS payment_status
      FROM courses c
      LEFT JOIN enrollments e ON e.course_id = c.id
      LEFT JOIN users u       ON u.id = e.user_id
      LEFT JOIN payments p    ON p.enrollment_id = e.id
     ORDER BY c.id, e.id, p.id
`;

class ReportModel {
    constructor(db) {
        this.db = db;
    }

    listFinancialRows() {
        return this.db.all(FINANCIAL_ROWS_SQL, []);
    }
}

module.exports = ReportModel;
