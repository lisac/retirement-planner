# HTMX Integration Guide

## What We Built

Your retirement calculator now uses HTMX for dynamic form submission without page reloads!

---

## Files Created/Modified

### New Files:
- ✅ `calculator/htmx_views.py` - HTMX endpoint that returns HTML fragments
- ✅ `calculator/templates/calculator/partials/results.html` - Results HTML partial
- ✅ `calculator/templates/calculator/partials/form_errors.html` - Error display partial

### Modified Files:
- ✅ `templates/base.html` - Added HTMX CDN script
- ✅ `calculator/templates/calculator/retirement_calculator.html` - Added HTMX attributes
- ✅ `calculator/urls.py` - Added HTMX endpoint URL

---

## How It Works

### 1. The Form (with HTMX attributes)

```html
<form method="post"
      hx-post="{% url 'calculator:calculate_htmx' %}"
      hx-target="#results-container"
      hx-indicator="#loading-indicator">
```

**Breakdown:**
- `hx-post="/calculator/calculate/"` → POST request to this URL
- `hx-target="#results-container"` → Replace content in this div
- `hx-indicator="#loading-indicator"` → Show loading spinner

### 2. The Submit Button (with loading state)

```html
<button type="submit">
    <!-- Hidden by default, shown during request -->
    <span class="htmx-indicator" id="loading-indicator">
        <svg class="animate-spin">...</svg>
    </span>

    <!-- Shown by default, hidden during request -->
    <span class="htmx-indicator-opposite" id="loading-indicator">
        Calculate My Retirement
    </span>

    <!-- Hidden by default, shown during request -->
    <span class="htmx-indicator" id="loading-indicator">
        Calculating...
    </span>
</button>
```

**How indicators work:**
- `.htmx-indicator` → Hidden by default, shown during request
- `.htmx-indicator-opposite` → Shown by default, hidden during request

### 3. The Target Container

```html
<div id="results-container">
    <!-- HTMX replaces everything inside this div -->
    {% if results %}
        <!-- Results display -->
    {% else %}
        <!-- Empty state -->
    {% endif %}
</div>
```

### 4. The HTMX View

```python
def calculate_htmx(request):
    """Returns HTML fragment, not full page"""
    if request.method == 'POST':
        form = RetirementCalculatorForm(request.POST)

        if form.is_valid():
            results = calculate_retirement_savings(...)

            # Return ONLY the results partial
            return render(request, 'calculator/partials/results.html', {
                'results': results
            })
        else:
            # Return validation errors partial
            return render(request, 'calculator/partials/form_errors.html', {
                'form': form
            })
```

**Key difference:** Returns partial HTML, not full page!

---

## HTMX Attributes Reference

### Most Common Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `hx-get` | Make GET request | `hx-get="/search"` |
| `hx-post` | Make POST request | `hx-post="/submit"` |
| `hx-put` | Make PUT request | `hx-put="/update/1"` |
| `hx-delete` | Make DELETE request | `hx-delete="/delete/1"` |
| `hx-target` | Where to put response | `hx-target="#result"` |
| `hx-swap` | How to swap content | `hx-swap="innerHTML"` |
| `hx-trigger` | When to trigger | `hx-trigger="keyup"` |
| `hx-indicator` | Loading indicator | `hx-indicator="#spinner"` |
| `hx-include` | Include other inputs | `hx-include="[name='age']"` |

### Target Selectors

```html
hx-target="#result"          <!-- Specific ID -->
hx-target=".results"         <!-- CSS class -->
hx-target="this"             <!-- Replace this element -->
hx-target="closest div"      <!-- Closest parent div -->
```

### Swap Options

```html
hx-swap="innerHTML"   <!-- Replace inner content (default) -->
hx-swap="outerHTML"   <!-- Replace entire element -->
hx-swap="beforebegin" <!-- Insert before element -->
hx-swap="afterbegin"  <!-- Insert at start of element -->
hx-swap="beforeend"   <!-- Insert at end of element -->
hx-swap="afterend"    <!-- Insert after element -->
hx-swap="delete"      <!-- Delete the target element -->
hx-swap="none"        <!-- Don't swap anything -->
```

### Trigger Options

```html
hx-trigger="click"                    <!-- On click (default for buttons) -->
hx-trigger="change"                   <!-- On change (default for inputs) -->
hx-trigger="keyup"                    <!-- On keyup -->
hx-trigger="keyup delay:500ms"        <!-- Debounced (wait 500ms) -->
hx-trigger="load"                     <!-- On page load -->
hx-trigger="revealed"                 <!-- When scrolled into view -->
hx-trigger="every 2s"                 <!-- Poll every 2 seconds -->
hx-trigger="click, keyup delay:500ms" <!-- Multiple triggers -->
```

---

## What Happens When You Submit?

### Traditional Django (before HTMX):
1. User fills form
2. User clicks "Calculate"
3. **Full page reload** 📄
4. Server renders entire HTML page
5. Browser displays new page

**Problem:** Slow, jarring experience, lose scroll position

### With HTMX (now):
1. User fills form
2. User clicks "Calculate"
3. **No page reload!** ⚡
4. HTMX makes POST request in background
5. Button shows loading spinner
6. Server returns just the results HTML fragment
7. HTMX swaps it into `#results-container`
8. Smooth, instant update!

**Benefits:** Fast, smooth, modern UX

---

## Testing Your HTMX Integration

### Start the servers:

**Terminal 1:**
```bash
source venv/bin/activate
python manage.py runserver
```

**Terminal 2:**
```bash
source venv/bin/activate
python manage.py tailwind start
```

### Visit:
http://127.0.0.1:8000/calculator/

### What to observe:

1. **Fill the form** with sample data:
   - Current Age: 30
   - Retirement Age: 65
   - Current Savings: $50,000
   - Monthly Contribution: $1,000
   - Expected Return: 7.5%

2. **Click "Calculate My Retirement"**

3. **Watch for:**
   - ✅ Button text changes to "Calculating..." with spinner
   - ✅ No page reload
   - ✅ Results appear smoothly in the right column
   - ✅ URL doesn't change
   - ✅ No flash/flicker

4. **Try entering invalid data** (e.g., retirement age < current age)
   - ✅ Error message appears without reload

---

## Debugging HTMX

### Browser DevTools

**Open Network tab:**
1. Submit the form
2. Look for request to `/calculator/calculate/`
3. Click on it
4. View "Response" tab - you should see just the HTML fragment!

**Console errors:**
- HTMX logs errors to console
- Look for red messages starting with "htmx:"

### Django Debug Toolbar (Optional)

Add to see HTMX requests:
```python
# settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

---

## Common HTMX Patterns

### Live Search

```html
<input
    type="text"
    name="search"
    hx-get="/search"
    hx-trigger="keyup changed delay:500ms"
    hx-target="#search-results">

<div id="search-results"></div>
```

### Infinite Scroll

```html
<div hx-get="/load-more?page=2"
     hx-trigger="revealed"
     hx-swap="afterend">
    Load More...
</div>
```

### Delete with Confirmation

```html
<button
    hx-delete="/delete/{{ item.id }}"
    hx-confirm="Are you sure?"
    hx-target="closest tr"
    hx-swap="outerHTML">
    Delete
</button>
```

### Polling (Auto-refresh)

```html
<div hx-get="/status"
     hx-trigger="every 2s"
     hx-target="this">
    Status: Loading...
</div>
```

---

## Best Practices

### ✅ DO
- Keep partials simple and focused
- Use meaningful IDs for targets
- Add loading indicators for slow requests
- Return appropriate HTTP status codes
- Use CSRF tokens with POST requests

### ❌ DON'T
- Return full HTML pages from HTMX endpoints
- Forget to handle validation errors
- Make too many simultaneous requests
- Rely on JavaScript for HTMX to work (it's all HTML!)

---

## Next Steps

### Want to add more HTMX features?

**Live preview while typing:**
```html
<input name="monthly_contribution"
       hx-get="/preview"
       hx-trigger="keyup changed delay:500ms"
       hx-include="[name='current_age'], [name='retirement_age']"
       hx-target="#live-preview">
```

**Scenario comparison:**
Add buttons to save multiple scenarios and compare them side-by-side.

**Charts/Graphs:**
Use HTMX to load chart data and render with Chart.js or similar.

---

## Resources

- **HTMX Docs:** https://htmx.org/docs/
- **Examples:** https://htmx.org/examples/
- **Django + HTMX:** https://django-htmx.readthedocs.io/

---

Your calculator is now HTMX-powered! No page reloads, smooth UX! 🎉
