// Notifications Component
class NotificationManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        this.createContainer();
        this.setupEventListeners();
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'notifications-container';
        this.container.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 1100;
            max-width: 400px;
        `;
        document.body.appendChild(this.container);
    }

    setupEventListeners() {
        // Listen for custom notification events
        document.addEventListener('showNotification', (e) => {
            this.show(e.detail.message, e.detail.type, e.detail.duration);
        });
    }

    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="notification-icon ${this.getIcon(type)}"></i>
                <div class="notification-body">
                    <div class="notification-message">${message}</div>
                </div>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            background: white;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            border-left: 4px solid ${this.getColor(type)};
            animation: slideInRight 0.3s ease-out;
            max-width: 400px;
        `;

        this.container.appendChild(notification);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.style.opacity = '0';
                    notification.style.transform = 'translateX(100%)';
                    setTimeout(() => notification.remove(), 300);
                }
            }, duration);
        }

        return notification;
    }

    getIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    getColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || colors.info;
    }

    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 5000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }

    // Programmatically trigger notification
    static notify(message, type = 'info', duration = 5000) {
        const event = new CustomEvent('showNotification', {
            detail: { message, type, duration }
        });
        document.dispatchEvent(event);
    }
}

// Initialize notification manager
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = new NotificationManager();
});

// Global helper functions
window.notify = {
    success: (message, duration) => NotificationManager.notify(message, 'success', duration),
    error: (message, duration) => NotificationManager.notify(message, 'error', duration),
    warning: (message, duration) => NotificationManager.notify(message, 'warning', duration),
    info: (message, duration) => NotificationManager.notify(message, 'info', duration)
};

// Add CSS animations
const notificationStyles = `
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.notification-close {
    background: none;
    border: none;
    color: #6c757d;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.3s ease;
}

.notification-close:hover {
    background: #f8f9fa;
    color: #495057;
}

.notification-content {
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.notification-icon {
    font-size: 1.2em;
    margin-top: 2px;
}

.notification-success .notification-icon { color: #28a745; }
.notification-error .notification-icon { color: #dc3545; }
.notification-warning .notification-icon { color: #ffc107; }
.notification-info .notification-icon { color: #17a2b8; }

.notification-body {
    flex: 1;
}

.notification-message {
    color: #2c3e50;
    font-weight: 500;
    line-height: 1.4;
}
`;

// Inject styles
const style = document.createElement('style');
style.textContent = notificationStyles;
document.head.appendChild(style);