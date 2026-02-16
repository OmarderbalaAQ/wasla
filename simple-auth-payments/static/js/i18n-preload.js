/**
 * i18n Preload Script
 * This script runs IMMEDIATELY to prevent FOUC (Flash of Unstyled Content)
 * Add this script in <head> BEFORE any other scripts
 */

// Add loading class immediately to hide content
document.documentElement.classList.add('i18n-loading');

// Log for debugging
console.log('🔒 Content hidden - waiting for i18n to load');
