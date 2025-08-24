// JARVIS AI Assistant v2.0 - Main JavaScript

class JarvisApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.isRecording = false;
        this.isMonitoring = false;
        this.socket = null;
        this.systemResources = {
            cpu: 45,
            memory: 62,
            disk: 78,
            battery: 85
        };
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupSystemMonitoring();
        this.setupTimeDisplay();
        this.setupSocketConnection();
        this.setupEventListeners();
        this.loadCurrentPage();
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.getAttribute('data-page');
                this.navigateToPage(page);
            });
        });
    }

    navigateToPage(page) {
        // Update active navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');

        // Load page content
        this.loadPageContent(page);
        this.currentPage = page;
    }

    async loadPageContent(page) {
        try {
            const response = await fetch(`/${page}`);
            const html = await response.text();
            
            // Extract content from the response
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const content = doc.querySelector('.main-content');
            
            if (content) {
                document.querySelector('.main-content').innerHTML = content.innerHTML;
                this.setupPageSpecificHandlers(page);
            }
        } catch (error) {
            console.error('Error loading page:', error);
        }
    }

    setupPageSpecificHandlers(page) {
        switch (page) {
            case 'dashboard':
                this.setupDashboard();
                break;
            case 'voice-control':
                this.setupVoiceControl();
                break;
            case 'screen-vision':
                this.setupScreenVision();
                break;
            case 'chat-interface':
                this.setupChatInterface();
                break;
            case 'commands':
                this.setupCommands();
                break;
            case 'settings':
                this.setupSettings();
                break;
        }
    }

    setupDashboard() {
        this.updateSystemResources();
        this.loadRecentActivity();
    }

    setupVoiceControl() {
        const micButton = document.querySelector('.microphone-button');
        if (micButton) {
            micButton.addEventListener('click', () => {
                this.toggleVoiceRecording();
            });
        }

        this.setupDeviceSelection();
        this.updateAudioLevel();
    }

    setupScreenVision() {
        const startButton = document.querySelector('.btn-success');
        const stopButton = document.querySelector('.btn-danger');
        const screenshotButton = document.querySelector('.btn-secondary');

        if (startButton) {
            startButton.addEventListener('click', () => {
                this.startScreenMonitoring();
            });
        }

        if (stopButton) {
            stopButton.addEventListener('click', () => {
                this.stopScreenMonitoring();
            });
        }

        if (screenshotButton) {
            screenshotButton.addEventListener('click', () => {
                this.takeScreenshot();
            });
        }
    }

    setupChatInterface() {
        const sendButton = document.querySelector('.send-button');
        const chatInput = document.querySelector('.chat-input');
        const exportButton = document.querySelector('.btn-secondary');
        const clearButton = document.querySelector('.btn-danger');

        if (sendButton) {
            sendButton.addEventListener('click', () => {
                this.sendChatMessage();
            });
        }

        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendChatMessage();
                }
            });
        }

        if (exportButton) {
            exportButton.addEventListener('click', () => {
                this.exportChat();
            });
        }

        if (clearButton) {
            clearButton.addEventListener('click', () => {
                this.clearChat();
            });
        }
    }

    setupCommands() {
        const categoryItems = document.querySelectorAll('.category-item');
        categoryItems.forEach(item => {
            item.addEventListener('click', () => {
                this.filterCommands(item.textContent.trim());
            });
        });
    }

    setupSettings() {
        this.loadSettings();
        this.setupSettingsHandlers();
    }

    setupSystemMonitoring() {
        // Update system resources every 5 seconds
        setInterval(() => {
            this.updateSystemResources();
        }, 5000);
    }

    setupTimeDisplay() {
        const updateTime = () => {
            const now = new Date();
            const timeString = now.toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            });
            document.getElementById('time-display').textContent = timeString;
        };

        updateTime();
        setInterval(updateTime, 1000);
    }

    setupSocketConnection() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to JARVIS server');
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from JARVIS server');
            this.updateConnectionStatus(false);
        });

        this.socket.on('system_resources', (resources) => {
            this.updateSystemMetrics(resources);
        });

        this.socket.on('command_result', (data) => {
            this.handleCommandResult(data);
        });

        this.socket.on('command_error', (data) => {
            this.handleCommandError(data);
        });
    }

    setupEventListeners() {
        // Global event listeners
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                this.showCommandPalette();
            }
        });
    }

    updateSystemResources() {
        fetch('/api/system-status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.updateSystemMetrics(data.data.resources);
                    this.updateSystemStatus(data.data.system_status);
                }
            })
            .catch(error => {
                console.error('Error fetching system status:', error);
            });
    }

    updateSystemMetrics(resources) {
        this.systemResources = resources;
        
        document.getElementById('cpu-metric').textContent = `${resources.cpu}%`;
        document.getElementById('memory-metric').textContent = `${resources.memory}%`;
        document.getElementById('disk-metric').textContent = `${resources.disk}%`;
        document.getElementById('battery-metric').textContent = `${resources.battery}%`;

        // Update dashboard cards if on dashboard
        if (this.currentPage === 'dashboard') {
            const cpuCard = document.querySelector('.resource-card:nth-child(1) .resource-value');
            const memoryCard = document.querySelector('.resource-card:nth-child(2) .resource-value');
            const diskCard = document.querySelector('.resource-card:nth-child(3) .resource-value');
            const batteryCard = document.querySelector('.resource-card:nth-child(4) .resource-value');

            if (cpuCard) cpuCard.textContent = `${resources.cpu}%`;
            if (memoryCard) memoryCard.textContent = `${resources.memory}%`;
            if (diskCard) diskCard.textContent = `${resources.disk}%`;
            if (batteryCard) batteryCard.textContent = `${resources.battery}%`;
        }
    }

    updateSystemStatus(status) {
        Object.keys(status).forEach(key => {
            const statusElement = document.getElementById(`${key}-status`);
            if (statusElement) {
                const dot = statusElement.querySelector('.status-dot');
                if (status[key]) {
                    dot.classList.remove('offline');
                    dot.classList.add('online');
                } else {
                    dot.classList.remove('online');
                    dot.classList.add('offline');
                }
            }
        });
    }

    updateConnectionStatus(connected) {
        const statusDots = document.querySelectorAll('.connection-status .status-dot');
        statusDots.forEach(dot => {
            if (connected) {
                dot.classList.remove('offline');
                dot.classList.add('online');
            } else {
                dot.classList.remove('online');
                dot.classList.add('offline');
            }
        });
    }

    // Voice Control Methods
    async toggleVoiceRecording() {
        if (this.isRecording) {
            await this.stopVoiceRecording();
        } else {
            await this.startVoiceRecording();
        }
    }

    async startVoiceRecording() {
        try {
            const response = await fetch('/api/voice-control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action: 'start_listening' })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.isRecording = true;
                this.showVoiceModal();
                this.updateMicrophoneButton(true);
            }
        } catch (error) {
            console.error('Error starting voice recording:', error);
        }
    }

    async stopVoiceRecording() {
        try {
            const response = await fetch('/api/voice-control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action: 'stop_listening' })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.isRecording = false;
                this.hideVoiceModal();
                this.updateMicrophoneButton(false);
            }
        } catch (error) {
            console.error('Error stopping voice recording:', error);
        }
    }

    updateMicrophoneButton(recording) {
        const micButton = document.querySelector('.microphone-button');
        if (micButton) {
            if (recording) {
                micButton.classList.add('recording');
                micButton.innerHTML = '<i class="fas fa-stop"></i>';
            } else {
                micButton.classList.remove('recording');
                micButton.innerHTML = '<i class="fas fa-microphone"></i>';
            }
        }
    }

    showVoiceModal() {
        const modal = document.createElement('div');
        modal.className = 'voice-modal active';
        modal.innerHTML = `
            <div class="voice-modal-content">
                <button class="voice-modal-close">&times;</button>
                <div class="voice-modal-icon">
                    <i class="fas fa-microphone"></i>
                </div>
                <div class="voice-modal-title">Voice Input</div>
                <div class="voice-modal-status">Processing...</div>
                <div class="voice-modal-transcript">
                    <div class="transcript-label">Transcript:</div>
                    <div class="transcript-text">Listening...</div>
                </div>
                <div class="voice-modal-recording">
                    <span class="recording-dot"></span>
                    Recording Active
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close modal functionality
        const closeBtn = modal.querySelector('.voice-modal-close');
        closeBtn.addEventListener('click', () => {
            this.hideVoiceModal();
        });
    }

    hideVoiceModal() {
        const modal = document.querySelector('.voice-modal');
        if (modal) {
            modal.remove();
        }
    }

    updateAudioLevel() {
        const audioLevelFill = document.querySelector('.audio-level-fill');
        if (audioLevelFill) {
            // Simulate audio level
            const level = this.isRecording ? Math.random() * 100 : 0;
            audioLevelFill.style.width = `${level}%`;
        }
    }

    setupDeviceSelection() {
        const deviceOptions = document.querySelectorAll('.device-option');
        deviceOptions.forEach(option => {
            option.addEventListener('click', () => {
                const radio = option.querySelector('.device-radio');
                const group = radio.closest('.device-group');
                
                // Remove selection from other options in the same group
                group.querySelectorAll('.device-radio').forEach(r => {
                    r.classList.remove('selected');
                });
                
                // Select this option
                radio.classList.add('selected');
            });
        });
    }

    // Screen Vision Methods
    async startScreenMonitoring() {
        try {
            const response = await fetch('/api/screen-vision', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action: 'start_monitoring' })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.isMonitoring = true;
                this.updateScreenViewer(true);
                this.updateMonitoringButton(true);
            }
        } catch (error) {
            console.error('Error starting screen monitoring:', error);
        }
    }

    async stopScreenMonitoring() {
        try {
            const response = await fetch('/api/screen-vision', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action: 'stop_monitoring' })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.isMonitoring = false;
                this.updateScreenViewer(false);
                this.updateMonitoringButton(false);
            }
        } catch (error) {
            console.error('Error stopping screen monitoring:', error);
        }
    }

    async takeScreenshot() {
        try {
            const response = await fetch('/api/screen-vision', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action: 'take_screenshot' })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.showNotification('Screenshot taken successfully', 'success');
            }
        } catch (error) {
            console.error('Error taking screenshot:', error);
        }
    }

    updateScreenViewer(monitoring) {
        const viewer = document.querySelector('.screen-viewer');
        if (viewer) {
            if (monitoring) {
                viewer.innerHTML = `
                    <div style="position: relative; height: 100%;">
                        <div style="position: absolute; top: 10px; right: 10px; color: #10b981; font-size: 12px;">
                            • Recording
                        </div>
                        <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #94a3b8;">
                            <div style="text-align: center;">
                                <i class="fas fa-camera" style="font-size: 64px; margin-bottom: 20px; opacity: 0.5;"></i>
                                <div style="font-size: 16px; margin-bottom: 8px;">Analyzing screen content in real-time...</div>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                viewer.innerHTML = `
                    <div class="screen-placeholder">
                        <i class="fas fa-camera"></i>
                        <div class="screen-placeholder-text">Click 'Start Monitoring' to begin screen analysis</div>
                        <div class="screen-placeholder-subtext">Real-time screen analysis and computer vision</div>
                    </div>
                `;
            }
        }
    }

    updateMonitoringButton(monitoring) {
        const startButton = document.querySelector('.btn-success');
        const stopButton = document.querySelector('.btn-danger');
        
        if (startButton) startButton.style.display = monitoring ? 'none' : 'inline-flex';
        if (stopButton) stopButton.style.display = monitoring ? 'inline-flex' : 'none';
    }

    // Chat Interface Methods
    async sendChatMessage() {
        const chatInput = document.querySelector('.chat-input');
        const message = chatInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addChatMessage(message, 'user');
        chatInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.addChatMessage(data.response, 'jarvis');
            } else {
                this.addChatMessage('Sorry, I encountered an error processing your request.', 'jarvis');
            }
        } catch (error) {
            console.error('Error sending chat message:', error);
            this.addChatMessage('Sorry, I encountered an error processing your request.', 'jarvis');
        }
    }

    addChatMessage(text, sender) {
        const chatMessages = document.querySelector('.chat-messages');
        if (!chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });

        messageDiv.innerHTML = `
            <div class="message-avatar ${sender}">
                <i class="fas fa-${sender === 'jarvis' ? 'robot' : 'user'}"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    <div class="message-text">${text}</div>
                    <div class="message-time">${timeString}</div>
                </div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    exportChat() {
        const messages = document.querySelectorAll('.message');
        let exportText = 'JARVIS AI Assistant - Chat Export\n';
        exportText += 'Generated on: ' + new Date().toLocaleString() + '\n\n';

        messages.forEach(message => {
            const sender = message.classList.contains('user') ? 'User' : 'JARVIS';
            const text = message.querySelector('.message-text').textContent;
            const time = message.querySelector('.message-time').textContent;
            
            exportText += `[${time}] ${sender}: ${text}\n`;
        });

        const blob = new Blob([exportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'jarvis-chat-export.txt';
        a.click();
        URL.revokeObjectURL(url);
    }

    clearChat() {
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
    }

    // Commands Methods
    filterCommands(category) {
        const categoryItems = document.querySelectorAll('.category-item');
        categoryItems.forEach(item => {
            item.classList.remove('active');
        });

        const selectedItem = Array.from(categoryItems).find(item => 
            item.textContent.trim() === category
        );
        if (selectedItem) {
            selectedItem.classList.add('active');
        }

        // Filter command cards based on category
        const commandCards = document.querySelectorAll('.command-card');
        commandCards.forEach(card => {
            if (category === 'All Commands' || card.dataset.category === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    // Settings Methods
    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.populateSettings(data.settings);
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    populateSettings(settings) {
        // Populate sliders
        const speechRateSlider = document.querySelector('input[name="speech_rate"]');
        const voiceVolumeSlider = document.querySelector('input[name="voice_volume"]');
        const micSensitivitySlider = document.querySelector('input[name="microphone_sensitivity"]');

        if (speechRateSlider) speechRateSlider.value = settings.speech_rate;
        if (voiceVolumeSlider) voiceVolumeSlider.value = settings.voice_volume;
        if (micSensitivitySlider) micSensitivitySlider.value = settings.microphone_sensitivity;

        // Populate checkboxes
        const continuousListeningCheckbox = document.querySelector('input[name="continuous_listening"]');
        const screenMonitoringCheckbox = document.querySelector('input[name="screen_monitoring"]');
        const notificationsCheckbox = document.querySelector('input[name="notifications"]');

        if (continuousListeningCheckbox) continuousListeningCheckbox.checked = settings.continuous_listening;
        if (screenMonitoringCheckbox) screenMonitoringCheckbox.checked = settings.screen_monitoring;
        if (notificationsCheckbox) notificationsCheckbox.checked = settings.notifications;

        // Populate API key
        const apiKeyInput = document.querySelector('input[name="api_key"]');
        if (apiKeyInput) apiKeyInput.value = settings.api_key || '';
    }

    setupSettingsHandlers() {
        // Slider handlers
        const sliders = document.querySelectorAll('.slider');
        sliders.forEach(slider => {
            slider.addEventListener('input', (e) => {
                const value = e.target.value;
                const valueDisplay = e.target.parentElement.querySelector('.slider-value');
                if (valueDisplay) {
                    valueDisplay.textContent = value;
                }
            });
        });

        // Save settings
        const saveButton = document.querySelector('.btn');
        if (saveButton) {
            saveButton.addEventListener('click', () => {
                this.saveSettings();
            });
        }
    }

    async saveSettings() {
        const settings = {
            speech_rate: document.querySelector('input[name="speech_rate"]')?.value,
            voice_volume: document.querySelector('input[name="voice_volume"]')?.value,
            microphone_sensitivity: document.querySelector('input[name="microphone_sensitivity"]')?.value,
            continuous_listening: document.querySelector('input[name="continuous_listening"]')?.checked,
            screen_monitoring: document.querySelector('input[name="screen_monitoring"]')?.checked,
            notifications: document.querySelector('input[name="notifications"]')?.checked,
            api_key: document.querySelector('input[name="api_key"]')?.value
        };

        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.showNotification('Settings saved successfully', 'success');
            } else {
                this.showNotification('Error saving settings', 'error');
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showNotification('Error saving settings', 'error');
        }
    }

    // Utility Methods
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    showCommandPalette() {
        // Implementation for command palette
        console.log('Command palette not implemented yet');
    }

    handleCommandResult(data) {
        this.showNotification(`Command executed: ${data.result}`, 'success');
    }

    handleCommandError(data) {
        this.showNotification(`Command error: ${data.error}`, 'error');
    }

    loadRecentActivity() {
        // Simulate loading recent activity
        const activities = [
            { text: 'Opened Spotify and played "Bohemian Rhapsody"', time: '14:32' },
            { text: 'Screen analysis completed', time: '14:28' },
            { text: 'Email drafted and sent via Gmail', time: '14:25' },
            { text: 'System sleep command executed', time: '14:20' },
            { text: 'Voice recognition initialized', time: '14:15' }
        ];

        const activityContainer = document.querySelector('.recent-activity');
        if (activityContainer) {
            const activityList = activityContainer.querySelector('.activity-list') || activityContainer;
            activityList.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <div class="activity-dot"></div>
                    <div class="activity-content">
                        <div class="activity-text">${activity.text}</div>
                        <div class="activity-time">${activity.time}</div>
                    </div>
                </div>
            `).join('');
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.jarvisApp = new JarvisApp();
});
