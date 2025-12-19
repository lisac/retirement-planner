from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RetirementCalculatorForm, CustomUserCreationForm
from .calculator import calculate_retirement_savings
from .phase_forms import (
    AccumulationPhaseForm,
    PhasedRetirementForm,
    ActiveRetirementForm,
    LateRetirementForm
)
from .models import Scenario


# =============================================================================
# SIMPLE CALCULATOR (Original Single-Phase)
# =============================================================================
# Legacy calculator for basic retirement projections.
# Uses calculator.py for calculations.
# Consider using multi-phase calculator for new features.

def retirement_calculator(request):
    """
    Handle retirement calculator form (original simple calculator).
    GET: Display empty form
    POST: Process form, calculate results, and display
    """
    results = None

    if request.method == 'POST':
        form = RetirementCalculatorForm(request.POST)
        if form.is_valid():
            # Calculate retirement savings using our clean calculator module
            results = calculate_retirement_savings(
                current_age=form.cleaned_data['current_age'],
                retirement_age=form.cleaned_data['retirement_age'],
                current_savings=form.cleaned_data['current_savings'],
                monthly_contribution=form.cleaned_data['monthly_contribution'],
                annual_return_rate=form.cleaned_data['expected_return'],
                variance=form.cleaned_data.get('variance')
            )
    else:
        # GET request - display empty form
        form = RetirementCalculatorForm()

    return render(request, 'calculator/retirement_calculator.html', {
        'form': form,
        'results': results
    })


def about(request):
    """
    Display the About page with information about the tool and creator.
    """
    return render(request, 'calculator/about.html')


# =============================================================================
# MULTI-PHASE CALCULATOR (Primary Feature)
# =============================================================================
# Advanced calculator with 4 retirement phases.
# Uses phase_calculator.py for calculations.
# Supports scenario loading and saving.

def multi_phase_calculator(request, scenario_id=None):
    """
    Multi-phase retirement calculator with tabbed interface.

    Displays all 4 retirement phases in separate tabs:
    - Phase 1: Accumulation (building wealth)
    - Phase 2: Phased Retirement (semi-retirement transition)
    - Phase 3: Active Retirement (early retirement years)
    - Phase 4: Late Retirement (legacy & healthcare)

    Optionally loads a saved scenario if scenario_id is provided.

    Args:
        request (HttpRequest): Django HTTP request object
        scenario_id (int, optional): Primary key of saved scenario to load

    Returns:
        HttpResponse: Rendered template with phase forms and loaded scenario data

    Template:
        calculator/multi_phase_calculator.html
    """
    # If scenario_id is provided, load the scenario data
    initial_data = {}
    scenario = None
    if scenario_id:
        # Only authenticated users can load scenarios
        if request.user.is_authenticated:
            scenario = get_object_or_404(Scenario, pk=scenario_id, user=request.user)
            initial_data = scenario.data

    # Initialize all forms (with scenario data if provided)
    accumulation_form = AccumulationPhaseForm(initial=initial_data)
    phased_retirement_form = PhasedRetirementForm(initial=initial_data)
    active_retirement_form = ActiveRetirementForm(initial=initial_data)
    late_retirement_form = LateRetirementForm(initial=initial_data)

    return render(request, 'calculator/multi_phase_calculator.html', {
        'accumulation_form': accumulation_form,
        'phased_retirement_form': phased_retirement_form,
        'active_retirement_form': active_retirement_form,
        'late_retirement_form': late_retirement_form,
        'loaded_scenario': scenario,
    })


# =============================================================================
# SCENARIO CRUD VIEWS
# =============================================================================
# Manage saved retirement scenarios (create, read, update, delete).
# Uses class-based views for standard CRUD operations.

class ScenarioListView(LoginRequiredMixin, ListView):
    """Display list of all saved scenarios for the logged-in user."""
    model = Scenario
    template_name = 'calculator/scenario_list.html'
    context_object_name = 'scenarios'

    def get_queryset(self):
        """Filter scenarios to only show the current user's scenarios."""
        return Scenario.objects.filter(user=self.request.user)


class ScenarioCreateView(LoginRequiredMixin, CreateView):
    """Create a new scenario."""
    model = Scenario
    fields = ['name', 'data']
    template_name = 'calculator/scenario_form.html'
    success_url = reverse_lazy('calculator:scenario_list')

    def form_valid(self, form):
        """Set the user before saving."""
        form.instance.user = self.request.user
        return super().form_valid(form)


class ScenarioUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing scenario."""
    model = Scenario
    fields = ['name', 'data']
    template_name = 'calculator/scenario_form.html'
    success_url = reverse_lazy('calculator:scenario_list')

    def get_queryset(self):
        """Only allow users to edit their own scenarios."""
        return Scenario.objects.filter(user=self.request.user)


class ScenarioDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a scenario."""
    model = Scenario
    template_name = 'calculator/scenario_confirm_delete.html'
    success_url = reverse_lazy('calculator:scenario_list')

    def get_queryset(self):
        """Only allow users to delete their own scenarios."""
        return Scenario.objects.filter(user=self.request.user)


# =============================================================================
# SCENARIO COMPARISON
# =============================================================================
# Compare two scenarios side-by-side and highlight better performer.

@login_required
def compare_scenarios(request):
    """
    Compare two scenarios side-by-side.
    GET: Display dropdown form to select scenarios
    POST: Calculate and display comparison results
    """
    from .phase_calculator import calculate_accumulation_phase
    from decimal import Decimal

    scenarios = Scenario.objects.filter(user=request.user)
    comparison_data = None
    error_message = None
    better_scenario = None

    if request.method == 'POST':
        scenario1_id = request.POST.get('scenario1')
        scenario2_id = request.POST.get('scenario2')

        # Validate selection
        if scenario1_id == scenario2_id:
            error_message = "Please select two different scenarios to compare."
        elif scenario1_id and scenario2_id:
            scenario1 = get_object_or_404(Scenario, pk=scenario1_id)
            scenario2 = get_object_or_404(Scenario, pk=scenario2_id)

            # Calculate results for both scenarios
            try:
                result1 = calculate_accumulation_phase(scenario1.data)
                result2 = calculate_accumulation_phase(scenario2.data)

                # Determine which scenario performs better (higher future value)
                if result1.future_value > result2.future_value:
                    better_scenario = 1
                elif result2.future_value > result1.future_value:
                    better_scenario = 2
                else:
                    better_scenario = 'tie'

                comparison_data = {
                    'scenario1': {
                        'name': scenario1.name,
                        'result': result1,
                    },
                    'scenario2': {
                        'name': scenario2.name,
                        'result': result2,
                    }
                }
            except (KeyError, ValueError) as e:
                error_message = f"Error calculating scenarios: {str(e)}"

    return render(request, 'calculator/scenario_compare.html', {
        'scenarios': scenarios,
        'comparison': comparison_data,
        'error_message': error_message,
        'better_scenario': better_scenario,
    })


# =============================================================================
# EMAIL SCENARIO REPORTS
# =============================================================================

@login_required
def email_scenario(request, scenario_id):
    """
    Queue scenario report email to be sent in the background.
    """
    from django_q.tasks import async_task

    # Check if user has an email address
    if not request.user.email:
        return HttpResponse(
            '<div class="text-red-600">Please add an email address to your profile to receive scenario reports.</div>'
        )

    # Get scenario (ensure user owns it)
    scenario = get_object_or_404(Scenario, pk=scenario_id, user=request.user)

    try:
        # Queue email task to run in background
        async_task(
            'calculator.tasks.send_scenario_email',
            scenario_id,
            request.user.email
        )

        return HttpResponse('<div class="text-green-600">✓ Scenario report email queued successfully! You\'ll receive it shortly.</div>')

    except Exception as e:
        return HttpResponse(f'<div class="text-red-600">Error queuing email: {str(e)}</div>')


# =============================================================================
# AUTHENTICATION
# =============================================================================

def register(request):
    """
    User registration view with required email.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            return redirect('calculator:multi_phase_calculator')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# =============================================================================
# PDF REPORT GENERATION
# =============================================================================

@login_required
def generate_pdf_report(request, scenario_id):
    """
    Generate and download a PDF report for a saved scenario.

    Monte Carlo charts are automatically included if the scenario has phase data.

    Args:
        scenario_id: ID of the scenario to generate PDF for
    """
    from .pdf_generator import generate_retirement_pdf

    # Get scenario and ensure user owns it
    scenario = get_object_or_404(Scenario, id=scenario_id, user=request.user)

    # Generate PDF (Monte Carlo charts included automatically)
    pdf_buffer = generate_retirement_pdf(scenario)

    # Create response
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')

    # Set filename (clean scenario name for filename)
    filename = f"{scenario.name.replace(' ', '_')}_Report.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
def generate_pdf_from_current(request):
    """
    Generate PDF from current calculator state (not saved scenario).

    Creates a temporary scenario from POST data and generates PDF.
    Monte Carlo charts are automatically included if phase data is available.
    """
    from .pdf_generator import generate_retirement_pdf
    from .models import Scenario

    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    # Create temporary scenario from POST data
    # Gather all phase data from the request
    scenario_data = {}

    # Phase 1 data
    if request.POST.get('current_age'):
        scenario_data['phase1'] = {
            'current_age': request.POST.get('current_age'),
            'retirement_start_age': request.POST.get('retirement_start_age'),
            'current_savings': request.POST.get('current_savings', 0),
            'monthly_contribution': request.POST.get('monthly_contribution', 0),
            'employer_match_rate': request.POST.get('employer_match_rate', 0),
            'expected_return': request.POST.get('expected_return', 7),
            'annual_salary_increase': request.POST.get('annual_salary_increase', 0),
            'return_volatility': request.POST.get('return_volatility', 10),  # For Monte Carlo
        }

    # Create temporary scenario (not saved to database)
    temp_scenario = Scenario(
        user=request.user,
        name=request.POST.get('scenario_name', 'Current Calculation'),
        data=scenario_data
    )

    # Generate PDF (Monte Carlo charts included automatically)
    pdf_buffer = generate_retirement_pdf(temp_scenario)

    # Create response
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')

    # Set filename
    filename = f"Retirement_Plan_Report.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
