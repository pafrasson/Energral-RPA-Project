const API_BASE = "http://localhost:3000";

// Carrega máquinas no select
function carregarMaquinas() {
    fetch(`${API_BASE}/api/maquinas`)
        .then(res => res.json())
        .then(maquinas => {
            localStorage.setItem("cached_maquinas", JSON.stringify(maquinas)); // salva localmente
            popularSelectMaquinas(maquinas);
        })
        .catch(() => {
            const cached = localStorage.getItem("cached_maquinas");
            if (cached) {
                popularSelectMaquinas(JSON.parse(cached));
            } else {
                alert("Erro ao carregar máquinas e não há dados locais.");
            }
        });
}

function popularSelectMaquinas(maquinas) {
    const select = document.getElementById("id_maquina");
    select.innerHTML = '<option value="">Selecione a máquina</option>';
    maquinas.forEach(maquina => {
        const option = document.createElement("option");
        option.value = maquina.id_equipamento;
        option.textContent = maquina.id_equipamento;
        select.appendChild(option);
    });
}

// Carrega técnicos no select
fetch(`${API_BASE}/api/tecnicos`)
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
    fetch(`${API_BASE}/api/registro`, {
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

    const promessas = pendentes.map((registro, index) => {
        return fetch(`${API_BASE}/api/registro`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(registro)
        })
            .then(res => res.json())
            .then(response => {
                if (response.success || response.id) {
                    console.log("Registro pendente enviado com sucesso:", registro);
                    return index; // marcar como enviado
                } else {
                    console.warn("Servidor respondeu com erro ao reenviar registro.");
                    return null;
                }
            })
            .catch(err => {
                console.warn("Erro ao reenviar registro pendente:", err);
                return null;
            });
    });

    Promise.all(promessas).then(indicesEnviados => {
        const enviadosComSucesso = indicesEnviados.filter(i => i !== null);
        const novosPendentes = pendentes.filter((_, i) => !enviadosComSucesso.includes(i));
        localStorage.setItem("registrosPendentes", JSON.stringify(novosPendentes));
    });
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

// Carregar máquinas
carregarMaquinas();
// Tentar reenviar registros pendentes ao carregar a página
window.addEventListener("load", () => {
    verificarEnviosPendentes();
});
