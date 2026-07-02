// ===== STATE =====
const state = {
    token: localStorage.getItem('access_token'),
    user: null,
    currentPage: 'dashboard',
    transactions: [],
    pagination: { page: 1, limit: 20, total: 0 },
    categories: [],
    charts: {}
};

// ===== API CONFIGURATION =====
const API_BASE = 'http://localhost:8000/api/v1';

// ===== THEME (Vault palette — keep in sync with dashboard-cred.css) =====
const THEME = {
    gold: '#D4AF6A',
    goldBright: '#F0D48A',
    goldDim: '#8A6E3F',
    success: '#3DDC84',
    danger: '#FF5C7A',
    warning: '#FFB454',
    text: '#F2F2F5',
    textLight: '#8B8B94',
    gridLine: 'rgba(255, 255, 255, 0.06)',
    cardBg: '#16161C',
    // Categorical palette for charts with several series — gold leads, cool
    // neutrals and the two status colors round it out so nothing clashes
    // with the success/danger meaning used elsewhere in the UI.
    categorical: ['#D4AF6A', '#8B8B94', '#3DDC84', '#FF5C7A', '#6E9BD1', '#B784D8']
};

Chart.defaults.color = THEME.textLight;
Chart.defaults.borderColor = THEME.gridLine;
Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";

// ===== AXIOS INSTANCE =====
const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Add auth interceptor
api.interceptors.request.use(config => {
    if (state.token) {
        config.headers.Authorization = `Bearer ${state.token}`;
    }
    return config;
});

// ===== AUTH FUNCTIONS =====
async function handleLogin() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await api.post('/auth/login', { username, password });
        state.token = response.data.access_token;
        localStorage.setItem('access_token', state.token);
        
        // Get user info
        const userResponse = await api.get('/auth/me');
        state.user = userResponse.data;
        
        showDashboard();
    } catch (error) {
        alert('Login failed: ' + (error.response?.data?.detail || error.message));
    }
}

async function handleRegister() {
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        await api.post('/auth/register', { email, username, password });
        alert('Registration successful! Please login.');
        showLogin();
    } catch (error) {
        alert('Registration failed: ' + (error.response?.data?.detail || error.message));
    }
}

function handleLogout() {
    state.token = null;
    localStorage.removeItem('access_token');
    state.user = null;
    document.getElementById('dashboard').style.display = 'none';
    document.getElementById('loginScreen').style.display = 'flex';
}

function showLogin() {
    document.getElementById('registerScreen').style.display = 'none';
    document.getElementById('loginScreen').style.display = 'flex';
}

function showRegister() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('registerScreen').style.display = 'flex';
}

function showDashboard() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('registerScreen').style.display = 'none';
    document.getElementById('dashboard').style.display = 'flex';
    document.getElementById('userName').textContent = `Welcome, ${state.user?.username || 'User'}`;
    
    // Load initial data
    loadDashboard();
    loadCategories();
}

// ===== PAGE NAVIGATION =====
function switchPage(page) {
    state.currentPage = page;
    
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    document.querySelector(`.nav-item[data-page="${page}"]`)?.classList.add('active');
    
    // Update title
    const titles = {
        dashboard: 'Dashboard',
        transactions: 'Transactions',
        analytics: 'Analytics',
        forecast: 'Forecast',
        budget: 'Budget',
        chat: 'AI Chat',
        subscriptions: 'Subscriptions'
    };
    document.getElementById('pageTitle').textContent = titles[page] || page;
    
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(p => p.style.display = 'none');
    
    // Show selected page
    const pageElement = document.getElementById(`page-${page}`);
    if (pageElement) {
        pageElement.style.display = 'block';
    }
    
    // Load page data
    switch(page) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'transactions':
            loadTransactions();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'forecast':
            loadForecast();
            break;
        case 'budget':
            loadBudget();
            break;
        case 'subscriptions':
            loadSubscriptions();
            break;
    }
}

// ===== DASHBOARD =====
async function loadDashboard() {
    try {
        // Load stats
        const [stats, health, category] = await Promise.all([
            api.get('/analytics/statistics'),
            api.get('/analytics/health'),
            api.get('/analytics/spending/category')
        ]);
        
        // Update stats
        document.getElementById('totalSpending').textContent = `₹${stats.data.total_spending.toFixed(2)}`;
        document.getElementById('transactionCount').textContent = stats.data.total_transactions;
        document.getElementById('avgAmount').textContent = `₹${stats.data.average_amount.toFixed(2)}`;
        document.getElementById('healthScore').textContent = `${health.data.score}/100`;
        
        const healthStatus = document.getElementById('healthStatus');
        if (health.data.score >= 70) {
            healthStatus.textContent = '✅ Good';
            healthStatus.className = 'stat-change positive';
        } else if (health.data.score >= 50) {
            healthStatus.textContent = '⚠️ Average';
            healthStatus.className = 'stat-change';
        } else {
            healthStatus.textContent = '❌ Needs Attention';
            healthStatus.className = 'stat-change negative';
        }
        
        // Load charts
        loadCategoryChart(category.data);
        loadTrendChart();
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ===== CHARTS =====
function loadCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    const categories = data.summary.map(item => item.category);
    const amounts = data.summary.map(item => item.total);
    
    if (state.charts.category) {
        state.charts.category.destroy();
    }
    
    state.charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories,
            datasets: [{
                data: amounts,
                backgroundColor: THEME.categorical.slice(0, categories.length),
                borderWidth: 2,
                borderColor: THEME.cardBg
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: THEME.textLight, padding: 14 }
                }
            }
        }
    });
}

async function loadTrendChart() {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    try {
        const response = await api.get('/analytics/spending/monthly?months=6');
        const data = response.data;
        const months = data.map(item => item.month_name || item.month);
        const amounts = data.map(item => item.total);
        
        if (state.charts.trend) {
            state.charts.trend.destroy();
        }
        
        state.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Monthly Spending',
                    data: amounts,
                    borderColor: THEME.gold,
                    backgroundColor: 'rgba(212, 175, 106, 0.12)',
                    pointBackgroundColor: THEME.goldBright,
                    pointBorderColor: THEME.cardBg,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: THEME.gridLine },
                        ticks: { color: THEME.textLight }
                    },
                    x: {
                        grid: { color: THEME.gridLine },
                        ticks: { color: THEME.textLight }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading trend chart:', error);
    }
}

// ===== TRANSACTIONS =====
async function loadTransactions() {
    const merchant = document.getElementById('searchMerchant').value;
    const category = document.getElementById('filterCategory').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    try {
        const params = {
            skip: (state.pagination.page - 1) * state.pagination.limit,
            limit: state.pagination.limit,
            ...(merchant && { merchant }),
            ...(category && { category }),
            ...(startDate && { start_date: startDate }),
            ...(endDate && { end_date: endDate })
        };
        
        const response = await api.get('/transactions', { params });
        state.transactions = response.data;
        state.pagination.total = response.headers['x-total-count'] || response.data.length;
        
        renderTransactions();
        updatePagination();
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

function renderTransactions() {
    const tbody = document.getElementById('transactionsBody');
    if (state.transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading-text">No transactions found</td></tr>';
        return;
    }
    
    tbody.innerHTML = state.transactions.map(t => `
        <tr>
            <td>${formatDate(t.transaction_date)}</td>
            <td><strong>${t.merchant}</strong></td>
            <td><span class="category-tag">${t.category}</span></td>
            <td>₹${t.amount.toFixed(2)}</td>
            <td>${t.description || '-'}</td>
        </tr>
    `).join('');
}

function updatePagination() {
    const totalPages = Math.ceil(state.pagination.total / state.pagination.limit);
    document.getElementById('pageInfo').textContent = `Page ${state.pagination.page} of ${totalPages}`;
}

function prevPage() {
    if (state.pagination.page > 1) {
        state.pagination.page--;
        loadTransactions();
    }
}

function nextPage() {
    const totalPages = Math.ceil(state.pagination.total / state.pagination.limit);
    if (state.pagination.page < totalPages) {
        state.pagination.page++;
        loadTransactions();
    }
}

function resetFilters() {
    document.getElementById('searchMerchant').value = '';
    document.getElementById('filterCategory').value = '';
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    state.pagination.page = 1;
    loadTransactions();
}

// ===== CATEGORIES =====
async function loadCategories() {
    try {
        const response = await api.get('/categories');
        state.categories = response.data;
        
        const select = document.getElementById('filterCategory');
        select.innerHTML = '<option value="">All Categories</option>' +
            state.categories.map(c => `<option value="${c}">${c}</option>`).join('');
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// ===== ANALYTICS =====
async function loadAnalytics() {
    try {
        // Category chart
        const categoryResponse = await api.get('/analytics/spending/category');
        const ctx = document.getElementById('analyticsCategoryChart').getContext('2d');
        
        if (state.charts.analyticsCategory) {
            state.charts.analyticsCategory.destroy();
        }
        
        const data = categoryResponse.data;
        state.charts.analyticsCategory = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.summary.map(item => item.category),
                datasets: [{
                    label: 'Spending by Category',
                    data: data.summary.map(item => item.total),
                    backgroundColor: THEME.categorical,
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: THEME.gridLine },
                        ticks: { color: THEME.textLight }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: THEME.textLight }
                    }
                }
            }
        });
        
        // Top merchants
        const merchantResponse = await api.get('/analytics/merchant/top?limit=5');
        const merchants = merchantResponse.data;
        document.getElementById('topMerchantsList').innerHTML = merchants.map(m => `
            <div class="forecast-item">
                <span class="label">${m.merchant}</span>
                <span class="value">₹${m.total.toFixed(2)}</span>
            </div>
        `).join('');
        
        // Statistics
        const statsResponse = await api.get('/analytics/statistics');
        const stats = statsResponse.data;
        document.getElementById('statisticsGrid').innerHTML = `
            <div class="stat-mini"><div class="value">${stats.total_transactions}</div><div class="label">Transactions</div></div>
            <div class="stat-mini"><div class="value">₹${stats.total_spending.toFixed(2)}</div><div class="label">Total</div></div>
            <div class="stat-mini"><div class="value">₹${stats.average_amount.toFixed(2)}</div><div class="label">Average</div></div>
            <div class="stat-mini"><div class="value">₹${stats.largest_amount.toFixed(2)}</div><div class="label">Largest</div></div>
            <div class="stat-mini"><div class="value">₹${stats.smallest_amount.toFixed(2)}</div><div class="label">Smallest</div></div>
            <div class="stat-mini"><div class="value">${stats.std_deviation.toFixed(2)}</div><div class="label">Std Dev</div></div>
        `;
        
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// ===== FORECAST =====
async function loadForecast() {
    try {
        // Monthly forecast
        const monthlyResponse = await api.get('/analytics/forecast/monthly');
        const monthly = monthlyResponse.data;
        document.getElementById('monthlyForecast').innerHTML = `
            <div class="forecast-item"><span class="label">Current Month</span><span class="value">${monthly.current_month.month}</span></div>
            <div class="forecast-item"><span class="label">Spent So Far</span><span class="value">₹${monthly.current_month.spent_so_far.toFixed(2)}</span></div>
            <div class="forecast-item"><span class="label">Projected Total</span><span class="value">₹${monthly.forecast.projected_total.toFixed(2)}</span></div>
            <div class="forecast-item"><span class="label">Daily Average</span><span class="value">₹${monthly.forecast.average_daily_spending.toFixed(2)}</span></div>
            <div class="forecast-item"><span class="label">Confidence</span><span class="value">${monthly.forecast.confidence}%</span></div>
            ${monthly.current_month.note ? `<div class="forecast-item"><span class="label">Note</span><span class="value">${monthly.current_month.note}</span></div>` : ''}
        `;
        
        // Cashflow forecast
        const cashflowResponse = await api.get('/analytics/forecast/cashflow?budget=50000');
        const cashflow = cashflowResponse.data;
        document.getElementById('cashflowForecast').innerHTML = `
            <div class="forecast-item"><span class="label">Budget</span><span class="value">₹${cashflow.budget.toFixed(2)}</span></div>
            <div class="forecast-item"><span class="label">Projected Spending</span><span class="value">₹${cashflow.projected_spending.toFixed(2)}</span></div>
            <div class="forecast-item"><span class="label">Projected Remaining</span><span class="value">₹${cashflow.projected_remaining.toFixed(2)}</span></div>
            <div class="forecast-item"><span class="label">Status</span><span class="value">${cashflow.status === 'good' ? '✅ On Track' : '⚠️ Warning'}</span></div>
            ${cashflow.suggestions ? cashflow.suggestions.map(s => `<div class="forecast-item"><span class="label">💡</span><span class="value">${s}</span></div>`).join('') : ''}
        `;
        
        // Category forecasts
        const categoriesResponse = await api.get('/analytics/forecast/categories');
        const categories = categoriesResponse.data.categories;
        document.getElementById('categoryForecasts').innerHTML = Object.entries(categories).map(([name, data]) => `
            <div class="forecast-item">
                <span class="label">${name}</span>
                <span class="value">Current: ₹${data.current_spent.toFixed(2)} | Forecast: ₹${data.forecast.toFixed(2)}</span>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading forecast:', error);
    }
}

// ===== BUDGET =====
async function loadBudget() {
    try {
        const budget = document.getElementById('budgetAmount').value || 50000;
        const response = await api.get('/analytics/budget', { params: { budget } });
        const data = response.data;
        
        document.getElementById('budgetStatus').innerHTML = `
            <div class="forecast-item"><span class="label">Budget</span><span class="value">₹${data.budget.toFixed(2)}</span></div>
            <div class="forecast-item"><span class="label">Spent</span><span class="value">₹${data.spent.toFixed(2)}</span></div>
            <div class="forecast-item"><span class="label">Remaining</span><span class="value">₹${data.remaining.toFixed(2)}</span></div>
            <div class="forecast-item"><span class="label">Used</span><span class="value">${data.percentage_used}%</span></div>
            <div class="forecast-item"><span class="label">Status</span><span class="value">${data.on_track ? '✅ On Track' : '⚠️ Over Budget'}</span></div>
        `;
        
        // Budget chart
        const ctx = document.getElementById('budgetChart').getContext('2d');
        if (state.charts.budget) {
            state.charts.budget.destroy();
        }
        state.charts.budget = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Spent', 'Remaining'],
                datasets: [{
                    data: [data.spent, data.remaining],
                    backgroundColor: [THEME.gold, THEME.success],
                    borderWidth: 2,
                    borderColor: THEME.cardBg
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: THEME.textLight, padding: 14 }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading budget:', error);
    }
}

async function updateBudget() {
    await loadBudget();
}

// ===== SUBSCRIPTIONS =====
async function loadSubscriptions() {
    try {
        const response = await api.get('/analytics/subscriptions');
        const data = response.data;
        
        if (data.length === 0) {
            document.getElementById('subscriptionsList').innerHTML = `
                <div class="loading-text">No recurring subscriptions detected</div>
            `;
            return;
        }
        
        document.getElementById('subscriptionsList').innerHTML = data.map(sub => `
            <div class="subscription-card">
                <div class="merchant">${sub.merchant}</div>
                <div class="amount">₹${sub.amount.toFixed(2)}</div>
                <div class="frequency">${sub.frequency} • Last: ${formatDate(sub.last_charge)}</div>
                ${sub.next_charge ? `<div class="frequency">Next: ${formatDate(sub.next_charge)}</div>` : ''}
                <div class="frequency">Confidence: ${sub.confidence}%</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading subscriptions:', error);
    }
}

// ===== AI CHAT =====
async function sendChat() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;
    
    const messagesContainer = document.getElementById('chatMessages');
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.textContent = message;
    messagesContainer.appendChild(userMsg);
    input.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    try {
        const response = await api.post('/chat', { message });
        const data = response.data;
        
        const botMsg = document.createElement('div');
        botMsg.className = 'message bot';
        botMsg.textContent = data.message || 'No response';
        messagesContainer.appendChild(botMsg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (error) {
        const errorMsg = document.createElement('div');
        errorMsg.className = 'message error';
        errorMsg.textContent = 'Sorry, I encountered an error. Please try again.';
        messagesContainer.appendChild(errorMsg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        console.error('Chat error:', error);
    }
}

function quickQuery(query) {
    document.getElementById('chatInput').value = query;
    sendChat();
}

// ===== UPLOAD =====
async function handleUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await api.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        alert(`✅ ${response.data.message}\nRows imported: ${response.data.rows_imported}`);
        loadDashboard();
        loadTransactions();
    } catch (error) {
        alert('Upload failed: ' + (error.response?.data?.detail || error.message));
    }
    
    event.target.value = '';
}

// ===== UTILITY FUNCTIONS =====
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

// ===== AUTO-LOGIN CHECK =====
document.addEventListener('DOMContentLoaded', () => {
    if (state.token) {
        api.get('/auth/me')
            .then(response => {
                state.user = response.data;
                showDashboard();
            })
            .catch(() => {
                // Token invalid, show login
                document.getElementById('loginScreen').style.display = 'flex';
            });
    } else {
        document.getElementById('loginScreen').style.display = 'flex';
    }
});

// ===== AUTO-REFRESH =====
setInterval(() => {
    if (state.token && state.currentPage === 'dashboard') {
        loadDashboard();
    }
}, 60000);