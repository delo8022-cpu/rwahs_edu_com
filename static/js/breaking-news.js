// static/js/breaking-news.js
// Breaking News Modal functionality with improved marquee

function openNewsModal() {
    const overlay = document.getElementById('newsModalOverlay');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    window.scrollTo(0, 0);
}

function closeNewsModal() {
    const overlay = document.getElementById('newsModalOverlay');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
}

// Improved Marquee Functionality
function initializeMarquee() {
    const marquee = document.getElementById('latest_news');
    if (!marquee) return;

    const items = marquee.querySelectorAll('.news-item');
    if (items.length <= 1) return;

    // Calculate total width of all items
    let totalWidth = 0;
    items.forEach(item => {
        totalWidth += item.offsetWidth;
    });

    // Duplicate content for seamless loop
    marquee.innerHTML += marquee.innerHTML;
    
    // Adjust animation duration based on content length
    const duration = Math.max(30, totalWidth / 50); // Base duration on content width
    marquee.style.animationDuration = duration + 's';
    
    console.log('Marquee initialized with', items.length, 'items, duration:', duration + 's');
}

// DOM লোড হওয়ার পর ইভেন্ট লিস্টেনার যোগ করুন
document.addEventListener('DOMContentLoaded', function() {
    const overlay = document.getElementById('newsModalOverlay');
    const modalContainer = document.querySelector('.custom-modal-container');
    
    // Initialize marquee
    setTimeout(initializeMarquee, 1000);
    
    if (overlay) {
        // Overlay ক্লিক করলে বন্ধ হবে
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeNewsModal();
            }
        });

        // ESC key প্রেস করলে বন্ধ হবে
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && overlay.classList.contains('active')) {
                closeNewsModal();
            }
        });

        // Modal বাইরের ক্লিক বন্ধ করা
        if (modalContainer) {
            modalContainer.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    }

    // Restart marquee when it finishes (fallback)
    const marquee = document.getElementById('latest_news');
    if (marquee) {
        marquee.addEventListener('animationiteration', function() {
            console.log('Marquee loop completed');
        });
    }
});

// Alternative marquee solution for better performance
function createSeamlessMarquee() {
    const marqueeWrapper = document.getElementById('marqueeWrapper');
    const marquee = document.getElementById('latest_news');
    
    if (!marqueeWrapper || !marquee) return;

    // Clone the marquee content for seamless loop
    const clone = marquee.cloneNode(true);
    marqueeWrapper.appendChild(clone);

    // Set animation
    const items = marquee.querySelectorAll('.news-item');
    const totalWidth = Array.from(items).reduce((width, item) => width + item.offsetWidth, 0);
    const duration = Math.max(40, totalWidth / 40);
    
    marquee.style.animationDuration = duration + 's';
    clone.style.animationDuration = duration + 's';
}