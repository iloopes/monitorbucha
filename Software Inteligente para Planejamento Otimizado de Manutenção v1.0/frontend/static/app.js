// API Base URL
const API_URL = 'http://localhost:8000/api';

// Verificar status da API ao carregar
document.addEventListener('DOMContentLoaded', () => {
    checkAPIStatus();
    setupEventListeners();
    loadEquipmentList();
});

function setupEventListeners() {
    // Formulário de configuração do banco
    document.getElementById('db-config-form').addEventListener('submit', configureDatabaseHandler);

    // Botão de inicializar banco
    document.getElementById('init-db-btn').addEventListener('click', initializeDatabaseHandler);

    // Formulário de geração de dados
    document.getElementById('generate-form').addEventListener('submit', generateDataHandler);

    // Formulário de otimização
    document.getElementById('optimize-form').addEventListener('submit', runOptimizationHandler);

    // Toggle de credenciais do banco
    document.getElementById('trusted-connection').addEventListener('change', (e) => {
        document.getElementById('credentials').style.display = e.target.checked ? 'none' : 'block';
    });
}

async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            document.getElementById('status-dot').className = 'status-indicator online';
            document.getElementById('status-text').textContent = `Sistema Online - v${data.version}`;
        }
    } catch (error) {
        document.getElementById('status-dot').className = 'status-indicator offline';
        document.getElementById('status-text').textContent = 'Sistema Offline - Verifique se a API está rodando';
        console.error('Erro ao verificar status da API:', error);
    }
}

async function configureDatabaseHandler(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const config = {
        server: formData.get('server'),
        database: formData.get('database'),
        trusted_connection: document.getElementById('trusted-connection').checked,
        username: formData.get('username') || null,
        password: formData.get('password') || null
    };

    showMessage('db-status', 'Conectando ao banco de dados...', 'info');

    try {
        const response = await fetch(`${API_URL}/database/configure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('db-status', `✓ ${data.message} (${data.server}/${data.database})`, 'success');
        } else {
            showMessage('db-status', `✗ Erro: ${data.detail}`, 'error');
        }
    } catch (error) {
        showMessage('db-status', `✗ Erro ao conectar: ${error.message}`, 'error');
    }
}

async function initializeDatabaseHandler() {
    showMessage('db-status', 'Criando tabelas no banco de dados...', 'info');

    try {
        const response = await fetch(`${API_URL}/database/init`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('db-status', `✓ ${data.message}\nTabelas: ${data.tables.join(', ')}`, 'success');
        } else {
            showMessage('db-status', `✗ Erro: ${data.detail}`, 'error');
        }
    } catch (error) {
        showMessage('db-status', `✗ Erro ao criar tabelas: ${error.message}`, 'error');
    }
}

async function generateDataHandler(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const request = {
        n_bushings: parseInt(formData.get('n_bushings')),
        days: parseInt(formData.get('days')),
        frequency_hours: parseInt(formData.get('frequency_hours')),
        degradation_rate: formData.get('degradation_rate'),
        save_to_database: document.getElementById('save-db').checked,
        scenario_name: formData.get('scenario_name') || null
    };

    showMessage('generate-status', 'Gerando dados... Por favor aguarde.', 'info');

    try {
        const response = await fetch(`${API_URL}/data/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('generate-status', `✓ Dados gerados com sucesso!`, 'success');
            displayResults(data);
        } else {
            showMessage('generate-status', `✗ Erro: ${data.detail}`, 'error');
        }
    } catch (error) {
        showMessage('generate-status', `✗ Erro ao gerar dados: ${error.message}`, 'error');
    }
}

function displayResults(data) {
    const resultsCard = document.getElementById('results-card');
    const resultsContent = document.getElementById('results-content');

    let html = `
        <div class="results-stats">
            <h3>📊 Estatísticas</h3>
            <ul>
                <li><strong>Cenário:</strong> ${data.scenario_name}</li>
                <li><strong>Número de Buchas:</strong> ${data.statistics.n_bushings}</li>
                <li><strong>Período:</strong> ${data.statistics.days} dias</li>
                <li><strong>Registros de Sensores:</strong> ${data.statistics.sensor_records}</li>
                <li><strong>Ordens de Serviço:</strong> ${data.statistics.maintenance_orders}</li>
                <li><strong>Data Inicial:</strong> ${new Date(data.statistics.date_range.start).toLocaleString('pt-BR')}</li>
                <li><strong>Data Final:</strong> ${new Date(data.statistics.date_range.end).toLocaleString('pt-BR')}</li>
            </ul>
        </div>
    `;

    if (data.database) {
        html += `
            <div class="database-status">
                <h3>💾 Status do Banco de Dados</h3>
                <ul>
                    <li><strong>Status:</strong> ${data.database.status}</li>
        `;

        if (data.database.status === 'success') {
            html += `
                    <li><strong>Sensores Inseridos:</strong> ${data.database.sensor_records_inserted}</li>
                    <li><strong>OS Inseridas:</strong> ${data.database.orders_inserted}</li>
            `;
        } else if (data.database.error) {
            html += `
                    <li><strong>Erro:</strong> ${data.database.error}</li>
            `;
        }

        html += `
                </ul>
            </div>
        `;
    }

    resultsContent.innerHTML = html;
    resultsCard.style.display = 'block';
}

async function viewSensorData() {
    const viewDiv = document.getElementById('view-results');
    viewDiv.innerHTML = '<p>Carregando dados...</p>';

    try {
        const response = await fetch(`${API_URL}/data/sensor?limit=50`);
        const data = await response.json();

        if (response.ok && data.data.length > 0) {
            let html = `
                <h3>Dados de Sensores (últimos 50 registros)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Equipamento</th>
                            <th>Corrente (mA)</th>
                            <th>TG Delta (%)</th>
                            <th>Capacitância (pF)</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.data.forEach(row => {
                html += `
                    <tr>
                        <td>${new Date(row.timestamp).toLocaleString('pt-BR')}</td>
                        <td>${row.equipment_id}</td>
                        <td>${row.corrente_fuga.toFixed(4)}</td>
                        <td>${row.tg_delta.toFixed(4)}</td>
                        <td>${row.capacitancia.toFixed(2)}</td>
                        <td>${getStateName(row.estado_saude)}</td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            viewDiv.innerHTML = html;
        } else {
            viewDiv.innerHTML = '<p>Nenhum dado encontrado. Gere dados primeiro.</p>';
        }
    } catch (error) {
        viewDiv.innerHTML = `<p class="error">Erro ao carregar dados: ${error.message}</p>`;
    }
}

async function viewMaintenanceOrders() {
    const viewDiv = document.getElementById('view-results');
    viewDiv.innerHTML = '<p>Carregando ordens...</p>';

    try {
        const response = await fetch(`${API_URL}/data/orders`);
        const data = await response.json();

        if (response.ok && data.orders.length > 0) {
            let html = `
                <h3>Ordens de Serviço (${data.count} registros)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>OS ID</th>
                            <th>Equipamento</th>
                            <th>Localização</th>
                            <th>Estado</th>
                            <th>Data Medição</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.orders.forEach(order => {
                html += `
                    <tr>
                        <td>${order.os_id}</td>
                        <td>${order.equipment_id}</td>
                        <td>${order.localizacao}</td>
                        <td>${getStateName(order.mf_dga)}</td>
                        <td>${new Date(order.mf_dga_data).toLocaleString('pt-BR')}</td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            viewDiv.innerHTML = html;
        } else {
            viewDiv.innerHTML = '<p>Nenhuma ordem encontrada. Gere dados primeiro.</p>';
        }
    } catch (error) {
        viewDiv.innerHTML = `<p class="error">Erro ao carregar ordens: ${error.message}</p>`;
    }
}

function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `result-message ${type}`;
}

function getStateName(state) {
    const states = {
        0: 'Normal',
        1: 'Degradado 1',
        2: 'Degradado 2',
        3: 'Degradado 3',
        4: 'Falha'
    };
    return states[state] || 'Desconhecido';
}

// ========== OTIMIZAÇÃO E CALENDÁRIO ==========

async function loadEquipmentList() {
    try {
        const response = await fetch(`${API_URL}/equipment/list`);

        // Verificar se houve erro de banco não configurado
        if (!response.ok) {
            const errorData = await response.json();

            // Se o banco não está configurado, mostrar mensagem específica
            if (errorData.detail && errorData.detail.includes("não configurado")) {
                showMessage('optimize-status',
                    '⚠️ Conecte ao banco de dados primeiro! Use a seção "Configuração do Banco de Dados" acima.',
                    'info');
                return;
            }

            // Outro tipo de erro
            showMessage('optimize-status', `Erro: ${errorData.detail || response.statusText}`, 'error');
            return;
        }

        const data = await response.json();
        const select = document.getElementById('equipment-select');

        if (data.equipment && data.equipment.length > 0) {
            // Limpar opções existentes (exceto "Todos")
            select.innerHTML = '<option value="all">🔄 Todos os Equipamentos</option>';

            // Adicionar cada equipamento
            data.equipment.forEach(eq => {
                const option = document.createElement('option');
                option.value = eq.equipment_id;
                option.textContent = `${eq.equipment_id} (${eq.localizacao})`;
                select.appendChild(option);
            });

            showMessage('optimize-status', `✓ ${data.count} equipamentos carregados`, 'success');
        } else {
            showMessage('optimize-status', 'Nenhum equipamento encontrado. Gere dados primeiro usando a seção "Geração de Dados".', 'info');
        }
    } catch (error) {
        showMessage('optimize-status', `Erro ao carregar equipamentos: ${error.message}`, 'error');
    }
}

async function runOptimizationHandler(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const selectedEquipment = document.getElementById('equipment-select').value;

    const request = {
        max_evaluations: parseInt(formData.get('max_evaluations')),
        population_size: parseInt(formData.get('population_size')),
        save_to_database: document.getElementById('save-optimization').checked,
        equipment_ids: selectedEquipment === 'all' ? null : [selectedEquipment]
    };

    showMessage('optimize-status', '⚙️ Executando algoritmos de otimização (Markov + NSGA-II)... Isso pode levar alguns minutos.', 'info');

    try {
        const response = await fetch(`${API_URL}/optimize/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        const data = await response.json();

        if (response.ok) {
            // Criar resumo dos resultados
            const summary = `
                ✓ Otimização concluída com sucesso!

                📊 Resumo:
                - Equipamentos otimizados: ${data.summary.total_optimized}
                - Custo médio: R$ ${data.summary.avg_cost.toFixed(2)}
                - Indisponibilidade média: ${data.summary.avg_unavailability.toFixed(4)}
                - Pontos do Pareto: ${data.summary.total_pareto_points}
            `;
            showMessage('optimize-status', summary, 'success');

            // Exibir resultados detalhados
            displayOptimizationResults(data.results);

            // Exibir calendário com os resultados (mesmo que não salvos no banco)
            displayCalendarFromResults(data.results);
        } else {
            showMessage('optimize-status', `✗ Erro: ${data.detail || data.message}`, 'error');
        }
    } catch (error) {
        showMessage('optimize-status', `✗ Erro ao executar otimização: ${error.message}`, 'error');
    }
}

function displayOptimizationResults(results) {
    if (!results || results.length === 0) return;

    const resultsCard = document.getElementById('results-card');
    const resultsContent = document.getElementById('results-content');

    let html = `
        <div class="summary-stats">
            <div class="stat-box">
                <div class="stat-value">${results.length}</div>
                <div class="stat-label">Equipamentos Otimizados</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${results.filter(r => r.prioridade >= 3).length}</div>
                <div class="stat-label">Alta Prioridade</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${Math.round(results.reduce((sum, r) => sum + r.t_days, 0) / results.length)}</div>
                <div class="stat-label">Dias Médios até Manutenção</div>
            </div>
        </div>

        <h3 style="margin-top: 30px;">Top 10 Equipamentos por Prioridade</h3>
        <table>
            <thead>
                <tr>
                    <th>Equipamento</th>
                    <th>Localização</th>
                    <th>Estado</th>
                    <th>Data Ótima</th>
                    <th>Custo</th>
                    <th>Prioridade</th>
                </tr>
            </thead>
            <tbody>
    `;

    results.slice(0, 10).forEach(result => {
        html += `
            <tr>
                <td><strong>${result.equipment_id}</strong></td>
                <td>${result.localizacao}</td>
                <td>${getStateName(result.estado_atual)}</td>
                <td>${new Date(result.data_otima).toLocaleDateString('pt-BR')}</td>
                <td>R$ ${result.custo.toFixed(2)}</td>
                <td><span class="urgencia-badge ${result.prioridade >= 3 ? 'urgente' : 'programada'}">${result.prioridade}</span></td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    resultsContent.innerHTML = html;
    resultsCard.style.display = 'block';
}

async function loadMaintenanceCalendar() {
    const calendarContent = document.getElementById('calendar-content');
    calendarContent.innerHTML = '<p class="info-text">Carregando calendário...</p>';

    try {
        const response = await fetch(`${API_URL}/calendar`);
        const data = await response.json();

        if (response.ok && data.calendar && data.calendar.length > 0) {
            let html = `
                <div style="margin-bottom: 20px;">
                    <h3>${data.total} Manutenções Programadas</h3>
                    <p style="color: #6b7280;">Calendário ordenado por prioridade e data</p>
                </div>
            `;

            data.calendar.forEach(item => {
                const dataFormatada = new Date(item.data_otima).toLocaleDateString('pt-BR', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });

                html += `
                    <div class="calendar-item ${item.urgencia}">
                        <div class="calendar-item-header">
                            <div>
                                <div class="calendar-equipment">${item.equipment_id}</div>
                                <div>${item.localizacao}</div>
                            </div>
                            <div>
                                <span class="urgencia-badge ${item.urgencia}">${item.urgencia}</span>
                            </div>
                        </div>
                        <div class="calendar-details">
                            <div class="calendar-detail">
                                <strong>📅 Data:</strong> ${dataFormatada}
                            </div>
                            <div class="calendar-detail">
                                <strong>⏱️ Dias:</strong> ${item.dias_ate_manutencao} dias ${item.dias_ate_manutencao < 0 ? '(ATRASADO)' : ''}
                            </div>
                            <div class="calendar-detail">
                                <strong>🔧 Estado:</strong> ${getStateName(item.estado_atual)}
                            </div>
                            <div class="calendar-detail">
                                <strong>💰 Custo:</strong> R$ ${item.custo ? item.custo.toFixed(2) : 'N/A'}
                            </div>
                            <div class="calendar-detail">
                                <strong>⚠️ Prioridade:</strong> ${item.prioridade}
                            </div>
                            <div class="calendar-detail">
                                <strong>📊 Indisponibilidade:</strong> ${item.indisponibilidade ? item.indisponibilidade.toFixed(4) : 'N/A'}
                            </div>
                        </div>
                    </div>
                `;
            });

            calendarContent.innerHTML = html;
        } else {
            calendarContent.innerHTML = '<p class="info-text">Nenhuma manutenção programada. Execute a otimização primeiro.</p>';
        }
    } catch (error) {
        calendarContent.innerHTML = `<p class="info-text" style="color: #ef4444;">Erro ao carregar calendário: ${error.message}</p>`;
    }
}

function displayCalendarFromResults(results) {
    if (!results || results.length === 0) return;

    const calendarContent = document.getElementById('calendar-content');

    // Ordenar por prioridade e data
    const sortedResults = [...results].sort((a, b) => {
        if (b.prioridade !== a.prioridade) {
            return b.prioridade - a.prioridade;
        }
        return new Date(a.data_otima) - new Date(b.data_otima);
    });

    let html = `
        <div style="margin-bottom: 20px;">
            <h3>${results.length} Manutenções Programadas</h3>
            <p style="color: #6b7280;">Calendário ordenado por prioridade e data (resultados da última otimização)</p>
        </div>
    `;

    sortedResults.forEach(item => {
        const dataOtima = new Date(item.data_otima);
        const hoje = new Date();
        const diasAteManutencao = Math.ceil((dataOtima - hoje) / (1000 * 60 * 60 * 24));

        // Determinar urgência
        let urgencia = 'programada';
        if (diasAteManutencao < 0) {
            urgencia = 'atrasado';
        } else if (diasAteManutencao <= 7) {
            urgencia = 'urgente';
        } else if (diasAteManutencao <= 30) {
            urgencia = 'proxima';
        }

        const dataFormatada = dataOtima.toLocaleDateString('pt-BR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        html += `
            <div class="calendar-item ${urgencia}">
                <div class="calendar-item-header">
                    <div>
                        <div class="calendar-equipment">${item.equipment_id}</div>
                        <div>${item.localizacao}</div>
                    </div>
                    <div>
                        <span class="urgencia-badge ${urgencia}">${urgencia}</span>
                    </div>
                </div>
                <div class="calendar-details">
                    <div class="calendar-detail">
                        <strong>📅 Data:</strong> ${dataFormatada}
                    </div>
                    <div class="calendar-detail">
                        <strong>⏱️ Dias:</strong> ${diasAteManutencao} dias ${diasAteManutencao < 0 ? '(ATRASADO)' : ''}
                    </div>
                    <div class="calendar-detail">
                        <strong>🔧 Estado:</strong> ${getStateName(item.estado_atual)}
                    </div>
                    <div class="calendar-detail">
                        <strong>💰 Custo:</strong> R$ ${item.custo ? item.custo.toFixed(2) : 'N/A'}
                    </div>
                    <div class="calendar-detail">
                        <strong>⚠️ Prioridade:</strong> ${item.prioridade}
                    </div>
                    <div class="calendar-detail">
                        <strong>📊 Indisponibilidade:</strong> ${item.indisponibilidade ? item.indisponibilidade.toFixed(4) : 'N/A'}
                    </div>
                </div>
            </div>
        `;
    });

    calendarContent.innerHTML = html;
}

let paretoChart = null; // Global para controlar o gráfico

async function viewParetoFront() {
    const viewDiv = document.getElementById('view-results');

    // Solicitar ID do equipamento
    const equipmentId = prompt('Digite o ID do equipamento (ex: SPGR.ATF1):');
    if (!equipmentId) return;

    viewDiv.innerHTML = '<p>Carregando fronteira de Pareto...</p>';

    try {
        const response = await fetch(`${API_URL}/pareto/${equipmentId}`);
        const data = await response.json();

        if (response.ok && data.pareto_points && data.pareto_points.length > 0) {
            // Destruir gráfico anterior se existir
            if (paretoChart) {
                paretoChart.destroy();
            }

            // Criar visualização com gráfico
            let html = `
                <h3>Fronteira de Pareto - ${equipmentId}</h3>
                <p style="margin-bottom: 20px; color: #6b7280;">
                    ${data.pareto_points.length} soluções ótimas encontradas
                </p>

                <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <canvas id="paretoChart"></canvas>
                </div>

                <div style="margin-top: 20px; padding: 15px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #3b82f6;">
                    <strong>💡 Interpretação:</strong>
                    <p style="margin-top: 10px; color: #1e40af;">
                        A Fronteira de Pareto mostra o trade-off entre custo e indisponibilidade.
                        Cada ponto representa uma solução ótima onde não é possível melhorar um objetivo sem piorar o outro.
                        Soluções à esquerda têm menor custo mas maior indisponibilidade.
                    </p>
                </div>

                <h4 style="margin-top: 30px; margin-bottom: 15px;">📋 Detalhes das Soluções</h4>
                <table>
                    <thead>
                        <tr>
                            <th>Tempo (dias)</th>
                            <th>Custo (R$)</th>
                            <th>Indisponibilidade</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.pareto_points.forEach(point => {
                html += `
                    <tr>
                        <td>${point.t_days}</td>
                        <td>R$ ${point.custo.toFixed(2)}</td>
                        <td>${point.indisponibilidade.toFixed(6)}</td>
                    </tr>
                `;
            });

            html += '</tbody></table>';

            viewDiv.innerHTML = html;

            // Criar gráfico
            const ctx = document.getElementById('paretoChart').getContext('2d');

            paretoChart = new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Fronteira de Pareto',
                        data: data.pareto_points.map(p => ({
                            x: p.custo,
                            y: p.indisponibilidade
                        })),
                        backgroundColor: 'rgba(102, 126, 234, 0.6)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Trade-off: Custo vs Indisponibilidade',
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        },
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const point = data.pareto_points[context.dataIndex];
                                    return [
                                        `Tempo: ${point.t_days} dias`,
                                        `Custo: R$ ${point.custo.toFixed(2)}`,
                                        `Indisponibilidade: ${point.indisponibilidade.toFixed(6)}`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Custo (R$)',
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                }
                            },
                            ticks: {
                                callback: function(value) {
                                    return 'R$ ' + value.toFixed(2);
                                }
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Indisponibilidade',
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                }
                            },
                            ticks: {
                                callback: function(value) {
                                    return value.toFixed(6);
                                }
                            }
                        }
                    }
                }
            });
        } else {
            viewDiv.innerHTML = `<p class="info-text" style="color: #ef4444;">${data.message || 'Equipamento não encontrado'}</p>`;
        }
    } catch (error) {
        viewDiv.innerHTML = `<p class="error">Erro ao carregar Pareto: ${error.message}</p>`;
    }
}
