const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const path = require('path');
// No need for 'util' module anymore, we'll manually promisify for db.run

const app = express();
const db = new sqlite3.Database('./database.db');

// Custom promisify for db.run to expose lastID and changes
// This function returns a Promise that resolves with an object
// containing lastID and changes, mirroring the original callback context.
const dbRunPromise = (query, params) => {
    return new Promise((resolve, reject) => {
        db.run(query, params, function (err) {
            if (err) {
                reject(err);
            } else {
                // 'this' context in the callback contains lastID and changes
                resolve({ lastID: this.lastID, changes: this.changes });
            }
        });
    });
};

// Promisify db.all for consistency (util.promisify is fine for this one)
const dbAllPromise = (query, params) => {
    return new Promise((resolve, reject) => {
        db.all(query, params, (err, rows) => {
            if (err) {
                reject(err);
            } else {
                resolve(rows);
            }
        });
    });
};


// Middleware
app.use(bodyParser.json());
// Serve static files from the 'public' directory, which is one level up from 'backend'
app.use(express.static(path.join(__dirname, '..', 'public')));

// Rotas para buscar máquinas e técnicos
app.get('/api/maquinas', async (req, res) => {
    try {
        // Use our custom promisified dbAllPromise
        const rows = await dbAllPromise(`SELECT id_equipamento FROM maquinas`);
        res.json(rows);
    } catch (err) {
        console.error('Error fetching machines:', err.message);
        res.status(500).json({ error: err.message });
    }
});

app.get('/api/tecnicos', async (req, res) => {
    try {
        // Use our custom promisified dbAllPromise
        const rows = await dbAllPromise(`SELECT id_funcionario, nome FROM funcionarios`);
        res.json(rows);
    } catch (err) {
        console.error('Error fetching technicians:', err.message);
        res.status(500).json({ error: err.message });
    }
});

// Rota para inserir novo registro
app.post('/api/registro', async (req, res) => {
    const { id_maquina, id_tecnico, data_hora, observacao, status } = req.body;

    // Basic validation (optional but recommended)
    if (!id_maquina || !id_tecnico || !data_hora || !status) {
        return res.status(400).json({ error: 'Missing required fields.' });
    }

    try {
        // First DB operation: INSERT into checklist
        // Use our custom promisified dbRunPromise
        const insertResult = await dbRunPromise(
            `INSERT INTO checklist (data_hora, id_equipamento, id_funcionario, observacao, status)
             VALUES (?, ?, ?, ?, ?)`,
            [data_hora, id_maquina, id_tecnico, observacao, status]
        );
        const newRecordId = insertResult.lastID; // Now lastID will be correctly available

        // Second DB operation: UPDATE maquinas status
        // Use our custom promisified dbRunPromise
        const updateResult = await dbRunPromise(
            `UPDATE maquinas SET status_maquina = ? WHERE id_equipamento = ?`,
            [status, id_maquina]
        );
        const updatedMachineChanges = updateResult.changes; // Now changes will be correctly available

        // Send a single response after both operations are successful
        res.json({
            success: true,
            message: 'Registro inserted and machine status updated successfully.',
            newRecordId: newRecordId,
            updatedMachineCount: updatedMachineChanges
        });

    } catch (err) {
        console.error('Error processing new registration:', err.message);
        // If an error occurs in either DB operation, send a 500 status
        res.status(500).json({ error: err.message });
    }
});

// Iniciar servidor
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});