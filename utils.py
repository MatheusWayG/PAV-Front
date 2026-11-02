import re
from datetime import datetime
from typing import Optional

class CpfValidator:
    """Validador e formatador de CPF em conformidade estrita com o backend."""

    _ALLOWED_FORMAT = re.compile(r"^[0-9.\-\s]+$")

    @staticmethod
    def normalize(raw_cpf: str) -> str:
        """Mantém apenas os dígitos: '123.456.789-01' -> '12345678901'."""
        return re.sub(r"[^0-9]", "", raw_cpf or "")

    @staticmethod
    def format_cpf(raw_cpf: str) -> str:
        """Formata os dígitos no padrão 000.000.000-00."""
        digits = re.sub(r"[^0-9]", "", raw_cpf or "")
        if len(digits) == 11:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        return raw_cpf

    @classmethod
    def is_valid(cls, raw_cpf: str) -> bool:
        if not raw_cpf or not cls._ALLOWED_FORMAT.match(raw_cpf):
            return False

        cpf = cls.normalize(raw_cpf)
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        digits = [int(char) for char in cpf]
        return (
            digits[9] == cls._check_digit(digits[:9])
            and digits[10] == cls._check_digit(digits[:10])
        )

    @staticmethod
    def _check_digit(digits: list[int]) -> int:
        weight = len(digits) + 1
        total = sum(digit * (weight - index) for index, digit in enumerate(digits))
        return (total * 10 % 11) % 10


def format_currency(val: Optional[float]) -> str:
    """Formata valor numérico em moeda BRL (R$ 1.234,56)."""
    if val is None:
        return "R$ 0,00"
    try:
        f = float(val)
        return f"R$ {f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(val)


def format_datetime(iso_str: Optional[str]) -> str:
    """Converte string ISO de data/hora para padrão legível DD/MM/AAAA HH:MM."""
    if not iso_str:
        return "-"
    try:
        # Trata formato ISO (ex: 2026-11-01T14:30:00)
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(iso_str)

