/**
 * i18n Library - Internationalization for Wasla
 * Handles language detection, translation loading, and language switching
 */

class I18n {
  constructor() {
    this.currentLanguage = this.detectLanguage();
    this.translations = {};
    this.isLoading = false;
  }

  /**
   * Detect language from localStorage or browser
   * @returns {string} 'en' or 'ar'
   */
  detectLanguage() {
    // PRIORITY 1: Check localStorage first (user preference persists across pages)
    const stored = localStorage.getItem('wasla_language');
    if (stored === 'en' || stored === 'ar') {
      console.log('✅ Language loaded from localStorage:', stored);
      return stored;
    }

    // TEMPORARY: Browser detection DISABLED for testing
    console.log('⚠️ No language preference found in localStorage');
    console.log('🔧 AUTO-DETECTION SUSPENDED - Defaulting to English');
    
    // Always default to English (browser detection suspended)
    const defaultLang = 'en';
    
    // Save to localStorage
    localStorage.setItem('wasla_language', defaultLang);
    console.log('💾 Default language saved to localStorage:', defaultLang);
    
    return defaultLang;
    
    /* BROWSER DETECTION CODE (SUSPENDED)
    const browserLang = navigator.language || navigator.userLanguage;
    console.log('🌐 Browser language detected:', browserLang);
    
    let detectedLang = 'en'; // Default
    
    // Check if browser language is Arabic
    if (browserLang && (browserLang.startsWith('ar') || browserLang.includes('ar'))) {
      console.log('🌐 Setting language to Arabic based on browser');
      detectedLang = 'ar';
    } else {
      console.log('🌐 Setting language to English (default)');
      detectedLang = 'en';
    }
    
    // IMPORTANT: Save detected language to localStorage immediately
    // This ensures browser detection only happens ONCE
    localStorage.setItem('wasla_language', detectedLang);
    console.log('💾 First-time detection saved to localStorage:', detectedLang);
    
    return detectedLang;
    */
  }

  /**
   * Load translations for a specific language
   * @param {string} lang - Language code ('en' or 'ar')
   * @returns {Promise<void>}
   */
  async loadLanguage(lang) {
    if (this.translations[lang]) {
      return; // Already loaded
    }

    if (this.isLoading) {
      return; // Already loading
    }

    this.isLoading = true;

    try {
      const response = await fetch(`/static/i18n/${lang}.json`);
      if (!response.ok) {
        throw new Error(`Failed to load ${lang}.json`);
      }
      this.translations[lang] = await response.json();
    } catch (error) {
      console.error(`Error loading language ${lang}:`, error);
      // Fallback to English if loading fails
      if (lang !== 'en') {
        await this.loadLanguage('en');
      }
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Initialize i18n - load current language
   * @returns {Promise<void>}
   */
  async init() {
    console.log('🚀 i18n.init() called');
    console.log('📍 Current language at init:', this.currentLanguage);
    console.log('💾 localStorage value at init:', localStorage.getItem('wasla_language'));
    
    await this.loadLanguage(this.currentLanguage);
    this.applyLanguage();
    
    console.log('✅ i18n initialized successfully');
  }

  /**
   * Get translation by key path (e.g., 'common.logo')
   * @param {string} key - Dot-notation key path
   * @param {*} defaultValue - Default value if key not found
   * @returns {string|*}
   */
  t(key, defaultValue = key) {
    const keys = key.split('.');
    let value = this.translations[this.currentLanguage];

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return defaultValue;
      }
    }

    return value;
  }

  /**
   * Set language and apply it
   * @param {string} lang - Language code ('en' or 'ar')
   * @returns {Promise<void>}
   */
  async setLanguage(lang) {
    if (lang !== 'en' && lang !== 'ar') {
      console.warn(`❌ Invalid language: ${lang}`);
      return;
    }

    console.log(`🔄 Changing language from ${this.currentLanguage} to: ${lang}`);
    this.currentLanguage = lang;
    
    // Save to localStorage for persistence across pages
    localStorage.setItem('wasla_language', lang);
    console.log('💾 Language saved to localStorage:', lang);
    
    // Verify it was saved
    const verification = localStorage.getItem('wasla_language');
    console.log('✅ Verification - localStorage now contains:', verification);

    // Load language if not already loaded
    await this.loadLanguage(lang);

    // Apply language to DOM
    this.applyLanguage();

    // Dispatch custom event for other scripts to listen
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
    console.log('📢 languageChanged event dispatched');
  }

  /**
   * Alias for setLanguage - for compatibility
   * @param {string} lang - Language code ('en' or 'ar')
   * @returns {Promise<void>}
   */
  async changeLanguage(lang) {
    return this.setLanguage(lang);
  }

  /**
   * Apply language to HTML document
   */
  applyLanguage() {
    const html = document.documentElement;
    html.lang = this.currentLanguage;
    // Keep LTR layout for both languages - no RTL flipping
    html.dir = 'ltr';

    // Add language class for CSS styling
    html.classList.remove('lang-en', 'lang-ar');
    html.classList.add(`lang-${this.currentLanguage}`);
    
    // Remove loading class to show content (prevents FOUC)
    html.classList.remove('i18n-loading');
  }

  /**
   * Get current language
   * @returns {string}
   */
  getLanguage() {
    return this.currentLanguage;
  }

  /**
   * Check if current language is Arabic
   * @returns {boolean}
   */
  isArabic() {
    return this.currentLanguage === 'ar';
  }

  /**
   * Check if current language is English
   * @returns {boolean}
   */
  isEnglish() {
    return this.currentLanguage === 'en';
  }
}

// Create global instance
const i18n = new I18n();

// Make sure i18n is available globally before any other scripts run
window.i18n = i18n;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOMContentLoaded - Initializing i18n');
    i18n.init().then(() => {
      console.log('✅ i18n initialization complete');
      // Dispatch event so other scripts know i18n is ready
      window.dispatchEvent(new CustomEvent('i18nReady'));
    });
  });
} else {
  console.log('🚀 DOM already loaded - Initializing i18n immediately');
  i18n.init().then(() => {
    console.log('✅ i18n initialization complete');
    window.dispatchEvent(new CustomEvent('i18nReady'));
  });
}
