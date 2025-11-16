# Frontend Quick Reference

## Theme Toggle

### HTML Setup
```html
<html x-data="{ darkMode: localStorage.getItem('darkMode') === 'true' }" 
      :class="{ 'dark': darkMode }">
```

### Toggle Button
```html
<button @click="darkMode = !darkMode; localStorage.setItem('darkMode', darkMode)">
    <!-- Icons toggle based on darkMode state -->
</button>
```

## Styled Card Template

```html
<div class="stat-card bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-4 shadow-sm hover:shadow-md">
    <h3 class="text-sm font-medium text-gray-600 dark:text-dark-text-secondary uppercase tracking-wide mb-2">
        METRIC LABEL
    </h3>
    <p class="text-2xl font-bold text-gray-900 dark:text-dark-text mb-1">
        $1,234.56
    </p>
    <span class="text-sm font-medium text-green-600 dark:text-green-400">
        ▲ +5.2%
    </span>
</div>
```

## Color Classes

### Backgrounds
```css
bg-gray-50          /* Light mode background */
dark:bg-dark-bg     /* Dark mode background (#1E1E1E) */

bg-white            /* Light mode card */
dark:bg-dark-card   /* Dark mode card (#2D2D2D) */
```

### Text
```css
text-gray-900       /* Light mode primary text */
dark:text-dark-text /* Dark mode primary text (#E5E5E5) */

text-gray-600       /* Light mode secondary text */
dark:text-dark-text-secondary /* Dark mode secondary (#B0B0B0) */
```

### Borders
```css
border-gray-200     /* Light mode border */
dark:border-dark-border /* Dark mode border (#3D3D3D) */
```

### Accent
```css
bg-accent           /* Accent background (#00BFA6) */
text-accent         /* Accent text (#00BFA6) */
hover:bg-accent-hover /* Accent hover (#00A890) */
```

## Message Bubbles

### User Message
```html
<div class="flex justify-end mb-4">
    <div class="max-w-3xl bg-accent text-white rounded-2xl rounded-tr-sm px-5 py-4 shadow-sm">
        <p>User's question here</p>
    </div>
</div>
```

### AI Message
```html
<div class="flex justify-start mb-4">
    <div class="max-w-3xl bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm">
        <p class="text-gray-700 dark:text-dark-text-secondary">AI response here</p>
    </div>
</div>
```

## Buttons

### Primary
```html
<button class="px-6 py-3 font-medium text-white bg-accent hover:bg-accent-hover rounded-lg transition-colors">
    Primary Action
</button>
```

### Secondary
```html
<button class="px-6 py-3 font-medium text-accent bg-transparent border-2 border-accent rounded-lg hover:bg-accent hover:text-white transition-all">
    Secondary Action
</button>
```

### Tertiary
```html
<button class="px-6 py-3 font-medium text-gray-700 dark:text-dark-text bg-gray-100 dark:bg-dark-card border border-gray-300 dark:border-dark-border rounded-lg hover:bg-gray-200 dark:hover:bg-dark-bg transition-colors">
    Tertiary Action
</button>
```

## Form Inputs

### Text Input
```html
<input 
    type="text" 
    placeholder="Enter text..." 
    class="w-full px-4 py-3 text-gray-900 dark:text-dark-text bg-gray-50 dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent">
```

### Textarea
```html
<textarea 
    rows="3" 
    placeholder="Enter text..." 
    class="w-full px-4 py-3 text-gray-900 dark:text-dark-text bg-gray-50 dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"></textarea>
```

## Responsive Grid

### 1-2-3-4 Column Grid
```html
<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
    <!-- Items -->
</div>
```

### Card Grid (for metrics)
```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Stat cards -->
</div>
```

## Icons (Heroicons)

### Database
```html
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path>
</svg>
```

### Chart
```html
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
</svg>
```

### Error
```html
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
</svg>
```

## Trend Indicators

### Positive (Green)
```html
<span class="text-sm font-medium text-green-600 dark:text-green-400">
    ▲ +5.2%
</span>
```

### Negative (Red)
```html
<span class="text-sm font-medium text-red-600 dark:text-red-400">
    ▼ -2.1%
</span>
```

### Neutral (Gray)
```html
<span class="text-sm font-medium text-gray-600 dark:text-gray-400">
    ➖ 0.0%
</span>
```

## JavaScript Card Creation

```javascript
const createStyledCard = (label, value, trend = null) => {
    const card = document.createElement('div');
    card.className = 'stat-card bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-4 shadow-sm hover:shadow-md';
    
    const labelEl = document.createElement('h3');
    labelEl.className = 'text-sm font-medium text-gray-600 dark:text-dark-text-secondary uppercase tracking-wide mb-2';
    labelEl.textContent = label;
    
    const valueEl = document.createElement('p');
    valueEl.className = 'text-2xl font-bold text-gray-900 dark:text-dark-text mb-1';
    valueEl.textContent = value;
    
    card.appendChild(labelEl);
    card.appendChild(valueEl);
    
    if (trend) {
        const trendEl = document.createElement('span');
        const isPositive = trend.includes('▲') || trend.includes('+');
        trendEl.className = `text-sm font-medium ${
            isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
        }`;
        trendEl.textContent = trend;
        card.appendChild(trendEl);
    }
    
    return card;
};

// Usage
const card = createStyledCard('TOTAL SALES', '$4,110,315.23', '▲ +2.85%');
container.appendChild(card);
```

## LocalStorage Theme

### Save Theme
```javascript
localStorage.setItem('darkMode', true);
```

### Load Theme
```javascript
const darkMode = localStorage.getItem('darkMode') === 'true';
```

### Clear Theme
```javascript
localStorage.removeItem('darkMode');
```

## Accessibility

### Focus Ring
```css
focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2
```

### ARIA Label
```html
<button aria-label="Toggle dark mode" title="Toggle dark mode">
    <!-- Icon -->
</button>
```

### Semantic HTML
```html
<nav><!-- Navigation --></nav>
<main><!-- Main content --></main>
<aside><!-- Sidebar --></aside>
<section><!-- Section --></section>
```

## Testing URLs

- Main App: `http://localhost:5000`
- UI Test: `file:///path/to/test_frontend_ui.html`

## Browser DevTools

### Test Responsive
1. Open DevTools (F12)
2. Click device toolbar icon
3. Select device or custom dimensions

### Test Accessibility
1. Chrome: Lighthouse > Accessibility
2. Firefox: Accessibility Inspector
3. Install WAVE or axe DevTools extension

### Test Dark Mode
1. Toggle theme button
2. Check localStorage in Application tab
3. Verify all colors change appropriately
