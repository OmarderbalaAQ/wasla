/**
 * Dynamic Content i18n Integration
 * Handles translation of JavaScript-generated content
 */

// Wait for i18n to be ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize dynamic content translations after i18n is loaded
  if (typeof i18n !== 'undefined') {
    i18n.init().then(() => {
      initializeDynamicTranslations();
    });
  }

  // Listen for language changes to update dynamic content
  window.addEventListener('languageChanged', function() {
    updateDynamicContent();
  });
});

/**
 * Initialize dynamic translations on page load
 */
function initializeDynamicTranslations() {
  updateDynamicContent();
}

/**
 * Update all dynamic content when language changes
 */
function updateDynamicContent() {
  // Update based on current page
  const currentPage = getCurrentPage();
  
  switch(currentPage) {
    case 'client_home':
      updateClientHomeDynamicContent();
      break;
    case 'login':
      updateLoginDynamicContent();
      break;
    case 'register':
      updateRegisterDynamicContent();
      break;
    case 'form':
      updateFormDynamicContent();
      break;
    case 'dashboard':
      updateDashboardDynamicContent();
      break;
    case 'admin':
      updateAdminDynamicContent();
      break;
  }
}

/**
 * Get current page name from URL
 */
function getCurrentPage() {
  const path = window.location.pathname;
  const filename = path.split('/').pop().split('.')[0];
  return filename || 'index';
}

/**
 * Update client home dynamic content
 */
function updateClientHomeDynamicContent() {
  // Override the original loadUserData function if it exists
  if (typeof window.originalLoadUserData === 'undefined' && typeof loadUserData === 'function') {
    window.originalLoadUserData = loadUserData;
    
    // Replace with i18n version
    window.loadUserData = async function() {
      try {
        const userResponse = await fetch(`${API_BASE_URL}/auth/me`, { headers: { 'Authorization': `Bearer ${token}` } });
        const user = await userResponse.json();
        
        document.getElementById('userName').textContent = user.full_name || user.email;
        document.getElementById('userEmailNav').textContent = user.email;

        const subResponse = await fetch(`${API_BASE_URL}/auth/me/subscription`, { headers: { 'Authorization': `Bearer ${token}` } });
        const subscription = await subResponse.json();

        const statusDiv = document.getElementById('subscriptionStatus');
        const dashboardBtn = document.getElementById('dashboardBtn');

        dashboardUrl = subscription.dashboard_url;
        hasAccess = subscription.has_access;

        if (subscription.has_access) {
          statusDiv.className = 'subscription-status active';
          statusDiv.innerHTML = `
            <div class="status-badge active">✓ ${i18n.t('clientHome.subscriptionStatus.active')}</div>
            <p><strong>${i18n.t('clientHome.subscriptionStatus.activeLabel')}</strong></p>
            ${subscription.subscription_end_date ? 
              `<p>${i18n.t('clientHome.subscriptionStatus.validUntil')} ${new Date(subscription.subscription_end_date).toLocaleDateString()}</p>` : 
              `<p>${i18n.t('clientHome.subscriptionStatus.accessGranted')}</p>`
            }
            ${subscription.bundle_name ? `<p>${i18n.t('clientHome.subscriptionStatus.plan')} ${subscription.bundle_name}</p>` : ''}
          `;
          dashboardBtn.disabled = false;
        } else {
          statusDiv.className = 'subscription-status expired';
          statusDiv.innerHTML = `
            <div class="status-badge expired">✗ ${i18n.t('clientHome.subscriptionStatus.noSubscription')}</div>
            <p><strong>${i18n.t('clientHome.subscriptionStatus.subscriptionRequired')}</strong></p>
            <p>${i18n.t('clientHome.subscriptionStatus.purchaseRequired')}</p>
          `;
          dashboardBtn.disabled = true;
        }
      } catch (error) {
        console.error('Error loading user data:', error);
        document.getElementById('errorMessage').textContent = i18n.t('clientHome.errorMessages.loadingError');
        document.getElementById('errorMessage').style.display = 'block';
      }
    };
  }

  // Override openDashboard function
  if (typeof window.originalOpenDashboard === 'undefined' && typeof openDashboard === 'function') {
    window.originalOpenDashboard = openDashboard;
    
    window.openDashboard = function() {
      if (!hasAccess) { 
        alert(i18n.t('clientHome.errorMessages.noSubscriptionAlert')); 
        return; 
      }
      if (!dashboardUrl) { 
        alert(i18n.t('clientHome.errorMessages.dashboardUrlError')); 
        return; 
      }
      window.open(dashboardUrl, '_blank');
    };
  }
}

/**
 * Update login dynamic content
 */
function updateLoginDynamicContent() {
  // Don't add duplicate event listener - login.html already handles form submission
  // This function is kept for future dynamic content updates if needed
  return;
}

/**
 * Update register dynamic content
 */
function updateRegisterDynamicContent() {
  // Don't add duplicate event listener - register.html already handles form submission
  // This function is kept for future dynamic content updates if needed
  return;
}

/**
 * Update form dynamic content
 */
function updateFormDynamicContent() {
  // Form submission is handled by contact-form.js
  // No additional handling needed here
}

/**
 * Update dashboard dynamic content
 */
function updateDashboardDynamicContent() {
  // Reload discount options and bundles with new language
  if (typeof loadDiscountOptions === 'function') {
    loadDiscountOptions();
  }
  if (typeof fetchBundles === 'function') {
    fetchBundles();
  }
}

/**
 * Update admin dynamic content
 */
function updateAdminDynamicContent() {
  // Admin panel translations will be handled separately
  // This is a placeholder for admin-specific dynamic content
}

/**
 * Utility function to safely get translation
 */
function safeTranslate(key, defaultValue = key) {
  if (typeof i18n !== 'undefined' && i18n.t) {
    return i18n.t(key, defaultValue);
  }
  return defaultValue;
}