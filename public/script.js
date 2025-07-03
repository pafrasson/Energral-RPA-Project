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

// Função para enviar dados (com fallback para localStorage)
function enviarRegistro(data) {
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
                verificarEnviosPendentes();
            } else {
                salvarLocalmente(data);
                alert("Servidor respondeu com erro. Registro salvo localmente.");
            }
        })
        .catch(err => {
            console.warn("Erro ao conectar com o servidor. Salvando localmente...");
            salvarLocalmente(data);
        });
}

function salvarLocalmente(data) {
    const pendentes = JSON.parse(localStorage.getItem("registrosPendentes")) || [];
    pendentes.push(data);
    localStorage.setItem("registrosPendentes", JSON.stringify(pendentes));
}

function verificarEnviosPendentes() {
    const pendentes = JSON.parse(localStorage.getItem("registrosPendentes")) || [];
    if (pendentes.length === 0) return;

    const enviados = [];

    pendentes.forEach((registro, index) => {
        fetch("/api/registro", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(registro)
        })
            .then(res => res.json())
            .then(response => {
                if (response.success || response.id) {
                    enviados.push(index);
                    console.log("Registro pendente enviado com sucesso.");
                }
            })
            .catch(err => {
                console.warn("Falha ao reenviar registro pendente.", err);
            });
    });

    // Remover os que foram enviados com sucesso
    setTimeout(() => {
        const atualizados = JSON.parse(localStorage.getItem("registrosPendentes")) || [];
        const novosPendentes = atualizados.filter((_, i) => !enviados.includes(i));
        localStorage.setItem("registrosPendentes", JSON.stringify(novosPendentes));
    }, 2000);
}

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

    enviarRegistro(data);
});

// Tentar reenviar registros pendentes ao carregar a página
window.addEventListener("load", verificarEnviosPendentes);

