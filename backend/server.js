const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const path = require('path');
const cors = require('cors');

const app = express();
app.use(cors());

const db = new sqlite3.Database('./database.db');

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '..', 'public')));

//ping
app.get('/api/ping', (req, res) => {
    res.status(200).json({ message: "pong" });
});

// Rotas para buscar máquinas e técnicos
app.get('/api/maquinas', (req, res) => {
    db.all(`SELECT id_equipamento, status_maquina FROM maquinas`, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

app.get('/api/tecnicos', (req, res) => {
    db.all(`SELECT id_funcionario, nome FROM funcionarios ORDER BY nome`, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// Rota para buscar TODOS os checklists
app.get('/api/checklist', (req, res) => {
    db.all(`SELECT * FROM checklist`, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// Rota para buscar TODOS os alertas
app.get('/api/alertas', (req, res) => {
    db.all(`SELECT * FROM alertas`, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// Atualiza o status de um registro no checklist
app.put('/api/checklist/:id/status', (req, res) => {
    const id = req.params.id;
    const { status } = req.body;

    if (!status) {
        return res.status(400).json({ error: 'Status é obrigatório.' });
    }

    const query = `UPDATE checklist SET status = ? WHERE id_checklist = ?`;

    db.run(query, [status, id], function (err) {
        if (err) {
            console.error("Erro ao atualizar status do checklist:", err.message);
            return res.status(500).json({ error: err.message });
        }

        if (this.changes === 0) {
            return res.status(404).json({ error: 'Registro não encontrado.' });
        }

        res.json({ success: true, message: 'Status atualizado com sucesso.' });
    });
});

// Rota para inserir novo registro
app.post('/api/registro', (req, res) => {
    const { id_maquina, id_tecnico, data_hora, observacao, status } = req.body;

    // Inicia uma transação
    db.serialize(() => {
        // 1. Insere na tabela checklist
        db.run(
            `INSERT INTO checklist (data_hora, id_equipamento, id_funcionario, observacao, status)
             VALUES (?, ?, ?, ?, ?)`,
            [data_hora, id_maquina, id_tecnico, observacao, status],
            function (err) {
                if (err) {
                    console.error("Erro ao inserir no checklist:", err.message);
                    return res.status(500).json({ error: err.message });
                }

                const insertedId = this.lastID;

                // 2. Atualiza o status da máquina correspondente
                db.run(
                    `UPDATE maquinas SET status_maquina = ? WHERE id_equipamento = ?`,
                    [status, id_maquina],
                    function (err2) {
                        if (err2) {
                            console.error("Erro ao atualizar status da máquina:", err2.message);
                            return res.status(500).json({ error: err2.message });
                        }

                        res.json({ success: true, id: insertedId });
                    }
                );
            }
        );
    });
});


// Iniciar servidor
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
