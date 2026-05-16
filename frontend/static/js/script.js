// ============================================
// FUNÇÕES GLOBAIS
// ============================================

function mostrarResultados(titulo, conteudo) {
    document.getElementById('resultado-titulo').innerHTML = titulo;
    document.getElementById('resultado-conteudo').innerHTML = conteudo;
    document.getElementById('resultados').style.display = 'block';
    document.getElementById('resultados').scrollIntoView({behavior: 'smooth'});
}

function fecharResultados() {
    document.getElementById('resultados').style.display = 'none';
}

// ============================================
// LISTAGEM DE PRODUTOS
// ============================================

function listarProdutos() {
    fetch('/api/produtos')
        .then(response => response.json())
        .then(data => {
            if (data.produtos && data.produtos.length > 0) {
                let html = '<table class="table table-striped">';
                html += '<thead><tr><th>EAN</th><th>Descrição</th><th>Validade</th><th>Status</th></tr></thead><tbody>';
                
                data.produtos.forEach(p => {
                    let statusClass = '';
                    if (p.status === 'vencido') statusClass = 'table-danger';
                    else if (p.status === 'prestes') statusClass = 'table-warning';
                    else statusClass = 'table-success';
                    
                    html += `<tr class="${statusClass}">`;
                    html += `<td>${p.ean}</td>`;
                    html += `<td>${p.descricao}</td>`;
                    html += `<td>${p.validade}</td>`;
                    html += `<td>${p.dias} dias</td>`;
                    html += '</tr>';
                });
                
                html += '</tbody></table>';
                mostrarResultados('📋 Todos os Produtos', html);
            } else {
                alert('Nenhum produto cadastrado neste setor');
            }
        })
        .catch(error => {
            alert('Erro ao carregar produtos');
            console.error(error);
        });
}

// ============================================
// PRESTES A VENCER
// ============================================

function verPrestes() {
    fetch('/api/produtos/prestes')
        .then(response => response.json())
        .then(data => {
            if (data.prestes && data.prestes.length > 0) {
                let html = `<p>Total: ${data.total} produtos</p>`;
                html += '<table class="table table-warning table-striped">';
                html += '<thead><tr><th><input type="checkbox" id="selecionar-todos" onclick="toggleTodos()"></th><th>EAN</th><th>Descrição</th><th>Validade</th><th>Dias</th><th>Sugestão</th></tr></thead><tbody>';
                
                data.prestes.forEach(p => {
                    html += `<tr>`;
                    html += `<td><input type="checkbox" class="prestes-check" value="${p.ean}"></td>`;
                    html += `<td>${p.ean}</td>`;
                    html += `<td>${p.descricao}</td>`;
                    html += `<td>${p.validade}</td>`;
                    html += `<td>${p.dias}</td>`;
                    html += `<td>${p.desconto} OFF</td>`;
                    html += '</tr>';
                });
                
                html += '</tbody></table>';
                html += '<button class="btn btn-success" onclick="retirarSelecionados()">Retirar Selecionados</button>';
                html += ' <button class="btn btn-warning" onclick="retirarTodos()">Retirar Todos</button>';
                
                mostrarResultados('⚠️ Produtos Prestes a Vencer', html);
            } else {
                alert('Nenhum produto prestes a vencer neste setor');
            }
        })
        .catch(error => {
            alert('Erro ao carregar prestes');
            console.error(error);
        });
}

function toggleTodos() {
    const selecionarTodos = document.getElementById('selecionar-todos').checked;
    const checks = document.querySelectorAll('.prestes-check');
    checks.forEach(c => c.checked = selecionarTodos);
}

function retirarSelecionados() {
    const checks = document.querySelectorAll('.prestes-check:checked');
    if (checks.length === 0) {
        alert('Selecione pelo menos um produto');
        return;
    }
    
    const eans = [];
    checks.forEach(c => eans.push(c.value));
    
    if (confirm(`Retirar ${eans.length} produto(s) da lista de prestes?`)) {
        fetch('/api/produtos/retirar-prestes', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({eans: eans})
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                alert(`${data.quantidade} produto(s) retirado(s) com sucesso!`);
                verPrestes();
            } else {
                alert('Erro ao retirar produtos');
            }
        })
        .catch(error => {
            alert('Erro ao conectar com servidor');
            console.error(error);
        });
    }
}

function retirarTodos() {
    const checks = document.querySelectorAll('.prestes-check');
    if (checks.length === 0) return;
    
    const eans = [];
    checks.forEach(c => eans.push(c.value));
    
    if (confirm(`Retirar TODOS os ${eans.length} produtos da lista de prestes?`)) {
        fetch('/api/produtos/retirar-prestes', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({eans: eans})
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                alert(`${data.quantidade} produto(s) retirado(s) com sucesso!`);
                verPrestes();
            } else {
                alert('Erro ao retirar produtos');
            }
        })
        .catch(error => {
            alert('Erro ao conectar com servidor');
            console.error(error);
        });
    }
}

// ============================================
// PRECIFICAÇÃO
// ============================================

function tirarPreco() {
    fetch('/api/precificacao/eans')
        .then(response => response.json())
        .then(data => {
            if (data.eans && data.eans.length > 0) {
                let html = `<p>Total: ${data.eans.length} EANs únicos</p>`;
                html += '<div class="alert alert-info">';
                html += '<strong>EANs copiados para área de transferência!</strong><br>';
                html += 'Cole no sistema de precificação (Ctrl+V)';
                html += '</div>';
                html += '<textarea class="form-control" rows="10" readonly id="eans-textarea">';
                html += data.eans.join('\n');
                html += '</textarea>';
                html += '<button class="btn btn-primary mt-2" onclick="copiarEans()">Copiar EANs</button>';
                
                mostrarResultados('💰 EANs para Precificação', html);
                copiarEans();
            } else {
                alert('Nenhum EAN disponível para precificação');
            }
        })
        .catch(error => {
            alert('Erro ao carregar EANs');
            console.error(error);
        });
}

function copiarEans() {
    const textarea = document.getElementById('eans-textarea');
    textarea.select();
    document.execCommand('copy');
    alert('EANs copiados para área de transferência!');
}

// ============================================
// CADASTRO DE PRODUTOS
// ============================================

function buscarProduto() {
    const ean = document.getElementById('ean-input').value.trim();
    if (!ean) {
        alert('Digite um EAN');
        return;
    }
    
    fetch('/api/produtos/buscar/' + ean)
        .then(response => response.json())
        .then(data => {
            const descricaoInfo = document.getElementById('descricao-info');
            const descricaoTexto = document.getElementById('descricao-texto');
            const descricaoInput = document.getElementById('descricao-input');
            
            if (data.encontrado) {
                descricaoTexto.innerHTML = `✅ Encontrado: ${data.descricao} (fonte: ${data.fonte})`;
                descricaoInfo.style.display = 'block';
                descricaoInput.value = data.descricao;
            } else {
                descricaoTexto.innerHTML = '❌ Produto não encontrado. Digite a descrição manualmente.';
                descricaoInfo.style.display = 'block';
                descricaoInput.value = '';
                descricaoInput.focus();
            }
        })
        .catch(error => {
            alert('Erro ao buscar produto');
            console.error(error);
        });
}

function salvarProduto() {
    const ean = document.getElementById('ean-input').value.trim();
    const descricao = document.getElementById('descricao-input').value.trim();
    const mes = document.getElementById('mes-select').value;
    const ano = document.getElementById('ano-select').value;
    
    if (!ean || !descricao) {
        alert('Preencha EAN e descrição');
        return;
    }
    
    fetch('/api/produtos/adicionar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ean, descricao, mes, ano})
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            alert('✅ Produto cadastrado com sucesso!');
            document.getElementById('ean-input').value = '';
            document.getElementById('descricao-input').value = '';
            document.getElementById('descricao-info').style.display = 'none';
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalCadastro'));
            modal.hide();
        } else {
            alert('Erro ao cadastrar: ' + (data.erro || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        alert('Erro ao conectar com servidor');
        console.error(error);
    });
}

// ============================================
// PESQUISA POR DATA
// ============================================

function pesquisarPeriodo() {
    const dataInicial = document.getElementById('data-inicial').value;
    const dataFinal = document.getElementById('data-final').value;
    
    if (!dataInicial && !dataFinal) {
        alert('Selecione pelo menos uma data');
        return;
    }
    
    fetch('/api/produtos/pesquisar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({data_inicial: dataInicial, data_final: dataFinal})
    })
    .then(response => response.json())
    .then(data => {
        if (data.resultados && data.resultados.length > 0) {
            let periodo = '';
            if (dataInicial && dataFinal) {
                periodo = `de ${formatarData(dataInicial)} a ${formatarData(dataFinal)}`;
            } else if (dataInicial) {
                periodo = `a partir de ${formatarData(dataInicial)}`;
            } else {
                periodo = `até ${formatarData(dataFinal)}`;
            }
            
            let html = `<p>Total: ${data.resultados.length} produtos encontrados ${periodo}</p>`;
            html += '<table class="table table-striped">';
            html += '<thead><tr><th>EAN</th><th>Descrição</th><th>Validade</th><th>Cadastro</th></tr></thead><tbody>';
            
            data.resultados.forEach(p => {
                html += `<tr>`;
                html += `<td>${p.ean}</td>`;
                html += `<td>${p.descricao}</td>`;
                html += `<td>${p.validade}</td>`;
                html += `<td>${p.data_cadastro}</td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            html += '<button class="btn btn-primary" onclick="copiarEansPesquisa()">Copiar EANs</button>';
            
            window.resultadosPesquisa = data.resultados;
            mostrarResultados('📅 Resultado da Pesquisa', html);
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalPesquisa'));
            modal.hide();
        } else {
            alert('Nenhum produto encontrado neste período');
        }
    })
    .catch(error => {
        alert('Erro ao pesquisar');
        console.error(error);
    });
}

function pesquisarHoje() {
    const hoje = new Date().toISOString().split('T')[0];
    document.getElementById('data-inicial').value = hoje;
    document.getElementById('data-final').value = hoje;
    pesquisarPeriodo();
}

function pesquisarSemana() {
    const hoje = new Date();
    const semana = new Date();
    semana.setDate(hoje.getDate() - 7);
    
    document.getElementById('data-inicial').value = semana.toISOString().split('T')[0];
    document.getElementById('data-final').value = hoje.toISOString().split('T')[0];
    pesquisarPeriodo();
}

function pesquisarMes() {
    const hoje = new Date();
    const mes = new Date();
    mes.setDate(hoje.getDate() - 30);
    
    document.getElementById('data-inicial').value = mes.toISOString().split('T')[0];
    document.getElementById('data-final').value = hoje.toISOString().split('T')[0];
    pesquisarPeriodo();
}

function formatarData(dataStr) {
    if (!dataStr) return '';
    const partes = dataStr.split('-');
    return `${partes[2]}/${partes[1]}/${partes[0]}`;
}

function copiarEansPesquisa() {
    if (!window.resultadosPesquisa || window.resultadosPesquisa.length === 0) return;
    
    const eans = window.resultadosPesquisa.map(p => p.ean);
    const texto = eans.join('\n');
    
    const textarea = document.createElement('textarea');
    textarea.value = texto;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    
    alert(`${eans.length} EANs copiados para área de transferência!`);
}