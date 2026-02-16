# Manual Testing Guide - Contact Form Fixes

## Quick Start

1. **Start the server**: `python main.py` or `uvicorn main:app --reload`
2. **Open browser**: Navigate to `http://localhost:8000/static/form.html`

---

## Test 1: Email Validation Animation ⚠️

### Steps:
1. Open the contact form
2. Click on the **Email** field
3. Type Arabic characters: `أحمد` or `محمد`
4. **Watch for**:
   - ⚠️ Yellow warning box appears below email field
   - Smooth fade-in and slide animation
   - Warning text: "Email must contain only English characters"
   - Email input field highlights in yellow
5. Delete the Arabic characters
6. **Watch for**:
   - Warning box fades out smoothly
   - Yellow highlight disappears

### Expected Result:
✅ Warning appears/disappears with smooth animation  
✅ Input field highlights when Arabic detected  
✅ Warning text is clear and helpful

---

## Test 2: Arabic Form Submission 🇸🇦

### Steps:
1. Click the **language selector** (🌐 EN) in the top navigation
2. Select **🇸🇦 Arabic**
3. **Verify**: Page content switches to Arabic (right-to-left)
4. Fill out the form with Arabic content:
   - **الاسم الأول**: أحمد
   - **اسم العائلة**: علي
   - **البريد الإلكتروني**: ahmed@example.com *(must be English)*
   - **رقم الهاتف**: 501234567
   - **البلد**: السعودية
   - **اسم المطعم/العمل**: مطعم الاختبار
   - **عدد الفروع**: 1
   - **كيف سمعت عنا؟**: وسائل التواصل
5. Click **ابدأ الآن** (Get Started)
6. **Watch for**:
   - Form submits successfully
   - Success message appears in Arabic
   - Message: "شكراً لاهتمامك! سيتواصل معك فريقنا قريباً."

### Expected Result:
✅ Form works correctly in Arabic mode  
✅ All fields accept Arabic content (except email)  
✅ Success message displays in Arabic  
✅ No JavaScript errors in console

---

## Test 3: RTL Error Messages 📝

### Steps:
1. Make sure page is in **Arabic** language (🇸🇦)
2. Leave all form fields **empty**
3. Click **ابدأ الآن** (Get Started)
4. **Watch for**:
   - Error message box appears at top of form
   - Error title: "يرجى تصحيح الأخطاء التالية:"
   - Error list displays **right-to-left**
   - Errors aligned to the right side
   - Red error box with ✕ icon

### Expected Result:
✅ Error messages display right-to-left  
✅ Text aligned to the right  
✅ Error list items aligned correctly  
✅ No layout issues

---

## Test 4: Rate Limiting ⏱️

### Steps:
1. Switch to **English** language (easier to read messages)
2. Fill out the form with valid data:
   - **First name**: John
   - **Last name**: Doe
   - **Email**: john@example.com
   - **Phone**: 501234567
   - **Country**: Saudi Arabia
   - **Business name**: Test Restaurant
   - **Locations**: 1
   - **How did you hear about us?**: Social Media
3. Click **Get started**
4. **Watch for**:
   - Success message: "Thank you for your interest! Our team will contact you shortly."
5. **Immediately** try to submit the form again (same or different data)
6. **Watch for**:
   - Error message appears
   - Status: 429 (Too Many Requests)
   - Message: "You can only submit the contact form once per hour. Please try again later."

### Expected Result:
✅ First submission succeeds  
✅ Second submission blocked with 429 error  
✅ Error message mentions "once per hour"  
✅ Rate limit is working correctly

---

## Test 5: CSV Arabic Export 📊

### Prerequisites:
- You need admin access
- At least one contact with Arabic content submitted

### Steps:
1. **Login as admin**:
   - Navigate to `http://localhost:8000/static/login.html`
   - Email: `admin@example.com`
   - Password: `admin123` (or your admin password)
2. **Navigate to Admin Panel**:
   - Click **Admin Panel** in navigation
   - Click **Leads** tab
3. **Export CSV**:
   - Click **Export to CSV** button
   - CSV file downloads automatically
4. **Open in Excel**:
   - Open the downloaded CSV file in Microsoft Excel
   - **Watch for**:
     - Arabic names display correctly (أحمد, علي)
     - Arabic business names display correctly (مطعم الاختبار)
     - No corrupted characters (�, ?, boxes)
     - Text is readable and properly formatted

### Expected Result:
✅ CSV downloads successfully  
✅ Arabic text displays correctly in Excel  
✅ No character corruption  
✅ All columns aligned properly

---

## Test 6: Mixed Language Content 🌍

### Steps:
1. Switch to **English** language
2. Fill out form with **mixed content**:
   - **First name**: أحمد (Arabic)
   - **Last name**: Smith (English)
   - **Email**: ahmed.smith@example.com (English only)
   - **Business name**: مطعم Smith Restaurant (Mixed)
3. Submit form
4. **Watch for**:
   - Form accepts mixed content
   - Only email field shows warning if Arabic entered
   - Success message appears

### Expected Result:
✅ Form accepts Arabic in name fields  
✅ Form accepts English in name fields  
✅ Email field only accepts English  
✅ Mixed content works correctly

---

## Troubleshooting

### Issue: Warning animation not working
- **Check**: Browser console for JavaScript errors
- **Check**: `static/js/contact-form.js` loaded correctly
- **Try**: Hard refresh (Ctrl+F5 or Cmd+Shift+R)

### Issue: Form doesn't work in Arabic
- **Check**: Browser console for errors
- **Check**: All inputs have `data-field` attributes
- **Try**: Clear browser cache and reload

### Issue: Rate limiting not working
- **Check**: Server is running
- **Check**: `main.py` has rate limit configuration
- **Try**: Restart server

### Issue: CSV Arabic text corrupted
- **Check**: File opened in Microsoft Excel (not Notepad)
- **Check**: CSV has UTF-8 BOM (`\ufeff`)
- **Try**: Open with Excel's "Import Data" feature

---

## Success Criteria

All tests should pass with these results:

- ✅ Email validation shows smooth animation
- ✅ Form works in both English and Arabic
- ✅ Error messages display RTL in Arabic
- ✅ Rate limiting blocks second submission
- ✅ CSV export shows Arabic correctly in Excel
- ✅ Mixed language content works

---

## Quick Test Checklist

Use this checklist to verify all fixes:

- [ ] Email warning animation appears when typing Arabic
- [ ] Email warning disappears when Arabic removed
- [ ] Form submits successfully in English mode
- [ ] Form submits successfully in Arabic mode
- [ ] Error messages display RTL in Arabic
- [ ] First form submission succeeds
- [ ] Second form submission blocked (429 error)
- [ ] Error message says "once per hour"
- [ ] CSV export downloads successfully
- [ ] Arabic text in CSV displays correctly in Excel
- [ ] Mixed language content works

---

## Notes

- **Rate Limit Reset**: Wait 1 hour between submissions, or restart server to reset
- **Admin Credentials**: Check `LOGIN_CREDENTIALS.txt` for admin login
- **Database**: Contact data stored in `dev.db` SQLite database
- **Logs**: Check terminal/console for server logs

---

## Need Help?

If any test fails:
1. Check browser console for JavaScript errors
2. Check server terminal for Python errors
3. Verify all files are saved and server restarted
4. Try clearing browser cache
5. Review `CONTACT_FORM_ALL_FIXES_COMPLETE.md` for implementation details

---

**Happy Testing!** 🎉
