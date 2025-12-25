/**
 * Tarix Platformasi - Asosiy JavaScript fayli
 */

// DOM yuklanganda barcha funksiyalarni ishga tushirish
document.addEventListener('DOMContentLoaded', function() {
    // Navbar toggler
    initNavbar();
    
    // Dropdown menyular
    initDropdowns();
    
    // Form validatsiyasi
    initForms();
    
    // Toast notificationlar
    initToasts();
    
    // Tooltips
    initTooltips();
    
    // Scroll animatsiyalari
    initScrollAnimations();
    
    // Dark/light mode
    initThemeSwitcher();
    
    // Search funksiyasi
    initSearch();
});

/**
 * Navbar funksiyalari
 */
function initNavbar() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Tashqi bosilganda menyuni yopish
        document.addEventListener('click', function(event) {
            if (!navbarToggler.contains(event.target) && !navbarCollapse.contains(event.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
    
    // Navbar scroll effekti
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.main-navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
}

/**
 * Dropdown menyular
 */
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (toggle && menu) {
            // Click event
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Boshqa dropdownlarni yopish
                closeAllDropdowns();
                
                // Bu dropdownni ochish
                menu.classList.add('show');
                this.classList.add('show');
            });
            
            // Hover event (faqat desktop)
            if (window.innerWidth > 768) {
                dropdown.addEventListener('mouseenter', function() {
                    menu.classList.add('show');
                    toggle.classList.add('show');
                });
                
                dropdown.addEventListener('mouseleave', function() {
                    menu.classList.remove('show');
                    toggle.classList.remove('show');
                });
            }
        }
    });
    
    // Tashqi bosilganda dropdownlarni yopish
    document.addEventListener('click', function() {
        closeAllDropdowns();
    });
    
    function closeAllDropdowns() {
        dropdowns.forEach(dropdown => {
            dropdown.querySelector('.dropdown-menu')?.classList.remove('show');
            dropdown.querySelector('.dropdown-toggle')?.classList.remove('show');
        });
    }
}

/**
 * Form validatsiyasi
 */
function initForms() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showFormErrors(this);
            }
        });
        
        // Real-time validatsiya
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    });
    
    // Parol ko'rsatish/yashirish
    const toggleButtons = document.querySelectorAll('.toggle-password');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            if (input) {
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                this.innerHTML = type === 'password' ? 
                    '<i class="fas fa-eye"></i>' : 
                    '<i class="fas fa-eye-slash"></i>';
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    let isValid = true;
    let errorMessage = '';
    
    // Required check
    if (field.hasAttribute('required') && !field.value.trim()) {
        isValid = false;
        errorMessage = 'Bu maydon to\'ldirilishi shart';
    }
    
    // Email validatsiyasi
    if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            isValid = false;
            errorMessage = 'To\'g\'ri email manzil kiriting';
        }
    }
    
    // Parol validatsiyasi
    if (field.type === 'password' && field.value) {
        if (field.value.length < 8) {
            isValid = false;
            errorMessage = 'Parol kamida 8 belgidan iborat bo\'lishi kerak';
        }
    }
    
    // Telefon raqami validatsiyasi
    if (field.name === 'phone' && field.value) {
        const phoneRegex = /^\+?[1-9]\d{1,14}$/;
        if (!phoneRegex.test(field.value.replace(/\D/g, ''))) {
            isValid = false;
            errorMessage = 'To\'g\'ri telefon raqam kiriting';
        }
    }
    
    // Xato yoki muvaffaqiyatni ko'rsatish
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
        showFieldSuccess(field);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback d-block';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle me-1"></i> ${message}`;
    
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    field.parentNode.appendChild(errorDiv);
}

function showFieldSuccess(field) {
    clearFieldError(field);
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
}

function clearFieldError(field) {
    field.classList.remove('is-invalid', 'is-valid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function showFormErrors(form) {
    const firstError = form.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}

/**
 * Toast notificationlar
 */
function initToasts() {
    // Auto-hide toastlar
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        if (toast.classList.contains('autohide')) {
            setTimeout(() => {
                const bsToast = new bootstrap.Toast(toast);
                bsToast.hide();
            }, 5000);
        }
    });
    
    // Xabar notification funksiyasi
    window.showToast = function(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            createToastContainer();
        }
        
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${getToastIcon(type)} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
        toast.show();
        
        // Toast yopilganda o'chirish
        toastElement.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    };
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1060';
        document.body.appendChild(container);
    }
    
    function getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

/**
 * Tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Scroll animatsiyalari
 */
function initScrollAnimations() {
    // Smooth scroll
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Scroll progress bar
    const progressBar = document.querySelector('.scroll-progress');
    if (progressBar) {
        window.addEventListener('scroll', function() {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            progressBar.style.width = scrolled + '%';
        });
    }
    
    // Fade-in animatsiya
    const fadeElements = document.querySelectorAll('.fade-in');
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    fadeElements.forEach(element => {
        observer.observe(element);
    });
}

/**
 * Dark/light mode
 */
function initThemeSwitcher() {
    const themeToggle = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Joriy temani o'rnatish
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-theme');
        if (themeToggle) themeToggle.checked = true;
    }
    
    // Theme toggle
    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-theme');
                localStorage.setItem('theme', 'light');
            }
        });
    }
}

/**
 * Search funksiyasi
 */
function initSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');
    
    if (searchInput && searchResults) {
        let timeoutId;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(timeoutId);
            
            const query = this.value.trim();
            if (query.length < 2) {
                searchResults.classList.remove('show');
                return;
            }
            
            timeoutId = setTimeout(() => {
                performSearch(query);
            }, 300);
        });
        
        // Tashqi bosilganda yopish
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.remove('show');
            }
        });
        
        // Escape tugmasi
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                searchResults.classList.remove('show');
            }
        });
    }
}

function performSearch(query) {
    // Bu yerda AJAX so'rov yuboriladi
    // Hozircha mock data bilan ishlaymiz
    const mockResults = [
        { title: 'Qadimgi Misr', type: 'topic', url: '/history/topic/qadimgi-misr' },
        { title: 'Amir Temur', type: 'figure', url: '/history/figure/amir-temur' },
        { title: 'Ikkinchi jahon urushi', type: 'topic', url: '/history/topic/ikkinchi-jahon-urushi' }
    ];
    
    displaySearchResults(mockResults);
}

function displaySearchResults(results) {
    const searchResults = document.querySelector('.search-results');
    if (!searchResults) return;
    
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="search-result-empty">Hech narsa topilmadi</div>';
    } else {
        let html = '';
        results.forEach(result => {
            html += `
                <a href="${result.url}" class="search-result-item">
                    <div class="result-type">${result.type}</div>
                    <div class="result-title">${result.title}</div>
                </a>
            `;
        });
        searchResults.innerHTML = html;
    }
    
    searchResults.classList.add('show');
}

/**
 * Umumiy funksiyalar
 */

// Format date
window.formatDate = function(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('uz-UZ', options);
};

// Format time
window.formatTime = function(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
};

// Copy to clipboard
window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Nusxalandi!', 'success');
    }).catch(err => {
        console.error('Copy failed:', err);
        showToast('Nusxalashda xatolik', 'danger');
    });
};

// Debounce funksiyasi
window.debounce = function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Throttle funksiyasi
window.throttle = function(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// Loading spinner
window.showLoading = function(element) {
    if (element) {
        const originalHTML = element.innerHTML;
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Yuklanmoqda...';
        element.disabled = true;
        element.dataset.originalHtml = originalHTML;
    }
};

window.hideLoading = function(element) {
    if (element && element.dataset.originalHtml) {
        element.innerHTML = element.dataset.originalHtml;
        element.disabled = false;
        delete element.dataset.originalHtml;
    }
};

// Confirm dialog
window.showConfirm = function(message, callback) {
    if (window.confirm(message)) {
        callback();
    }
};

// Ajax so'rov
window.ajaxRequest = function(url, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open(method, url);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    resolve(response);
                } catch (e) {
                    resolve(xhr.responseText);
                }
            } else {
                reject(xhr.statusText);
            }
        };
        
        xhr.onerror = function() {
            reject('Network error');
        };
        
        xhr.send(data ? JSON.stringify(data) : null);
    });
};