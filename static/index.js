// Função para gerar a análise baseada nos valores inseridos
function generateAnalysis() {
    // Obter valores dos inputs
    const itemName = document.getElementById('itemName').value;
    const L = document.getElementById('LValue').value.replace(',', '.');
    const A = document.getElementById('AValue').value.replace(',', '.');
    const B = document.getElementById('BValue').value.replace(',', '.');

    // Validação simples: verificar se L, A e B são números válidos
    if (isNaN(parseFloat(L)) || isNaN(parseFloat(A)) || isNaN(parseFloat(B))) {
        alert('Por favor, insira valores numéricos válidos para L*, a* e b*.');
        return;
    }

    // Preparar dados para envio
    const data = {
        L: L,
        A: A,
        B: B
    };

    // Fazer requisição para o servidor Flask
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Parse the graph JSON from the server
        const graph = JSON.parse(data);
        Plotly.newPlot('graph', graph.data, graph.layout);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Falha ao gerar o gráfico. Verifique o console para detalhes.');
    });
}

// Adicionar event listener para impedir o envio do formulário
document.getElementById('inputForm').addEventListener('submit', function(event) {
    event.preventDefault();
    generateAnalysis(); // Chamar a função de análise ao submeter o formulário
});
