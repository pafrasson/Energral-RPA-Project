const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const db = new sqlite3.Database('./database.db');

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '..', 'public')));

// Criação das tabelas
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS maquinas (
        id TEXT PRIMARY KEY,
        nome TEXT
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS tecnicos (
        id TEXT PRIMARY KEY,
        nome TEXT
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_maquina TEXT,
        id_tecnico TEXT,
        data_hora TEXT,
        observacao TEXT,
        status TEXT,
        FOREIGN KEY (id_maquina) REFERENCES maquinas(id),
        FOREIGN KEY (id_tecnico) REFERENCES tecnicos(id)
    )`);

    db.run(`INSERT OR IGNORE INTO maquinas (id, nome) VALUES ('M001', 'Máquina 1'), ('M002', 'Máquina 2')`);
    db.run(`INSERT OR IGNORE INTO tecnicos (id, nome) VALUES ('T001', 'Técnico João'), ('T002', 'Técnico Ana')`);

});

// Rotas para buscar máquinas e técnicos
app.get('/api/maquinas', (req, res) => {
    db.all(`SELECT id, nome FROM maquinas`, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

app.get('/api/tecnicos', (req, res) => {
    db.all(`SELECT id, nome FROM tecnicos`, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// Rota para inserir novo registro
app.post('/api/registro', (req, res) => {
    const { id_maquina, id_tecnico, data_hora, observacao, status } = req.body;

    db.run(
        `INSERT INTO registros (id_maquina, id_tecnico, data_hora, observacao, status)
         VALUES (?, ?, ?, ?, ?)`,
        [id_maquina, id_tecnico, data_hora, observacao, status],
        function (err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ id: this.lastID });
        }
    );
});

// Iniciar servidor
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
