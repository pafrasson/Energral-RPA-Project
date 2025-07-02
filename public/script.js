// Carrega máquinas no select
fetch("/api/maquinas")
    .then(res => res.json())
    .then(maquinas => {
        const select = document.getElementById("id_maquina");
        maquinas.forEach(maquina => {
            const option = document.createElement("option");
            option.value = maquina.id_equipamento;
            option.textContent = maquina.id_equipamento;
            select.appendChild(option);
        });
    })
    .catch(err => console.error("Erro ao carregar máquinas:", err));

// Carrega técnicos no select
fetch("/api/tecnicos")
    .then(res => res.json())
    .then(tecnicos => {
        const select = document.getElementById("id_tecnico");
        tecnicos.forEach(tecnico => {
            const option = document.createElement("option");
            option.value = tecnico.id_funcionario;
            option.textContent = tecnico.nome;
            select.appendChild(option);
        });
    })
    .catch(err => console.error("Erro ao carregar técnicos:", err));

// Envio do formulário
document.getElementById("formulario").addEventListener("submit", function (e) {
    e.preventDefault();

    const data = {
        id_maquina: document.getElementById("id_maquina").value,
        id_tecnico: document.getElementById("id_tecnico").value,
        data_hora: document.getElementById("data_hora").value,
        observacao: document.getElementById("observacao").value,
        status: document.getElementById("status").value
    };

    fetch("/api/registro", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(response => {
            if (response.success || response.id) {
                alert("Registro salvo com sucesso!");
                document.getElementById("formulario").reset();
            } else {
                alert("Erro ao salvar registro.");
            }
        })
        .catch(err => {
            alert("Erro ao conectar com o servidor.");
            console.error(err);
        });
});
