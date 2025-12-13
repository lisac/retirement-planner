"""
HTMX-specific views for dynamic, partial page updates.

These views return HTML fragments instead of full pages.
Includes views for all four retirement phases.

Uses django-htmx's request.htmx to detect HTMX requests and return
appropriate templates (partials for HTMX, full pages for direct access).
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import json
from .forms import RetirementCalculatorForm, ScenarioNameForm
from .calculator import calculate_retirement_savings
from .phase_forms import (
    AccumulationPhaseForm,
    PhasedRetirementForm,
    ActiveRetirementForm,
    LateRetirementForm
)
from .phase_calculator import (
    calculate_accumulation_phase,
    calculate_phased_retirement_phase,
    calculate_active_retirement_phase,
    calculate_late_retirement_phase
)
from .models import Scenario


# ===== SHARED HELPER =====

def _process_phase_calculation(request, form_class, calculator_func, results_template):
    """
    Shared helper for processing phase calculations.

    This reduces code duplication across all phase views.

    Args:
        request: Django request object
        form_class: Form class to use for validation
        calculator_func: Calculator function to call with cleaned data
        results_template: Template path for results partial

    Returns:
        HttpResponse with results or errors HTML fragment
    """
    if request.method != 'POST':
        return HttpResponse('<div class="text-gray-500">Invalid request method</div>')

    form = form_class(request.POST)

    if form.is_valid():
        # Calculate results using the provided calculator function
        results = calculator_func(form.cleaned_data)

        # Return results partial
        return render(request, results_template, {'results': results})
    else:
        # Return validation errors
        return render(request, 'calculator/partials/form_errors.html', {'form': form})


# ===== ORIGINAL SIMPLE CALCULATOR (BACKWARDS COMPATIBILITY) =====

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
            results = calculate_retirement_savings(
                current_age=form.cleaned_data['current_age'],
                retirement_age=form.cleaned_data['retirement_age'],
                current_savings=form.cleaned_data['current_savings'],
                monthly_contribution=form.cleaned_data['monthly_contribution'],
                annual_return_rate=form.cleaned_data['expected_return'],
                variance=form.cleaned_data.get('variance')
            )

            # Use request.htmx to detect HTMX requests
            if request.htmx:
                # Return partial for HTMX request
                return render(request, 'calculator/partials/results.html', {'results': results})
            else:
                # Return full page for regular POST (fallback)
                return render(request, 'calculator/retirement_calculator.html', {
                    'form': form,
                    'results': results
                })
        else:
            # Return validation errors
            if request.htmx:
                return render(request, 'calculator/partials/form_errors.html', {'form': form})
            else:
                return render(request, 'calculator/retirement_calculator.html', {'form': form})

    return HttpResponse('<div class="text-gray-500">Invalid request</div>')


# ===== PHASE 1: ACCUMULATION =====

def calculate_accumulation(request):
    """
    HTMX endpoint: Calculate Phase 1 - Accumulation.

    Building wealth during working years with contributions and employer match.
    """
    return _process_phase_calculation(
        request,
        AccumulationPhaseForm,
        calculate_accumulation_phase,
        'calculator/partials/accumulation_results.html'
    )


# ===== PHASE 2: PHASED RETIREMENT =====

def calculate_phased_retirement(request):
    """
    HTMX endpoint: Calculate Phase 2 - Phased Retirement.

    Semi-retired with optional part-time income and contributions.
    """
    return _process_phase_calculation(
        request,
        PhasedRetirementForm,
        calculate_phased_retirement_phase,
        'calculator/partials/phased_retirement_results.html'
    )


# ===== PHASE 3: ACTIVE RETIREMENT =====

def calculate_active_retirement(request):
    """
    HTMX endpoint: Calculate Phase 3 - Active Retirement.

    Early retirement years with active lifestyle and moderate healthcare costs.
    """
    return _process_phase_calculation(
        request,
        ActiveRetirementForm,
        calculate_active_retirement_phase,
        'calculator/partials/active_retirement_results.html'
    )


# ===== PHASE 4: LATE RETIREMENT =====

def calculate_late_retirement(request):
    """
    HTMX endpoint: Calculate Phase 4 - Late Retirement.

    Final years with high healthcare and long-term care costs.
    """
    return _process_phase_calculation(
        request,
        LateRetirementForm,
        calculate_late_retirement_phase,
        'calculator/partials/late_retirement_results.html'
    )


# ===== SCENARIO MANAGEMENT =====

@login_required
def save_scenario(request):
    """
    HTMX endpoint: Save current calculator state as a scenario.

    Captures all form data from the multi-phase calculator and saves as JSON.
    """
    if request.method != 'POST':
        return HttpResponse('<div class="text-red-500">Invalid request method</div>')

    form = ScenarioNameForm(request.POST)

    if form.is_valid():
        # Create scenario with name from form
        scenario = form.save(commit=False)

        # Set the user to the logged-in user
        scenario.user = request.user

        # Capture all form data as JSON (excluding csrf_token and scenario_name)
        data = {}
        for key, value in request.POST.items():
            if key not in ['csrfmiddlewaretoken', 'name']:
                data[key] = value

        scenario.data = data
        scenario.save()

        # Return success message
        return HttpResponse(f'''
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                ✓ Scenario "{scenario.name}" saved successfully!
                <a href="/calculator/scenarios/" class="underline ml-2">View all scenarios</a>
            </div>
        ''')
    else:
        # Return error message
        errors = '<br>'.join([f'{field}: {error}' for field, error in form.errors.items()])
        return HttpResponse(f'<div class="text-red-500">{errors}</div>')
