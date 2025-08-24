// JARVIS AI Assistant v2.0 - Socket.IO Client

class JarvisSocket {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.init();
    }

    init() {
        this.connect();
        this.setupEventListeners();
    }

    connect() {
        try {
            this.socket = io({
                transports: ['websocket', 'polling'],
                timeout: 20000,
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: this.reconnectDelay
            });
        } catch (error) {
            console.error('Failed to connect to JARVIS server:', error);
            this.scheduleReconnect();
        }
    }

    setupEventListeners() {
        if (!this.socket) return;

        this.socket.on('connect', () => {
            console.log('Connected to JARVIS server');
            this.connected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from JARVIS server');
            this.connected = false;
            this.updateConnectionStatus(false);
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.connected = false;
            this.updateConnectionStatus(false);
        });

        this.socket.on('reconnect', (attemptNumber) => {
            console.log(`Reconnected to JARVIS server after ${attemptNumber} attempts`);
            this.connected = true;
            this.updateConnectionStatus(true);
        });

        this.socket.on('reconnect_failed', () => {
            console.error('Failed to reconnect to JARVIS server');
            this.connected = false;
            this.updateConnectionStatus(false);
        });

        // Custom events
        this.socket.on('system_resources', (resources) => {
            this.handleSystemResources(resources);
        });

        this.socket.on('system_status', (status) => {
            this.handleSystemStatus(status);
        });

        this.socket.on('command_result', (data) => {
            this.handleCommandResult(data);
        });

        this.socket.on('command_error', (data) => {
            this.handleCommandError(data);
        });

        this.socket.on('voice_transcript', (data) => {
            this.handleVoiceTranscript(data);
        });

        this.socket.on('screen_analysis', (data) => {
            this.handleScreenAnalysis(data);
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

        // Update top bar status
        const topBarStatus = document.querySelector('.top-bar-center .status-indicator');
        if (topBarStatus) {
            if (connected) {
                topBarStatus.innerHTML = '<span class="status-dot"></span>Ready JARVIS AI Assistant';
            } else {
                topBarStatus.innerHTML = '<span class="status-dot offline"></span>Connecting...';
            }
        }
    }

    handleSystemResources(resources) {
        // Update system metrics in top bar
        const cpuMetric = document.getElementById('cpu-metric');
        const memoryMetric = document.getElementById('memory-metric');
        const diskMetric = document.getElementById('disk-metric');
        const batteryMetric = document.getElementById('battery-metric');

        if (cpuMetric) cpuMetric.textContent = `${resources.cpu}%`;
        if (memoryMetric) memoryMetric.textContent = `${resources.memory}%`;
        if (diskMetric) diskMetric.textContent = `${resources.disk}%`;
        if (batteryMetric) batteryMetric.textContent = `${resources.battery}%`;

        // Update dashboard cards if on dashboard
        const dashboardCpu = document.getElementById('dashboard-cpu');
        const dashboardMemory = document.getElementById('dashboard-memory');
        const dashboardDisk = document.getElementById('dashboard-disk');
        const dashboardBattery = document.getElementById('dashboard-battery');

        if (dashboardCpu) dashboardCpu.textContent = `${resources.cpu}%`;
        if (dashboardMemory) dashboardMemory.textContent = `${resources.memory}%`;
        if (dashboardDisk) dashboardDisk.textContent = `${resources.disk}%`;
        if (dashboardBattery) dashboardBattery.textContent = `${resources.battery}%`;
    }

    handleSystemStatus(status) {
        // Update system status indicators
        Object.keys(status.system_status).forEach(key => {
            const statusElement = document.getElementById(`${key}-status`);
            if (statusElement) {
                const dot = statusElement.querySelector('.status-dot');
                if (status.system_status[key]) {
                    dot.classList.remove('offline');
                    dot.classList.add('online');
                } else {
                    dot.classList.remove('online');
                    dot.classList.add('offline');
                }
            }
        });
    }

    handleCommandResult(data) {
        console.log('Command result:', data);
        
        // Show notification
        if (window.jarvisApp) {
            window.jarvisApp.showNotification(`Command executed: ${data.result}`, 'success');
        }

        // Update last command in voice control if applicable
        const lastCommandText = document.querySelector('.last-command-text');
        if (lastCommandText) {
            lastCommandText.textContent = data.command;
        }
    }

    handleCommandError(data) {
        console.error('Command error:', data);
        
        // Show notification
        if (window.jarvisApp) {
            window.jarvisApp.showNotification(`Command error: ${data.error}`, 'error');
        }
    }

    handleVoiceTranscript(data) {
        console.log('Voice transcript:', data);
        
        // Update voice modal transcript
        const transcriptText = document.querySelector('.transcript-text');
        if (transcriptText) {
            transcriptText.textContent = data.transcript;
        }

        // Update last command
        const lastCommandText = document.querySelector('.last-command-text');
        if (lastCommandText) {
            lastCommandText.textContent = data.transcript;
        }
    }

    handleScreenAnalysis(data) {
        console.log('Screen analysis:', data);
        
        // Update detection stats
        const elementsDetected = document.querySelector('.stat-item:nth-child(1) .stat-value');
        const clickableAreas = document.querySelector('.stat-item:nth-child(2) .stat-value');
        const textRegions = document.querySelector('.stat-item:nth-child(3) .stat-value');
        const uiElements = document.querySelector('.stat-item:nth-child(4) .stat-value');

        if (elementsDetected) elementsDetected.textContent = data.elements_detected || '0';
        if (clickableAreas) clickableAreas.textContent = data.clickable_areas || '0';
        if (textRegions) textRegions.textContent = data.text_regions || '0';
        if (uiElements) uiElements.textContent = data.ui_elements || '0';

        // Update detected objects
        const detectedObjects = document.querySelector('.detected-objects');
        if (detectedObjects && data.objects) {
            const objectsList = detectedObjects.querySelector('.objects-list') || detectedObjects;
            objectsList.innerHTML = data.objects.map(obj => `
                <div class="object-item">
                    <div class="object-dot ${obj.confidence > 90 ? 'green' : obj.confidence > 70 ? 'yellow' : 'red'}"></div>
                    <div class="object-name">${obj.name}</div>
                    <div class="object-confidence">${obj.confidence}%</div>
                </div>
            `).join('');
        }
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    // Public methods for sending events
    sendCommand(command) {
        if (this.connected && this.socket) {
            this.socket.emit('execute_command', { command: command });
        } else {
            console.error('Socket not connected');
        }
    }

    sendVoiceCommand(action) {
        if (this.connected && this.socket) {
            this.socket.emit('voice_control', { action: action });
        } else {
            console.error('Socket not connected');
        }
    }

    sendScreenCommand(action) {
        if (this.connected && this.socket) {
            this.socket.emit('screen_vision', { action: action });
        } else {
            console.error('Socket not connected');
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Initialize Socket.IO client when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.jarvisSocket = new JarvisSocket();
});
