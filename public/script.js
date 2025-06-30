
async function carregarSelects() {
    const maquinas = await fetch('/api/maquinas').then(res => res.json());
    const tecnicos = await fetch('/api/tecnicos').then(res => res.json());

    const selectMaquina = document.getElementById('id_maquina');
    const selectTecnico = document.getElementById('id_tecnico');

    maquinas.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.id;
        opt.textContent = m.nome;
        selectMaquina.appendChild(opt);
    });

    tecnicos.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.textContent = t.nome;
        selectTecnico.appendChild(opt);
    });
}

document.addEventListener('DOMContentLoaded', carregarSelects);


document.getElementById('formulario').addEventListener('submit', async function (e) {
    e.preventDefault();

    const dados = {
        id_maquina: document.getElementById('id_maquina').value,
        id_tecnico: document.getElementById('id_tecnico').value,
        data_hora: document.getElementById('data_hora').value,
        observacao: document.getElementById('observacao').value,
        status: document.getElementById('status').value
    };

    const resposta = await fetch('/api/registro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    });

    const resultado = await resposta.json();
    alert('Registro criado com ID: ' + resultado.id);
});
