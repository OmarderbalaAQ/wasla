/**
 * Page Translator - Converts hardcoded HTML content to i18n translations
 * Handles static text content translation on page load and language change
 */

// Wait for i18n to be fully ready before translating
let i18nReady = false;

window.addEventListener('i18nReady', function() {
  console.log('📢 i18nReady event received - Starting translation');
  i18nReady = true;
  translatePage();
});

document.addEventListener('DOMContentLoaded', function() {
  console.log('📄 Page DOM loaded');
  
  // If i18n is already ready, translate immediately
  if (typeof i18n !== 'undefined' && i18n.translations && i18n.translations[i18n.currentLanguage]) {
    console.log('✅ i18n already ready - Translating immediately');
    i18nReady = true;
    translatePage();
  } else {
    console.log('⏳ Waiting for i18n to be ready...');
    // Otherwise wait for i18nReady event (handled above)
  }

  // Listen for language changes to retranslate page
  window.addEventListener('languageChanged', function() {
    console.log('🔄 Language changed - Retranslating page');
    translatePage();
  });
});

/**
 * Translate the current page based on its content
 */
function translatePage() {
  const currentPage = getCurrentPageName();
  
  console.log('🌐 Translating page:', currentPage);
  
  // Always translate common elements first
  translateCommonElements();
  
  // Then translate page-specific content
  switch(currentPage) {
    case 'index':
      translateIndexPage();
      break;
    case 'login':
      translateLoginPage();
      break;
    case 'register':
      translateRegisterPage();
      break;
    case 'client_home':
      translateClientHomePage();
      break;
    case 'dashboard':
      translateDashboardPage();
      break;
    case 'form':
      translateFormPage();
      break;
    case 'FAQ':
      translateFAQPage();
      break;
    case 'solutions':
      translateSolutionsPage();
      break;
    case 'pricing-non registered':
      translatePricingPage();
      break;
  }
  
  // Remove loading class to show content (smooth fade-in)
  document.documentElement.classList.remove('i18n-loading');
  console.log('✅ Translation complete - content visible');
}

/**
 * Get current page name from URL
 */
function getCurrentPageName() {
  const path = window.location.pathname;
  const filename = path.split('/').pop().split('.')[0];
  return filename || 'index';
}

/**
 * Translate common elements (navigation, footer, etc.)
 */
function translateCommonElements() {
  // Update page title
  const currentPage = getCurrentPageName();
  const pageTitle = i18n.t(`${currentPage}.pageTitle`);
  if (pageTitle && pageTitle !== `${currentPage}.pageTitle`) {
    document.title = pageTitle;
  }

  // Translate all elements with data-i18n attributes
  translateElementsWithDataI18n();
  
  // Translate placeholder attributes
  translatePlaceholders();

  // Footer - handle both new and legacy footer structures
  translateFooter();
}

/**
 * Translate index page content
 */
/**
 * Translate index page content using data-i18n attributes
 */
function translateIndexPage() {
  // All content is now handled by data-i18n attributes
  // The main translation system will automatically handle all elements
  translateElementsWithDataI18n();
}

/**
 * Translate all elements with data-i18n attributes
 */
function translateElementsWithDataI18n() {
  const elements = document.querySelectorAll('[data-i18n]');
  elements.forEach(element => {
    const key = element.getAttribute('data-i18n');
    const prefix = element.getAttribute('data-i18n-prefix') || '';
    const useHtml = element.getAttribute('data-i18n-html') === 'true';
    
    if (typeof i18n !== 'undefined' && i18n.t) {
      const translation = i18n.t(key);
      
      if (translation && translation !== key) {
        if (useHtml) {
          // For elements that need HTML content (like line breaks)
          element.innerHTML = translation;
        } else {
          // For regular text content
          element.textContent = prefix + translation;
        }
      }
    }
  });
}

/**
 * Translate placeholder attributes
 */
function translatePlaceholders() {
  const elements = document.querySelectorAll('[data-i18n-placeholder]');
  elements.forEach(element => {
    const key = element.getAttribute('data-i18n-placeholder');
    
    if (typeof i18n !== 'undefined' && i18n.t) {
      const translation = i18n.t(key);
      if (translation && translation !== key) {
        element.placeholder = translation;
      }
    }
  });
}

/**
 * Translate footer content using pure JSON approach
 */
function translateFooter() {
  // Translate all footer elements with data-i18n attributes
  const footerElements = document.querySelectorAll('footer [data-i18n]');
  footerElements.forEach(element => {
    const key = element.getAttribute('data-i18n');
    const prefix = element.getAttribute('data-i18n-prefix') || '';
    
    if (typeof i18n !== 'undefined' && i18n.t) {
      const translation = i18n.t(key);
      if (translation && translation !== key) {
        element.textContent = prefix + translation;
      }
    }
  });

  // Legacy footer support (for other pages that might still use the old footer structure)
  const navColumns = document.querySelectorAll('.nav-column');
  navColumns.forEach(column => {
    const heading = column.querySelector('h4');
    if (heading) {
      const headingText = heading.textContent.trim();
      if (headingText === 'Resources' || headingText === 'الموارد') {
        const translation = i18n.t('footer.resources');
        if (translation && translation !== 'footer.resources') {
          heading.textContent = translation;
        }
        
        // Update Resources links
        const links = column.querySelectorAll('a');
        links.forEach(link => {
          const text = link.textContent.trim();
          if (text === 'About us' || text === 'من نحن') {
            const translation = i18n.t('footer.aboutUs');
            if (translation && translation !== 'footer.aboutUs') {
              link.textContent = translation;
            }
          } else if (text === 'Contact us' || text === 'اتصل بنا') {
            const translation = i18n.t('footer.contactUs');
            if (translation && translation !== 'footer.contactUs') {
              link.textContent = translation;
            }
          } else if (text === 'FAQ' || text === 'الأسئلة الشائعة') {
            const translation = i18n.t('footer.faq');
            if (translation && translation !== 'footer.faq') {
              link.textContent = translation;
            }
          }
        });
      } else if (headingText === 'Solutions' || headingText === 'الحلول') {
        const translation = i18n.t('footer.solutions');
        if (translation && translation !== 'footer.solutions') {
          heading.textContent = translation;
        }
        
        // Update Solutions links
        const links = column.querySelectorAll('a');
        links.forEach(link => {
          const href = link.getAttribute('href');
          const text = link.textContent.trim();
          
          if (href === 'dashboard.html' || text === 'Pricing' || text === 'الأسعار') {
            const translation = i18n.t('common.pricing');
            if (translation && translation !== 'common.pricing') {
              link.textContent = translation;
            }
          } else if (href === 'form.html' || text === 'Get Started' || text === 'ابدأ') {
            const translation = i18n.t('common.getStarted');
            if (translation && translation !== 'common.getStarted') {
              link.textContent = translation;
            }
          }
        });
      }
    }
  });
}

/**
 * Placeholder functions for other pages
 */
function translateLoginPage() {
  // All content is now handled by data-i18n attributes
  // The main translation system will automatically handle all elements
  translateElementsWithDataI18n();
  
  // Handle placeholder translations
  translatePlaceholders();
}

function translateRegisterPage() {
  // Register page translations handled by dynamic-content-i18n.js
}

function translateClientHomePage() {
  // All content is now handled by data-i18n attributes
  // The main translation system will automatically handle all elements
  translateElementsWithDataI18n();
  
  // Handle placeholder translations
  translatePlaceholders();
}

function translateDashboardPage() {
  // Dashboard translations handled by dynamic-content-i18n.js
}

function translateFormPage() {
  // Form translations handled by dynamic-content-i18n.js
}

function translateFAQPage() {
  // All content is now handled by data-i18n attributes
  // The main translation system will automatically handle all elements
  translateElementsWithDataI18n();
}

function translateSolutionsPage() {
  // All content is now handled by data-i18n attributes
  // The main translation system will automatically handle all elements
  translateElementsWithDataI18n();
}

function translatePricingPage() {
  // All content is now handled by data-i18n attributes
  // The main translation system will automatically handle all elements
  translateElementsWithDataI18n();
}

/**
 * Utility function to safely get translation
 */
function safeTranslate(key, defaultValue = null) {
  if (typeof i18n !== 'undefined' && i18n.t) {
    const translation = i18n.t(key);
    // If translation returns the key itself, use default value
    if (translation === key && defaultValue !== null) {
      return defaultValue;
    }
    return translation;
  }
  return defaultValue || key;
}