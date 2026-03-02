# Mobile Navigation - Quick Reference Card

## 🎯 Quick Facts

**Breakpoint**: 992px (hamburger menu appears below this)
**Animation**: 0.4s slide from right
**Colors**: #2E4275 → #324c8f gradient
**Icons**: `elements/hamburger/` folder

## 📱 What Shows Where

### Desktop (> 992px)
```
[Logo] [Home] [Pricing] [Solutions] [FAQ] [🌐 EN] [Log in] [Get Started]
```

### Mobile (≤ 992px)
```
[Logo] [🌐 EN] [Get Started] [☰]
```
Click ☰ → Full menu overlay with all links

## 🔧 Key Files

| File | Purpose |
|------|---------|
| `dd.css` | All styles & responsive rules |
| `js/hamburger-menu.js` | Menu open/close logic |
| `*.html` | Updated headers on all pages |

## 🎨 CSS Classes

### Main Classes
```css
.hamburger-btn          /* Hamburger icon button */
.mobile-menu-overlay    /* Full-screen overlay */
.mobile-menu-close      /* Close button (X) */
.mobile-nav-links       /* Navigation links in overlay */
.mobile-menu-actions    /* Buttons in overlay */
```

### State Classes
```css
.mobile-menu-overlay.active  /* When menu is open */
.nav-links a.active          /* Current page indicator */
```

## 📐 Responsive Sizes

### Font Sizes
| Element | Desktop | Tablet | Mobile |
|---------|---------|--------|--------|
| Main Headline | 52px | 36px | 28px |
| Section Title | 48px | 32px | 26px |
| Body Text | 16px | 15px | 15px |
| Nav Links (Mobile) | - | 24px | 20px |

### Button Sizes
| Button | Desktop | Mobile |
|--------|---------|--------|
| Get Started | 16px / 20px padding | 13px / 8-16px padding |
| Hamburger Icon | Hidden | 28×28px |

## 🎬 How It Works

### Opening Menu
1. User clicks hamburger icon
2. `.active` class added to overlay
3. Overlay slides in from right (0.4s)
4. Body scroll disabled

### Closing Menu
1. User clicks:
   - Close button (X), OR
   - Outside menu area, OR
   - Any nav link, OR
   - Presses Escape key
2. `.active` class removed
3. Overlay slides out to right
4. Body scroll restored

## 🔍 Quick Debugging

### Menu Won't Open?
```javascript
// Check in browser console:
console.log(document.querySelector('.hamburger-btn'));
console.log(document.querySelector('.mobile-menu-overlay'));
// Both should return elements, not null
```

### Icons Not Showing?
```
Check paths:
✓ elements/hamburger/burger-menu-not opened.svg
✓ elements/hamburger/burger-menu-right-opened.svg
```

### Styles Not Applied?
```
1. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
2. Check dd.css is loaded
3. Verify viewport meta tag in HTML
```

## 📋 Testing Checklist

Quick test on each page:
- [ ] Resize to < 992px → hamburger appears
- [ ] Click hamburger → menu opens
- [ ] Click X → menu closes
- [ ] Click link → navigates & closes
- [ ] Press Escape → menu closes
- [ ] Logo, language switcher visible
- [ ] Text readable at all sizes

## 🚀 Adding New Pages

Copy this structure to new pages:

```html
<!-- In <head> -->
<script src="js/hamburger-menu.js"></script>

<!-- In header nav-actions -->
<button class="hamburger-btn" aria-label="Open menu">
    <img src="elements/hamburger/burger-menu-not opened.svg" alt="Menu">
</button>

<!-- After header -->
<div class="mobile-menu-overlay">
    <button class="mobile-menu-close" aria-label="Close menu">
        <img src="elements/hamburger/burger-menu-right-opened.svg" alt="Close">
    </button>
    <div class="mobile-menu-content">
        <!-- Copy nav structure from existing page -->
    </div>
</div>
```

## 🎨 Customization Quick Tips

### Change Menu Color
```css
/* In dd.css, find .mobile-menu-overlay */
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Change Animation Speed
```css
/* In dd.css, find .mobile-menu-overlay */
transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
/*                 ^^^^ Change this value */
```

### Change Breakpoint
```css
/* In dd.css, find all instances of */
@media (max-width: 992px)
/*                 ^^^^ Change this value */
```

### Adjust Font Sizes
```css
/* In dd.css, find responsive sections */
@media (max-width: 576px) {
    .main-headline {
        font-size: 28px; /* Adjust this */
    }
}
```

## 📞 Common Questions

**Q: Can I add more menu items?**
A: Yes! Add to both `.nav-links` (desktop) and `.mobile-nav-links` (mobile)

**Q: Can I change the slide direction?**
A: Yes! Change `right: -100%` to `left: -100%` in CSS

**Q: Does it work with RTL languages?**
A: Yes! The i18n system handles RTL. May need minor CSS adjustments.

**Q: Can I add a search bar?**
A: Yes! Add it to `.mobile-menu-content` in the overlay

**Q: Will it work on old browsers?**
A: Modern browsers (2020+) fully supported. IE11 needs polyfills.

## 🔗 Related Files

- `MOBILE_RESPONSIVE_IMPLEMENTATION.md` - Full documentation
- `TESTING_GUIDE.md` - Complete testing procedures
- `CHANGES_SUMMARY.md` - All changes made

## 💡 Pro Tips

1. **Test on real devices**, not just DevTools
2. **Clear cache** when testing CSS changes
3. **Check console** for JavaScript errors
4. **Use DevTools** device toolbar for quick testing
5. **Test landscape** orientation on tablets

## ⚡ Performance Notes

- Menu overlay is in DOM but hidden (display: none equivalent via transform)
- Animations use GPU acceleration (transform property)
- No external dependencies
- Minimal JavaScript overhead
- CSS-based animations for smoothness

## 🎯 Key Measurements

| Metric | Value |
|--------|-------|
| JavaScript File Size | ~1.5 KB |
| CSS Addition | ~5 KB |
| Animation Duration | 400ms |
| Breakpoint | 992px |
| Touch Target Size | 44×44px minimum |

---

**Quick Start**: Open any page, resize to < 992px, click hamburger icon ☰

**Need Help?** Check TESTING_GUIDE.md for detailed troubleshooting
