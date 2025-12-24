import { api } from './api.js';

// DOM элементы
const productGrid = document.getElementById('productGrid');
const cartBtn = document.getElementById('cartBtn');
const cartPanel = document.getElementById('cartPanel');
const closeCart = document.getElementById('closeCart');
const cartItemsWrap = document.getElementById('cartItems');
const cartCount = document.getElementById('cartCount');
const cartTotal = document.getElementById('cartTotal');
const checkoutBtn = document.getElementById('checkoutBtn');
const clearCartBtn = document.getElementById('clearCartBtn');
const authBtn = document.getElementById('authBtn');
const authModal = document.getElementById('authModal');
const closeAuth = document.getElementById('closeAuth');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const authTabs = document.querySelectorAll('.auth-tab');
const logoutBtn = document.getElementById('logoutBtn');
const userPanel = document.getElementById('userPanel');
const userName = document.getElementById('userName');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const categoryGrid = document.getElementById('categoryGrid');
const notification = document.getElementById('notification');

// Состояние приложения
let cart = {};
let currentUser = null;

// Утилиты
function formatPrice(n) {
    return n.toLocaleString('ru-RU') + ' ₽';
}

function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Работа с товарами
async function loadProducts() {
    try {
        const response = await api.getItems({
            per_page: 8,
            sort_by: 'rating',
            sort_order: 'desc'
        });
        
        if (response && response.items) {
            renderProducts(response.items);
        }
    } catch (error) {
        console.error('Failed to load products:', error);
        productGrid.innerHTML = '<p class="error">Не удалось загрузить товары</p>';
    }
}

function renderProducts(products) {
    productGrid.innerHTML = '';
    
    products.forEach(product => {
        const el = document.createElement('div');
        el.className = 'product';
        el.innerHTML = `
            <a href="product.html?id=${product.id}">
                <img src="${product.main_image_url || 'https://via.placeholder.com/300x200/cccccc/666666?text=Товар'}" alt="${product.name}">
            </a>
            <a href="product.html?id=${product.id}" class="title">${product.name}</a>
            <div class="meta">${product.brand?.name || ''}</div>
            <div class="price-row">
                <div class="price">${formatPrice(product.price)}</div>
                ${product.discount_price ? `<div class="old-price">${formatPrice(product.discount_price)}</div>` : ''}
            </div>
            <div class="product-actions">
                <button class="add-btn" data-id="${product.id}">
                    <i class="fas fa-cart-plus"></i> Добавить
                </button>
                <button class="compare-btn" data-id="${product.id}" title="Добавить к сравнению">
                    <i class="fas fa-balance-scale"></i>
                </button>
            </div>
        `;
        productGrid.appendChild(el);
    });
}

// Работа с категориями
async function loadCategories() {
    try {
        const categories = await api.getCategories();
        if (categories && categories.length > 0) {
            renderCategories(categories.slice(0, 6)); // Показываем первые 6
        }
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}

function renderCategories(categories) {
    categoryGrid.innerHTML = '';
    
    categories.forEach(category => {
        const el = document.createElement('a');
        el.href = `catalog.html?category=${category.id}`;
        el.className = 'category-card';
        el.innerHTML = `
            <div class="category-icon">
                <i class="fas fa-mobile-alt"></i>
            </div>
            <h4>${category.name}</h4>
            <p>${category.item_count || 0} товаров</p>
        `;
        categoryGrid.appendChild(el);
    });
}

// Работа с корзиной
async function loadCart() {
    try {
        const cartData = await api.getCart();
        if (cartData) {
            cart = cartData.items.reduce((acc, item) => {
                acc[item.item_id] = {
                    id: item.item_id,
                    title: item.item_name,
                    price: item.item_price,
                    img: item.item_image_url,
                    qty: item.quantity
                };
                return acc;
            }, {});
            updateCartUI();
        }
    } catch (error) {
        console.error('Failed to load cart:', error);
    }
}

function updateCartUI() {
    const ids = Object.keys(cart);
    const totalCount = ids.reduce((sum, id) => sum + cart[id].qty, 0);
    cartCount.textContent = totalCount;
    
    cartItemsWrap.innerHTML = '';
    
    if (ids.length === 0) {
        cartItemsWrap.innerHTML = '<p class="empty">Корзина пуста</p>';
        cartTotal.textContent = formatPrice(0);
        return;
    }
    
    let total = 0;
    ids.forEach(id => {
        const item = cart[id];
        total += item.price * item.qty;
        
        const node = document.createElement('div');
        node.className = 'cart-item';
        node.innerHTML = `
            <img src="${item.img || 'https://via.placeholder.com/60/cccccc/666666?text=Товар'}" alt="${item.title}">
            <div style="flex:1">
                <div class="meta">${item.title}</div>
                <div class="cart-item-controls">
                    <button data-op="dec" data-id="${id}" class="qty-btn">−</button>
                    <div class="qty-display">${item.qty}</div>
                    <button data-op="inc" data-id="${id}" class="qty-btn">＋</button>
                    <button data-op="remove" data-id="${id}" class="remove-btn" title="Удалить">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="cart-item-price">${formatPrice(item.price * item.qty)}</div>
        `;
        cartItemsWrap.appendChild(node);
    });
    
    cartTotal.textContent = formatPrice(total);
}

async function addToCart(id) {
    if (!api.isAuthenticated()) {
        showNotification('Для добавления в корзину необходимо войти в систему', 'warning');
        authModal.classList.add('open');
        return;
    }
    
    try {
        await api.addToCart(id, 1);
        await loadCart();
        showNotification('Товар добавлен в корзину', 'success');
    } catch (error) {
        showNotification('Ошибка при добавлении в корзину', 'error');
    }
}

async function changeCartQty(id, delta) {
    if (!cart[id]) return;
    
    const newQty = cart[id].qty + delta;
    
    if (newQty <= 0) {
        await removeFromCart(id);
    } else {
        try {
            await api.updateCartItem(id, newQty);
            await loadCart();
        } catch (error) {
            showNotification('Ошибка при обновлении корзины', 'error');
        }
    }
}

async function removeFromCart(id) {
    try {
        await api.removeFromCart(id);
        await loadCart();
        showNotification('Товар удален из корзины', 'info');
    } catch (error) {
        showNotification('Ошибка при удалении товара', 'error');
    }
}

async function clearCart() {
    if (Object.keys(cart).length === 0) return;
    
    if (confirm('Вы уверены, что хотите очистить корзину?')) {
        try {
            await api.clearCart();
            cart = {};
            updateCartUI();
            showNotification('Корзина очищена', 'info');
        } catch (error) {
            showNotification('Ошибка при очистке корзины', 'error');
        }
    }
}

// Аутентификация
async function checkAuth() {
    currentUser = await api.getCurrentUser();
    
    if (currentUser) {
        authBtn.style.display = 'none';
        userPanel.style.display = 'flex';
        userName.textContent = currentUser.name || currentUser.email;
        
        // Загружаем корзину для авторизованного пользователя
        await loadCart();
    } else {
        authBtn.style.display = 'block';
        userPanel.style.display = 'none';
    }
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        await api.login(email, password);
        authModal.classList.remove('open');
        await checkAuth();
        showNotification('Вы успешно вошли в систему', 'success');
    } catch (error) {
        showNotification('Ошибка входа. Проверьте email и пароль', 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const phone = document.getElementById('registerPhone').value;
    
    const userData = {
        name,
        email,
        password,
        role_id: 3 // customer
    };
    
    if (phone) {
        userData.phone = phone;
    }
    
    try {
        await api.register(userData);
        authModal.classList.remove('open');
        await checkAuth();
        showNotification('Регистрация успешна!', 'success');
    } catch (error) {
        showNotification('Ошибка регистрации. Возможно, email уже используется', 'error');
    }
}

async function handleLogout() {
    try {
        await api.logout();
        cart = {};
        updateCartUI();
        await checkAuth();
        showNotification('Вы вышли из системы', 'info');
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Поиск
function handleSearch() {
    const query = searchInput.value.trim();
    if (query) {
        window.location.href = `catalog.html?search=${encodeURIComponent(query)}`;
    }
}

// Инициализация
async function init() {
    // Проверяем авторизацию
    await checkAuth();
    
    // Загружаем данные
    await loadProducts();
    await loadCategories();
    
    // Назначаем обработчики событий
    // Добавление в корзину
    document.body.addEventListener('click', async (e) => {
        const addBtn = e.target.closest('.add-btn');
        if (addBtn) {
            const id = addBtn.dataset.id;
            await addToCart(id);
            return;
        }
        
        // Управление количеством в корзине
        const cartOp = e.target.closest('[data-op]');
        if (cartOp) {
            const id = cartOp.dataset.id;
            const operation = cartOp.dataset.op;
            
            if (operation === 'inc') {
                await changeCartQty(id, 1);
            } else if (operation === 'dec') {
                await changeCartQty(id, -1);
            } else if (operation === 'remove') {
                await removeFromCart(id);
            }
            return;
        }
    });
    
    // Корзина
    cartBtn.addEventListener('click', () => {
        cartPanel.classList.toggle('open');
    });
    
    closeCart.addEventListener('click', () => {
        cartPanel.classList.remove('open');
    });
    
    checkoutBtn.addEventListener('click', () => {
        if (Object.keys(cart).length === 0) {
            showNotification('Корзина пуста', 'warning');
            return;
        }
        
        if (!api.isAuthenticated()) {
            showNotification('Для оформления заказа необходимо войти в систему', 'warning');
            authModal.classList.add('open');
            return;
        }
        
        window.location.href = 'checkout.html';
    });
    
    clearCartBtn.addEventListener('click', clearCart);
    
    // Авторизация
    authBtn.addEventListener('click', () => {
        authModal.classList.add('open');
    });
    
    closeAuth.addEventListener('click', () => {
        authModal.classList.remove('open');
    });
    
    authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            
            // Обновляем активные табы
            authTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Показываем активную форму
            document.querySelectorAll('.auth-form').forEach(form => {
                form.classList.remove('active');
            });
            document.getElementById(`${tabName}Form`).classList.add('active');
        });
    });
    
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Поиск
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    // Закрытие модалок при клике вне
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.cart-panel') && !e.target.closest('#cartBtn')) {
            cartPanel.classList.remove('open');
        }
        
        if (!e.target.closest('.auth-modal') && !e.target.closest('#authBtn')) {
            authModal.classList.remove('open');
        }
    });
    
    // Закрытие по Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            cartPanel.classList.remove('open');
            authModal.classList.remove('open');
        }
    });
}

// Запускаем приложение когда DOM загружен
document.addEventListener('DOMContentLoaded', init);