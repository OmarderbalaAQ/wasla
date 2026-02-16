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

            // Update the arrow icon - fix the bug where both cases showed ↑
            const icon = question.querySelector('.faq-toggle-icon');
            if (icon) {
                icon.textContent = isCurrentlyOpen ? '↑' : '↓';
            }
        });
    });
});

// Alternative function for onclick handlers (if needed)
function toggleFAQ(questionElement) {
    const faqItem = questionElement.closest('.faq-item');
    faqItem.classList.toggle('open');
    
    const isCurrentlyOpen = faqItem.classList.contains('open');
    questionElement.setAttribute('aria-expanded', isCurrentlyOpen);
    
    const icon = questionElement.querySelector('.faq-toggle-icon');
    if (icon) {
        icon.textContent = isCurrentlyOpen ? '↑' : '↓';
    }
}