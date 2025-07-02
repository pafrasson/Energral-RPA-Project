const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const db = new sqlite3.Database('./database.db');

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '..', 'public')));

// Rotas para buscar máquinas e técnicos
app.get('/api/maquinas', (req, res) => {
    db.all(`SELECT id_equipamento FROM maquinas`, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

app.get('/api/tecnicos', (req, res) => {
    db.all(`SELECT id_funcionario, nome FROM funcionarios`, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// Rota para inserir novo registro
app.post('/api/registro', (req, res) => {
    const { id_maquina, id_tecnico, data_hora, observacao, status } = req.body;

    db.run(
        `INSERT INTO checklist (data_hora, id_equipamento, id_funcionario, observacao, status)
         VALUES (?, ?, ?, ?, ?)`,
        [data_hora, id_maquina, id_tecnico, observacao, status],
        function (err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ success: true, id: this.lastID });
        }
    );
});

// Iniciar servidor
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
