// =================== CHATBOT JAVASCRIPT ===================

class VeterinaryChatbot {
    constructor() {
        this.isRecording = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.currentLanguage = 'en';
        this.voices = [];
        this.settings = {
            ttsEnabled: true,
            voiceInputEnabled: true,
            darkModeEnabled: false,
            autoScrollEnabled: true,
            voiceLanguage: 'en-US'
        };
        
        this.init();
    }

    init() {
        try {
            console.log('🚀 Starting chatbot initialization...');
            
            this.loadSettings();
            console.log('✅ Settings loaded');
            
            this.setupEventListeners();
            console.log('✅ Event listeners setup complete');
            
            // Initialize speech features (non-critical)
            try {
                this.initializeSpeechRecognition();
                console.log('✅ Speech recognition initialized');
            } catch (speechError) {
                console.warn('⚠️ Speech recognition initialization failed:', speechError);
            }
            
            try {
                this.loadVoices();
                console.log('✅ Voices loaded');
            } catch (voiceError) {
                console.warn('⚠️ Voice loading failed:', voiceError);
            }
            
            try {
                this.loadLanguages();
                console.log('✅ Languages loading initiated');
            } catch (langError) {
                console.warn('⚠️ Language loading failed:', langError);
            }
            
            try {
                this.setupFileUpload();
                console.log('✅ File upload setup complete');
            } catch (fileError) {
                console.warn('⚠️ File upload setup failed:', fileError);
            }
            
            try {
                this.autoResizeTextarea();
                console.log('✅ Textarea auto-resize setup complete');
            } catch (resizeError) {
                console.warn('⚠️ Textarea resize setup failed:', resizeError);
            }
            
            // Set default language and voice (non-critical)
            try {
                this.updateVoiceLanguageForChat(this.currentLanguage);
                console.log('✅ Voice language updated');
            } catch (voiceLangError) {
                console.warn('⚠️ Voice language update failed:', voiceLangError);
            }
            
            // Check chatbot health (non-critical)
            try {
                this.checkChatbotHealth();
                console.log('✅ Health check initiated');
            } catch (healthError) {
                console.warn('⚠️ Health check failed:', healthError);
            }
            
            console.log('🎉 Veterinary Chatbot initialized successfully!');
            console.log('🌍 Current language:', this.currentLanguage);
            console.log('🗣️ Voice language:', this.settings.voiceLanguage);
            
        } catch (error) {
            console.error('❌ Critical error during chatbot initialization:', error);
            console.error('Stack trace:', error.stack);
            
            // Try minimal initialization
            this.setupBasicEventListeners();
        }
    }

    setupBasicEventListeners() {
        console.log('🔧 Setting up BASIC event listeners only...');
        
        try {
            const sendBtn = document.getElementById('sendBtn');
            if (sendBtn) {
                sendBtn.addEventListener('click', () => {
                    console.log('📤 Send button clicked (basic mode)');
                    const input = document.getElementById('messageInput');
                    if (input && input.value.trim()) {
                        // Use toast instead of alert
                        this.showToast('Basic mode: ' + input.value.trim(), 'info');
                        input.value = '';
                    }
                });
                console.log('✅ Basic send button listener added');
            }
            
            const voiceBtn = document.getElementById('voiceBtn');
            if (voiceBtn) {
                voiceBtn.addEventListener('click', () => {
                    console.log('🎤 Voice button clicked (basic mode)');
                    // Use toast instead of alert
                    this.showToast('Voice feature temporarily unavailable', 'error');
                });
                console.log('✅ Basic voice button listener added');
            }
            
        } catch (basicError) {
            console.error('❌ Even basic event listeners failed:', basicError);
        }
    }

    // =================== SETTINGS MANAGEMENT ===================

    loadSettings() {
        try {
            console.log('📋 Loading settings...');
            const savedSettings = localStorage.getItem('chatbot-settings');
            if (savedSettings) {
                this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
                console.log('✅ Settings loaded from localStorage');
            } else {
                console.log('ℹ️ No saved settings found, using defaults');
            }
            this.applySettings();
        } catch (error) {
            console.error('❌ Error loading settings:', error);
            console.log('🔄 Using default settings');
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('chatbot-settings', JSON.stringify(this.settings));
            console.log('💾 Settings saved successfully');
        } catch (error) {
            console.error('❌ Error saving settings:', error);
        }
    }

    applySettings() {
        try {
            console.log('🎨 Applying settings...');
            
            // Apply dark mode
            if (this.settings.darkModeEnabled) {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }

            // Apply other settings if elements exist
            const ttsCheckbox = document.getElementById('ttsEnabled');
            if (ttsCheckbox) {
                ttsCheckbox.checked = this.settings.ttsEnabled;
            }

            const voiceCheckbox = document.getElementById('voiceInputEnabled');
            if (voiceCheckbox) {
                voiceCheckbox.checked = this.settings.voiceInputEnabled;
            }

            const darkCheckbox = document.getElementById('darkModeEnabled');
            if (darkCheckbox) {
                darkCheckbox.checked = this.settings.darkModeEnabled;
            }

            const scrollCheckbox = document.getElementById('autoScrollEnabled');
            if (scrollCheckbox) {
                scrollCheckbox.checked = this.settings.autoScrollEnabled;
            }

            const voiceLanguageSelect = document.getElementById('voiceLanguageSelect');
            if (voiceLanguageSelect) {
                voiceLanguageSelect.value = this.settings.voiceLanguage;
            }
            
            console.log('✅ Settings applied successfully');
        } catch (error) {
            console.error('❌ Error applying settings:', error);
        }
    }

    // =================== EVENT LISTENERS ===================

    setupEventListeners() {
        console.log('🔧 Setting up event listeners...');
        
        // Send message
        const sendBtn = document.getElementById('sendBtn');
        const messageInput = document.getElementById('messageInput');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                console.log('📤 Send button clicked!');
                this.sendMessage();
            });
            console.log('✅ Send button listener added');
        } else {
            console.error('❌ Send button not found!');
        }

        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    console.log('⌨️ Enter key pressed!');
                    this.sendMessage();
                }
            });
            
            messageInput.addEventListener('input', () => {
                this.updateSendButton();
                // Removed showSuggestions() to prevent popup during typing
                // this.showSuggestions();
            });
            console.log('✅ Message input listeners added');
        } else {
            console.error('❌ Message input not found!');
        }

        // Voice input
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => {
                console.log('🎤 Voice button clicked!');
                this.toggleVoiceInput();
            });
            console.log('✅ Voice button listener added');
        } else {
            console.error('❌ Voice button not found!');
        }

        // File upload
        const fileUploadBtn = document.getElementById('fileUploadBtn');
        if (fileUploadBtn) {
            fileUploadBtn.addEventListener('click', () => {
                console.log('📁 File upload button clicked!');
                this.triggerFileUpload();
            });
            console.log('✅ File upload button listener added');
        } else {
            console.error('❌ File upload button not found!');
        }

        // Clear chat
        const clearChatBtn = document.getElementById('clearChatBtn');
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => {
                console.log('🗑️ Clear chat button clicked!');
                this.clearChat();
            });
            console.log('✅ Clear chat button listener added');
        } else {
            console.error('❌ Clear chat button not found!');
        }

        // Settings
        const settingsBtn = document.getElementById('settingsBtn');
        const closeSettingsBtn = document.getElementById('closeSettingsBtn');
        const cancelSettingsBtn = document.getElementById('cancelSettingsBtn');
        
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                console.log('⚙️ Settings button clicked!');
                this.openSettings();
            });
            console.log('✅ Settings button listener added');
        } else {
            console.error('❌ Settings button not found!');
        }
        
        if (closeSettingsBtn) {
            closeSettingsBtn.addEventListener('click', () => {
                console.log('❌ Close settings button clicked!');
                this.closeSettings();
            });
            console.log('✅ Close settings button listener added');
        } else {
            console.error('❌ Close settings button not found!');
        }

        if (cancelSettingsBtn) {
            cancelSettingsBtn.addEventListener('click', () => {
                console.log('❌ Cancel settings button clicked!');
                this.closeSettings();
            });
            console.log('✅ Cancel settings button listener added');
        } else {
            console.error('❌ Cancel settings button not found!');
        }

        // Settings changes - only add if elements exist
        this.setupSettingsListeners();

        // Language selector
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                console.log('🌍 Language changed to:', e.target.value);
                this.currentLanguage = e.target.value;
                this.updateVoiceLanguageForChat(e.target.value);
            });
            console.log('✅ Language selector listener added');
        } else {
            console.error('❌ Language selector not found!');
        }

        // Quick actions
        this.setupQuickActions();

        // Input suggestions
        this.setupSuggestionListeners();

        console.log('✅ Event listeners setup completed');
    }

    setupSettingsListeners() {
        console.log('⚙️ Setting up settings listeners...');
        
        // Settings changes - only add if elements exist
        const ttsEnabled = document.getElementById('ttsEnabled');
        const voiceInputEnabled = document.getElementById('voiceInputEnabled');
        const darkModeEnabled = document.getElementById('darkModeEnabled');
        const autoScrollEnabled = document.getElementById('autoScrollEnabled');
        const voiceLanguageSelect = document.getElementById('voiceLanguageSelect');
        
        if (ttsEnabled) {
            ttsEnabled.addEventListener('change', (e) => {
                console.log('🔊 TTS setting changed:', e.target.checked);
                this.settings.ttsEnabled = e.target.checked;
                this.saveSettings();
            });
        }
        
        if (voiceInputEnabled) {
            voiceInputEnabled.addEventListener('change', (e) => {
                console.log('🎤 Voice input setting changed:', e.target.checked);
                this.settings.voiceInputEnabled = e.target.checked;
                this.saveSettings();
            });
        }
        
        if (darkModeEnabled) {
            darkModeEnabled.addEventListener('change', (e) => {
                console.log('🌙 Dark mode setting changed:', e.target.checked);
                this.settings.darkModeEnabled = e.target.checked;
                this.applySettings();
                this.saveSettings();
            });
        }
        
        if (autoScrollEnabled) {
            autoScrollEnabled.addEventListener('change', (e) => {
                console.log('📜 Auto-scroll setting changed:', e.target.checked);
                this.settings.autoScrollEnabled = e.target.checked;
                this.saveSettings();
            });
        }
        
        if (voiceLanguageSelect) {
            voiceLanguageSelect.addEventListener('change', (e) => {
                console.log('🗣️ Voice language setting changed:', e.target.value);
                this.settings.voiceLanguage = e.target.value;
                this.saveSettings();
            });
        }
    }

    setupQuickActions() {
        console.log('⚡ Setting up quick actions...');
        const quickActions = this.safeQuerySelectorAll('.quick-action');
        console.log(`Found ${quickActions.length} quick action buttons`);
        
        quickActions.forEach(btn => {
            if (btn && btn.addEventListener) {
                btn.addEventListener('click', (e) => {
                    const action = e.currentTarget.dataset.action;
                    console.log('⚡ Quick action clicked:', action);
                    this.handleQuickAction(action);
                });
            }
        });
    }

    setupSuggestionListeners() {
        console.log('💡 Setting up suggestion listeners...');
        const suggestions = this.safeQuerySelectorAll('.suggestion');
        console.log(`Found ${suggestions.length} suggestion items`);
        
        suggestions.forEach(suggestion => {
            if (suggestion && suggestion.addEventListener) {
                suggestion.addEventListener('click', (e) => {
                    const text = e.currentTarget.dataset.text;
                    console.log('💡 Suggestion clicked:', text);
                    const messageInput = document.getElementById('messageInput');
                    if (messageInput) {
                        messageInput.value = text;
                        this.updateSendButton();
                    }
                });
            }
        });
    }

    // =================== SPEECH RECOGNITION ===================

    initializeSpeechRecognition() {
        // Check if HTTPS is required and warn user
        if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
            console.warn('⚠️ Speech recognition may not work over HTTP. Consider using HTTPS.');
        }

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.maxAlternatives = 1;
            this.recognition.lang = this.settings.voiceLanguage || 'en-US';

            this.recognition.onstart = () => {
                console.log('🎤 Speech recognition started');
                this.isRecording = true;
                const voiceBtn = document.getElementById('voiceBtn');
                if (voiceBtn) {
                    voiceBtn.classList.add('recording');
                    const icon = this.safeQuerySelector(voiceBtn, 'i');
                    if (icon) {
                        icon.className = 'fas fa-stop';
                    }
                }
                this.showToast('🎤 Listening... Speak now', 'info');
            };

            this.recognition.onresult = (event) => {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const result = event.results[i];
                    if (result.isFinal) {
                        transcript += result[0].transcript;
                    }
                }
                
                if (transcript.trim()) {
                    console.log('🎤 Speech recognized:', transcript);
                    const messageInput = document.getElementById('messageInput');
                    if (messageInput) {
                        messageInput.value = transcript.trim();
                        this.updateSendButton();
                    }
                    this.hideToast('info');
                    this.showToast('✅ Speech captured successfully!', 'success');
                }
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopRecording();
                
                let errorMessage = 'Voice recognition error';
                switch (event.error) {
                    case 'network':
                        // Often 'network' errors are actually permission issues in disguise
                        errorMessage = '🎤 Microphone access issue - please click the microphone icon in your browser\'s address bar and allow access, then try again';
                        break;
                    case 'not-allowed':
                        errorMessage = 'Microphone access denied - please allow microphone permissions in your browser settings';
                        break;
                    case 'no-speech':
                        errorMessage = 'No speech detected - please speak clearly and try again';
                        break;
                    case 'audio-capture':
                        errorMessage = 'Audio capture failed - please check your microphone connection';
                        break;
                    case 'service-not-allowed':
                        errorMessage = 'Speech service not allowed - please check your browser settings';
                        break;
                    case 'bad-grammar':
                        errorMessage = 'Speech recognition grammar error - please try again';
                        break;
                    case 'language-not-supported':
                        errorMessage = 'Selected language not supported for speech recognition';
                        break;
                    default:
                        errorMessage = `Voice recognition error: ${event.error}. Please check microphone permissions and try again.`;
                }
                this.showToast('❌ ' + errorMessage, 'error');
            };

            this.recognition.onend = () => {
                console.log('🎤 Speech recognition ended');
                this.stopRecording();
            };
        } else {
            console.warn('Speech recognition not supported in this browser');
            this.settings.voiceInputEnabled = false;
            this.showToast('❌ Speech recognition not supported in this browser', 'error');
        }
    }

    async toggleVoiceInput() {
        if (!this.settings.voiceInputEnabled) {
            this.showToast('❌ Voice input is disabled in settings', 'error');
            return;
        }

        if (!this.recognition) {
            this.showToast('❌ Voice recognition not supported in this browser', 'error');
            return;
        }

        try {
            if (this.isRecording) {
                console.log('🛑 Stopping voice recognition');
                this.recognition.stop();
            } else {
                console.log('🎤 Starting voice recognition');
                
                // Check microphone permission first
                await this.checkMicrophonePermission();
                
                this.recognition.lang = this.settings.voiceLanguage || 'en-US';
                this.recognition.start();
            }
        } catch (error) {
            console.error('Voice recognition error:', error);
            if (error.message.includes('Microphone access denied')) {
                this.showToast('❌ Microphone access denied - please allow microphone permissions in your browser settings', 'error');
            } else if (error.message.includes('No microphone found')) {
                this.showToast('❌ No microphone found - please connect a microphone and try again', 'error');
            } else {
                this.showToast('❌ Failed to start voice recognition: ' + error.message, 'error');
            }
            this.stopRecording();
        }
    }

    async checkMicrophonePermission() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('MediaDevices not supported in this browser');
        }

        try {
            // Try to get microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            // Stop the stream immediately as we just needed to check permission
            stream.getTracks().forEach(track => track.stop());
            console.log('✅ Microphone permission granted');
            return true;
        } catch (error) {
            console.error('Microphone permission check failed:', error);
            if (error.name === 'NotAllowedError') {
                throw new Error('Microphone access denied by user');
            } else if (error.name === 'NotFoundError') {
                throw new Error('No microphone found');
            } else if (error.name === 'NotSupportedError') {
                throw new Error('Microphone not supported');
            } else if (error.name === 'NotReadableError') {
                throw new Error('Microphone is being used by another application');
            } else {
                throw new Error('Microphone access failed: ' + error.message);
            }
        }
    }

    stopRecording() {
        this.isRecording = false;
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.classList.remove('recording');
            const icon = this.safeQuerySelector(voiceBtn, 'i');
            if (icon) {
                icon.className = 'fas fa-microphone';
            }
        }
        this.hideToast('info');
    }

    // =================== TEXT-TO-SPEECH ===================

    loadVoices() {
        const updateVoices = () => {
            this.voices = this.synthesis.getVoices();
            console.log(`🔊 Loaded ${this.voices.length} voices`);
            
            // Log available languages for debugging
            if (this.voices.length > 0) {
                const languages = [...new Set(this.voices.map(v => v.lang))].sort();
                console.log('🌍 Available voice languages:', languages);
                
                // Check for Indian languages specifically
                const indianLangs = languages.filter(lang => lang.includes('-IN'));
                if (indianLangs.length > 0) {
                    console.log('🇮🇳 Indian language voices found:', indianLangs);
                }
            }
        };
        
        updateVoices();
        
        // Voices might load asynchronously
        if (this.voices.length === 0) {
            this.synthesis.onvoiceschanged = updateVoices;
        }
    }

    // =================== HELPER FUNCTIONS ===================
    
    safeQuerySelector(element, selector) {
        try {
            if (!element) return null;
            return element.querySelector(selector);
        } catch (error) {
            console.warn(`⚠️ QuerySelector error for "${selector}":`, error);
            return null;
        }
    }
    
    safeQuerySelectorAll(selector) {
        try {
            return document.querySelectorAll(selector) || [];
        } catch (error) {
            console.warn(`⚠️ QuerySelectorAll error for "${selector}":`, error);
            return [];
        }
    }

    // =================== DEBUG FUNCTIONS ===================
    
    // Test TTS in different languages (call from browser console: chatbot.testTTS('hi'))
    testTTS(langCode = 'en') {
        console.log(`🧪 Testing TTS for language: ${langCode}`);
        
        // Update language temporarily
        const originalLang = this.currentLanguage;
        this.currentLanguage = langCode;
        this.updateVoiceLanguageForChat(langCode);
        
        // Test phrases for different languages
        const testPhrases = {
            'en': 'Hello, this is a test of English text to speech.',
            'hi': 'नमस्ते, यह हिंदी टेक्स्ट टू स्पीच का परीक्षण है।',
            'mr': 'नमस्कार, हे मराठी मजकूर ते भाषण चाचणी आहे।',
            'ta': 'வணக்கம், இது தமிழ் உரை மொழி சோதனை ஆகும்।',
            'te': 'నమస్కారం, ఇది తెలుగు టెక్స్ట్ టు స్పీచ్ పరీక్ష।'
        };
        
        const testText = testPhrases[langCode] || testPhrases['en'];
        console.log(`🔊 Speaking: "${testText}"`);
        this.speak(testText);
        
        // Restore original language after a delay
        setTimeout(() => {
            this.currentLanguage = originalLang;
            this.updateVoiceLanguageForChat(originalLang);
        }, 100);
    }
    
    // List all available voices (call from console: chatbot.listVoices())
    listVoices() {
        console.log('🔊 All available voices:');
        this.voices.forEach((voice, index) => {
            console.log(`${index + 1}. ${voice.name} (${voice.lang}) - ${voice.default ? 'DEFAULT' : 'available'}`);
        });
        return this.voices;
    }

    speak(text) {
        if (!this.settings.ttsEnabled || !text || !text.trim()) {
            console.log('🔇 TTS disabled or empty text');
            return;
        }

        try {
            // Stop any ongoing speech
            this.synthesis.cancel();

            // Clean up text for better speech
            const cleanText = text
                .replace(/[🔥🩺💉🐄🐮🐎🐑🐷🐔🌡️💧😷🦵🥛]/g, '') // Remove emojis
                .replace(/\*\*(.*?)\*\*/g, '$1') // Remove markdown bold
                .replace(/\*(.*?)\*/g, '$1') // Remove markdown italic
                .replace(/`(.*?)`/g, '$1') // Remove code blocks
                .trim();

            if (!cleanText) return;

            const utterance = new SpeechSynthesisUtterance(cleanText);
            
            // Use the current voice language setting (which gets updated when chat language changes)
            const voiceLang = this.settings.voiceLanguage || 'en-US';
            console.log(`🔊 Speaking in language: ${voiceLang} (chat language: ${this.currentLanguage})`);
            
            // Use the pre-selected voice from settings if available
            if (this.settings.selectedVoice) {
                utterance.voice = this.settings.selectedVoice;
                utterance.lang = this.settings.selectedVoice.lang;
                console.log(`🔊 Using pre-selected voice: ${this.settings.selectedVoice.name} (${this.settings.selectedVoice.lang})`);
            } else {
                // Find the best matching voice for the selected language
                let voice = null;
                
                // First, try exact match with the voice language
                voice = this.voices.find(v => 
                    v.lang.toLowerCase() === voiceLang.toLowerCase()
                );
                
                // If no exact match, try matching just the language code (e.g., 'hi' from 'hi-IN')
                if (!voice) {
                    const langCode = voiceLang.split('-')[0];
                    voice = this.voices.find(v => 
                        v.lang.toLowerCase().startsWith(langCode.toLowerCase())
                    );
                }
                
                // Fallback to English if no voice found for the selected language
                if (!voice) {
                    voice = this.voices.find(v => v.lang.startsWith('en'));
                    console.warn(`⚠️ No voice found for ${voiceLang}, falling back to English`);
                }
                
                if (voice) {
                    utterance.voice = voice;
                    utterance.lang = voice.lang;
                    // Cache this voice selection for future use
                    this.settings.selectedVoice = voice;
                    console.log(`🔊 Selected and cached voice: ${voice.name} (${voice.lang})`);
                } else {
                    // If no voice is found, set the language manually
                    utterance.lang = voiceLang;
                    console.log(`🔊 No specific voice found, using language: ${voiceLang}`);
                }
            }
            
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 0.8;

            utterance.onstart = () => {
                console.log('🔊 TTS started');
            };

            utterance.onend = () => {
                console.log('🔊 TTS ended');
            };

            utterance.onerror = (event) => {
                console.error('TTS error:', event.error);
            };

            console.log(`🎯 Speaking text: "${cleanText.substring(0, 30)}..." in ${utterance.lang}`);
            this.synthesis.speak(utterance);
        } catch (error) {
            console.error('Text-to-speech error:', error);
        }
    }

    // =================== LANGUAGE MANAGEMENT ===================

    updateVoiceLanguageForChat(languageCode) {
        // Map chat language codes to speech recognition language codes
        const langMap = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'mr': 'mr-IN',
            'te': 'te-IN',
            'ta': 'ta-IN',
            'bn': 'bn-IN',
            'gu': 'gu-IN',
            'kn': 'kn-IN',
            'ml': 'ml-IN',
            'pa': 'pa-IN',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE'
        };
        
        const voiceLang = langMap[languageCode] || 'en-US';
        this.settings.voiceLanguage = voiceLang;
        this.saveSettings();
        
        // Update voice language selector if it exists
        const voiceSelect = document.getElementById('voiceLanguageSelect');
        if (voiceSelect) {
            voiceSelect.value = voiceLang;
        }
        
        // Force voice selection to update for the new language
        this.selectVoiceForLanguage(voiceLang);
        
        console.log(`🗣️ Voice language updated to: ${voiceLang} for chat language: ${languageCode}`);
    }

    async loadLanguages() {
        try {
            const response = await fetch('/api/chat/languages');
            const data = await response.json();
            
            if (data.success) {
                const select = document.getElementById('languageSelect');
                select.innerHTML = '';
                
                Object.entries(data.languages).forEach(([code, name]) => {
                    const option = document.createElement('option');
                    option.value = code;
                    option.textContent = name;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading languages:', error);
        }
    }

    // =================== MESSAGE HANDLING ===================

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();

        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);
        
        // Clear input
        input.value = '';
        this.updateSendButton();
        
        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    language: this.currentLanguage
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.hideTypingIndicator();
                this.addMessage('bot', data.response);
                this.speak(data.response);
            } else {
                this.hideTypingIndicator();
                // Handle improved error responses
                if (data.fallback_response) {
                    this.addMessage('bot', data.fallback_response);
                    this.speak(data.fallback_response);
                } else {
                    this.addMessage('bot', `❌ ${data.error || 'Sorry, I encountered an error. Please try again.'}`);
                }
                
                // Show error toast with more detail
                this.showToast(data.error || 'Service temporarily unavailable', 'error');
                console.error('Chat error:', data.error);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            
            // More helpful error message for network issues
            const errorMessage = error.message.includes('fetch') 
                ? 'Unable to connect to the server. Please check your internet connection and try again.'
                : `An error occurred: ${error.message}`;
            
            this.addMessage('bot', `❌ ${errorMessage}`);
            this.showToast('Connection failed: ' + error.message, 'error');
        }
        // Removed the finally block with hideLoading() since we removed showLoading()
    }

    addMessage(sender, text) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const timestamp = new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-user-md'}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(text)}</div>
                <div class="message-timestamp">${timestamp}</div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        
        if (this.settings.autoScrollEnabled) {
            this.scrollToBottom();
        }
    }

    formatMessage(text) {
        // Convert markdown-like formatting
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        text = text.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Convert newlines to breaks
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message';
        typingDiv.id = 'typingIndicator';

        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user-md"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span>AI is thinking</span>
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        `;

        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // =================== FILE HANDLING ===================

    setupFileUpload() {
        try {
            console.log('📁 Setting up file upload...');
            
            const fileInput = document.getElementById('fileInput');
            const uploadArea = document.getElementById('fileUploadArea');

            if (fileInput) {
                fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files));
                console.log('✅ File input event listener added');
            } else {
                console.warn('⚠️ File input element not found');
            }

            if (uploadArea) {
                // Drag and drop
                uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    uploadArea.classList.add('dragover');
                });

                uploadArea.addEventListener('dragleave', () => {
                    uploadArea.classList.remove('dragover');
                });

                uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                    this.handleFileSelect(e.dataTransfer.files);
                });

                uploadArea.addEventListener('click', () => this.triggerFileUpload());
                console.log('✅ Upload area event listeners added');
            } else {
                console.warn('⚠️ Upload area element not found');
            }
        } catch (error) {
            console.error('❌ Error setting up file upload:', error);
        }
    }

    triggerFileUpload() {
        const uploadArea = document.getElementById('fileUploadArea');
        
        if (uploadArea.style.display === 'none' || !uploadArea.style.display) {
            uploadArea.style.display = 'block';
        } else {
            document.getElementById('fileInput').click();
        }
    }

    async handleFileSelect(files) {
        if (files.length === 0) return;

        const file = files[0];
        const maxSize = 16 * 1024 * 1024; // 16MB

        if (file.size > maxSize) {
            this.showToast('File too large. Maximum size is 16MB.', 'error');
            return;
        }

        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            this.showToast('Unsupported file type. Please upload images or PDF files.', 'error');
            return;
        }

        // Hide upload area
        document.getElementById('fileUploadArea').style.display = 'none';

        // Show file info message
        this.addMessage('user', `📎 Uploaded file: ${file.name} (${this.formatFileSize(file.size)})`);

        // Show immediate processing message instead of spinner
        this.addMessage('bot', '🔍 Analyzing your file, please wait...');

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('language', this.currentLanguage);
            formData.append('question', 'Please analyze this file and provide insights about animal health or disease information.');

            const response = await fetch('/api/chat/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            // Remove the "analyzing" message safely
            try {
                const messages = document.getElementById('chatMessages');
                if (messages) {
                    const lastMessage = messages.lastElementChild;
                    if (lastMessage && lastMessage.textContent && lastMessage.textContent.includes('Analyzing your file')) {
                        lastMessage.remove();
                    }
                }
            } catch (removeError) {
                console.warn('Could not remove analyzing message:', removeError);
            }

            if (data.success) {
                this.addMessage('bot', data.response);
                this.speak(data.response);
                
                if (data.type === 'image_analysis') {
                    this.showSidePanel('Image Analysis Results', data.response);
                }
            } else {
                // Handle improved error responses
                if (data.fallback_response) {
                    this.addMessage('bot', data.fallback_response);
                    this.speak(data.fallback_response);
                } else {
                    this.addMessage('bot', `❌ ${data.error || 'File analysis failed'}`);
                }
                
                // Show error toast with more detail
                this.showToast(data.error || 'File analysis service unavailable', 'error');
                console.error('File analysis error:', data.error);
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            
            // Remove the "analyzing" message safely
            try {
                const messages = document.getElementById('chatMessages');
                if (messages) {
                    const lastMessage = messages.lastElementChild;
                    if (lastMessage && lastMessage.textContent && lastMessage.textContent.includes('Analyzing your file')) {
                        lastMessage.remove();
                    }
                }
            } catch (removeError) {
                console.warn('Could not remove analyzing message:', removeError);
            }
            
            this.addMessage('bot', '❌ I encountered an error analyzing your file. Please try again.');
            this.showToast('File upload failed: ' + (error.message || 'Unknown error'), 'error');
        }
        // No finally block needed since we removed hideLoading()
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // =================== UI HELPERS ===================

    updateSendButton() {
        const input = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const hasText = input.value.trim().length > 0;
        
        sendBtn.disabled = !hasText;
        sendBtn.style.opacity = hasText ? '1' : '0.5';
    }

    showSuggestions() {
        const input = document.getElementById('messageInput');
        const suggestions = document.getElementById('inputSuggestions');
        
        if (input.value.length > 2 && input.value.length < 10) {
            suggestions.style.display = 'block';
        } else {
            suggestions.style.display = 'none';
        }
    }

    autoResizeTextarea() {
        try {
            const textarea = document.getElementById('messageInput');
            
            if (textarea) {
                textarea.addEventListener('input', () => {
                    textarea.style.height = 'auto';
                    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
                });
                console.log('✅ Textarea auto-resize enabled');
            } else {
                console.warn('⚠️ Message input textarea not found');
            }
        } catch (error) {
            console.error('❌ Error setting up textarea auto-resize:', error);
        }
    }

    scrollToBottom() {
        try {
            const messagesContainer = document.getElementById('chatMessages');
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        } catch (error) {
            console.error('❌ Error scrolling to bottom:', error);
        }
    }

    // =================== CHATBOT HEALTH ===================

    async checkChatbotHealth() {
        try {
            const response = await fetch('/api/chat/health');
            const data = await response.json();
            
            if (data.success && data.healthy) {
                console.log('✅ Chatbot service is healthy');
                console.log('🔧 Available services:', data.services);
            } else {
                console.warn('⚠️ Chatbot service issues detected:', data.message);
                this.showToast(`⚠️ Some chatbot features may be limited: ${data.message}`, 'info', 3000);
            }
        } catch (error) {
            console.error('❌ Failed to check chatbot health:', error);
            this.showToast('⚠️ Unable to verify chatbot status. Some features may be limited.', 'error', 5000);
        }
    }

    // =================== TTS VOICE MANAGEMENT ===================

    selectVoiceForLanguage(targetLanguage) {
        if (!window.speechSynthesis) {
            console.warn('⚠️ Speech synthesis not supported');
            return;
        }

        const voices = window.speechSynthesis.getVoices();
        console.log(`🔍 Selecting voice for language: ${targetLanguage} from ${voices.length} available voices`);

        // First try exact language match
        let selectedVoice = voices.find(voice => voice.lang === targetLanguage);
        
        // If no exact match, try language code match (e.g., 'hi-IN' matches 'hi')
        if (!selectedVoice) {
            const langCode = targetLanguage.split('-')[0];
            selectedVoice = voices.find(voice => voice.lang.startsWith(langCode));
        }

        // Default to English if no match found
        if (!selectedVoice) {
            selectedVoice = voices.find(voice => voice.lang.startsWith('en'));
        }

        if (selectedVoice) {
            this.settings.selectedVoice = selectedVoice;
            console.log(`✅ Selected voice: ${selectedVoice.name} (${selectedVoice.lang})`);
        } else {
            console.warn('⚠️ No suitable voice found, using system default');
        }
    }

    // =================== QUICK ACTIONS ===================

    handleQuickAction(action) {
        const messages = {
            symptoms: "What are the common symptoms I should look for in sick animals?",
            treatment: "Can you guide me through basic treatment options for common animal diseases?",
            prevention: "What prevention measures should I take to keep my animals healthy?",
            emergency: "I think my animal has an emergency. What should I do immediately?"
        };

        const message = messages[action];
        if (message) {
            document.getElementById('messageInput').value = message;
            this.updateSendButton();
        }
    }

    // =================== CHAT MANAGEMENT ===================

    async clearChat() {
        if (!confirm('Are you sure you want to clear the chat history?')) return;

        try {
            const response = await fetch('/api/chat/clear', {
                method: 'POST'
            });

            const data = await response.json();
            
            if (data.success) {
                // Clear UI safely
                const messagesContainer = document.getElementById('chatMessages');
                if (messagesContainer) {
                    const welcomeMessage = this.safeQuerySelector(messagesContainer, '.welcome-message');
                    messagesContainer.innerHTML = '';
                    if (welcomeMessage) {
                        messagesContainer.appendChild(welcomeMessage);
                    }
                }
                
                this.showToast('Chat cleared successfully', 'success');
            } else {
                throw new Error(data.error || 'Failed to clear chat');
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
            this.showToast('Failed to clear chat: ' + error.message, 'error');
        }
    }

    // =================== MODALS ===================

    showLoading(text = 'Processing...') {
        const modal = document.getElementById('loadingModal');
        const loadingText = document.getElementById('loadingText');
        loadingText.textContent = text;
        modal.style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingModal').style.display = 'none';
    }

    openSettings() {
        document.getElementById('settingsModal').style.display = 'flex';
    }

    closeSettings() {
        document.getElementById('settingsModal').style.display = 'none';
    }

    showSidePanel(title, content) {
        const panel = document.getElementById('sidePanel');
        if (!panel) {
            console.warn('⚠️ Side panel element not found');
            return;
        }
        
        const header = this.safeQuerySelector(panel, '.side-panel-header h3');
        const contentDiv = document.getElementById('sidePanelContent');
        
        if (header) {
            header.textContent = title;
        }
        
        if (contentDiv) {
            contentDiv.innerHTML = `<div class="analysis-content">${this.formatMessage(content)}</div>`;
        }
        
        panel.style.display = 'flex';
    }

    closeSidePanel() {
        document.getElementById('sidePanel').style.display = 'none';
    }

    // =================== NOTIFICATIONS ===================

    showToast(message, type = 'error', duration = 5000) {
        // Map toast types to actual toast elements
        let toastId, messageId;
        
        switch(type) {
            case 'success':
                toastId = 'successToast';
                messageId = 'successMessage';
                break;
            case 'info':
                toastId = 'successToast'; // Use success toast for info messages
                messageId = 'successMessage';
                break;
            case 'error':
            default:
                toastId = 'errorToast';
                messageId = 'errorMessage';
        }
        
        const toast = document.getElementById(toastId);
        const messageElement = document.getElementById(messageId);
        
        if (toast && messageElement) {
            messageElement.textContent = message;
            toast.style.display = 'flex';
            
            // Auto hide after duration
            setTimeout(() => {
                this.hideToast(type);
            }, duration);
        } else {
            // Fallback to console if toast elements don't exist
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    hideToast(type) {
        // Map toast types to actual toast elements
        let toastId;
        
        switch(type) {
            case 'success':
            case 'info':
                toastId = 'successToast';
                break;
            case 'error':
            default:
                toastId = 'errorToast';
        }
        
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.style.display = 'none';
        }
    }
}

// =================== INITIALIZATION ===================

// Initialize the chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.veterinaryChatbot = new VeterinaryChatbot();
        // Add shorter alias for console testing
        window.chatbot = window.veterinaryChatbot;
        console.log('✅ Chatbot initialization completed successfully');
        console.log('🧪 For testing: Use chatbot.testTTS("hi") or chatbot.listVoices() in console');
    } catch (error) {
        console.error('❌ Chatbot initialization failed:', error);
        
        // Show error message to user
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f44336;
            color: white;
            padding: 15px;
            border-radius: 5px;
            z-index: 10000;
            max-width: 300px;
        `;
        errorDiv.innerHTML = `
            <strong>⚠️ Initialization Error</strong><br>
            Some chatbot features may not work properly.<br>
            Please refresh the page.
        `;
        document.body.appendChild(errorDiv);
        
        // Auto-remove error after 10 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 10000);
    }
});

// Handle page visibility changes for speech synthesis
document.addEventListener('visibilitychange', () => {
    try {
        if (document.hidden && window.speechSynthesis && window.speechSynthesis.speaking) {
            window.speechSynthesis.pause();
        } else if (!document.hidden && window.speechSynthesis && window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
        }
    } catch (error) {
        console.warn('Speech synthesis visibility handling error:', error);
    }
});

// Handle beforeunload to cleanup speech
window.addEventListener('beforeunload', () => {
    try {
        if (window.speechSynthesis && window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }
    } catch (error) {
        console.warn('Speech synthesis cleanup error:', error);
    }
});