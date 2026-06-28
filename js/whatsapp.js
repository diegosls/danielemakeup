const WHATSAPP_NUMBER = "+5583988559025";

/**
 * Abre o WhatsApp com uma mensagem personalizada.
 * @param {string} mensagem
 */
function abrirWhatsapp(mensagem) {

    const url =
        `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(mensagem)}`;

    window.open(url, "_blank");

}

function abrirWhatsappGeral() {
    abrirWhatsapp(
        "Olá Daniele! Conheci seu site e gostaria de solicitar um orçamento para uma maquiagem."
    );
}

function solicitarOrcamento(servico) {
    abrirWhatsapp(
        `Olá Daniele! Gostaria de solicitar um orçamento para ${servico}.`
    );

}