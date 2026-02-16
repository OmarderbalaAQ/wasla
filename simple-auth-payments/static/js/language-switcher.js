/**
 * Language Switcher Handler
 * Adds functionality to language switcher UI elements
 * Supports both old dropdown format and new modern language switcher
 */

document.addEventListener('DOMContentLoaded', function() {
  initializeLanguageSwitchers();
});

function initializeLanguageSwitchers() {
  // Initialize modern language switcher (new format)
  initializeModernLanguageSwitcher();
  
  // Initialize legacy language switcher (old format)
  initializeLegacyLanguageSwitcher();
}

/**
 * Initialize modern language switcher with proper styling and functionality
 */
function initializeModernLanguageSwitcher() {
  const languageBtn = document.getElementById('languageBtn');
  const languageDropdown = document.getElementById('languageDropdown');
  const languageOptions = document.querySelectorAll('.language-option');

  if (!languageBtn || !languageDropdown) return;

  // Toggle dropdown on button click
  languageBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    languageDropdown.classList.toggle('active');
  });

  // Handle language option clicks
  languageOptions.forEach(option => {
    option.addEventListener('click', function(e) {
      e.preventDefault();
      const lang = this.getAttribute('data-lang');
      
      if (lang && typeof i18n !== 'undefined') {
        i18n.setLanguage(lang);
        updateModernLanguageSwitcherDisplay();
        languageDropdown.classList.remove('active');
      }
    });
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.language-switcher')) {
      languageDropdown.classList.remove('active');
    }
  });

  // Listen for language changes from other sources
  window.addEventListener('languageChanged', function() {
    updateModernLanguageSwitcherDisplay();
  });

  // Initialize display
  updateModernLanguageSwitcherDisplay();
}

/**
 * Update modern language switcher display
 */
function updateModernLanguageSwitcherDisplay() {
  const languageBtn = document.getElementById('languageBtn');
  if (!languageBtn || typeof i18n === 'undefined') return;

  const currentLang = i18n.getLanguage();
  const flagSpan = languageBtn.querySelector('.flag');
  const langTextSpan = languageBtn.querySelector('.lang-text');

  if (flagSpan && langTextSpan) {
    if (currentLang === 'ar') {
      flagSpan.textContent = '🇸🇦';
      langTextSpan.textContent = 'AR';
    } else {
      flagSpan.textContent = '🇺🇸';
      langTextSpan.textContent = 'EN';
    }
  }
}

/**
 * Initialize legacy language switcher (old dropdown format)
 */
function initializeLegacyLanguageSwitcher() {
  // Find all language selector elements
  const langSelectors = document.querySelectorAll('.lang-selector');
  const langLists = document.querySelectorAll('.lang-list');

  if (langSelectors.length === 0) return;

  // Add click handlers to language selector buttons
  langSelectors.forEach((selector, index) => {
    selector.addEventListener('click', function(e) {
      e.stopPropagation();
      
      // Toggle the corresponding language list
      if (langLists[index]) {
        langLists[index].classList.toggle('active');
      }

      // Close other language lists
      langLists.forEach((list, i) => {
        if (i !== index) {
          list.classList.remove('active');
        }
      });
    });
  });

  // Add click handlers to language options
  const langOptions = document.querySelectorAll('.lang-list a');
  langOptions.forEach(option => {
    option.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Determine which language was clicked
      const text = this.textContent.trim();
      let lang = 'en';
      
      if (text.includes('Arabic') || text.includes('العربية')) {
        lang = 'ar';
      } else if (text.includes('English') || text.includes('الإنجليزية')) {
        lang = 'en';
      }

      // Change language
      if (typeof i18n !== 'undefined') {
        i18n.setLanguage(lang);
        updateLegacyLanguageSelectorDisplay();
      }

      // Close the dropdown
      langLists.forEach(list => {
        list.classList.remove('active');
      });
    });
  });

  // Close dropdowns when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.lang-dropdown-wrapper')) {
      langLists.forEach(list => {
        list.classList.remove('active');
      });
    }
  });

  // Listen for language changes from other sources
  window.addEventListener('languageChanged', function() {
    updateLegacyLanguageSelectorDisplay();
  });

  // Initialize display
  updateLegacyLanguageSelectorDisplay();
}

/**
 * Update legacy language selector display to show current language
 */
function updateLegacyLanguageSelectorDisplay() {
  const langSelectors = document.querySelectorAll('.lang-selector');
  if (langSelectors.length === 0 || typeof i18n === 'undefined') return;

  const currentLang = i18n.getLanguage();
  const displayText = currentLang === 'ar' ? 'AR' : 'EN';
  
  langSelectors.forEach(selector => {
    // Update the text content while preserving the globe icon
    const globeIcon = selector.querySelector('.globe-icon');
    selector.textContent = '';
    if (globeIcon) {
      selector.appendChild(globeIcon);
    }
    selector.appendChild(document.createTextNode(' ' + displayText));
  });
}
