# Django + HTMX Integration Guide

## Table of Contents
1. [Using django-htmx](#using-django-htmx)
2. [Detecting HTMX Requests](#detecting-htmx-requests)
3. [Animations & Transitions](#animations--transitions)
4. [Best Practices](#best-practices)

---

## Using django-htmx

### Installation

```bash
pip install django-htmx
```

### Configuration

Add to `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'django_htmx',
]

MIDDLEWARE = [
    # ...
    'django_htmx.middleware.HtmxMiddleware',
]
```

### Benefits

- **request.htmx**: Boolean property to detect HTMX requests
- **request.htmx.target**: Get the target element ID
- **request.htmx.trigger**: Get the triggering element ID
- **request.htmx.current_url**: Current URL before HTMX request
- **request.htmx.boosted**: Whether request is boosted

---

## Detecting HTMX Requests

### Pattern: Return Partial vs Full Page

**Use Case:** Same view should work for both HTMX and regular requests.

```python
from django.shortcuts import render

def my_view(request):
    # Process data
    results = calculate_something(request.POST)

    # Detect HTMX request
    if request.htmx:
        # Return partial HTML fragment
        return render(request, 'partials/results.html', {
            'results': results
        })
    else:
        # Return full page (fallback for direct access)
        return render(request, 'full_page.html', {
            'results': results
        })
```

### Example from Our Calculator

```python
def calculate_htmx(request):
    """
    HTMX endpoint: Original simple retirement calculator.

    Detects HTMX requests using request.htmx and returns appropriate template:
    - HTMX request: Returns partial HTML fragment
    - Regular request: Returns full page (fallback for direct access)
    """
    if request.method == 'POST':
        form = RetirementCalculatorForm(request.POST)

        if form.is_valid():
            results = calculate_retirement_savings(...)

            # Use request.htmx to detect HTMX requests
            if request.htmx:
                # Return partial for HTMX request
                return render(request, 'calculator/partials/results.html', {
                    'results': results
                })
            else:
                # Return full page for regular POST (fallback)
                return render(request, 'calculator/retirement_calculator.html', {
                    'form': form,
                    'results': results
                })
        else:
            # Return validation errors
            if request.htmx:
                return render(request, 'calculator/partials/form_errors.html', {
                    'form': form
                })
            else:
                return render(request, 'calculator/retirement_calculator.html', {
                    'form': form
                })
```

### Advanced: Using HX Headers

```python
from django_htmx.http import HttpResponseClientRefresh, HttpResponseClientRedirect

def my_view(request):
    # After successful action, redirect using HTMX
    if request.htmx:
        return HttpResponseClientRedirect('/success/')
    else:
        return redirect('/success/')
```

**Available HTMX Response Classes:**
- `HttpResponseClientRedirect` - Client-side redirect
- `HttpResponseClientRefresh` - Refresh the page
- `HttpResponseStopPolling` - Stop polling
- `trigger_client_event` - Trigger custom events

---

## Animations & Transitions

### HTMX Swap Animations

HTMX provides built-in CSS classes during swaps:

```html
<form
    hx-post="/calculate/"
    hx-target="#results"
    hx-swap="innerHTML swap:0.3s settle:0.3s">
</form>
```

**HTMX CSS Classes:**
- `.htmx-swapping` - Applied during swap (before content changes)
- `.htmx-settling` - Applied after swap (content settling)

### CSS for HTMX Animations

```css
/* Fade out old content */
.htmx-swapping {
    opacity: 0;
    transition: opacity 0.3s ease-out;
}

/* Fade in new content */
.htmx-settling {
    opacity: 1;
    transition: opacity 0.3s ease-in;
}
```

### Tailwind + Custom Animations

**HTML:**
```html
<div id="results" class="transition-all duration-500">
    <div class="animate-fade-in">
        <!-- Results content -->
    </div>
</div>
```

**CSS:**
```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-fade-in {
    animation: fadeIn 0.5s ease-out;
}
```

### Form Input Focus Animations

```css
/* Subtle scale on focus */
input:focus, select:focus, textarea:focus {
    transform: scale(1.01);
    transition: transform 0.2s ease-out;
}
```

### Button Hover Effects

```css
.tab-button {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

### HTMX Swap Options

```html
<!-- Default: innerHTML -->
hx-swap="innerHTML"

<!-- With timing -->
hx-swap="innerHTML swap:300ms"

<!-- With timing and settle delay -->
hx-swap="innerHTML swap:300ms settle:300ms"

<!-- Different swap strategies -->
hx-swap="outerHTML"      <!-- Replace entire element -->
hx-swap="beforebegin"    <!-- Insert before element -->
hx-swap="afterbegin"     <!-- Insert at start -->
hx-swap="beforeend"      <!-- Insert at end (default for append) -->
hx-swap="afterend"       <!-- Insert after element -->
hx-swap="delete"         <!-- Delete target element -->
hx-swap="none"           <!-- Don't swap anything -->
```

### Loading Indicators with Animations

```html
<button type="submit">
    <!-- Spinner (hidden by default, shown during request) -->
    <span class="htmx-indicator" id="loading-spinner">
        <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10"
                    stroke="currentColor" stroke-width="4" fill="none"/>
            <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
    </span>

    <!-- Button text (shown by default, hidden during request) -->
    <span class="htmx-indicator-opposite" id="loading-spinner">
        Calculate
    </span>

    <!-- Loading text (hidden by default, shown during request) -->
    <span class="htmx-indicator" id="loading-spinner">
        Calculating...
    </span>
</button>
```

---

## Best Practices

### 1. Always Provide Fallbacks

```python
# Good: Works for both HTMX and regular requests
if request.htmx:
    return render(request, 'partials/content.html', context)
else:
    return render(request, 'full_page.html', context)
```

### 2. Use Semantic HTML

```html
<!-- Good: Semantic, accessible -->
<button hx-post="/action/">Submit</button>

<!-- Bad: Divs aren't buttons -->
<div hx-post="/action/">Submit</div>
```

### 3. Keep Partials Simple

**Partial template should contain only the fragment:**

```html
<!-- partials/results.html -->
<div class="results">
    <h3>Results</h3>
    <p>{{ results.value }}</p>
</div>
```

**Not a full page:**
```html
<!-- BAD: Don't include base template in partials -->
{% extends "base.html" %}
{% block content %}
<div class="results">...</div>
{% endblock %}
```

### 4. Handle Errors Gracefully

```python
if form.is_valid():
    # Success case
    if request.htmx:
        return render(request, 'partials/success.html', context)
else:
    # Error case
    if request.htmx:
        return render(request, 'partials/errors.html', {'form': form})
```

### 5. Use CSRF Tokens

```html
<form method="post" hx-post="/submit/">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### 6. Optimize for Performance

```html
<!-- Debounce search input -->
<input
    type="text"
    hx-get="/search"
    hx-trigger="keyup changed delay:500ms"
    hx-target="#results">
```

### 7. Use Indicators for Long Operations

```html
<form
    hx-post="/calculate/"
    hx-indicator="#loading">

    <div id="loading" class="htmx-indicator">
        Loading...
    </div>
</form>
```

### 8. Preserve Scroll Position

```html
<!-- HTMX preserves scroll by default, but you can control it -->
<div hx-get="/content" hx-swap="innerHTML scroll:top">
    <!-- Scroll to top after swap -->
</div>
```

---

## Common Patterns

### Live Search

```html
<input
    type="text"
    name="query"
    hx-get="/search"
    hx-trigger="keyup changed delay:500ms"
    hx-target="#search-results">

<div id="search-results"></div>
```

### Infinite Scroll

```html
<div
    hx-get="/load-more?page=2"
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

### Polling / Auto-refresh

```html
<div
    hx-get="/status"
    hx-trigger="every 2s"
    hx-target="this">
    Status: Loading...
</div>
```

---

## Debugging Tips

### 1. Check Network Tab

Look for:
- Request headers (HX-Request: true)
- Response should be HTML fragment
- Status codes (200 OK, 400 Bad Request, etc.)

### 2. HTMX Event Logging

```html
<body hx-on="htmx:afterRequest: console.log(event.detail)">
```

### 3. Django Debug Toolbar

Shows:
- Which view was called
- SQL queries
- Template rendering time

### 4. Browser Console

HTMX logs events to console by default.

---

## Resources

- **django-htmx docs**: https://django-htmx.readthedocs.io/
- **HTMX docs**: https://htmx.org/docs/
- **HTMX examples**: https://htmx.org/examples/
- **Tailwind CSS**: https://tailwindcss.com/docs

---

Your retirement calculator uses all these patterns! Check the code for live examples. 🚀
