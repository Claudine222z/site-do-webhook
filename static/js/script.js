// Função para copiar texto para clipboard
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copiado para a área de transferência!', 'success');
        }).catch(err => {
            console.error('Erro ao copiar:', err);
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

// Fallback para navegadores mais antigos
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";
    textArea.style.opacity = "0";
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showToast('Copiado para a área de transferência!', 'success');
        } else {
            showToast('Erro ao copiar texto', 'error');
        }
    } catch (err) {
        console.error('Fallback: Erro ao copiar:', err);
        showToast('Erro ao copiar texto', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Função para mostrar toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Adicionar estilos do toast se não existirem
    if (!document.querySelector('#toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .toast {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 9999;
                display: flex;
                align-items: center;
                gap: 1rem;
                min-width: 300px;
                animation: slideInRight 0.3s ease-out;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            
            .toast-success {
                background: #48bb78;
            }
            
            .toast-error {
                background: #f56565;
            }
            
            .toast-info {
                background: #4299e1;
            }
            
            .toast-content {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                flex: 1;
            }
            
            .toast-close {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                opacity: 0.8;
                transition: opacity 0.2s;
            }
            
            .toast-close:hover {
                opacity: 1;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @media (max-width: 480px) {
                .toast {
                    right: 10px;
                    left: 10px;
                    min-width: auto;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    // Auto remove após 5 segundos
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'slideInRight 0.3s ease-out reverse';
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }
    }, 5000);
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Função para mostrar dados do log no modal
function showLogData(data) {
    const modal = document.getElementById('logModal');
    const logDataElement = document.getElementById('logData');
    
    try {
        // Tentar formatar como JSON se possível
        const parsedData = JSON.parse(data);
        logDataElement.textContent = JSON.stringify(parsedData, null, 2);
    } catch (e) {
        // Se não for JSON válido, mostrar como texto
        logDataElement.textContent = data;
    }
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Função para fechar modal
function closeLogModal() {
    const modal = document.getElementById('logModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Fechar modal ao clicar fora dele
    const modal = document.getElementById('logModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeLogModal();
            }
        });
    }
    
    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal && modal.style.display === 'block') {
            closeLogModal();
        }
    });
    
    // Auto-hide alerts após 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.animation = 'slideIn 0.3s ease-out reverse';
                setTimeout(() => {
                    if (alert.parentElement) {
                        alert.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
    
    // Adicionar loading state aos formulários
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    });
    
    // Validação em tempo real do nome do webhook
    const webhookNameInput = document.getElementById('name');
    if (webhookNameInput) {
        webhookNameInput.addEventListener('input', function() {
            const value = this.value;
            const isValid = /^[a-zA-Z0-9_]*$/.test(value);
            
            if (!isValid && value.length > 0) {
                this.style.borderColor = '#f56565';
                showValidationMessage(this, 'Apenas letras, números e underscore são permitidos');
            } else {
                this.style.borderColor = '#e2e8f0';
                hideValidationMessage(this);
            }
        });
    }
});

// Função para mostrar mensagem de validação
function showValidationMessage(input, message) {
    hideValidationMessage(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'validation-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        color: #f56565;
        font-size: 0.875rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    `;
    
    const icon = document.createElement('i');
    icon.className = 'fas fa-exclamation-circle';
    errorDiv.insertBefore(icon, errorDiv.firstChild);
    
    input.parentElement.appendChild(errorDiv);
}

// Função para esconder mensagem de validação
function hideValidationMessage(input) {
    const existingError = input.parentElement.querySelector('.validation-error');
    if (existingError) {
        existingError.remove();
    }
}

// Função para atualizar estatísticas em tempo real (opcional)
function updateWebhookStats() {
    fetch('/api/webhooks')
        .then(response => response.json())
        .then(data => {
            data.forEach(webhook => {
                const webhookCard = document.querySelector(`[data-webhook-id="${webhook.id}"]`);
                if (webhookCard) {
                    // Atualizar contador de requisições
                    const requestCount = webhookCard.querySelector('.request-count');
                    if (requestCount) {
                        requestCount.textContent = `${webhook.request_count} requisições`;
                    }
                    
                    // Atualizar última requisição
                    const lastRequest = webhookCard.querySelector('.last-request');
                    if (lastRequest && webhook.last_request) {
                        const date = new Date(webhook.last_request);
                        lastRequest.textContent = `Última: ${date.toLocaleDateString('pt-BR')} às ${date.toLocaleTimeString('pt-BR')}`;
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erro ao atualizar estatísticas:', error);
        });
}

// Atualizar estatísticas a cada 30 segundos (opcional)
// setInterval(updateWebhookStats, 30000);

// Função para testar webhook
function testWebhook(webhookName, token) {
    const testData = {
        test: true,
        message: "Teste do webhook",
        timestamp: new Date().toISOString()
    };
    
    fetch(`/webhook/${webhookName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(testData)
    })
    .then(response => response.json())
    .then(data => {
        showToast('Webhook testado com sucesso!', 'success');
        console.log('Resposta do webhook:', data);
    })
    .catch(error => {
        showToast('Erro ao testar webhook', 'error');
        console.error('Erro:', error);
    });
}

// Função para exportar configurações dos webhooks
function exportWebhooks() {
    fetch('/api/webhooks')
        .then(response => response.json())
        .then(data => {
            const exportData = {
                export_date: new Date().toISOString(),
                webhooks: data.map(webhook => ({
                    name: webhook.name,
                    endpoint: webhook.endpoint,
                    created_at: webhook.created_at,
                    is_active: webhook.is_active
                }))
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                type: 'application/json'
            });
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `webhooks_export_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showToast('Configurações exportadas com sucesso!', 'success');
        })
        .catch(error => {
            showToast('Erro ao exportar configurações', 'error');
            console.error('Erro:', error);
        });
}

// Função para filtrar webhooks
function filterWebhooks(searchTerm) {
    const webhookCards = document.querySelectorAll('.webhook-card');
    const searchLower = searchTerm.toLowerCase();
    
    webhookCards.forEach(card => {
        const webhookName = card.querySelector('.webhook-name span').textContent.toLowerCase();
        const shouldShow = webhookName.includes(searchLower);
        
        card.style.display = shouldShow ? 'block' : 'none';
    });
    
    // Mostrar mensagem se nenhum resultado for encontrado
    const visibleCards = Array.from(webhookCards).filter(card => card.style.display !== 'none');
    const noResultsMsg = document.querySelector('.no-results-message');
    
    if (visibleCards.length === 0 && searchTerm.trim() !== '') {
        if (!noResultsMsg) {
            const message = document.createElement('div');
            message.className = 'no-results-message empty-state';
            message.innerHTML = `
                <div class="empty-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h3>Nenhum webhook encontrado</h3>
                <p>Tente usar outros termos de busca</p>
            `;
            document.querySelector('.webhooks-grid').appendChild(message);
        }
    } else if (noResultsMsg) {
        noResultsMsg.remove();
    }
}

// Função para ordenar webhooks
function sortWebhooks(criteria) {
    const webhooksGrid = document.querySelector('.webhooks-grid');
    const webhookCards = Array.from(webhooksGrid.querySelectorAll('.webhook-card'));
    
    webhookCards.sort((a, b) => {
        switch (criteria) {
            case 'name':
                const nameA = a.querySelector('.webhook-name span').textContent;
                const nameB = b.querySelector('.webhook-name span').textContent;
                return nameA.localeCompare(nameB);
                
            case 'created':
                const dateA = new Date(a.dataset.created || 0);
                const dateB = new Date(b.dataset.created || 0);
                return dateB - dateA;
                
            case 'requests':
                const requestsA = parseInt(a.querySelector('.request-count')?.textContent || '0');
                const requestsB = parseInt(b.querySelector('.request-count')?.textContent || '0');
                return requestsB - requestsA;
                
            default:
                return 0;
        }
    });
    
    // Reordenar no DOM
    webhookCards.forEach(card => webhooksGrid.appendChild(card));
}

// Função para toggle do tema escuro (opcional)
function toggleDarkMode() {
    const body = document.body;
    const isDark = body.classList.toggle('dark-mode');
    
    localStorage.setItem('darkMode', isDark);
    
// Adicionar estilos do tema escuro se não existirem
    if (!document.querySelector('#dark-mode-styles')) {
        const style = document.createElement('style');
        style.id = 'dark-mode-styles';
        style.textContent = `
            .dark-mode {
                --text-color: #e2e8f0;
                --text-muted: #a0aec0;
                --light-color: #2d3748;
                --border-color: #4a5568;
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
            }
            
            .dark-mode .card,
            .dark-mode .webhook-card {
                background: #1a202c;
                color: var(--text-color);
            }
            
            .dark-mode .card-header,
            .dark-mode .webhook-header,
            .dark-mode .webhook-actions {
                background: #2d3748;
                border-color: var(--border-color);
            }
            
            .dark-mode .navbar {
                background: rgba(26, 32, 44, 0.95);
            }
            
            .dark-mode .form-group input {
                background: #2d3748;
                color: var(--text-color);
                border-color: var(--border-color);
            }
            
            .dark-mode .endpoint-url,
            .dark-mode .token-field {
                background: #2d3748;
                border-color: var(--border-color);
            }
            
            .dark-mode .logs-table th {
                background: #2d3748;
                color: var(--text-color);
            }
            
            .dark-mode .logs-table tr:hover {
                background: #2d3748;
            }
        `;
        document.head.appendChild(style);
    }
    
    showToast(`Tema ${isDark ? 'escuro' : 'claro'} ativado`, 'info');
}

// Carregar preferência do tema escuro
document.addEventListener('DOMContentLoaded', function() {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        toggleDarkMode();
    }
});

// Função para confirmar ações perigosas
function confirmAction(message, callback) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 400px;">
            <div class="modal-header">
                <h4><i class="fas fa-exclamation-triangle" style="color: #ed8936;"></i> Confirmação</h4>
            </div>
            <div class="modal-body">
                <p>${message}</p>
                <div style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem;">
                    <button class="btn btn-outline" onclick="closeConfirmModal()">Cancelar</button>
                    <button class="btn btn-danger" onclick="confirmAndClose()">Confirmar</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
    
    window.closeConfirmModal = function() {
        modal.remove();
        document.body.style.overflow = 'auto';
    };
    
    window.confirmAndClose = function() {
        callback();
        closeConfirmModal();
    };
    
    // Fechar com ESC
    const escHandler = function(e) {
        if (e.key === 'Escape') {
            closeConfirmModal();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

// Função para mostrar detalhes rápidos do webhook
function showQuickDetails(webhookId) {
    fetch(`/api/webhooks/${webhookId}`)
        .then(response => response.json())
        .then(webhook => {
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h4><i class="fas fa-robot"></i> ${webhook.name}</h4>
                        <button class="modal-close" onclick="this.closest('.modal').remove(); document.body.style.overflow = 'auto';">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="info-grid">
                            <div class="info-item">
                                <label>Status:</label>
                                <span class="status-badge ${webhook.is_active ? 'active' : 'inactive'}">
                                    ${webhook.is_active ? 'Ativo' : 'Inativo'}
                                </span>
                            </div>
                            <div class="info-item">
                                <label>Endpoint:</label>
                                <code>${webhook.endpoint}</code>
                            </div>
                            <div class="info-item">
                                <label>Requisições:</label>
                                <span class="stat-number">${webhook.request_count}</span>
                            </div>
                            <div class="info-item">
                                <label>Criado em:</label>
                                <span>${new Date(webhook.created_at).toLocaleDateString('pt-BR')}</span>
                            </div>
                        </div>
                        <div style="margin-top: 1.5rem; display: flex; gap: 0.5rem;">
                            <button class="btn btn-primary" onclick="testWebhook('${webhook.name}', '${webhook.token}')">
                                <i class="fas fa-play"></i> Testar
                            </button>
                            <button class="btn btn-info" onclick="window.location.href='/webhook_details/${webhook.id}'">
                                <i class="fas fa-eye"></i> Ver Detalhes
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            document.body.style.overflow = 'hidden';
        })
        .catch(error => {
            showToast('Erro ao carregar detalhes do webhook', 'error');
            console.error('Erro:', error);
        });
}

// Adicionar funcionalidades de acessibilidade
document.addEventListener('keydown', function(e) {
    // Navegação por teclado nos cards de webhook
    if (e.key === 'Tab') {
        const webhookCards = document.querySelectorAll('.webhook-card');
        webhookCards.forEach(card => {
            if (!card.hasAttribute('tabindex')) {
                card.setAttribute('tabindex', '0');
            }
        });
    }
    
    // Enter para ativar botões focados
    if (e.key === 'Enter' && e.target.classList.contains('webhook-card')) {
        const detailsBtn = e.target.querySelector('.btn-info');
        if (detailsBtn) {
            detailsBtn.click();
        }
    }
});

// Função para monitorar performance
function monitorPerformance() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                
                if (loadTime > 3000) {
                    console.warn('Página carregou lentamente:', loadTime + 'ms');
                }
            }, 0);
        });
    }
}

// Inicializar monitoramento
monitorPerformance();

// Service Worker para cache (opcional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('SW registrado com sucesso:', registration.scope);
            })
            .catch(function(error) {
                console.log('Falha ao registrar SW:', error);
            });
    });
}

// Profile Dropdown
function toggleProfileDropdown() {
    const dropdown = document.querySelector('.profile-dropdown');
    dropdown.classList.toggle('active');
}

// Fechar dropdown ao clicar fora
document.addEventListener('click', function(event) {
    const dropdown = document.querySelector('.profile-dropdown');
    const profileBtn = document.querySelector('.profile-btn');
    
    if (dropdown && !dropdown.contains(event.target) && !profileBtn.contains(event.target)) {
        dropdown.classList.remove('active');
    }
});
