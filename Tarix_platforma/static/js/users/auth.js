/**
 * Users Authentication JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Login form
    initLoginForm();
    
    // Register form
    initRegisterForm();
    
    // Password strength checker
    initPasswordStrength();
    
    // Form validation
    initAuthForms();
    
    // Social login buttons
    initSocialLogin();
});

/**
 * Login form funksiyalari
 */
function initLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;
    
    // Remember me checkbox
    const rememberMe = loginForm.querySelector('#remember_me');
    if (rememberMe) {
        const savedUsername = localStorage.getItem('rememberedUsername');
        if (savedUsername) {
            const usernameInput = loginForm.querySelector('#id_username');
            if (usernameInput) {
                usernameInput.value = savedUsername;
                rememberMe.checked = true;
            }
        }
        
        rememberMe.addEventListener('change', function() {
            if (!this.checked) {
                localStorage.removeItem('rememberedUsername');
            }
        });
    }
    
    // Form submit
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validateLoginForm(this)) {
            return;
        }
        
        // Remember username
        if (rememberMe && rememberMe.checked) {
            const usernameInput = this.querySelector('#id_username');
            if (usernameInput) {
                localStorage.setItem('rememberedUsername', usernameInput.value);
            }
        }
        
        // Show loading
        const submitBtn = this.querySelector('button[type="submit"]');
        showLoading(submitBtn);
        
        // Submit form
        this.submit();
    });
    
    // Auto-focus username field
    const usernameInput = loginForm.querySelector('#id_username');
    if (usernameInput && !usernameInput.value) {
        setTimeout(() => {
            usernameInput.focus();
        }, 300);
    }
}

function validateLoginForm(form) {
    let isValid = true;
    const errors = [];
    
    const username = form.querySelector('#id_username').value.trim();
    const password = form.querySelector('#id_password').value.trim();
    
    if (!username) {
        isValid = false;
        errors.push('Foydalanuvchi nomi yoki email kiriting');
    }
    
    if (!password) {
        isValid = false;
        errors.push('Parol kiriting');
    }
    
    if (!isValid) {
        showAuthErrors(form, errors);
    }
    
    return isValid;
}

/**
 * Register form funksiyalari
 */
function initRegisterForm() {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;
    
    // Username availability check
    const usernameInput = registerForm.querySelector('#id_username');
    const checkUsernameBtn = document.getElementById('checkUsername');
    
    if (usernameInput && checkUsernameBtn) {
        // Real-time username validation
        let usernameTimeout;
        usernameInput.addEventListener('input', debounce(function() {
            const username = this.value.trim();
            if (username.length >= 3) {
                checkUsernameAvailability(username);
            }
        }, 500));
        
        // Manual check button
        checkUsernameBtn.addEventListener('click', function() {
            const username = usernameInput.value.trim();
            if (username.length >= 3) {
                checkUsernameAvailability(username);
            } else {
                showToast('Foydalanuvchi nomi kamida 3 belgidan iborat bo\'lishi kerak', 'warning');
            }
        });
    }
    
    // Email confirmation
    const emailInput = registerForm.querySelector('#id_email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value.trim();
            if (email && !isValidEmail(email)) {
                showFieldError(this, 'To\'g\'ri email manzil kiriting');
            }
        });
    }
    
    // Password confirmation match
    const password1 = registerForm.querySelector('#id_password1');
    const password2 = registerForm.querySelector('#id_password2');
    
    if (password1 && password2) {
        password2.addEventListener('input', function() {
            checkPasswordMatch(password1, password2);
        });
    }
    
    // Terms agreement
    const termsCheckbox = registerForm.querySelector('#terms');
    if (termsCheckbox) {
        termsCheckbox.addEventListener('change', function() {
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = !this.checked;
            }
        });
    }
    
    // Form submit
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validateRegisterForm(this)) {
            return;
        }
        
        // Show loading
        const submitBtn = this.querySelector('button[type="submit"]');
        showLoading(submitBtn);
        
        // Submit form
        this.submit();
    });
}

function checkUsernameAvailability(username) {
    const usernameInput = document.getElementById('id_username');
    const checkBtn = document.getElementById('checkUsername');
    const validFeedback = document.getElementById('usernameValid');
    const invalidFeedback = document.getElementById('usernameInvalid');
    
    if (!usernameInput || !checkBtn) return;
    
    // Show checking state
    checkBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    checkBtn.disabled = true;
    
    // Mock AJAX request - aslida serverga so'rov yuboriladi
    setTimeout(() => {
        // Mock response: 70% ehtimol bilan mavjud emas
        const isAvailable = Math.random() > 0.3;
        
        checkBtn.innerHTML = '<i class="fas fa-check"></i>';
        checkBtn.disabled = false;
        
        if (isAvailable) {
            usernameInput.classList.add('is-valid');
            usernameInput.classList.remove('is-invalid');
            if (validFeedback) validFeedback.style.display = 'block';
            if (invalidFeedback) invalidFeedback.style.display = 'none';
            showToast('Bu foydalanuvchi nomi mavjud emas', 'success');
        } else {
            usernameInput.classList.add('is-invalid');
            usernameInput.classList.remove('is-valid');
            if (validFeedback) validFeedback.style.display = 'none';
            if (invalidFeedback) invalidFeedback.style.display = 'block';
            showToast('Bu foydalanuvchi nomi band', 'warning');
        }
    }, 1000);
}

function checkPasswordMatch(password1, password2) {
    const matchText = document.getElementById('passwordMatch');
    if (!matchText) return;
    
    if (!password2.value) {
        matchText.textContent = '';
        matchText.style.color = '';
        return;
    }
    
    if (password1.value === password2.value) {
        matchText.innerHTML = '<i class="fas fa-check-circle me-1"></i>Parollar mos keladi';
        matchText.style.color = '#28a745';
        password2.classList.add('is-valid');
        password2.classList.remove('is-invalid');
    } else {
        matchText.innerHTML = '<i class="fas fa-times-circle me-1"></i>Parollar mos kelmadi';
        matchText.style.color = '#dc3545';
        password2.classList.add('is-invalid');
        password2.classList.remove('is-valid');
    }
}

function validateRegisterForm(form) {
    let isValid = true;
    const errors = [];
    
    // Username
    const username = form.querySelector('#id_username').value.trim();
    if (!username) {
        isValid = false;
        errors.push('Foydalanuvchi nomi kiriting');
    } else if (username.length < 3) {
        isValid = false;
        errors.push('Foydalanuvchi nomi kamida 3 belgidan iborat bo\'lishi kerak');
    } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        isValid = false;
        errors.push('Foydalanuvchi nomi faqat harflar, raqamlar va _ belgisidan iborat bo\'lishi kerak');
    }
    
    // Email
    const email = form.querySelector('#id_email').value.trim();
    if (!email) {
        isValid = false;
        errors.push('Email manzil kiriting');
    } else if (!isValidEmail(email)) {
        isValid = false;
        errors.push('To\'g\'ri email manzil kiriting');
    }
    
    // First name
    const firstName = form.querySelector('#id_first_name').value.trim();
    if (!firstName) {
        isValid = false;
        errors.push('Ismingizni kiriting');
    }
    
    // Last name
    const lastName = form.querySelector('#id_last_name').value.trim();
    if (!lastName) {
        isValid = false;
        errors.push('Familiyangizni kiriting');
    }
    
    // Password
    const password1 = form.querySelector('#id_password1').value;
    if (!password1) {
        isValid = false;
        errors.push('Parol kiriting');
    } else if (password1.length < 8) {
        isValid = false;
        errors.push('Parol kamida 8 belgidan iborat bo\'lishi kerak');
    }
    
    // Password confirmation
    const password2 = form.querySelector('#id_password2').value;
    if (password1 !== password2) {
        isValid = false;
        errors.push('Parollar mos kelmadi');
    }
    
    // Terms agreement
    const terms = form.querySelector('#terms');
    if (terms && !terms.checked) {
        isValid = false;
        errors.push('Foydalanish shartlarini qabul qilishingiz kerak');
    }
    
    if (!isValid) {
        showAuthErrors(form, errors);
    }
    
    return isValid;
}

/**
 * Password strength checker
 */
function initPasswordStrength() {
    const passwordInput = document.getElementById('id_password1');
    if (!passwordInput) return;
    
    const strengthBar = document.getElementById('passwordStrength');
    const strengthText = document.getElementById('strengthText');
    
    if (!strengthBar || !strengthText) return;
    
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const strength = calculatePasswordStrength(password);
        
        // Update strength bar
        strengthBar.style.width = strength.percentage + '%';
        strengthBar.style.backgroundColor = strength.color;
        
        // Update text
        strengthText.textContent = 'Parol kuchi: ' + strength.text;
        strengthText.style.color = strength.color;
    });
}

function calculatePasswordStrength(password) {
    let strength = 0;
    
    // Length check
    if (password.length >= 8) strength += 1;
    if (password.length >= 12) strength += 1;
    
    // Character variety
    if (/[a-z]/.test(password)) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    
    // Calculate percentage
    const percentage = Math.min(100, strength * 20);
    
    // Determine strength level
    let text, color;
    if (strength <= 2) {
        text = 'Kuchsiz';
        color = '#dc3545';
    } else if (strength <= 4) {
        text = 'O\'rtacha';
        color = '#ffc107';
    } else {
        text = 'Kuchli';
        color = '#28a745';
    }
    
    return {
        percentage: percentage,
        text: text,
        color: color,
        level: strength
    };
}

/**
 * Auth forms umumiy funksiyalari
 */
function initAuthForms() {
    // Toggle password visibility
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
    
    // Auto-capitalize first letter for names
    const nameInputs = document.querySelectorAll('input[name="first_name"], input[name="last_name"]');
    nameInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = this.value.charAt(0).toUpperCase() + this.value.slice(1).toLowerCase();
            }
        });
    });
}

function showAuthErrors(form, errors) {
    // Clear previous errors
    const oldAlerts = form.querySelectorAll('.auth-alert');
    oldAlerts.forEach(alert => alert.remove());
    
    // Create error alert
    if (errors.length > 0) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger auth-alert';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            <strong>Quyidagi xatoliklarni tuzating:</strong>
            <ul class="mb-0 mt-2">
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
        `;
        
        form.insertBefore(alertDiv, form.firstChild);
        
        // Scroll to errors
        alertDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Social login funksiyalari
 */
function initSocialLogin() {
    const socialButtons = document.querySelectorAll('.btn-social');
    socialButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const provider = this.classList.contains('google') ? 'google' :
                           this.classList.contains('telegram') ? 'telegram' :
                           this.classList.contains('facebook') ? 'facebook' : 'unknown';
            
            // Show loading
            const originalHTML = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Kirilmoqda...';
            this.disabled = true;
            
            // Mock social login
            setTimeout(() => {
                this.innerHTML = originalHTML;
                this.disabled = false;
                
                // In a real app, this would redirect to OAuth endpoint
                showToast(`${provider.charAt(0).toUpperCase() + provider.slice(1)} orqali kirish hozircha mavjud emas`, 'info');
            }, 1500);
        });
    });
}

/**
 * Yordamchi funksiyalar
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showLoading(element) {
    if (element) {
        const originalHTML = element.innerHTML;
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Amalga oshirilmoqda...';
        element.disabled = true;
        element.dataset.originalHtml = originalHTML;
    }
}

function hideLoading(element) {
    if (element && element.dataset.originalHtml) {
        element.innerHTML = element.dataset.originalHtml;
        element.disabled = false;
        delete element.dataset.originalHtml;
    }
}

function showFieldError(field, message) {
    // Remove existing error
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback d-block';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle me-1"></i> ${message}`;
    
    field.classList.add('is-invalid');
    field.parentNode.appendChild(errorDiv);
    
    // Scroll to field
    field.scrollIntoView({ behavior: 'smooth', block: 'center' });
    field.focus();
}