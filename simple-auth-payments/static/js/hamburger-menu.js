/**
 * Hamburger Menu Controller
 * Handles mobile navigation overlay with smooth animations
 */

document.addEventListener('DOMContentLoaded', () => {
    const hamburgerBtn = document.querySelector('.hamburger-btn');
    const hamburgerIcon = hamburgerBtn ? hamburgerBtn.querySelector('.hamburger-icon') : null;
    const mobileOverlay = document.querySelector('.mobile-menu-overlay');
    const closeBtn = document.querySelector('.mobile-menu-close');
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-links a');
    const body = document.body;
    const header = document.querySelector('.main-header');

    // Scroll detection for sticky header shrink effect
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });

    // Open mobile menu
    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            
            // Add active class to trigger animations
            mobileOverlay.classList.add('active');
            if (hamburgerIcon) hamburgerIcon.classList.add('open');
            body.style.overflow = 'hidden';
            
            // Disable hamburger button temporarily during transition
            hamburgerBtn.style.pointerEvents = 'none';
            setTimeout(() => {
                hamburgerBtn.style.pointerEvents = '';
            }, 500);
        });
    }

    // Close mobile menu
    if (closeBtn) {
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeMenu();
        });
    }

    // Function to close menu
    function closeMenu() {
        mobileOverlay.classList.remove('active');
        if (hamburgerIcon) hamburgerIcon.classList.remove('open');
        body.style.overflow = '';
        
        // Disable close button temporarily during transition
        if (closeBtn) {
            closeBtn.style.pointerEvents = 'none';
            setTimeout(() => {
                closeBtn.style.pointerEvents = '';
            }, 500);
        }
    }

    // Close menu when clicking on a navigation link
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', () => {
            closeMenu();
        });
    });

    // Close menu when clicking on backdrop
    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', (e) => {
            if (e.target === mobileOverlay) {
                closeMenu();
            }
        });
    }

    // Handle escape key to close menu
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && mobileOverlay.classList.contains('active')) {
            closeMenu();
        }
    });
});
