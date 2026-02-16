/**
 * Contact Form Handler
 * Handles form submission, validation, and API communication for the contact form
 */

class ContactForm {
    constructor(formId) {
        this.form = document.getElementById(formId);
        if (!this.form) {
            console.error(`Form with id "${formId}" not found`);
            return;
        }

        this.API_BASE_URL = window.location.origin;
        this.isSubmitting = false;
        this.submitButton = this.form.querySelector('button[type="submit"]');
        this.originalButtonText = this.submitButton ? this.submitButton.textContent : 'Get started';
        
        this.setupEventListeners();
        this.createMessageContainer();
    }

    /**
     * Set up form event listeners
     */
    setupEventListeners() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        
        // Add real-time email validation
        const emailInput = this.form.querySelector('input[type="email"]');
        if (emailInput) {
            emailInput.addEventListener('input', this.handleEmailInput.bind(this));
            emailInput.addEventListener('blur', this.handleEmailBlur.bind(this));
        }
    }

    /**
     * Handle email input in real-time
     * @param {Event} event - Input event
     */
    handleEmailInput(event) {
        const emailInput = event.target;
        const email = emailInput.value;
        
        // Check if email contains Arabic characters
        if (email && !this.isEnglishOnly(email)) {
            this.showEmailWarning(emailInput);
        } else {
            this.hideEmailWarning(emailInput);
        }
    }

    /**
     * Handle email blur event
     * @param {Event} event - Blur event
     */
    handleEmailBlur(event) {
        const emailInput = event.target;
        const email = emailInput.value;
        
        // Validate on blur
        if (email && !this.isEnglishOnly(email)) {
            this.showEmailWarning(emailInput);
        }
    }

    /**
     * Show email warning with smooth animation
     * @param {HTMLElement} emailInput - Email input element
     */
    showEmailWarning(emailInput) {
        const t = (key) => window.i18n ? window.i18n.t(key, key) : key;
        
        // Check if warning already exists
        let warning = emailInput.parentElement.querySelector('.email-warning');
        if (!warning) {
            warning = document.createElement('div');
            warning.className = 'email-warning';
            warning.innerHTML = `<span class="warning-icon">⚠️</span> ${t('form.validation.emailEnglishOnly')}`;
            emailInput.parentElement.appendChild(warning);
            
            // Trigger animation
            setTimeout(() => {
                warning.classList.add('show');
            }, 10);
        }
        
        // Add error styling to input
        emailInput.classList.add('input-error');
    }

    /**
     * Hide email warning with smooth animation
     * @param {HTMLElement} emailInput - Email input element
     */
    hideEmailWarning(emailInput) {
        const warning = emailInput.parentElement.querySelector('.email-warning');
        if (warning) {
            warning.classList.remove('show');
            setTimeout(() => {
                warning.remove();
            }, 300); // Match CSS transition duration
        }
        
        // Remove error styling
        emailInput.classList.remove('input-error');
    }

    /**
     * Create a container for success/error messages
     */
    createMessageContainer() {
        // Check if message container already exists
        let messageContainer = this.form.querySelector('.form-message');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.className = 'form-message';
            messageContainer.style.display = 'none';
            // Insert at the beginning of the form
            this.form.insertBefore(messageContainer, this.form.firstChild);
        }
        this.messageContainer = messageContainer;
    }

    /**
     * Main form submission handler
     * @param {Event} event - Form submit event
     */
    async handleSubmit(event) {
        event.preventDefault();

        // Prevent duplicate submissions
        if (this.isSubmitting) {
            return;
        }

        // Clear any previous messages
        this.clearMessages();

        // Collect form data
        const formData = this.collectFormData();

        // Validate form data
        const validationErrors = this.validateForm(formData);
        if (validationErrors.length > 0) {
            this.showErrorMessage(validationErrors);
            return;
        }

        // Submit to API
        await this.submitToAPI(formData);
    }

    /**
     * Collect form data from inputs
     * @returns {Object} Form data object
     */
    collectFormData() {
        const inputs = this.form.querySelectorAll('input, select');
        const formData = {};

        inputs.forEach(input => {
            const fieldName = input.getAttribute('data-field');
            
            if (!fieldName) {
                // Handle special cases without data-field
                if (input.type === 'checkbox' && input.id === 'marketing') {
                    formData.marketing_consent = input.checked;
                }
                return;
            }

            // Handle different input types
            if (input.type === 'radio') {
                if (input.checked) {
                    formData[fieldName] = input.value;
                }
            } else if (input.type === 'checkbox') {
                formData[fieldName] = input.checked;
            } else if (input.tagName === 'SELECT' || input.type === 'text' || input.type === 'email' || input.type === 'tel') {
                formData[fieldName] = input.value.trim();
            }
        });

        // Add language preference
        formData.language_preference = window.i18n ? window.i18n.getLanguage() : 'en';

        return formData;
    }

    /**
     * Validate form data
     * @param {Object} formData - Form data to validate
     * @returns {Array} Array of error messages
     */
    validateForm(formData) {
        const errors = [];
        const t = (key) => window.i18n ? window.i18n.t(key, key) : key;

        // Required fields
        if (!formData.first_name || formData.first_name.length === 0) {
            errors.push(t('form.validation.firstNameRequired'));
        } else if (formData.first_name.length > 255) {
            errors.push(t('form.validation.firstNameTooLong'));
        }

        if (!formData.last_name || formData.last_name.length === 0) {
            errors.push(t('form.validation.lastNameRequired'));
        } else if (formData.last_name.length > 255) {
            errors.push(t('form.validation.lastNameTooLong'));
        }

        if (!formData.email || formData.email.length === 0) {
            errors.push(t('form.validation.emailRequired'));
        } else if (!this.isEnglishOnly(formData.email)) {
            errors.push(t('form.validation.emailEnglishOnly'));
        } else if (!this.isValidEmail(formData.email)) {
            errors.push(t('form.validation.emailInvalid'));
        } else if (formData.email.length > 255) {
            errors.push(t('form.validation.emailTooLong'));
        }

        if (!formData.phone || formData.phone.length === 0) {
            errors.push(t('form.validation.phoneRequired'));
        } else if (!this.isValidPhone(formData.phone)) {
            errors.push(t('form.validation.phoneInvalid'));
        } else if (formData.phone.length > 20) {
            errors.push(t('form.validation.phoneTooLong'));
        }

        if (!formData.country_code) {
            errors.push(t('form.validation.countryCodeRequired'));
        }

        if (!formData.country) {
            errors.push(t('form.validation.countryRequired'));
        }

        if (!formData.business_name || formData.business_name.length === 0) {
            errors.push(t('form.validation.businessNameRequired'));
        } else if (formData.business_name.length > 255) {
            errors.push(t('form.validation.businessNameTooLong'));
        }

        if (!formData.num_locations) {
            errors.push(t('form.validation.locationsRequired'));
        }

        if (!formData.referral_source) {
            errors.push(t('form.validation.hearAboutRequired'));
        }

        return errors;
    }

    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {boolean}
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Check if email contains only English characters
     * @param {string} email - Email to check
     * @returns {boolean}
     */
    isEnglishOnly(email) {
        // Check if email contains only ASCII characters (English)
        // Arabic characters are in Unicode range \u0600-\u06FF
        const arabicRegex = /[\u0600-\u06FF]/;
        return !arabicRegex.test(email);
    }

    /**
     * Validate phone format
     * @param {string} phone - Phone to validate
     * @returns {boolean}
     */
    isValidPhone(phone) {
        const phoneRegex = /^[0-9\s\-\+\(\)]+$/;
        return phoneRegex.test(phone);
    }

    /**
     * Submit form data to API
     * @param {Object} formData - Form data to submit
     */
    async submitToAPI(formData) {
        this.isSubmitting = true;
        this.disableSubmitButton();

        try {
            const response = await fetch(`${this.API_BASE_URL}/contacts/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                this.handleSuccess(data);
            } else {
                this.handleError(response, data);
            }
        } catch (error) {
            const t = (key) => window.i18n ? window.i18n.t(key, key) : key;
            console.error('Network error:', error);
            this.showErrorMessage([t('form.messages.networkError')]);
        } finally {
            this.isSubmitting = false;
            this.enableSubmitButton();
        }
    }

    /**
     * Handle successful submission
     * @param {Object} data - Response data
     */
    handleSuccess(data) {
        const t = (key) => window.i18n ? window.i18n.t(key, key) : key;
        // Show success message at top of form with animation
        this.showSuccessMessage(t('form.messages.success'));
        this.clearForm();
        
        // Scroll to message
        this.messageContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Handle error response
     * @param {Response} response - Fetch response
     * @param {Object} data - Response data
     */
    handleError(response, data) {
        const t = (key) => window.i18n ? window.i18n.t(key, key) : key;
        let errors = [];

        if (response.status === 429) {
            // Rate limiting error - use translated message
            errors.push(t('form.messages.rateLimitError'));
        } else if (response.status === 422 || response.status === 400) {
            // Validation errors
            if (data.detail && Array.isArray(data.detail)) {
                errors = data.detail.map(err => {
                    const field = err.loc ? err.loc[err.loc.length - 1] : 'field';
                    return `${field}: ${err.msg}`;
                });
            } else if (data.detail) {
                errors.push(data.detail);
            } else {
                errors.push('Please check your input and try again.');
            }
        } else {
            errors.push('An error occurred. Please try again later.');
        }

        this.showErrorMessage(errors);
    }

    /**
     * Show success message
     * @param {string} message - Success message
     */
    showSuccessMessage(message) {
        this.messageContainer.className = 'form-message success';
        this.messageContainer.innerHTML = `
            <div class="message-content">
                <span class="message-icon">✓</span>
                <span class="message-text">${message}</span>
            </div>
        `;
        this.messageContainer.style.display = 'block';
    }

    /**
     * Show error messages
     * @param {Array} errors - Array of error messages
     */
    showErrorMessage(errors) {
        const t = (key) => window.i18n ? window.i18n.t(key, key) : key;
        const errorList = errors.map(err => `<li>${err}</li>`).join('');
        
        // Get current language for RTL support
        const currentLang = window.i18n ? window.i18n.getLanguage() : 'en';
        const isRTL = currentLang === 'ar';
        const dirAttr = isRTL ? 'dir="rtl"' : '';
        const textAlignClass = isRTL ? 'rtl-text' : '';
        
        this.messageContainer.className = `form-message error ${textAlignClass}`;
        this.messageContainer.innerHTML = `
            <div class="message-content" ${dirAttr}>
                <span class="message-icon">✕</span>
                <div class="message-text">
                    <strong>${t('form.messages.errorTitle')}</strong>
                    <ul>${errorList}</ul>
                </div>
            </div>
        `;
        this.messageContainer.style.display = 'block';
        
        // Scroll to message
        this.messageContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Clear all messages
     */
    clearMessages() {
        this.messageContainer.style.display = 'none';
        this.messageContainer.innerHTML = '';
    }

    /**
     * Clear form fields after successful submission
     */
    clearForm() {
        // Reset all input fields
        const inputs = this.form.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"]');
        inputs.forEach(input => {
            input.value = '';
        });

        // Reset checkboxes
        const checkboxes = this.form.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        // Reset radio buttons to first option
        const firstRadio = this.form.querySelector('input[type="radio"][value="1"]');
        if (firstRadio) {
            firstRadio.checked = true;
        }

        // Reset selects to first option
        const selects = this.form.querySelectorAll('select');
        selects.forEach(select => {
            if (!select.classList.contains('country-code')) {
                select.selectedIndex = 0;
            }
        });
    }

    /**
     * Disable submit button during submission
     */
    disableSubmitButton() {
        if (this.submitButton) {
            const t = (key) => window.i18n ? window.i18n.t(key, key) : key;
            this.submitButton.disabled = true;
            this.submitButton.textContent = t('form.buttons.submitting');
            this.submitButton.style.opacity = '0.6';
            this.submitButton.style.cursor = 'not-allowed';
        }
    }

    /**
     * Enable submit button after submission
     */
    enableSubmitButton() {
        if (this.submitButton) {
            this.submitButton.disabled = false;
            this.submitButton.textContent = this.originalButtonText;
            this.submitButton.style.opacity = '1';
            this.submitButton.style.cursor = 'pointer';
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ContactForm('contactForm');
    });
} else {
    new ContactForm('contactForm');
}
