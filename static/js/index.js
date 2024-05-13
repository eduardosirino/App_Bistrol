document.addEventListener('DOMContentLoaded', () => {
    const statusMessage = $('.status-message');
    statusMessage.text('Pronto').css('color', 'green');

    // Fetch inicial para coletar os itens da tabela
    fetch('/item-names')
        .then(response => response.json())
        .then(items => {
            $('#itemName').autocomplete({
                source: items.map(item => ({ label: item.Nome, value: item.Nome, data: item })),
                select: function(event, ui) {
                    $('#itemName').val(ui.item.value);
                    $('#LValue').attr('data-original', ui.item.data['L*']);
                    $('#AValue').attr('data-original', ui.item.data['a*']);
                    $('#BValue').attr('data-original', ui.item.data['b*']);
                    $('#LValue-label').text(ui.item.data['L*']);
                    $('#AValue-label').text(ui.item.data['a*']);
                    $('#BValue-label').text(ui.item.data['b*']);

                    updateInputColors();
                    generateAnalysis();
                    return false;
                },
                minLength: 0
            }).focus(function () {
                $(this).autocomplete("search", "");
            });
        })
        .catch(error => console.error('Erro ao buscar nomes de itens:', error));

    // Função para alterar as cores dos inputs
    function updateInputColors() {
        ['LValue', 'AValue', 'BValue'].forEach(id => {
            const input = $('#' + id);
            const original = parseFloat(input.attr('data-original'));
            const current = parseFloat(input.val().replace(',', '.'));
            input.css('background-color', isNaN(original) || isNaN(current) ? '' : (original === current ? '#90EE90' : '#FFB6C1'));
        });
    }
    
    // Função para coletar os dados, enviar ao back e retornar plotando o gráfico
    function generateAnalysis() {
        statusMessage.text('Gerando...').css('color', 'yellow');

        const itemName = $('#itemName').val();
        const L = $('#LValue').val().replace(',', '.');
        const A = $('#AValue').val().replace(',', '.');
        const B = $('#BValue').val().replace(',', '.');

        const data = {
            name: itemName,
            L: L,
            A: A,
            B: B
        };

        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            drawGraph(data);
            statusMessage.text('Pronto').css('color', 'green');
        })
        .catch(error => {
            console.error('Error:', error);
            statusMessage.text('Erro!').css('color', 'red');
            alert('Falha ao gerar o gráfico. Verifique o console para detalhes.');
        });
    }

    // Função para plotar o gráfico
    function drawGraph(data) {
        Plotly.newPlot('graph', JSON.parse(data).data, JSON.parse(data).layout);
    }

    // Função para resetar a página sem recarregar
    function resetMainContainer() {
        $('.input-group input[type="text"]').val('');
        $('.input-group span').text('');
        Plotly.purge('graph');
    }    

    // Listeners para alterações nos inputs de valores
    document.getElementById('LValue').addEventListener('input', () => {
        updateInputColors();
        generateAnalysis();
    });
    document.getElementById('AValue').addEventListener('input', () => {
        updateInputColors();
        generateAnalysis();
    });
    document.getElementById('BValue').addEventListener('input', () => {
        updateInputColors();
        generateAnalysis();
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            updateInputColors();
            generateAnalysis();
        } else if (event.key === 'Escape') {
            event.preventDefault();
            resetMainContainer();
        }
    });
    document.getElementById("reset").addEventListener('click', (event) => {
        event.preventDefault();
        resetMainContainer();
    })
});
