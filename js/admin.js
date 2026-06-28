const API = "https://danielemakeup.onrender.com/api";
const IMG_BASE = "https://danielemakeup.onrender.com/api";
let servicoEditandoId  = null;
let imagemUpladada     = null; // caminho retornado pelo backend após upload

// ─── Inicialização ────────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", async () => {
    const { logado } = await (await fetch(`${API}/admin/check`, { credentials: "include" })).json();
    if (logado) mostrarPainel();
    configurarUpload();
});

// ─── Login / Logout ───────────────────────────────────────────────────────────
async function fazerLogin() {
    const username = document.getElementById("input-usuario").value.trim();
    const password = document.getElementById("input-senha").value.trim();
    const erroEl   = document.getElementById("erro-login");

    const res = await fetch(`${API}/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username, password })
    });

    if (res.ok) { erroEl.style.display = "none"; mostrarPainel(); }
    else        { erroEl.style.display = "block"; }
}

document.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && document.getElementById("tela-login").style.display !== "none") {
        fazerLogin();
    }
});

async function fazerLogout() {
    await fetch(`${API}/admin/logout`, { method: "POST", credentials: "include" });
    document.getElementById("tela-painel").style.display = "none";
    document.getElementById("tela-login").style.display  = "flex";
}

function mostrarPainel() {
    document.getElementById("tela-login").style.display  = "none";
    document.getElementById("tela-painel").style.display = "block";
    carregarServicos();
}

// ─── Listagem ─────────────────────────────────────────────────────────────────
async function carregarServicos() {
    const container = document.getElementById("lista-servicos");
    container.innerHTML = `<p class="carregando">Carregando serviços...</p>`;

    try {
        const dados    = await (await fetch(`${API}/services`, { credentials: "include" })).json();
        const servicos = dados.services || [];

        if (servicos.length === 0) {
            container.innerHTML = `<p class="carregando">Nenhum serviço cadastrado ainda.</p>`;
            return;
        }

        container.innerHTML = servicos.map(s => `
            <div class="card-admin">
                <img src="${IMG_BASE}/${s.imagem || ''}" alt="${s.titulo || ''}"
                     onerror="this.style.display='none'">
                <div class="card-body">
                    ${s.destaque ? `<span class="badge">⭐ Mais Procurado</span>` : ""}
                    <div class="categoria">${s.categoria || ""}</div>
                    <h3>${s.titulo || ""}</h3>
                    <p>${s.descricao || ""}</p>
                    <div class="acoes">
                        <button class="btn-editar" onclick='abrirEdicao(${JSON.stringify(s)})'>✏️ Editar</button>
                        <button class="btn-deletar" onclick="deletarServico(${s.id}, '${s.titulo.replace(/'/g, "\\'")}')">🗑️ Deletar</button>
                    </div>
                </div>
            </div>
        `).join("");

    } catch (e) {
        container.innerHTML = `<p class="carregando" style="color:red">Erro ao carregar serviços.</p>`;
    }
}

// ─── Upload de imagem ─────────────────────────────────────────────────────────
function configurarUpload() {
    const inputArquivo = document.getElementById("f-imagem-arquivo");
    const uploadArea   = document.getElementById("upload-area");

    // Drag & drop
    uploadArea.addEventListener("dragover",  (e) => { e.preventDefault(); uploadArea.classList.add("drag-over"); });
    uploadArea.addEventListener("dragleave", ()  => uploadArea.classList.remove("drag-over"));
    uploadArea.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadArea.classList.remove("drag-over");
        const arquivo = e.dataTransfer.files[0];
        if (arquivo) processarArquivo(arquivo);
    });

    inputArquivo.addEventListener("change", () => {
        if (inputArquivo.files[0]) processarArquivo(inputArquivo.files[0]);
    });
}

async function processarArquivo(arquivo) {
    const status  = document.getElementById("upload-status");
    const preview = document.getElementById("preview-imagem");

    // Preview local imediato
    const leitor = new FileReader();
    leitor.onload = (e) => {
        preview.src     = e.target.result;
        preview.style.display = "block";
    };
    leitor.readAsDataURL(arquivo);

    // Envia para o backend
    status.textContent = "⏳ Enviando imagem...";
    status.style.color = "#888";

    const form = new FormData();
    form.append("imagem", arquivo);

    try {
        const res  = await fetch(`${API}/admin/upload`, {
            method: "POST",
            credentials: "include",
            body: form
        });
        const dado = await res.json();

        if (res.ok) {
            imagemUpladada = dado.imagem; // ex: "img/casamento.png"
            document.getElementById("f-imagem-path").value = imagemUpladada;
            status.textContent = `✅ Imagem salva: ${dado.imagem}`;
            status.style.color = "green";
        } else {
            status.textContent = `❌ Erro: ${dado.erro}`;
            status.style.color = "red";
        }
    } catch (e) {
        status.textContent = "❌ Falha no envio. Tente novamente.";
        status.style.color = "red";
    }
}

// ─── Modal ────────────────────────────────────────────────────────────────────
function abrirModal(servico = null) {
    servicoEditandoId = servico ? servico.id : null;
    imagemUpladada    = null;

    document.getElementById("modal-titulo").textContent  = servico ? "Editar Serviço" : "Novo Serviço";
    document.getElementById("f-titulo").value            = servico?.titulo    || "";
    document.getElementById("f-descricao").value         = servico?.descricao || "";
    document.getElementById("f-categoria").value         = servico?.categoria || "";
    document.getElementById("f-tempo").value             = servico?.tempo     || "";
    document.getElementById("f-mensagem").value          = servico?.mensagem  || "";
    document.getElementById("f-destaque").checked        = servico?.destaque  || false;
    document.getElementById("f-imagem-path").value       = servico?.imagem    || "";
    document.getElementById("f-imagem-arquivo").value    = "";
    document.getElementById("upload-status").textContent = "";

    // Preview da imagem atual
    const preview = document.getElementById("preview-imagem");
    if (servico?.imagem) {
        preview.src           = `${IMG_BASE}/${servico.imagem}`;
        preview.style.display = "block";
        preview.onerror       = () => { preview.style.display = "none"; };
    } else {
        preview.style.display = "none";
        preview.src           = "";
    }

    const lista = document.getElementById("lista-beneficios");
    lista.innerHTML = "";
    (servico?.beneficios || []).forEach(b => adicionarItemBeneficio(b));

    document.getElementById("overlay").classList.add("ativo");
}

function abrirEdicao(servico) { abrirModal(servico); }

function fecharModal() {
    document.getElementById("overlay").classList.remove("ativo");
    servicoEditandoId = null;
    imagemUpladada    = null;
}

document.getElementById("overlay").addEventListener("click", (e) => {
    if (e.target === document.getElementById("overlay")) fecharModal();
});

// ─── Benefícios ───────────────────────────────────────────────────────────────
function adicionarBeneficio() {
    const input = document.getElementById("input-beneficio");
    const texto = input.value.trim();
    if (!texto) return;
    adicionarItemBeneficio(texto);
    input.value = "";
    input.focus();
}

function adicionarItemBeneficio(texto) {
    const li = document.createElement("li");
    li.dataset.valor = texto;
    li.innerHTML = `<span>✔ ${texto}</span><button onclick="this.parentElement.remove()" title="Remover">×</button>`;
    document.getElementById("lista-beneficios").appendChild(li);
}

document.getElementById("input-beneficio").addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); adicionarBeneficio(); }
});

function coletarBeneficios() {
    return [...document.querySelectorAll("#lista-beneficios li")].map(li => li.dataset.valor);
}

// ─── Salvar ───────────────────────────────────────────────────────────────────
async function salvarServico() {
    const titulo = document.getElementById("f-titulo").value.trim();
    if (!titulo) { alert("O título é obrigatório."); return; }

    // Usa imagem recém-enviada ou mantém a atual
    const imagem = imagemUpladada || document.getElementById("f-imagem-path").value || "";

    const payload = {
        titulo,
        descricao:  document.getElementById("f-descricao").value.trim(),
        categoria:  document.getElementById("f-categoria").value.trim(),
        tempo:      document.getElementById("f-tempo").value.trim(),
        mensagem:   document.getElementById("f-mensagem").value.trim(),
        destaque:   document.getElementById("f-destaque").checked,
        beneficios: coletarBeneficios(),
        imagem
    };

    const url    = servicoEditandoId ? `${API}/admin/services/${servicoEditandoId}` : `${API}/admin/services`;
    const method = servicoEditandoId ? "PUT" : "POST";

    const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload)
    });

    if (res.ok) { fecharModal(); carregarServicos(); }
    else        { alert("Erro ao salvar serviço. Tente novamente."); }
}

// ─── Deletar ──────────────────────────────────────────────────────────────────
async function deletarServico(id, titulo) {
    if (!confirm(`Deseja deletar o serviço "${titulo}"?`)) return;

    const res = await fetch(`${API}/admin/services/${id}`, {
        method: "DELETE",
        credentials: "include"
    });

    if (res.ok) carregarServicos();
    else        alert("Erro ao deletar. Tente novamente.");
}
