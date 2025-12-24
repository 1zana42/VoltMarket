import { api } from './api.js';

// DOM элементы
const productsGrid = document.getElementById('productsGrid');
const productsCount = document.getElementById('productsCount');
const pagination = document.getElementById('pagination');
const sortSelect = document.getElementById('sortSelect');
const viewBtns = document.querySelectorAll('.view-btn');
const categoryFilter = document.getElementById('categoryFilter');
const brandFilter = document.getElementById('brandFilter');
const minPrice = document.getElementById('minPrice');
const maxPrice = document.getElementById('maxPrice');
const inStockOnly = document.getElementById('inStockOnly');
const applyFiltersBtn = document.getElementById('applyFilters');
const resetFiltersBtn = document.getElementById('resetFilters');
const applyPriceBtn = document.getElementById('applyPrice');

// Состояние
let currentPage = 1;
let totalPages = 1;
let currentFilters = {
    page: 1,
    per_page: 12,
    sort_by: 'created_at',
    sort_order: 'desc'
};

// Инициализация
async function init() {
    await loadCategories();
    await loadBrands();
    await loadProducts();
    
    // Обработчики событий
    sortSelect.addEventListener('change', handleSortChange);
    
    viewBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            viewBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            productsGrid.className = `products-grid ${view}-view`;
        });
    });
    
    applyFiltersBtn.addEventListener('click', applyFilters);
    resetFiltersBtn.addEventListener('click', resetFilters);
    applyPriceBtn.addEventListener('click', applyPriceFilter);
    
    // Обработчик для чекбоксов категорий и брендов
    document.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox' && 
            (e.target.closest('#categoryFilter') || e.target.closest('#brandFilter'))) {
            applyFilters();
        }
    });
}

// Загрузка категорий для фильтра
async function loadCategories() {
    try {
        const categories = await api.getCategories();
        if (categories && categories.length > 0) {
            renderCategoryFilter(categories);
        }
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}

function renderCategoryFilter(categories) {
    categoryFilter.innerHTML = '';
    
    categories.forEach(category => {
        const item = document.createElement('div');
        item.className = 'filter-item';
        item.innerHTML = `
            <input type="checkbox" id="cat_${category.id}" value="${category.id}">
            <label for="cat_${category.id}">${category.name} (${category.item_count || 0})</label>
        `;
        categoryFilter.appendChild(item);
    });
}

// Загрузка брендов для фильтра
async function loadBrands() {
    // Здесь нужно будет добавить API для брендов
    // Пока используем заглушку
    const brands = [
        { id: 1, name: 'Apple', count: 42 },
        { id: 2, name: 'Samsung', count: 38 },
        { id: 3, name: 'Xiaomi', count: 25 },
        { id: 4, name: 'Lenovo', count: 18 },
        { id: 5, name: 'Sony', count: 15 },
    ];
    
    renderBrandFilter(brands);
}

function renderBrandFilter(brands) {
    brandFilter.innerHTML = '';
    
    brands.forEach(brand => {
        const item = document.createElement('div');
        item.className = 'filter-item';
        item.innerHTML = `
            <input type="checkbox" id="brand_${brand.id}" value="${brand.id}">
            <label for="brand_${brand.id}">${brand.name} (${brand.count})</label>
        `;
        brandFilter.appendChild(item);
    });
}

// Загрузка товаров
async function loadProducts() {
    try {
        productsGrid.innerHTML = '<div class="loading">Загрузка товаров...</div>';
        
        const response = await api.getItems(currentFilters);
        
        if (response && response.items) {
            renderProducts(response.items);
            updatePagination(response.pagination);
            productsCount.textContent = `Найдено ${response.pagination.total} товаров`;
        }
    } catch (error) {
        console.error('Failed to load products:', error);
        productsGrid.innerHTML = '<p class="error">Не удалось загрузить товары</p>';
    }
}

function renderProducts(products) {
    productsGrid.innerHTML = '';
    
    if (products.length === 0) {
        productsGrid.innerHTML = '<p class="empty">Товары не найдены</p>';
        return;
    }
    
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
        productsGrid.appendChild(el);
    });
}

function formatPrice(n) {
    return n.toLocaleString('ru-RU') + ' ₽';
}

// Пагинация
function updatePagination(pagination) {
    pagination.innerHTML = '';
    totalPages = pagination.total_pages;
    currentPage = pagination.page;
    
    // Кнопка "Назад"
    const prevBtn = document.createElement('button');
    prevBtn.className = 'page-btn';
    prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener('click', () => goToPage(currentPage - 1));
    pagination.appendChild(prevBtn);
    
    // Номера страниц
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.className = `page-btn ${i === currentPage ? 'active' : ''}`;
        pageBtn.textContent = i;
        pageBtn.addEventListener('click', () => goToPage(i));
        pagination.appendChild(pageBtn);
    }
    
    // Кнопка "Вперед"
    const nextBtn = document.createElement('button');
    nextBtn.className = 'page-btn';
    nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.addEventListener('click', () => goToPage(currentPage + 1));
    pagination.appendChild(nextBtn);
}

function goToPage(page) {
    if (page < 1 || page > totalPages) return;
    currentFilters.page = page;
    loadProducts();
}

// Сортировка
function handleSortChange() {
    const value = sortSelect.value;
    const [field, order] = value.split('_');
    
    currentFilters.sort_by = field;
    currentFilters.sort_order = order;
    currentFilters.page = 1;
    
    loadProducts();
}

// Фильтры
function applyFilters() {
    // Категории
    const selectedCategories = Array.from(
        document.querySelectorAll('#categoryFilter input:checked')
    ).map(input => input.value);
    
    if (selectedCategories.length > 0) {
        currentFilters.category_id = selectedCategories.join(',');
    } else {
        delete currentFilters.category_id;
    }
    
    // Бренды
    const selectedBrands = Array.from(
        document.querySelectorAll('#brandFilter input:checked')
    ).map(input => input.value);
    
    if (selectedBrands.length > 0) {
        currentFilters.brand_id = selectedBrands.join(',');
    } else {
        delete currentFilters.brand_id;
    }
    
    // Наличие
    currentFilters.in_stock = inStockOnly.checked;
    
    // Цена уже применена через applyPriceFilter
    
    currentFilters.page = 1;
    loadProducts();
}

function applyPriceFilter() {
    const min = parseInt(minPrice.value) || null;
    const max = parseInt(maxPrice.value) || null;
    
    if (min !== null) {
        currentFilters.min_price = min;
    } else {
        delete currentFilters.min_price;
    }
    
    if (max !== null) {
        currentFilters.max_price = max;
    } else {
        delete currentFilters.max_price;
    }
}

function resetFilters() {
    // Сброс чекбоксов
    document.querySelectorAll('#categoryFilter input, #brandFilter input').forEach(input => {
        input.checked = false;
    });
    
    // Сброс цен
    minPrice.value = '';
    maxPrice.value = '';
    
    // Сброс наличия
    inStockOnly.checked = false;
    
    // Сброс фильтров в состоянии
    currentFilters = {
        page: 1,
        per_page: 12,
        sort_by: 'created_at',
        sort_order: 'desc'
    };
    
    // Сброс сортировки
    sortSelect.value = 'created_at_desc';
    
    loadProducts();
}

// Добавление в корзину (делегирование)
document.addEventListener('click', async (e) => {
    const addBtn = e.target.closest('.add-btn');
    if (addBtn) {
        const id = addBtn.dataset.id;
        // Используем общую функцию из api.js
        if (window.api && window.api.addToCart) {
            await window.api.addToCart(id);
        } else {
            console.error('API not available');
        }
    }
});

// Запуск
document.addEventListener('DOMContentLoaded', init);