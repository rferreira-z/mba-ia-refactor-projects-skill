// Caso de uso do relatório financeiro: agrega as linhas da consulta única em
// um resultado por curso, aplicando a regra de receita (só pagamentos PAID).
const { PAYMENT_STATUS, UNKNOWN_STUDENT } = require('../config/constants');

class ReportController {
    constructor({ reports }) {
        this.reports = reports;
    }

    async financialReport() {
        const rows = await this.reports.listFinancialRows();

        const byCourse = new Map();
        const countedEnrollments = new Set();

        for (const row of rows) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
            }

            // Curso sem matrícula entra no relatório com a lista vazia.
            if (row.enrollment_id === null || countedEnrollments.has(row.enrollment_id)) continue;
            countedEnrollments.add(row.enrollment_id);

            const courseEntry = byCourse.get(row.course_id);
            if (row.payment_status === PAYMENT_STATUS.PAID) {
                courseEntry.revenue += row.payment_amount;
            }
            courseEntry.students.push({
                student: row.student_name || UNKNOWN_STUDENT,
                paid: row.payment_amount === null || row.payment_amount === undefined ? 0 : row.payment_amount,
            });
        }

        return Array.from(byCourse.values());
    }
}

module.exports = ReportController;
