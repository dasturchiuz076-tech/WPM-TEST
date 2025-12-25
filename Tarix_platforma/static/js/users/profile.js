/**
 * Profile Page JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Avatar upload
    initAvatarUpload();
    
    // Profile form
    initProfileForm();
    
    // Security settings
    initSecuritySettings();
    
    // Activity tracking
    initActivityTracking();
    
    // Theme settings
    initThemeSettings();
    
    // Statistics
    initStatistics();
});

/**
 * Avatar upload funksiyalari
 */
function initAvatarUpload() {
    const avatarModal = document.getElementById('avatarModal');
    if (!avatarModal) return;
    
    const avatarInput = document.getElementById('avatarInput');
    const uploadBtn = document.getElementById('uploadAvatar');
    const saveBtn = document.getElementById('saveAvatar');
    const imagePreview = document.getElementById('imagePreview');
    const templateAvatars = document.querySelectorAll('.template-avatar');
    
    let selectedAvatar = null;
    
    // Open file dialog
    if (uploadBtn && avatarInput) {
        uploadBtn.addEventListener('click', function() {
            avatarInput.click();
        });
        
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                // Validate file
                if (!validateImageFile(file)) {
                    showToast('Rasm formati yoki hajmi noto\'g\'ri', 'danger');
                    return;
                }
                
                // Preview image
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded-circle">`;
                    selectedAvatar = {
                        type: 'upload',
                        data: e.target.result
                    };
                    
                    // Reset template selection
                    templateAvatars.forEach(t => t.classList.remove('selected'));
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Template avatar selection
    templateAvatars.forEach(avatar => {
        avatar.addEventListener('click', function() {
            const templateId = this.dataset.template;
            
            // Update selection
            templateAvatars.forEach(t => t.classList.remove('selected'));
            this.classList.add('selected');
            
            // Set preview
            const imgSrc = this.querySelector('img').src;
            imagePreview.innerHTML = `<img src="${imgSrc}" class="img-fluid rounded-circle">`;
            
            selectedAvatar = {
                type: 'template',
                template: templateId
            };
        });
    });
    
    // Save avatar
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            if (!selectedAvatar) {
                showToast('Iltimos, avatar tanlang yoki yuklang', 'warning');
                return;
            }
            
            showLoading(this);
            
            // Mock save - in real app, send to server
            setTimeout(() => {
                hideLoading(this);
                
                // Update main avatar preview
                const mainAvatar = document.getElementById('avatarPreview');
                if (mainAvatar) {
                    const newImage = imagePreview.querySelector('img');
                    if (newImage) {
                        if (mainAvatar.tagName === 'IMG') {
                            mainAvatar.src = newImage.src;
                        } else {
                            mainAvatar.innerHTML = `<img src="${newImage.src}" class="img-fluid rounded-circle">`;
                        }
                    }
                }
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(avatarModal);
                modal.hide();
                
                showToast('Avatar muvaffaqiyatli yangilandi!', 'success');
            }, 1500);
        });
    }
}

function validateImageFile(file) {
    // Check file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        return false;
    }
    
    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        return false;
    }
    
    return true;
}

/**
 * Profile form funksiyalari
 */
function initProfileForm() {
    const profileForm = document.getElementById('profileForm');
    if (!profileForm) return;
    
    // Bio character counter
    const bioTextarea = profileForm.querySelector('#bio');
    const bioCounter = document.getElementById('bioCounter');
    
    if (bioTextarea && bioCounter) {
        bioTextarea.addEventListener('input', function() {
            const length = this.value.length;
            bioCounter.textContent = `${length}/500`;
            
            if (length > 500) {
                bioCounter.classList.add('text-danger');
            } else {
                bioCounter.classList.remove('text-danger');
            }
        });
        
        // Initialize counter
        bioTextarea.dispatchEvent(new Event('input'));
    }
    
    // Date of birth validation
    const birthDateInput = profileForm.querySelector('#birth_date');
    if (birthDateInput) {
        birthDateInput.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const today = new Date();
            
            // Check if date is in future
            if (selectedDate > today) {
                showFieldError(this, 'Tug\'ilgan sana kelajakda bo\'lishi mumkin emas');
                return;
            }
            
            // Check if user is at least 13 years old
            const minDate = new Date();
            minDate.setFullYear(today.getFullYear() - 13);
            
            if (selectedDate > minDate) {
                showFieldError(this, 'Foydalanuvchi kamida 13 yoshda bo\'lishi kerak');
                return;
            }
            
            clearFieldError(this);
        });
    }
    
    // Form submission
    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validateProfileForm(this)) {
            return;
        }
        
        const submitBtn = this.querySelector('button[type="submit"]');
        showLoading(submitBtn);
        
        // Mock submission
        setTimeout(() => {
            hideLoading(submitBtn);
            showToast('Profil ma\'lumotlari muvaffaqiyatli yangilandi!', 'success');
            
            // In real app, this would be form.submit()
            // this.submit();
        }, 1500);
    });
}

function validateProfileForm(form) {
    let isValid = true;
    
    // First name
    const firstName = form.querySelector('#first_name').value.trim();
    if (!firstName) {
        showFieldError(form.querySelector('#first_name'), 'Ism kiriting');
        isValid = false;
    }
    
    // Last name
    const lastName = form.querySelector('#last_name').value.trim();
    if (!lastName) {
        showFieldError(form.querySelector('#last_name'), 'Familiya kiriting');
        isValid = false;
    }
    
    // Email
    const email = form.querySelector('#email').value.trim();
    if (!email) {
        showFieldError(form.querySelector('#email'), 'Email manzil kiriting');
        isValid = false;
    } else if (!isValidEmail(email)) {
        showFieldError(form.querySelector('#email'), 'To\'g\'ri email manzil kiriting');
        isValid = false;
    }
    
    // Bio length
    const bio = form.querySelector('#bio').value.trim();
    if (bio.length > 500) {
        showFieldError(form.querySelector('#bio'), 'Bio 500 belgidan oshmasligi kerak');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Security settings funksiyalari
 */
function initSecuritySettings() {
    // Password change form
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!validatePasswordForm(this)) {
                return;
            }
            
            const submitBtn = this.querySelector('button[type="submit"]');
            showLoading(submitBtn);
            
            // Mock submission
            setTimeout(() => {
                hideLoading(submitBtn);
                showToast('Parol muvaffaqiyatli yangilandi!', 'success');
                this.reset();
            }, 1500);
        });
    }
    
    // Two-factor authentication toggle
    const twoFactorToggle = document.getElementById('twoFactorToggle');
    if (twoFactorToggle) {
        twoFactorToggle.addEventListener('change', function() {
            if (this.checked) {
                showConfirm('Ikki faktorli autentifikatsiyani yoqmoqchimisiz? ' +
                          'Har safar kirishda Telegram orqali kod yuboriladi.', 
                          function() {
                    // In real app, enable 2FA
                    showToast('Ikki faktorli autentifikatsiya yoqildi', 'success');
                });
            } else {
                showConfirm('Ikki faktorli autentifikatsiyani o\'chirmoqchimisiz?', 
                          function() {
                    // In real app, disable 2FA
                    showToast('Ikki faktorli autentifikatsiya o\'chirildi', 'info');
                });
            }
        });
    }
    
    // Logout from all devices
    const logoutAllBtn = document.getElementById('logoutAll');
    if (logoutAllBtn) {
        logoutAllBtn.addEventListener('click', function() {
            showConfirm('Barcha qurilmalardan chiqmoqchimisiz? ' +
                       'Bu har qanday faol sessiyani tugatadi.', 
                       function() {
                showLoading(logoutAllBtn);
                
                setTimeout(() => {
                    hideLoading(logoutAllBtn);
                    showToast('Barcha qurilmalardan chiqildi', 'success');
                    // In real app, redirect to login page
                    // window.location.href = '/users/login/';
                }, 1500);
            });
        });
    }
    
    // Delete account
    const deleteAccountBtn = document.getElementById('confirmDeleteBtn');
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', function() {
            showConfirm('Hisobingizni o\'chirmoqchimisiz? ' +
                       'Bu amalni qaytarib bo\'lmaydi. ' +
                       'Barcha ma\'lumotlaringiz butunlay o\'chiriladi.', 
                       function() {
                showLoading(deleteAccountBtn);
                
                setTimeout(() => {
                    hideLoading(deleteAccountBtn);
                    showToast('Hisob o\'chirildi. Xayr!', 'info');
                    
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteAccountModal'));
                    modal.hide();
                    
                    // In real app, redirect to home page
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                }, 2000);
            });
        });
    }
}

function validatePasswordForm(form) {
    let isValid = true;
    
    const currentPassword = form.querySelector('#current_password').value;
    const newPassword = form.querySelector('#new_password').value;
    const confirmPassword = form.querySelector('#confirm_password').value;
    
    // Current password
    if (!currentPassword) {
        showFieldError(form.querySelector('#current_password'), 'Joriy parolni kiriting');
        isValid = false;
    }
    
    // New password
    if (!newPassword) {
        showFieldError(form.querySelector('#new_password'), 'Yangi parolni kiriting');
        isValid = false;
    } else if (newPassword.length < 8) {
        showFieldError(form.querySelector('#new_password'), 'Parol kamida 8 belgidan iborat bo\'lishi kerak');
        isValid = false;
    }
    
    // Confirm password
    if (!confirmPassword) {
        showFieldError(form.querySelector('#confirm_password'), 'Yangi parolni tasdiqlang');
        isValid = false;
    } else if (newPassword !== confirmPassword) {
        showFieldError(form.querySelector('#confirm_password'), 'Parollar mos kelmadi');
        isValid = false;
    }
    
    // Check if new password is same as current
    if (currentPassword && newPassword && currentPassword === newPassword) {
        showFieldError(form.querySelector('#new_password'), 'Yangi parol joriy paroldan farqli bo\'lishi kerak');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Activity tracking funksiyalari
 */
function initActivityTracking() {
    // Load more activities
    const loadMoreBtn = document.querySelector('.load-more-activities');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            showLoading(this);
            
            // Mock loading more activities
            setTimeout(() => {
                hideLoading(this);
                
                // Add mock activities
                const activityFeed = document.querySelector('.activity-feed');
                if (activityFeed) {
                    const newActivity = document.createElement('div');
                    newActivity.className = 'activity-item';
                    newActivity.innerHTML = `
                        <div class="activity-icon">
                            <i class="fas fa-eye"></i>
                        </div>
                        <div class="activity-content">
                            <div class="activity-text">Yangi mavzuni ko'rdi</div>
                            <div class="activity-time">hozirgina</div>
                        </div>
                    `;
                    activityFeed.appendChild(newActivity);
                }
                
                showToast('Qo\'shimcha faolliklar yuklandi', 'success');
            }, 1000);
        });
    }
    
    // Export activity data
    const exportBtn = document.querySelector('.export-activities');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            showLoading(this);
            
            setTimeout(() => {
                hideLoading(this);
                showToast('Faollik ma\'lumotlari yuklab olindi', 'success');
            }, 1500);
        });
    }
}

/**
 * Theme settings funksiyalari
 */
function initThemeSettings() {
    // Theme selection
    const themeOptions = document.querySelectorAll('.theme-option');
    themeOptions.forEach(option => {
        option.addEventListener('click', function() {
            const theme = this.dataset.theme;
            
            // Update selection
            themeOptions.forEach(o => o.classList.remove('active'));
            this.classList.add('active');
            
            // Apply theme
            applyTheme(theme);
            
            // Save preference
            localStorage.setItem('theme', theme);
            showToast(`"${this.querySelector('span').textContent}" mavzusi tanlandi`, 'success');
        });
    });
    
    // Font size control
    const decreaseFont = document.getElementById('decreaseFont');
    const increaseFont = document.getElementById('increaseFont');
    const fontSizeValue = document.getElementById('fontSizeValue');
    
    if (decreaseFont && increaseFont && fontSizeValue) {
        let fontSize = parseInt(localStorage.getItem('fontSize') || 16);
        updateFontSize();
        
        decreaseFont.addEventListener('click', function() {
            if (fontSize > 12) {
                fontSize--;
                updateFontSize();
            }
        });
        
        increaseFont.addEventListener('click', function() {
            if (fontSize < 24) {
                fontSize++;
                updateFontSize();
            }
        });
        
        function updateFontSize() {
            fontSizeValue.textContent = fontSize + 'px';
            document.documentElement.style.fontSize = fontSize + 'px';
            localStorage.setItem('fontSize', fontSize);
        }
    }
    
    // Notification toggles
    const notificationToggles = document.querySelectorAll('.form-check-input[type="checkbox"]');
    notificationToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const setting = this.id;
            const isEnabled = this.checked;
            
            // Save preference
            const settings = JSON.parse(localStorage.getItem('notificationSettings') || '{}');
            settings[setting] = isEnabled;
            localStorage.setItem('notificationSettings', JSON.stringify(settings));
            
            showToast(`Bildirishnoma ${isEnabled ? 'yoqildi' : 'o\'chirildi'}`, 'info');
        });
    });
}

function applyTheme(theme) {
    const body = document.body;
    
    // Remove existing theme classes
    body.classList.remove('theme-light', 'theme-dark');
    
    // Add new theme class
    body.classList.add(`theme-${theme}`);
    
    // Update CSS variables
    if (theme === 'dark') {
        document.documentElement.style.setProperty('--primary-color', '#1a252f');
        document.documentElement.style.setProperty('--secondary-color', '#3498db');
        document.documentElement.style.setProperty('--light-bg', '#2c3e50');
        document.documentElement.style.setProperty('--white', '#34495e');
        document.documentElement.style.setProperty('--text-dark', '#ecf0f1');
        document.documentElement.style.setProperty('--border-color', '#4a6572');
    } else {
        // Reset to light theme
        document.documentElement.style.setProperty('--primary-color', '#2c3e50');
        document.documentElement.style.setProperty('--secondary-color', '#3498db');
        document.documentElement.style.setProperty('--light-bg', '#f8f9fa');
        document.documentElement.style.setProperty('--white', '#ffffff');
        document.documentElement.style.setProperty('--text-dark', '#2c3e50');
        document.documentElement.style.setProperty('--border-color', '#dee2e6');
    }
}

/**
 * Statistics funksiyalari
 */
function initStatistics() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initProgressCharts();
    }
    
    // Progress bars animation
    const progressBars = document.querySelectorAll('.progress-bar-animated');
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 300);
    });
}

function initProgressCharts() {
    // Topic completion chart
    const topicCtx = document.getElementById('topicCompletionChart');
    if (topicCtx) {
        new Chart(topicCtx, {
            type: 'doughnut',
            data: {
                labels: ['Yakunlangan', 'Jarayonda', 'Boshlanmagan'],
                datasets: [{
                    data: [65, 20, 15],
                    backgroundColor: [
                        'rgba(39, 174, 96, 0.8)',
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(236, 240, 241, 0.8)'
                    ],
                    borderColor: [
                        'rgba(39, 174, 96, 1)',
                        'rgba(52, 152, 219, 1)',
                        'rgba(189, 195, 199, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Quiz performance chart
    const quizCtx = document.getElementById('quizPerformanceChart');
    if (quizCtx) {
        new Chart(quizCtx, {
            type: 'bar',
            data: {
                labels: ['Oson', 'O\'rta', 'Qiyin', 'Mutanosib'],
                datasets: [{
                    label: 'O\'rtacha ball (%)',
                    data: [85, 72, 58, 45],
                    backgroundColor: 'rgba(52, 152, 219, 0.8)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

/**
 * Yordamchi funksiyalar
 */
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
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showConfirm(message, callback) {
    if (window.confirm(message)) {
        callback();
    }
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