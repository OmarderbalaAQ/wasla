# i18n Translation Files

This directory contains language translation files for the Wasla platform.

## Current Files

- **en.json** - English translations (complete)
- **ar.json** - Arabic translations (pending - to be provided by user)

## File Structure

The JSON files are organized hierarchically by page/component:

```
{
  "common": { ... },           // Shared UI elements across all pages
  "dashboard": { ... },        // Subscription plans page
  "clientHome": { ... },       // User dashboard home page
  "login": { ... },            // Login page
  "register": { ... },         // Registration page
  "faq": { ... },              // FAQ page
  "index": { ... },            // Home page
  "solutions": { ... },        // Solutions page
  "pricing": { ... },          // Pricing page (non-registered)
  "form": { ... }              // Contact/signup form page
}
```

## Key Organization

Each section contains:
- **title** - Page title
- **heading/subtitle** - Main headings
- **form** - Form labels and placeholders
- **buttons** - Button text
- **messages** - Error/success messages
- **faq** - FAQ questions and answers
- **features** - Feature lists
- **footer** - Footer content

## Usage

When implementing i18n, use keys like:
- `en.dashboard.pricing.title` → "Choose Your Subscription Plan"
- `en.login.form.email` → "Email address"
- `en.common.logout` → "Log out"

## Next Steps

1. User provides Arabic JSON file (ar.json)
2. Implement i18n system in frontend using these translation files
3. Add language switcher functionality
4. Test both English and Arabic versions

## Notes

- All text has been extracted from the specified pages
- Admin panel (admin.html) is excluded as per requirements
- Hierarchical keys make it easy to organize and maintain translations
- Ready for implementation with any i18n library (i18next, vue-i18n, etc.)
