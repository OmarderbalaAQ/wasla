document.addEventListener('DOMContentLoaded', () => {
    // Select all clickable question headers
    const faqQuestions = document.querySelectorAll('.faq-question');

    faqQuestions.forEach(question => {
        question.addEventListener('click', () => {
            // Get the parent .faq-item
            const faqItem = question.closest('.faq-item');
            
            // Toggle the 'open' class on the parent item
            faqItem.classList.toggle('open');
            
            // Update ARIA attributes for accessibility
            const isCurrentlyOpen = faqItem.classList.contains('open');
            question.setAttribute('aria-expanded', isCurrentlyOpen);

            // Update the arrow icon (optional, using CSS transform is cleaner)
            // If you rely on HTML content for the arrow (↑ / ↓):
            const icon = question.querySelector('.faq-toggle-icon');
            if (icon) {
                icon.textContent = isCurrentlyOpen ? '↑' : '↑';
            }
        });
    });
});


