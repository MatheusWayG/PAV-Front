import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from client_api import ApiClient
from utils import CpfValidator, format_currency, format_datetime


class TestCpfValidator(unittest.TestCase):
    def test_valid_cpfs(self):
        # Known valid Brazilian test CPFs
        valid_cpfs = [
            "52998224725",
            "529.982.247-25",
            "11144477735",
            "111.444.777-35",
        ]
        for cpf in valid_cpfs:
            self.assertTrue(CpfValidator.is_valid(cpf), f"Failed for {cpf}")

    def test_invalid_cpfs(self):
        invalid_cpfs = [
            "11111111111",  # Repeated digits
            "00000000000",
            "12345678900",  # Invalid checksum
            "123",          # Too short
            "abc12345678",  # Non-digit
            "",
            None,
        ]
        for cpf in invalid_cpfs:
            self.assertFalse(CpfValidator.is_valid(cpf), f"Should be invalid for {cpf}")

    def test_normalization(self):
        self.assertEqual(CpfValidator.normalize("123.456.789-01"), "12345678901")
        self.assertEqual(CpfValidator.normalize(" 12345678901 "), "12345678901")

    def test_formatting(self):
        self.assertEqual(CpfValidator.format_cpf("12345678901"), "123.456.789-01")


class TestFormatters(unittest.TestCase):
    def test_format_currency(self):
        self.assertEqual(format_currency(1234.56), "R$ 1.234,56")
        self.assertEqual(format_currency(0), "R$ 0,00")
        self.assertEqual(format_currency(None), "R$ 0,00")

    def test_format_datetime(self):
        self.assertEqual(format_datetime("2026-11-01T14:30:00"), "01/11/2026 14:30")
        self.assertEqual(format_datetime(None), "-")


class TestApiClient(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient(base_url="http://127.0.0.1:8000")

    def test_token_and_headers(self):
        self.assertFalse(self.client.is_authenticated())
        self.client.set_token("test-jwt-token")
        self.assertTrue(self.client.is_authenticated())

        headers = self.client._headers()
        self.assertEqual(headers["Authorization"], "Bearer test-jwt-token")
        self.assertEqual(headers["Content-Type"], "application/json")

        self.client.logout()
        self.assertFalse(self.client.is_authenticated())
        headers_after_logout = self.client._headers()
        self.assertNotIn("Authorization", headers_after_logout)

    @patch("requests.request")
    def test_error_extraction_422_pydantic(self, mock_request):
        # Simula resposta 422 com erros de validação
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "detail": "Invalid data.",
            "errors": [
                {"field": "cpf", "message": "Invalid CPF."},
                {"field": "monthly_income", "message": "Input should be greater than 0"},
            ],
        }
        mock_request.return_value = mock_response

        success, error_msg = self.client.create_client({"name": "Test"})
        self.assertFalse(success)
        self.assertIn("• cpf: Invalid CPF.", error_msg)
        self.assertIn("• monthly_income: Input should be greater than 0", error_msg)

    @patch("requests.request")
    def test_error_extraction_409_conflict(self, mock_request):
        # Simula conflito de integridade (ex: cliente possui transações)
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_response.json.return_value = {
            "detail": "This client has transactions and cannot be deleted. Deactivate the client instead."
        }
        mock_request.return_value = mock_response

        success, error_msg = self.client.delete_client(1)
        self.assertFalse(success)
        self.assertIn("This client has transactions and cannot be deleted", error_msg)


if __name__ == "__main__":
    unittest.main()

