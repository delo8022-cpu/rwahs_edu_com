// Sidebar Component JavaScript
class SidebarManager {
    constructor() {
        this.sidebar = document.querySelector('.admin-sidebar');
        this.overlay = document.querySelector('.sidebar-overlay');
        this.body = document.body;
        this.init();
    }

    init() {
        this.createMobileToggle();
        this.addEventListeners();
        this.handleResize();
    }

    createMobileToggle() {
        // Create mobile menu toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'sidebar-toggle mobile-only';
        toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
        toggleBtn.setAttribute('aria-label', 'Toggle sidebar');
        
        const headerActions = document.querySelector('.header-actions');
        if (headerActions) {
            headerActions.prepend(toggleBtn);
        }
    }

    addEventListeners() {
        // Mobile toggle
        document.addEventListener('click', (e) => {
            if (e.target.closest('.sidebar-toggle')) {
                this.toggleSidebar();
            }
            
            if (e.target.closest('.sidebar-overlay')) {
                this.closeSidebar();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'm') {
                e.preventDefault();
                this.toggleSidebar();
            }
        });

        // Resize handler
        window.addEventListener('resize', () => this.handleResize());
    }

    toggleSidebar() {
        this.body.classList.toggle('sidebar-open');
        
        // Add animation class
        if (this.body.classList.contains('sidebar-open')) {
            this.sidebar.style.animation = 'slideInLeft 0.3s ease-out';
        }
    }

    closeSidebar() {
        this.body.classList.remove('sidebar-open');
    }

    handleResize() {
        if (window.innerWidth > 1024) {
            this.body.classList.remove('sidebar-open');
        }
    }

    // Collapse sidebar for desktop (optional feature)
    toggleCollapse() {
        this.body.classList.toggle('sidebar-collapsed');
        
        // Save state to localStorage
        const isCollapsed = this.body.classList.contains('sidebar-collapsed');
        localStorage.setItem('sidebarCollapsed', isCollapsed);
    }

    // Load saved sidebar state
    loadSavedState() {
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) {
            this.body.classList.add('sidebar-collapsed');
        }
    }
}

// Initialize sidebar when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SidebarManager().loadSavedState();
});

// Export for use in other modules
window.SidebarManager = SidebarManager;