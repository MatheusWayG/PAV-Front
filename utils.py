import re
from datetime import datetime
from typing import Callable, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

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
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(iso_str)


def criar_botao_acao(texto: str, cor_tipo: str, callback: Optional[Callable] = None) -> QPushButton:
    """Cria botões de ação estilizados e nítidos para uso nas células de tabelas."""
    btn = QPushButton(texto)
    btn.setFixedHeight(28)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)

    cores = {
        "blue": ("rgba(56, 189, 248, 0.22)", "rgba(56, 189, 248, 0.65)", "#38bdf8"),
        "amber": ("rgba(245, 158, 11, 0.22)", "rgba(245, 158, 11, 0.65)", "#fbbf24"),
        "green": ("rgba(16, 185, 129, 0.22)", "rgba(16, 185, 129, 0.65)", "#34d399"),
        "red": ("rgba(239, 68, 68, 0.22)", "rgba(239, 68, 68, 0.65)", "#f87171"),
        "purple": ("rgba(168, 85, 247, 0.22)", "rgba(168, 85, 247, 0.65)", "#c084fc"),
    }
    bg, border, text_color = cores.get(cor_tipo, cores["blue"])

    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg};
            border: 1px solid {border};
            border-radius: 6px;
            color: {text_color};
            font-size: 11px;
            font-weight: bold;
            padding: 3px 9px;
            font-family: 'Segoe UI', sans-serif;
            text-decoration: none;
        }}
        QPushButton:hover {{
            background-color: {border};
            color: #ffffff;
        }}
        QPushButton:pressed {{
            background-color: {bg};
        }}
    """)
    if callback:
        btn.clicked.connect(callback)
    return btn
