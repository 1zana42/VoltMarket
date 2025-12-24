// Конфигурация API
const API_BASE_URL = 'http://localhost:8000';
const API_ENDPOINTS = {
    auth: {
        register: '/auth/register',
        login: '/auth/login',
        logout: '/auth/logout',
        me: '/auth/me'
    },
    items: {
        list: '/items/',
        detail: (id) => `/items/${id}`,
        search: '/items/'
    },
    categories: {
        list: '/categories/',
        detail: (id) => `/categories/${id}`
    },
    cart: {
        get: '/cart/',
        add: '/cart/items',
        update: (itemId) => `/cart/items/${itemId}`,
        remove: (itemId) => `/cart/items/${itemId}`,
        clear: '/cart/'
    },
    orders: {
        create: '/orders/',
        list: '/orders/',
        detail: (id) => `/orders/${id}`
    },
    comparisons: {
        list: '/comparisons/',
        create: '/comparisons/',
        addItem: (id) => `/comparisons/${id}/items`,
        detail: (id) => `/comparisons/${id}`
    },
    reviews: {
        list: (itemId) => `/reviews/items/${itemId}`,
        create: '/reviews/'
    }
};

// Класс для работы с API
class VoltMarketAPI {
    constructor() {
        this.token = this.getToken();
    }

    // Работа с токеном
    getToken() {
        return localStorage.getItem('access_token');
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('access_token', token);
        } else {
            localStorage.removeItem('access_token');
        }
    }

    // Проверка аутентификации
    isAuthenticated() {
        return !!this.token;
    }

    // Общий метод для запросов
    async request(endpoint, options = {}) {
        const url = API_BASE_URL + endpoint;
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Добавляем токен, если есть
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        // Настройки по умолчанию
        const config = {
            credentials: 'include', // Для работы с куки
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            
            // Проверяем статус ответа
            if (!response.ok) {
                if (response.status === 401) {
                    // Неавторизован - очищаем токен
                    this.setToken(null);
                    window.location.href = '/login.html';
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // Парсим JSON, если есть контент
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Авторизация
    async login(email, password) {
        const data = { email, password };
        const response = await this.request(API_ENDPOINTS.auth.login, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        
        return response;
    }

    async register(userData) {
        const response = await this.request(API_ENDPOINTS.auth.register, {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        // Автоматически логиним после регистрации
        if (response.status === 'OK') {
            const loginResponse = await this.login(userData.email, userData.password);
            return loginResponse;
        }
        
        return response;
    }

    async logout() {
        const response = await this.request(API_ENDPOINTS.auth.logout, {
            method: 'POST'
        });
        
        this.setToken(null);
        return response;
    }

    async getCurrentUser() {
        if (!this.isAuthenticated()) return null;
        
        try {
            return await this.request(API_ENDPOINTS.auth.me);
        } catch (error) {
            return null;
        }
    }

    // Товары
    async getItems(params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const endpoint = queryParams 
            ? `${API_ENDPOINTS.items.list}?${queryParams}`
            : API_ENDPOINTS.items.list;
        
        return await this.request(endpoint);
    }

    async getItem(id) {
        return await this.request(API_ENDPOINTS.items.detail(id));
    }

    // Категории
    async getCategories() {
        return await this.request(API_ENDPOINTS.categories.list);
    }

    async getCategory(id) {
        return await this.request(API_ENDPOINTS.categories.detail(id));
    }

    // Корзина
    async getCart() {
        return await this.request(API_ENDPOINTS.cart.get);
    }

    async addToCart(itemId, quantity = 1) {
        const data = { item_id: itemId, quantity };
        return await this.request(API_ENDPOINTS.cart.add, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateCartItem(itemId, quantity) {
        const data = { quantity };
        return await this.request(API_ENDPOINTS.cart.update(itemId), {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async removeFromCart(itemId) {
        return await this.request(API_ENDPOINTS.cart.remove(itemId), {
            method: 'DELETE'
        });
    }

    async clearCart() {
        return await this.request(API_ENDPOINTS.cart.clear, {
            method: 'DELETE'
        });
    }

    // Заказы
    async createOrder(orderData) {
        return await this.request(API_ENDPOINTS.orders.create, {
            method: 'POST',
            body: JSON.stringify(orderData)
        });
    }

    async getOrders(page = 1, perPage = 10) {
        return await this.request(`${API_ENDPOINTS.orders.list}?page=${page}&per_page=${perPage}`);
    }

    // Сравнения
    async getComparisons() {
        return await this.request(API_ENDPOINTS.comparisons.list);
    }

    async createComparison(name) {
        const data = { name };
        return await this.request(API_ENDPOINTS.comparisons.create, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async addToComparison(comparisonId, itemId) {
        const data = { item_id: itemId };
        return await this.request(API_ENDPOINTS.comparisons.addItem(comparisonId), {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Отзывы
    async getReviews(itemId, page = 1, perPage = 10) {
        return await this.request(`${API_ENDPOINTS.reviews.list(itemId)}?page=${page}&per_page=${perPage}`);
    }

    async createReview(reviewData) {
        return await this.request(API_ENDPOINTS.reviews.create, {
            method: 'POST',
            body: JSON.stringify(reviewData)
        });
    }
}

// Создаем глобальный экземпляр API
const api = new VoltMarketAPI();

// Экспортируем для использования в других модулях
export { api, API_ENDPOINTS };