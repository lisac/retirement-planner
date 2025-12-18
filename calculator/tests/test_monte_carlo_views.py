"""
Tests for Monte Carlo HTMX views.
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse


class MonteCarloAccumulationViewTests(TestCase):
    """Tests for accumulation phase Monte Carlo HTMX view."""

    def setUp(self):
        self.client = Client()

    def test_monte_carlo_accumulation_requires_post(self):
        """Test that GET requests are not allowed."""
        response = self.client.get(reverse('calculator:monte_carlo_accumulation'))
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_monte_carlo_accumulation_with_valid_data(self):
        """Test Monte Carlo accumulation with valid input data."""
        data = {
            'current_savings': '50000',
            'monthly_contribution': '1000',
            'years_to_retirement': '30',
            'expected_return': '7.0',
            'variance': '2.0',
        }

        response = self.client.post(
            reverse('calculator:monte_carlo_accumulation'),
            data=data,
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Monte Carlo Analysis', response.content)
        self.assertIn(b'percentile', response.content)
        self.assertIn(b'10th', response.content)
        self.assertIn(b'Median', response.content)
        self.assertIn(b'90th', response.content)

    def test_monte_carlo_accumulation_missing_required_field(self):
        """Test that missing required fields still run with zero defaults."""
        data = {
            'current_savings': '50000',
            # Missing monthly_contribution - will default to 0
            'years_to_retirement': '30',
            'expected_return': '7.0',
        }

        response = self.client.post(
            reverse('calculator:monte_carlo_accumulation'),
            data=data,
            HTTP_HX_REQUEST='true'
        )

        # Should still work with defaults (not an error)
        self.assertEqual(response.status_code, 200)

    def test_monte_carlo_accumulation_invalid_data_type(self):
        """Test that invalid data types return error."""
        data = {
            'current_savings': 'not-a-number',
            'monthly_contribution': '1000',
            'years_to_retirement': '30',
            'expected_return': '7.0',
        }

        response = self.client.post(
            reverse('calculator:monte_carlo_accumulation'),
            data=data,
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 400)

    def test_monte_carlo_accumulation_uses_default_variance(self):
        """Test that variance defaults to 2.0 if not provided."""
        data = {
            'current_savings': '50000',
            'monthly_contribution': '1000',
            'years_to_retirement': '30',
            'expected_return': '7.0',
            # No variance provided
        }

        response = self.client.post(
            reverse('calculator:monte_carlo_accumulation'),
            data=data,
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Monte Carlo Analysis', response.content)


class MonteCarloWithdrawalViewTests(TestCase):
    """Tests for withdrawal phase Monte Carlo HTMX view."""

    def setUp(self):
        self.client = Client()

    def test_monte_carlo_withdrawal_requires_post(self):
        """Test that GET requests are not allowed."""
        response = self.client.get(reverse('calculator:monte_carlo_withdrawal'))
        self.assertEqual(response.status_code, 405)

    def test_monte_carlo_withdrawal_with_valid_data(self):
        """Test Monte Carlo withdrawal with valid input data."""
        data = {
            'starting_portfolio': '1000000',
            'annual_withdrawal': '40000',
            'years': '30',
            'expected_return': '5.0',
            'variance': '2.0',
            'inflation_rate': '3.0',
        }

        response = self.client.post(
            reverse('calculator:monte_carlo_withdrawal'),
            data=data,
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Monte Carlo Analysis', response.content)
        self.assertIn(b'Success Rate', response.content)
        self.assertIn(b'Percentile', response.content)

    def test_monte_carlo_withdrawal_uses_default_inflation(self):
        """Test that inflation_rate defaults to 3.0 if not provided."""
        data = {
            'starting_portfolio': '1000000',
            'annual_withdrawal': '40000',
            'years': '30',
            'expected_return': '5.0',
            'variance': '2.0',
            # No inflation_rate
        }

        response = self.client.post(
            reverse('calculator:monte_carlo_withdrawal'),
            data=data,
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 200)

    def test_monte_carlo_withdrawal_missing_required_field(self):
        """Test that missing required fields still run with zero defaults."""
        data = {
            'starting_portfolio': '1000000',
            # Missing annual_withdrawal - will default to 0
            'years': '30',
            'expected_return': '5.0',
        }

        response = self.client.post(
            reverse('calculator:monte_carlo_withdrawal'),
            data=data,
            HTTP_HX_REQUEST='true'
        )

        # Should still work with defaults (not an error)
        self.assertEqual(response.status_code, 200)

    def test_monte_carlo_withdrawal_invalid_data_type(self):
        """Test that invalid data types return error."""
        data = {
            'starting_portfolio': 'invalid',
            'annual_withdrawal': '40000',
            'years': '30',
            'expected_return': '5.0',
        }

        response = self.client.post(
            reverse('calculator:monte_carlo_withdrawal'),
            data=data,
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 400)
