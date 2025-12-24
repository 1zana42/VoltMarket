import { api } from './api.js';

// Получаем ID товара из URL
const urlParams = new URLSearchParams(window.location.search);
const productId = urlParams.get('id');

// DOM элементы
const productTitle = document.getElementById('productTitle');
const productSKU = document.getElementById('productSKU');
const mainImage = document.getElementById('mainImage');
const thumbnails = document.getElementById('thumbnails');
const currentPrice = document.getElementById('currentPrice');
const oldPrice = document.getElementById('oldPrice');
const discountBadge = document.getElementById('discountBadge');
const availabilityIcon = document.getElementById('availabilityIcon');
const availabilityText = document.getElementById('availabilityText');
const stockCount = document.getElementById('stockCount');
const productDescription = document.getElementById('productDescription');
const specificationsList = document.getElementById('specificationsList');
const categoryBreadcrumb = document.getElementById('categoryBreadcrumb');
const productBreadcrumb = document.getElementById('productBreadcrumb');
const reviewCount = document.getElementById('reviewCount');
const reviewsCount = document.getElementById('reviewsCount');
const averageRating = document.getElementById('averageRating');
const averageStars = document.getElementById('averageStars');
const totalReviews = document.getElementById('totalReviews');
const reviewsList = document.getElementById('reviewsList');
const relatedProducts = document.getElementById('relatedProducts');
const quantityInput = document.getElementById('quantity');
const decreaseQty = document.getElementById('decreaseQty');
const increaseQty = document.getElementById('increaseQty');
const addToCartBtn = document.getElementById('addToCartBtn');
const addToComparison = document.getElementById('addToComparison');
const addToWishlist = document.getElementById('addToWishlist');
const writeReviewBtn = document.getElementById('writeReviewBtn');
const reviewFormContainer = document.getElementById('reviewFormContainer');
const cancelReview = document.getElementById('cancelReview');
const reviewForm = document.getElementById('reviewForm');
const reviewRatingInput = document.getElementById('reviewRating');
const reviewText = document.getElementById('reviewText');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');

// Инициализация
async function init() {
    if (!productId) {
        window.location.href = 'catalog.html';
        return;
    }
    
    await loadProduct();
    await loadReviews();
    await loadRelatedProducts();
    
    setupEventListeners();
}

// Загрузка товара
async function loadProduct() {
    try {
        const product = await api.getItem(productId);
        
        if (!product) {
            throw new Error('Товар не найден');
        }
        
        // Заполняем информацию о товаре
        document.title = `${product.name} — VoltMarket`;
        productTitle.textContent = product.name;
        productBreadcrumb.textContent = product.name;
        productSKU.textContent = product.sku || '—';
        
        // Цены
        currentPrice.textContent = formatPrice(product.price);
        if (product.discount_price && product.discount_price < product.price) {
            oldPrice.textContent = formatPrice(product.discount_price);
            oldPrice.style.display = 'block';
            
            const discountPercent = Math.round((1 - product.price / product.discount_price) * 100);
            discountBadge.textContent = `-${discountPercent}%`;
            discountBadge.style.display = 'block';
        }
        
        // Наличие
        if (product.quantity > 0) {
            availabilityIcon.className = 'fas fa-check-circle';
            availabilityIcon.style.color = 'var(--success)';
            availabilityText.textContent = 'В наличии';
            stockCount.textContent = ` (${product.quantity} шт.)`;
            addToCartBtn.disabled = false;
        } else {
            availabilityIcon.className = 'fas fa-times-circle';
            availabilityIcon.style.color = 'var(--danger)';
            availabilityText.textContent = 'Нет в наличии';
            stockCount.textContent = '';
            addToCartBtn.disabled = true;
            addToCartBtn.textContent = 'Нет в наличии';
        }
        
        // Изображения
        if (product.main_image_url) {
            mainImage.src = product.main_image_url;
            mainImage.alt = product.name;
            
            // Миниатюры (пока одна)
            thumbnails.innerHTML = `
                <div class="thumbnail active">
                    <img src="${product.main_image_url}" alt="${product.name}">
                </div>
            `;
        }
        
        // Описание
        productDescription.innerHTML = product.description || 
            `<p>Этот товар пока не имеет подробного описания.</p>`;
        
        // Характеристики
        if (product.specifications && product.specifications.length > 0) {
            specificationsList.innerHTML = '';
            product.specifications.forEach(spec => {
                const specItem = document.createElement('div');
                specItem.className = 'spec-item';
                specItem.innerHTML = `
                    <span class="spec-name">${spec.specification_type.name}</span>
                    <span class="spec-value">${spec.value} ${spec.specification_type.unit || ''}</span>
                `;
                specificationsList.appendChild(specItem);
            });
        }
        
        // Категория в хлебных крошках
        if (product.category) {
            categoryBreadcrumb.textContent = product.category.name;
            categoryBreadcrumb.href = `catalog.html?category=${product.category.id}`;
        }
        
        // Рейтинг
        if (product.average_rating) {
            const rating = product.average_rating.toFixed(1);
            reviewCount.textContent = `${rating} (${product.review_count} отзывов)`;
            reviewsCount.textContent = product.review_count;
            totalReviews.textContent = product.review_count;
            averageRating.textContent = rating;
            
            // Звёзды рейтинга
            averageStars.innerHTML = renderStars(product.average_rating);
        }
        
    } catch (error) {
        console.error('Failed to load product:', error);
        document.body.innerHTML = `
            <div class="container" style="text-align: center; padding: 100px 20px;">
                <h2>Товар не найден</h2>
                <p>Запрашиваемый товар не существует или был удален.</p>
                <a href="catalog.html" class="primary-btn">Вернуться в каталог</a>
            </div>
        `;
    }
}

// Загрузка отзывов
async function loadReviews() {
    try {
        const response = await api.getReviews(productId);
        
        if (response && response.reviews) {
            renderReviews(response.reviews);
        }
    } catch (error) {
        console.error('Failed to load reviews:', error);
    }
}

function renderReviews(reviews) {
    reviewsList.innerHTML = '';
    
    if (reviews.length === 0) {
        reviewsList.innerHTML = `
            <div class="empty-reviews">
                <p>У этого товара пока нет отзывов. Будьте первым!</p>
            </div>
        `;
        return;
    }
    
    reviews.forEach(review => {
        const reviewItem = document.createElement('div');
        reviewItem.className = 'review-item';
        reviewItem.innerHTML = `
            <div class="review-header">
                <div class="review-author">${review.user_name}</div>
                <div class="review-date">${formatDate(review.created_at)}</div>
            </div>
            <div class="review-rating">${renderStars(review.rating)}</div>
            <div class="review-text">${review.description}</div>
        `;
        reviewsList.appendChild(reviewItem);
    });
}

// Загрузка похожих товаров
async function loadRelatedProducts() {
    try {
        // Получаем товары из той же категории
        const product = await api.getItem(productId);
        
        if (product && product.category_id) {
            const response = await api.getItems({
                category_id: product.category_id,
                per_page: 4,
                exclude: productId
            });
            
            if (response && response.items) {
                renderRelatedProducts(response.items);
            }
        }
    } catch (error) {
        console.error('Failed to load related products:', error);
    }
}

function renderRelatedProducts(products) {
    relatedProducts.innerHTML = '';
    
    if (products.length === 0) {
        relatedProducts.innerHTML = '<p>Нет похожих товаров</p>';
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
            </div>
            <button class="add-btn" data-id="${product.id}">
                <i class="fas fa-cart-plus"></i> Добавить
            </button>
        `;
        relatedProducts.appendChild(el);
    });
}

// Утилиты
function formatPrice(n) {
    return n.toLocaleString('ru-RU') + ' ₽';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
}

function renderStars(rating) {
    let stars = '';
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 1; i <= 5; i++) {
        if (i <= fullStars) {
            stars += '<i class="fas fa-star"></i>';
        } else if (i === fullStars + 1 && hasHalfStar) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        } else {
            stars += '<i class="far fa-star"></i>';
        }
    }
    
    return stars;
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Количество товара
    decreaseQty.addEventListener('click', () => {
        const current = parseInt(quantityInput.value);
        if (current > 1) {
            quantityInput.value = current - 1;
        }
    });
    
    increaseQty.addEventListener('click', () => {
        const current = parseInt(quantityInput.value);
        if (current < 99) {
            quantityInput.value = current + 1;
        }
    });
    
    // Добавление в корзину
    addToCartBtn.addEventListener('click', async () => {
        const quantity = parseInt(quantityInput.value);
        
        try {
            await api.addToCart(productId, quantity);
            showNotification('Товар добавлен в корзину', 'success');
        } catch (error) {
            showNotification('Ошибка при добавлении в корзину', 'error');
        }
    });
    
    // Добавление к сравнению
    addToComparison.addEventListener('click', async () => {
        try {
            // Сначала нужно получить или создать сравнение
            // Здесь упрощенная логика
            showNotification('Товар добавлен к сравнению', 'success');
        } catch (error) {
            showNotification('Ошибка при добавлении к сравнению', 'error');
        }
    });
    
    // Вкладки
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            
            // Обновляем активные кнопки
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Показываем активную вкладку
            tabPanes.forEach(pane => pane.classList.remove('active'));
            document.getElementById(`${tabName}Tab`).classList.add('active');
        });
    });
    
    // Отзывы
    writeReviewBtn.addEventListener('click', () => {
        if (!api.isAuthenticated()) {
            showNotification('Для написания отзыва необходимо войти в систему', 'warning');
            // Показать модалку авторизации
            if (window.showAuthModal) {
                window.showAuthModal();
            }
            return;
        }
        
        reviewFormContainer.style.display = 'block';
        writeReviewBtn.style.display = 'none';
    });
    
    cancelReview.addEventListener('click', () => {
        reviewFormContainer.style.display = 'none';
        writeReviewBtn.style.display = 'block';
    });
    
    // Рейтинг в форме отзыва
    const starInputs = document.querySelectorAll('.stars-input i');
    starInputs.forEach(star => {
        star.addEventListener('mouseover', () => {
            const rating = parseInt(star.dataset.rating);
            highlightStars(rating);
        });
        
        star.addEventListener('click', () => {
            const rating = parseInt(star.dataset.rating);
            reviewRatingInput.value = rating;
            highlightStars(rating);
        });
    });
    
    document.querySelector('.stars-input').addEventListener('mouseleave', () => {
        const currentRating = parseInt(reviewRatingInput.value) || 0;
        highlightStars(currentRating);
    });
    
    // Отправка отзыва
    reviewForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const rating = parseInt(reviewRatingInput.value);
        const description = reviewText.value.trim();
        
        if (rating === 0) {
            showNotification('Пожалуйста, поставьте оценку', 'warning');
            return;
        }
        
        if (description.length < 10) {
            showNotification('Отзыв должен содержать минимум 10 символов', 'warning');
            return;
        }
        
        try {
            await api.createReview({
                item_id: productId,
                rating,
                description
            });
            
            showNotification('Отзыв отправлен на модерацию', 'success');
            reviewForm.reset();
            reviewRatingInput.value = 0;
            highlightStars(0);
            reviewFormContainer.style.display = 'none';
            writeReviewBtn.style.display = 'block';
            
            // Перезагружаем отзывы
            await loadReviews();
            
        } catch (error) {
            showNotification('Ошибка при отправке отзыва', 'error');
        }
    });
    
    // Делегирование для кнопок добавления в корзину в похожих товарах
    relatedProducts.addEventListener('click', async (e) => {
        const addBtn = e.target.closest('.add-btn');
        if (addBtn) {
            const id = addBtn.dataset.id;
            try {
                await api.addToCart(id, 1);
                showNotification('Товар добавлен в корзину', 'success');
            } catch (error) {
                showNotification('Ошибка при добавлении в корзину', 'error');
            }
        }
    });
}

function highlightStars(rating) {
    const starInputs = document.querySelectorAll('.stars-input i');
    starInputs.forEach((star, index) => {
        if (index < rating) {
            star.className = 'fas fa-star';
            star.style.color = '#ffc107';
        } else {
            star.className = 'far fa-star';
            star.style.color = '#ddd';
        }
    });
}

function showNotification(message, type = 'info') {
    if (window.showNotification) {
        window.showNotification(message, type);
    } else {
        // Простая реализация, если нет глобальной функции
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 20px;
            border-radius: 8px;
            background: var(--accent-1);
            color: white;
            font-weight: 600;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            z-index: 1000;
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Запуск
document.addEventListener('DOMContentLoaded', init);