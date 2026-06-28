const API = "http://127.0.0.1:5000/api/services";

document.addEventListener("DOMContentLoaded", carregarServicos);

async function carregarServicos() {
    try {
        const resposta = await fetch(API);

        // Garante que erros HTTP (4xx, 5xx) também sejam capturados
        if (!resposta.ok) {
            throw new Error(`Erro na API: ${resposta.status} ${resposta.statusText}`);
        }

        const dados = await resposta.json();
        renderizarServicos(dados);

    } catch (erro) {
        console.error("Falha ao carregar serviços:", erro);

        const container = document.getElementById("services-container");
        if (container) {
            container.innerHTML = `
                <p style="text-align:center; color:red;">
                    Não foi possível carregar os serviços. Verifique sua conexão ou tente novamente.
                </p>`;
        }
    }
}

function renderizarServicos(dados) {
    // Suporta tanto { services: [...] } quanto [...]
    const servicos = Array.isArray(dados) ? dados : (dados.services || []);

    const container = document.getElementById("services-container");

    if (!container) {
        console.error("Container #services-container não encontrado no HTML!");
        return;
    }

    if (servicos.length === 0) {
        container.innerHTML = "<p>Nenhum serviço disponível no momento.</p>";
        return;
    }

    container.innerHTML = "";

    servicos.forEach((servico) => {
        const beneficiosLista = Array.isArray(servico.beneficios) ? servico.beneficios : [];

        const beneficios = beneficiosLista
            .map(item => `<li>✔ ${escaparHtml(item)}</li>`)
            .join("");

        // Escapa a mensagem para uso seguro dentro do onclick
        const mensagemSegura = (servico.mensagem || "").replace(/'/g, "\\'");

        container.insertAdjacentHTML("beforeend", `
            <div class="col-lg-4">
                <div class="service-card">
                    ${servico.destaque ? `<span class="badge-premium">Mais Procurado</span>` : ""}
                    <div class="service-image">
                        <img src="${escaparHtml(servico.imagem || '')}" alt="${escaparHtml(servico.titulo || '')}">
                    </div>
                    <div class="service-content">
                        <span class="service-category">
                            ${escaparHtml(servico.categoria || '')}
                        </span>
                        <h3>${escaparHtml(servico.titulo || '')}</h3>
                        <p>${escaparHtml(servico.descricao || '')}</p>
                        <ul class="service-benefits">
                            ${beneficios}
                        </ul>
                        <div class="service-footer">
                            <span>⏱ ${escaparHtml(servico.tempo || '')}</span>
                            <button
                                class="btn btn-gold"
                                onclick="abrirWhatsapp('${mensagemSegura}')">
                                Solicitar orçamento
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    });
}

// Previne XSS escapando caracteres especiais HTML
function escaparHtml(texto) {
    const mapa = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
    return String(texto).replace(/[&<>"']/g, c => mapa[c]);
}