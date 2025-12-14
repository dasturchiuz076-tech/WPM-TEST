class WPMTester {
    constructor() {
        this.initElements();
        this.initVariables();
        this.initEventListeners();
        this.initChart();
        this.loadSettings();
        this.loadStats();
        this.generateNewText();
        this.updateDisplay();
    }

    initElements() {
        // UI elementlari
        this.elements = {
            textDisplay: document.getElementById('textDisplay'),
            textInput: document.getElementById('textInput'),
            startBtn: document.getElementById('startBtn'),
            pauseBtn: document.getElementById('pauseBtn'),
            restartBtn: document.getElementById('restartBtn'),
            newTextBtn: document.getElementById('newTextBtn'),
            leaderboardBtn: document.getElementById('leaderboardBtn'),
            applySettings: document.getElementById('applySettings'),
            resultsPanel: document.getElementById('resultsPanel'),
            
            // Statistikalar
            liveWPM: document.getElementById('liveWPM'),
            liveAccuracy: document.getElementById('liveAccuracy'),
            liveTimer: document.getElementById('liveTimer'),
            liveErrors: document.getElementById('liveErrors'),
            bestWPM: document.getElementById('bestWPM'),
            totalTests: document.getElementById('totalTests'),
            avgWPM: document.getElementById('avgWPM'),
            avgAccuracy: document.getElementById('avgAccuracy'),
            totalWords: document.getElementById('totalWords'),
            
            // Natijalar
            resultWPM: document.getElementById('resultWPM'),
            resultAccuracy: document.getElementById('resultAccuracy'),
            resultErrors: document.getElementById('resultErrors'),
            resultTime: document.getElementById('resultTime'),
            
            // Sozlamalar
            timeSelect: document.getElementById('timeSelect'),
            difficultySelect: document.getElementById('difficultySelect'),
            languageSelect: document.getElementById('languageSelect'),
            backspaceToggle: document.getElementById('backspaceToggle'),
            soundToggle: document.getElementById('soundToggle'),
            backspaceStatus: document.getElementById('backspaceStatus'),
            soundStatus: document.getElementById('soundStatus'),
            
            // Boshqalar
            progressBar: document.getElementById('progressBar'),
            textSource: document.getElementById('textSource'),
            wordCount: document.getElementById('wordCount'),
            charCount: document.getElementById('charCount'),
            themeToggle: document.getElementById('themeToggle'),
            version: document.getElementById('version')
        };
    }

    initVariables() {
        // Test holati
        this.state = {
            isActive: false,
            isPaused: false,
            timeLeft: 60,
            totalTime: 60,
            startTime: null,
            timer: null,
            
            // Statistikalar
            correctChars: 0,
            totalTypedChars: 0,
            errors: 0,
            currentWordIndex: 0,
            wordsTyped: 0,
            
            // Matn
            currentText: '',
            words: [],
            language: 'uz',
            difficulty: 'medium',
            
            // Sozlamalar
            allowBackspace: true,
            soundEnabled: true,
            
            // Natijalar tarixi
            history: [],
            bestWPM: 0,
            totalTests: 0,
            totalWordsTyped: 0
        };

        // Matnlar bazasi
        this.textDatabase = {
            uz: {
                easy: [
                "Salom, yaxshimisiz? Bugun havo juda yaxshi. Keling, birga dars qilamiz. Kitob o'qish foydali mashg'ulot. Har kuni yangi so'z o'rganing. O'zbekiston go'zal mamlakat. Unda ko'plab tarixiy joylar bor. Dasturlash - zamonaviy kasb. Buni o'rganish uchun sabr kerak. Sport - sog'lom turmush kaliti. Har kuni jismoniy mashq qiling."
                ],
                medium: [
                    "JavaScript - bu dinamik, prototipga asoslangan dasturlash tili bo'lib, u asosan veb-brauzerlarda ishlatiladi. Sun'iy intellekt inson miyasining ishini takrorlashga qaratilgan texnologiya sohasidir. Tarixda ilm-fan rivojlanishi insoniyatning eng muhim yutuqlaridan biri bo'lgan. Iqtisodiy o'sish va barqaror rivojlanish har qanday davlatning asosiy maqsadlaridan biridir. Adabiyot inson ruhiyatini aks ettiruvchi san'at turi bo'lib, madaniyatning ajralmas qismidir."
                ],
                hard: [
                    "Kvant hisoblash - bu kvant mexanikasi hodisalaridan foydalanadigan hisoblash usuli bo'lib, klassik kompyuterlardan sezilarli darajada tezroq masalalarni hal qilishi mumkin. Neyron tarmoqlar sun'iy intellektning asosiy tarkibiy qismi bo'lib, inson miyasining ishlash printsipini taqlid qilishga harakat qiladi. Algoritmlarning murakkabligi va samaradorligini baholash - informatikaning asosiy yo'nalishlaridan biri hisoblanadi. Kriptografiya - bu axborotni himoya qilish fanidir. Zamonaviy kriptografiya raqamli imzolar, elektron pul va boshqalarni o'z ichiga oladi. Kosmik tadqiqotlar insoniyatning koinotni o'rganishdagi sa'y-harakatlarini ifodalaydi. Bu soha texnologiyaning eng yuqori cho'qqilarini talab qiladi."
                ],
                expert: [
                    "Kompleks tizimlarning xaotik xatti-harakati va fraktal geometriyaning o'zaro bog'liqligi zamonaviy matematikaning eng qizg'in mavzularidan biridir. Kvant gravitatsiyasi - bu kvant mexanikasi va umumiy nisbiylik nazariyasini birlashtirishga urinish bo'lib, fizikaning asosiy muammolaridan birini hal qilishga qaratilgan. Transhumanizm - bu insonning jismoniy va intellektual qobiliyatlarini ilmiy-texnikaviy yutuqlar orqali oshirishga qaratilgan falsafiy harakatdir. Sintetik biologiya - tirik organizmlarni dasturlash va ularning xususiyatlarini o'zgartirishga qaratilgan fan bo'lib, tibbiyot va biotexnologiyada inqilob qilmoqda. Kognitiv neyrologiya - miyaning qanday ishlashini o'rganadigan fan bo'lib, ong, xotira va qaror qabul qilish jarayonlarini tushunishga yordam beradi."
                ]
            },
            en: {
                easy: [
                    "The quick brown fox jumps over the lazy dog. This sentence uses all letters. Practice makes perfect. Keep typing every day to improve your skills. JavaScript is fun to learn. You can build amazing things with it. Technology changes rapidly. We must keep learning new things. Health is wealth. Take care of your body and mind every day." ],
                medium: [
                    "Artificial intelligence is transforming industries across the globe, creating new opportunities. The internet has connected people from different cultures and backgrounds like never before. Climate change represents one of the greatest challenges facing humanity today. Blockchain technology offers transparent and secure ways to transfer digital assets. Machine learning algorithms can recognize patterns in data that humans might miss."
                ],
                hard: [
                    "Quantum computing leverages quantum mechanical phenomena to perform computations exponentially faster than classical computers for certain problems. Neural architecture search automates the design of artificial neural networks, optimizing them for specific tasks through machine learning. Homomorphic encryption allows computations to be performed on encrypted data without decrypting it first, preserving privacy. The implementation of federated learning enables machine learning models to be trained across decentralized devices while keeping data localized. Explainable artificial intelligence aims to make the decision-making processes of AI systems transparent and understandable to human users."
                ]
            },
            ru: {
                easy: [
                    "Привет, как дела? Сегодня прекрасная погода. Давайте учиться вместе. Чтение книг полезно для ума. Учите новые слова каждый день. Россия - большая страна. Здесь много исторических мест. Программирование - современная профессия. Нужно терпение для обучения. Спорт - ключ к здоровой жизни. Занимайтесь физкультурой ежедневно."
                ],
                medium: [
                    "Искусственный интеллект преобразует промышленность по всему миру, создавая новые возможности.Интернет соединил людей из разных культур и слоев общества как никогда раньше.Климатические изменения представляют одну из величайших проблем, стоящих перед человечеством.Блокчейн технология предлагает прозрачные и безопасные способы передачи цифровых активов.Машинное обучение может распознавать закономерности в данных, которые люди могут пропустить."
                ]
            }
        };
    }

    initEventListeners() {
        // Tugmalar
        this.elements.startBtn.addEventListener('click', () => this.startTest());
        this.elements.pauseBtn.addEventListener('click', () => this.togglePause());
        this.elements.restartBtn.addEventListener('click', () => this.restartTest());
        this.elements.newTextBtn.addEventListener('click', () => this.generateNewText());
        this.elements.applySettings.addEventListener('click', () => this.saveSettings());
        this.elements.leaderboardBtn.addEventListener('click', () => this.showLeaderboard());
        
        // Matn kiritish
        this.elements.textInput.addEventListener('input', (e) => this.handleInput(e));
        this.elements.textInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Sozlamalar
        this.elements.backspaceToggle.addEventListener('change', () => this.updateToggleStatus());
        this.elements.soundToggle.addEventListener('change', () => this.updateToggleStatus());
        
        // Tema
        this.elements.themeToggle.addEventListener('click', () => this.toggleTheme());
        
        // Qisqartma tugmalari
        document.addEventListener('keydown', (e) => this.handleGlobalShortcuts(e));
        
        // Versiyani ko'rsatish
        this.elements.version.textContent = 'v2.1.0';
    }

    initChart() {
        const ctx = document.getElementById('statsChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'WPM',
                    data: [],
                    borderColor: '#4cc9f0',
                    backgroundColor: 'rgba(76, 201, 240, 0.1)',
                    tension: 0.4,
                    fill: true
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
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#8b949e'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#8b949e'
                        }
                    }
                }
            }
        });
    }

    loadSettings() {
        const settings = JSON.parse(localStorage.getItem('wpmSettings') || '{}');
        
        this.state.allowBackspace = settings.allowBackspace ?? true;
        this.state.soundEnabled = settings.soundEnabled ?? true;
        this.state.language = settings.language || 'uz';
        this.state.difficulty = settings.difficulty || 'medium';
        
        const savedTime = settings.testTime || '60';
        this.state.timeLeft = parseInt(savedTime);
        this.state.totalTime = parseInt(savedTime);
        
        // UI ni yangilash
        this.elements.timeSelect.value = savedTime;
        this.elements.difficultySelect.value = this.state.difficulty;
        this.elements.languageSelect.value = this.state.language;
        this.elements.backspaceToggle.checked = this.state.allowBackspace;
        this.elements.soundToggle.checked = this.state.soundEnabled;
        
        this.updateToggleStatus();
    }

    saveSettings() {
        const settings = {
            testTime: this.elements.timeSelect.value,
            difficulty: this.elements.difficultySelect.value,
            language: this.elements.languageSelect.value,
            allowBackspace: this.elements.backspaceToggle.checked,
            soundEnabled: this.elements.soundToggle.checked
        };
        
        localStorage.setItem('wpmSettings', JSON.stringify(settings));
        
        // Yangi sozlamalarni qo'llash
        this.loadSettings();
        this.generateNewText();
        
        // Xabar ko'rsatish
        this.showNotification('Sozlamalar saqlandi!', 'success');
    }

    loadStats() {
        const stats = JSON.parse(localStorage.getItem('wpmStats') || '{}');
        
        this.state.history = stats.history || [];
        this.state.bestWPM = stats.bestWPM || 0;
        this.state.totalTests = stats.totalTests || 0;
        this.state.totalWordsTyped = stats.totalWordsTyped || 0;
        
        // UI ni yangilash
        this.updateStatsDisplay();
        this.updateChart();
    }

    saveStats() {
        const stats = {
            history: this.state.history.slice(-50), // Oxirgi 50 ta natijani saqlash
            bestWPM: this.state.bestWPM,
            totalTests: this.state.totalTests,
            totalWordsTyped: this.state.totalWordsTyped,
            lastUpdated: new Date().toISOString()
        };
        
        localStorage.setItem('wpmStats', JSON.stringify(stats));
    }

    generateNewText() {
        const texts = this.textDatabase[this.state.language]?.[this.state.difficulty];
        
        if (texts && texts.length > 0) {
            const randomIndex = Math.floor(Math.random() * texts.length);
            this.state.currentText = texts[randomIndex];
            this.state.words = this.state.currentText.split(' ');
            
            this.updateTextDisplay();
            this.elements.textInput.value = '';
            this.resetTypingStats();
            
            // Matn manbasini ko'rsatish
            const sources = {
                uz: ['Oʻzbek adabiyoti', 'Ilmiy maqola', 'Texnologiya yangiliklari', 'Tarixiy matn', 'Darslik'],
                en: ['English Literature', 'Scientific Article', 'Technology News', 'Historical Text', 'Textbook'],
                ru: ['Русская литература', 'Научная статья', 'Технологические новости', 'Исторический текст', 'Учебник']
            };
            
            const source = sources[this.state.language] || sources.uz;
            this.elements.textSource.textContent = `Matn manbai: ${source[Math.floor(Math.random() * source.length)]}`;
            this.elements.wordCount.textContent = `Soʻzlar soni: ${this.state.words.length}`;
        }
    }

    updateTextDisplay() {
        const chars = this.state.currentText.split('');
        this.elements.textDisplay.innerHTML = chars.map((char, index) => 
            `<span class="char" id="char-${index}">${char}</span>`
        ).join('');
        
        // Kursor qo'shish
        const cursor = document.createElement('div');
        cursor.className = 'cursor';
        cursor.id = 'cursor';
        this.elements.textDisplay.appendChild(cursor);
        this.updateCursorPosition();
    }

    updateCursorPosition() {
        const cursor = document.getElementById('cursor');
        const currentChar = document.getElementById(`char-0`);
        
        if (cursor && currentChar) {
            const rect = currentChar.getBoundingClientRect();
            const containerRect = this.elements.textDisplay.getBoundingClientRect();
            
            cursor.style.left = `${rect.left - containerRect.left}px`;
            cursor.style.top = `${rect.top - containerRect.top}px`;
        }
    }

    startTest() {
        if (this.state.isActive && !this.state.isPaused) return;
        
        if (!this.state.isActive) {
            this.state.startTime = new Date();
            this.state.isActive = true;
            this.elements.textInput.disabled = false;
            this.elements.textInput.focus();
            this.resetTypingStats();
        }
        
        if (this.state.isPaused) {
            this.state.isPaused = false;
            this.state.startTime = new Date(Date.now() - (this.state.totalTime - this.state.timeLeft) * 1000);
        }
        
        this.startTimer();
        this.updateUIForActiveTest();
        this.playSound('start');
    }

    togglePause() {
        if (!this.state.isActive) return;
        
        this.state.isPaused = !this.state.isPaused;
        
        if (this.state.isPaused) {
            clearInterval(this.state.timer);
            this.elements.textInput.disabled = true;
            this.elements.pauseBtn.innerHTML = '<i class="fas fa-play"></i> Davom ettirish';
            this.playSound('pause');
        } else {
            this.state.startTime = new Date(Date.now() - (this.state.totalTime - this.state.timeLeft) * 1000);
            this.startTimer();
            this.elements.textInput.disabled = false;
            this.elements.textInput.focus();
            this.elements.pauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pauza';
            this.playSound('resume');
        }
    }

    startTimer() {
        clearInterval(this.state.timer);
        
        this.state.timer = setInterval(() => {
            if (this.state.isPaused) return;
            
            const elapsed = Math.floor((new Date() - this.state.startTime) / 1000);
            this.state.timeLeft = Math.max(0, this.state.totalTime - elapsed);
            
            this.elements.liveTimer.textContent = `${this.state.timeLeft}s`;
            
            // Progress barni yangilash
            const progress = ((this.state.totalTime - this.state.timeLeft) / this.state.totalTime) * 100;
            this.elements.progressBar.style.width = `${progress}%`;
            
            // Vaqt tugagan
            if (this.state.timeLeft <= 0) {
                this.endTest();
            }
            
            this.updateStats();
        }, 100);
    }

    handleInput(e) {
        if (!this.state.isActive || this.state.isPaused) return;
        
        const typedText = e.target.value;
        const originalText = this.state.currentText;
        
        this.state.totalTypedChars = typedText.length;
        
        // Har bir belgini tekshirish
        let correct = 0;
        let errors = 0;
        
        for (let i = 0; i < typedText.length; i++) {
            const charElement = document.getElementById(`char-${i}`);
            
            if (!charElement) continue;
            
            if (i < originalText.length && typedText[i] === originalText[i]) {
                charElement.className = 'char correct';
                correct++;
            } else {
                charElement.className = 'char incorrect';
                errors++;
                
                // Xato uchun animatsiya
                if (this.state.soundEnabled) {
                    charElement.classList.add('shake');
                    setTimeout(() => charElement.classList.remove('shake'), 300);
                }
            }
            
            // Kursor pozitsiyasini yangilash
            if (i === typedText.length - 1) {
                const nextChar = document.getElementById(`char-${typedText.length}`);
                const cursor = document.getElementById('cursor');
                
                if (cursor && nextChar) {
                    const rect = nextChar.getBoundingClientRect();
                    const containerRect = this.elements.textDisplay.getBoundingClientRect();
                    
                    cursor.style.left = `${rect.left - containerRect.left}px`;
                    cursor.style.top = `${rect.top - containerRect.top}px`;
                }
            }
        }
        
        // Qolgan belgilarni normal holatga qaytarish
        for (let i = typedText.length; i < originalText.length; i++) {
            const charElement = document.getElementById(`char-${i}`);
            if (charElement) {
                charElement.className = 'char';
            }
        }
        
        // Joriy belgini ko'rsatish
        const currentChar = document.getElementById(`char-${typedText.length}`);
        if (currentChar) {
            currentChar.classList.add('current');
        }
        
        this.state.correctChars = correct;
        this.state.errors = errors;
        this.state.wordsTyped = typedText.trim().split(/\s+/).length;
        
        // So'zlar sonini yangilash
        this.elements.charCount.textContent = `Belgilar: ${typedText.length}`;
        
        // Agar matn to'liq terilgan bo'lsa
        if (typedText === originalText) {
            setTimeout(() => {
                this.generateNewText();
                this.elements.textInput.value = '';
                this.resetTypingStats();
            }, 500);
        }
        
        this.updateStats();
    }

    handleKeyDown(e) {
        // Backspace nazorati
        if (e.key === 'Backspace' && !this.state.allowBackspace) {
            e.preventDefault();
            this.showNotification("Backspace ochirildi!", "warning");
            return;
        }
        
        // Testni boshlash
        if (e.key === ' ' && e.target === this.elements.textInput && !this.state.isActive) {
            e.preventDefault();
            this.startTest();
        }
    }

    handleGlobalShortcuts(e) {
        // Faqat Ctrl/Alt/Shift kombinatsiyalari va maxsus tugmalar
        if (e.ctrlKey || e.altKey || e.metaKey) {
            switch(e.key.toLowerCase()) {
                case 'r':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.restartTest();
                    }
                    break;
                case 's':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.elements.applySettings.click();
                    }
                    break;
                case 'p':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.togglePause();
                    }
                    break;
            }
        } else {
            switch(e.key) {
                case 'Escape':
                    e.preventDefault();
                    this.togglePause();
                    break;
                case 'Tab':
                    e.preventDefault();
                    this.generateNewText();
                    break;
                case ' ':
                    if (document.activeElement !== this.elements.textInput && !this.state.isActive) {
                        e.preventDefault();
                        this.startTest();
                    }
                    break;
            }
        }
    }

    updateStats() {
        if (!this.state.isActive || this.state.isPaused) return;
        
        const elapsed = Math.max(1, (new Date() - this.state.startTime) / 1000 / 60); // daqiqalarda
        const wpm = Math.round(this.state.wordsTyped / elapsed);
        const accuracy = this.state.totalTypedChars > 0 
            ? Math.round((this.state.correctChars / this.state.totalTypedChars) * 100)
            : 100;
        
        // Real vaqt statistikasi
        this.elements.liveWPM.textContent = wpm;
        this.elements.liveAccuracy.textContent = `${accuracy}%`;
        this.elements.liveErrors.textContent = this.state.errors;
        
        // Har 5 soniyada statistikani saqlash
        const currentSecond = Math.floor((this.state.totalTime - this.state.timeLeft));
        if (currentSecond % 5 === 0) {
            this.saveLiveStats(wpm, accuracy);
        }
    }

    saveLiveStats(wpm, accuracy) {
        // Real vaqt statistikasini saqlash (faqat grafik uchun)
        if (!this.liveStats) this.liveStats = [];
        this.liveStats.push({ wpm, accuracy, time: new Date() });
        
        // Faqat oxirgi 20 ta yozuvni saqlash
        if (this.liveStats.length > 20) {
            this.liveStats.shift();
        }
    }

    endTest() {
        clearInterval(this.state.timer);
        this.state.isActive = false;
        this.state.isPaused = false;
        
        // Yakuniy statistikani hisoblash
        const finalWPM = Math.round(this.state.wordsTyped / (this.state.totalTime / 60));
        const finalAccuracy = this.state.totalTypedChars > 0 
            ? Math.round((this.state.correctChars / this.state.totalTypedChars) * 100)
            : 0;
        
        // Natijalarni ko'rsatish
        this.showResults(finalWPM, finalAccuracy);
        
        // Rekordni yangilash
        if (finalWPM > this.state.bestWPM) {
            this.state.bestWPM = finalWPM;
            this.elements.bestWPM.textContent = `Rekord: ${finalWPM} WPM`;
            this.showNotification(`Yangi rekord: ${finalWPM} WPM! 🎉`, 'success');
            this.playSound('record');
        }
        
        // Umumiy statistikani yangilash
        this.state.totalTests++;
        this.state.totalWordsTyped += this.state.wordsTyped;
        
        // Tarixga qo'shish
        this.state.history.push({
            wpm: finalWPM,
            accuracy: finalAccuracy,
            errors: this.state.errors,
            time: new Date().toISOString(),
            language: this.state.language,
            difficulty: this.state.difficulty
        });
        
        // Saqlash
        this.saveStats();
        this.updateStatsDisplay();
        this.updateChart();
        
        // UI ni yangilash
        this.updateUIForInactiveTest();
        this.playSound('complete');
    }

    showResults(wpm, accuracy) {
        this.elements.resultWPM.textContent = wpm;
        this.elements.resultAccuracy.textContent = `${accuracy}%`;
        this.elements.resultErrors.textContent = this.state.errors;
        this.elements.resultTime.textContent = `${this.state.totalTime}s`;
        
        this.elements.resultsPanel.style.display = 'block';
        
        // WPM ga qarab rang berish
        const wpmElement = this.elements.resultWPM.parentElement;
        wpmElement.classList.remove('highlight');
        
        if (wpm >= 80) {
            wpmElement.style.background = 'linear-gradient(135deg, #2ecc71, #27ae60)';
        } else if (wpm >= 60) {
            wpmElement.style.background = 'linear-gradient(135deg, #3498db, #2980b9)';
        } else if (wpm >= 40) {
            wpmElement.style.background = 'linear-gradient(135deg, #f39c12, #e67e22)';
        } else {
            wpmElement.style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
        }
    }

    restartTest() {
        clearInterval(this.state.timer);
        
        this.state.isActive = false;
        this.state.isPaused = false;
        this.state.timeLeft = this.state.totalTime;
        
        this.elements.textInput.value = '';
        this.elements.textInput.disabled = true;
        this.resetTypingStats();
        
        this.updateTextDisplay();
        this.updateUIForInactiveTest();
        this.elements.resultsPanel.style.display = 'none';
        
        this.elements.liveTimer.textContent = `${this.state.timeLeft}s`;
        this.elements.progressBar.style.width = '0%';
        
        this.playSound('restart');
    }

    resetTypingStats() {
        this.state.correctChars = 0;
        this.state.totalTypedChars = 0;
        this.state.errors = 0;
        this.state.wordsTyped = 0;
        this.state.currentWordIndex = 0;
        
        this.elements.liveWPM.textContent = '0';
        this.elements.liveAccuracy.textContent = '100%';
        this.elements.liveErrors.textContent = '0';
        this.elements.charCount.textContent = 'Belgilar: 0';
    }

    updateUIForActiveTest() {
        this.elements.startBtn.disabled = true;
        this.elements.pauseBtn.disabled = false;
        this.elements.textInput.classList.add('active');
        
        this.elements.startBtn.innerHTML = '<i class="fas fa-running"></i> Test davom etmoqda';
        this.elements.pauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pauza';
    }

    updateUIForInactiveTest() {
        this.elements.startBtn.disabled = false;
        this.elements.pauseBtn.disabled = true;
        this.elements.textInput.classList.remove('active');
        
        this.elements.startBtn.innerHTML = '<i class="fas fa-play"></i> Testni Boshlash';
        this.elements.pauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pauza';
    }

    updateStatsDisplay() {
        this.elements.bestWPM.textContent = `Rekord: ${this.state.bestWPM} WPM`;
        this.elements.totalTests.textContent = `Testlar: ${this.state.totalTests}`;
        
        // Oʻrtacha WPM
        const avgWPM = this.state.history.length > 0
            ? Math.round(this.state.history.reduce((sum, test) => sum + test.wpm, 0) / this.state.history.length)
            : 0;
        this.elements.avgWPM.textContent = avgWPM;
        
        // Oʻrtacha aniqlik
        const avgAccuracy = this.state.history.length > 0
            ? Math.round(this.state.history.reduce((sum, test) => sum + test.accuracy, 0) / this.state.history.length)
            : 0;
        this.elements.avgAccuracy.textContent = `${avgAccuracy}%`;
        
        // Jami soʻzlar
        this.elements.totalWords.textContent = this.state.totalWordsTyped;
    }

    updateChart() {
        if (this.state.history.length === 0) return;
        
        const recentTests = this.state.history.slice(-10); // Oxirgi 10 ta test
        const labels = recentTests.map((_, i) => `Test ${i + 1}`);
        const data = recentTests.map(test => test.wpm);
        
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;
        this.chart.update();
    }

    updateToggleStatus() {
        this.elements.backspaceStatus.textContent = 
            this.elements.backspaceToggle.checked ? 'Yoqilgan' : 'Oʻchirilgan';
        
        this.elements.soundStatus.textContent = 
            this.elements.soundToggle.checked ? 'Yoqilgan' : 'Oʻchirilgan';
    }

    toggleTheme() {
        document.body.classList.toggle('light-theme');
        const icon = this.elements.themeToggle.querySelector('i');
        
        if (document.body.classList.contains('light-theme')) {
            icon.className = 'fas fa-sun';
            this.showNotification('Yorugʻ tema yoqildi', 'info');
        } else {
            icon.className = 'fas fa-moon';
            this.showNotification('Qorongʻu tema yoqildi', 'info');
        }
        
        // Chart ni yangilash
        this.chart.update();
    }

    showLeaderboard() {
        const leaderboard = this.state.history
            .sort((a, b) => b.wpm - a.wpm)
            .slice(0, 10);
        
        let leaderboardHTML = '<h3><i class="fas fa-trophy"></i> Eng yaxshi natijalar</h3><ol>';
        
        leaderboard.forEach((test, index) => {
            const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '🏅';
            const date = new Date(test.time).toLocaleDateString();
            leaderboardHTML += `
                <li>
                    ${medal} <strong>${test.wpm} WPM</strong> 
                    (${test.accuracy}% aniqlik) 
                    <span class="leaderboard-date">${date}</span>
                </li>
            `;
        });
        
        leaderboardHTML += '</ol>';
        
        // Modal oynada ko'rsatish
        this.showModal('Reyting jadvali', leaderboardHTML);
    }

    showModal(title, content) {
        // Mavjud modalni o'chirish
        const existingModal = document.querySelector('.modal');
        if (existingModal) existingModal.remove();
        
        // Yangi modal yaratish
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">${content}</div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Modal uchun CSS
        const style = document.createElement('style');
        style.textContent = `
            .modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
                backdrop-filter: blur(5px);
            }
            .modal-content {
                background: var(--card-bg);
                border-radius: 20px;
                padding: 30px;
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
            }
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            .modal-close {
                background: none;
                border: none;
                color: var(--text-secondary);
                font-size: 28px;
                cursor: pointer;
                transition: color 0.3s;
            }
            .modal-close:hover {
                color: var(--danger);
            }
            .leaderboard-date {
                font-size: 12px;
                color: var(--text-secondary);
                margin-left: 10px;
            }
        `;
        document.head.appendChild(style);
        
        // Yopish tugmasi
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.remove();
            style.remove();
        });
        
        // Tashqariga bosganda yopish
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
                style.remove();
            }
        });
    }

    showNotification(message, type = 'info') {
        // Mavjud bildirishnlarni o'chirish
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(n => n.remove());
        
        // Yangi bildirishn yaratish
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 
                                  type === 'warning' ? 'exclamation-triangle' : 
                                  type === 'error' ? 'times-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Bildirishn uchun CSS
        const style = document.createElement('style');
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--card-bg);
                border-radius: 12px;
                padding: 15px 25px;
                border-left: 5px solid;
                border-color: ${type === 'success' ? '#2ecc71' : 
                              type === 'warning' ? '#f39c12' : 
                              type === 'error' ? '#e74c3c' : '#3498db'};
                box-shadow: var(--shadow);
                z-index: 1001;
                animation: slideInRight 0.3s ease, fadeOut 0.3s ease 2.7s;
                animation-fill-mode: forwards;
                max-width: 400px;
            }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 15px;
                color: var(--text-primary);
            }
            .notification i {
                font-size: 20px;
                color: ${type === 'success' ? '#2ecc71' : 
                        type === 'warning' ? '#f39c12' : 
                        type === 'error' ? '#e74c3c' : '#3498db'};
            }
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes fadeOut {
                to { opacity: 0; transform: translateX(100%); }
            }
        `;
        document.head.appendChild(style);
        
        // 3 soniyadan keyin o'chirish
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
                style.remove();
            }
        }, 3000);
    }

    playSound(type) {
        if (!this.state.soundEnabled) return;
        
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        let frequency = 440;
        let duration = 0.1;
        
        switch(type) {
            case 'start':
                frequency = 523.25; // C5
                duration = 0.2;
                break;
            case 'pause':
                frequency = 392; // G4
                duration = 0.15;
                break;
            case 'resume':
                frequency = 493.88; // B4
                duration = 0.15;
                break;
            case 'complete':
                frequency = 659.25; // E5
                duration = 0.3;
                break;
            case 'record':
                frequency = 783.99; // G5
                duration = 0.4;
                break;
            case 'restart':
                frequency = 349.23; // F4
                duration = 0.15;
                break;
            case 'error':
                frequency = 220; // A3
                duration = 0.1;
                break;
        }
        
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + duration);
    }

    updateDisplay() {
        // Har 100ms da ekranni yangilash
        setInterval(() => {
            if (this.state.isActive && !this.state.isPaused) {
                this.updateCursorPosition();
            }
        }, 100);
    }
}

// Dasturni ishga tushirish
document.addEventListener('DOMContentLoaded', () => {
    const wpmTester = new WPMTester();
    
    // Global o'zgaruvchi (debug uchun)
    window.wpmTester = wpmTester;
    
    console.log('🚀 ProWPM Tester ishga tushdi!');
    console.log('Qisqartma tugmalari:');
    console.log('Space - Testni boshlash');
    console.log('Esc - Pauza');
    console.log('Tab - Yangi matn');
    console.log('Ctrl+R - Qayta boshlash');
    console.log('Ctrl+S - Sozlamalarni saqlash');
});