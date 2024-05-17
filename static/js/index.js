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

    // Função para adicionar o listener de teclas quando a modal é aberta
    function addModalKeyListeners() {
        document.removeEventListener('keydown', originalKeyHandler);
        document.addEventListener('keydown', modalKeyHandler);
    }

    // Função para remover o listener de teclas quando a modal é fechada
    function removeModalKeyListeners() {
        document.removeEventListener('keydown', modalKeyHandler);
        document.addEventListener('keydown', originalKeyHandler);
    }

    // Manipulador de eventos de teclado para a modal
    function modalKeyHandler(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            $('#change-password-form').submit();
        } else if (event.key === 'Escape') {
            event.preventDefault();
            $('#change-password-modal').dialog('close');
        }
    }

    // Manipulador de eventos de teclado original
    function originalKeyHandler(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            updateInputColors();
            generateAnalysis();
        } else if (event.key === 'Escape') {
            event.preventDefault();
            resetMainContainer();
        }
    }

    // Troca de senha
    $(document).ready(function() {
        document.addEventListener('keydown', originalKeyHandler);

        $('#change-password-button').click(function() {
            $('.modal-overlay').show();
            $('#change-password-modal').dialog({
                modal: true,
                width: 400,
                close: function() {
                    removeModalKeyListeners();
                    $('.modal-overlay').hide();
                },
                open: function() {
                    addModalKeyListeners();
                },
                create: function(event, ui) {
                    var widget = $(this).dialog("widget");
                    $(".ui-dialog-titlebar-close").appendTo(widget).css({
                        "position": "absolute",
                        "top": "10px",
                        "right": "10px",
                        "color": "#fff"
                    });
                    widget.css("padding", "0");
                }
            });
        });

        $('#cancel-change-password').click(function() {
            $('#change-password-modal').dialog('close');
        });

        $('#overlay-modal').click(function() {
            $('#change-password-modal').dialog('close');
        });

        $('#change-password-form').submit(function(event) {
            event.preventDefault();
            const currentPassword = $('#current-password').val();
            const newPassword = $('#new-password').val();
            const confirmPassword = $('#confirm-password').val();

            if (newPassword !== confirmPassword) {
                alert('A nova senha e a confirmação da nova senha não coincidem!');
                return;
            }

            $.ajax({
                url: '/change-password',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    currentPassword: currentPassword,
                    newPassword: newPassword
                }),
                success: function(response) {
                    alert(response.message);
                    if (response.success) {
                        $('#change-password-modal').dialog('close');
                    }
                },
                error: function(xhr, status, error) {
                    let errorMessage = "Erro ao tentar trocar a senha.";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    }
                    alert(errorMessage);
                }
            });
        });
    });

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
    document.getElementById("reset").addEventListener('click', (event) => {
        event.preventDefault();
        resetMainContainer();
    })
});
