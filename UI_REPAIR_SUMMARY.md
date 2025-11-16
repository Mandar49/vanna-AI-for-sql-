# UI REPAIR - Dark/Light Mode Fix

## Issue Fixed
The UI had washed-out, unreadable cards with light grey text on white backgrounds. Dark mode and light mode were not working properly.

## Root Cause
1. CSS variables were not properly defined for dark/light modes
2. Inline styles in JavaScript were overriding CSS classes
3. Text colors were not inheriting properly from parent elements
4. Card backgrounds were using fallback values instead of theme-specific colors

## Changes Made

### 1. templates/index.html - CSS Variables
**Added proper CSS variable definitions:**

**Light Mode (`:root`):**
- `--card-bg-data: #F8F9FA` (light grey)
- `--card-bg-insight: #F5F7FA` (lighter grey)
- `--card-bg-strategist: #F0F4FF` (light blue)
- `--card-bg-sql: #F9FAFB` (very light grey)
- `--card-text: #1F2937` (dark grey - 100% opaque)
- `--card-text-secondary: #6B7280` (medium grey)

**Dark Mode (`.dark`):**
- `--card-bg-data: #1E1E1E` (dark grey)
- `--card-bg-insight: #232323` (slightly lighter dark grey)
- `--card-bg-strategist: #1A1D2E` (dark blue)
- `--card-bg-sql: #1E1E1E` (dark grey)
- `--card-text: #FFFFFF` (pure white - 100% opaque)
- `--card-text-secondary: #B0B0B0` (light grey)

**Enhanced Card Styles:**
- Removed all opacity/transparency issues
- Added `!important` flags to ensure card backgrounds apply correctly
- Fixed text color inheritance with `color: var(--card-text)`
- Improved hover effects for both modes
- Fixed SQL code block styling

### 2. static/script.js - Removed Inline Styles
**Cleaned up `createCard()` function:**
- Removed all inline `style.cssText` that was overriding CSS classes
- Let CSS classes handle all styling via variables
- Kept only essential display logic (show/hide for collapsible SQL)

**Fixed text color inheritance:**
- Added `color: inherit` to all formatted content elements
- Ensures text respects parent card's color scheme
- Applied to: `<p>`, `<div>`, `<li>`, `<ul>`, `<pre>` elements

## Result
✅ **Dark Mode:** Clean black background (#1E1E1E) with white text (#FFFFFF)  
✅ **Light Mode:** Clean white background with dark text (#1F2937)  
✅ **Card Colors:** Properly themed for both modes  
✅ **Text Visibility:** 100% opaque, fully readable  
✅ **Theme Persistence:** Stored in localStorage, applies on page load  
✅ **No Layout Changes:** Only CSS repairs, no structural modifications

## Testing
To test the fix:
1. Start the server: `python ad_ai_app.py`
2. Open browser and navigate to the app
3. Toggle dark/light mode using the sun/moon icon
4. Ask a question and verify:
   - Cards have proper background colors
   - Text is fully visible (not washed out)
   - SQL blocks are readable
   - Theme persists on page reload

## Files Modified
- `templates/index.html` - CSS variables and card styling
- `static/script.js` - Removed inline styles, fixed text color inheritance
