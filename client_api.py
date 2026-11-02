import re
from typing import Any, Dict, List, Optional, Tuple, Union
import requests

class ApiClient:
    """Cliente unificado para comunicação com a API REST FastAPI (Python-PAV/PAV-Project)."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.current_user: Optional[Dict[str, Any]] = None
        self.timeout = 5.0

    def set_base_url(self, url: str) -> None:
        self.base_url = url.rstrip("/")

    def set_token(self, token: Optional[str]) -> None:
        self.token = token

    def set_current_user(self, user: Optional[Dict[str, Any]]) -> None:
        self.current_user = user

    def is_authenticated(self) -> bool:
        return bool(self.token)

    def logout(self) -> None:
        self.token = None
        self.current_user = None

    def _headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def _extract_error(self, response: requests.Response) -> str:
        """Extrai mensagens de erro claras e amigáveis das respostas de erro da API."""
        try:
            data = response.json()
        except Exception:
            return response.text or f"Erro HTTP {response.status_code}"

        # 1. Trata validações do Pydantic (status 422)
        if "errors" in data and isinstance(data["errors"], list):
            mensagens = []
            for err in data["errors"]:
                field = err.get("field", "campo")
                msg = err.get("message", "valor inválido")
                mensagens.append(f"• {field}: {msg}")
            return "Dados inválidos:\n" + "\n".join(mensagens)

        # 2. Trata campo 'detail' padrão do FastAPI
        if "detail" in data:
            detail = data["detail"]
            if isinstance(detail, list):
                mensagens = [f"• {e.get('loc', [''])[ -1]}: {e.get('msg', '')}" for e in detail if isinstance(e, dict)]
                return "Dados inválidos:\n" + "\n".join(mensagens)
            return str(detail)

        # 3. Trata outros formatos
        if "error" in data:
            return str(data["error"])
        if "message" in data:
            return str(data["message"])

        return f"Erro HTTP {response.status_code}: {data}"

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[bool, Union[Any, str]]:
        url = f"{self.base_url}{path}"
        try:
            req_headers = self._headers(headers)
            if data is not None and "Content-Type" in req_headers and "application/json" in req_headers["Content-Type"]:
                req_headers.pop("Content-Type", None)

            response = requests.request(
                method=method,
                url=url,
                json=json,
                data=data,
                params=params,
                headers=req_headers,
                timeout=self.timeout,
            )

            if response.status_code in (200, 201):
                try:
                    return True, response.json()
                except Exception:
                    return True, response.text
            elif response.status_code == 204:
                return True, None
            else:
                return False, self._extract_error(response)

        except requests.exceptions.ConnectionError:
            return (
                False,
                f"Não foi possível conectar ao servidor backend em {self.base_url}.\n"
                "Verifique se o backend FastAPI está em execução.",
            )
        except requests.exceptions.Timeout:
            return False, "Tempo de resposta do servidor esgotado (Timeout)."
        except requests.exceptions.RequestException as e:
            return False, f"Falha na requisição de rede: {str(e)}"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    # ==========================================
    # HEALTH CHECK
    # ==========================================
    def health_check(self) -> Tuple[bool, Union[Dict[str, Any], str]]:
        return self._request("GET", "/")

    # ==========================================
    # DOMÍNIO: AUTENTICAÇÃO (AUTH)
    # ==========================================
    def login(self, username_or_cpf: str, password: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """Realiza login no backend. Suporta CPF formatado ou apenas dígitos."""
        # Remove caracteres não numéricos se for CPF
        cpf_clean = re.sub(r"[^0-9]", "", username_or_cpf)
        cpf_val = cpf_clean if len(cpf_clean) == 11 else username_or_cpf

        payload = {"cpf": cpf_val, "password": password}
        success, res = self._request("POST", "/auth/login", json=payload)
        if success and isinstance(res, dict) and "access_token" in res:
            self.set_token(res["access_token"])
            # Busca dados do cliente logado
            me_success, me_res = self.get_me()
            if me_success and isinstance(me_res, dict):
                self.set_current_user(me_res)
            return True, res
        return False, res

    def get_me(self) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """Retorna o perfil do cliente autenticado."""
        return self._request("GET", "/auth/me")

    # ==========================================
    # DOMÍNIO: CLIENTES (CLIENTS)
    # ==========================================
    def list_clients(self, skip: int = 0, limit: int = 100) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        return self._request("GET", "/clients", params={"skip": skip, "limit": limit})

    def get_client(self, client_id: int) -> Tuple[bool, Union[Dict[str, Any], str]]:
        return self._request("GET", f"/clients/{client_id}")

    def create_client(self, data: Dict[str, Any]) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """Cria um novo cliente conforme ClientCreate."""
        return self._request("POST", "/clients", json=data)

    def update_client(self, client_id: int, data: Dict[str, Any]) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """Atualiza dados do cliente conforme ClientUpdate."""
        return self._request("PUT", f"/clients/{client_id}", json=data)

    def delete_client(self, client_id: int) -> Tuple[bool, Union[None, str]]:
        """Exclui cliente. Se possuir transações, o backend retorna 409 Conflict."""
        return self._request("DELETE", f"/clients/{client_id}")

    # ==========================================
    # DOMÍNIO: TRANSAÇÕES (TRANSACTIONS)
    # ==========================================
    def list_transactions(
        self,
        client_id: Optional[int] = None,
        classification: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        params: Dict[str, Any] = {"skip": skip, "limit": limit}
        if client_id is not None:
            params["client_id"] = client_id
        if classification and classification != "TODAS":
            params["classification"] = classification
        return self._request("GET", "/transactions", params=params)

    def get_transaction(self, transaction_id: int) -> Tuple[bool, Union[Dict[str, Any], str]]:
        return self._request("GET", f"/transactions/{transaction_id}")

    def create_transaction(self, data: Dict[str, Any]) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """Registra uma transação e aciona o motor de detecção de fraudes."""
        return self._request("POST", "/transactions", json=data)

    def update_transaction(self, transaction_id: int, data: Dict[str, Any]) -> Tuple[bool, Union[Dict[str, Any], str]]:
        return self._request("PUT", f"/transactions/{transaction_id}", json=data)

    def delete_transaction(self, transaction_id: int) -> Tuple[bool, Union[None, str]]:
        return self._request("DELETE", f"/transactions/{transaction_id}")

    # ==========================================
    # DOMÍNIO: REGRAS (RULES)
    # ==========================================
    def list_rules(self, skip: int = 0, limit: int = 100) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        return self._request("GET", "/rules", params={"skip": skip, "limit": limit})

    def get_rule(self, rule_id: int) -> Tuple[bool, Union[Dict[str, Any], str]]:
        return self._request("GET", f"/rules/{rule_id}")

    def create_rule(self, data: Dict[str, Any]) -> Tuple[bool, Union[Dict[str, Any], str]]:
        return self._request("POST", "/rules", json=data)

    def update_rule(self, rule_id: int, data: Dict[str, Any]) -> Tuple[bool, Union[Dict[str, Any], str]]:
        return self._request("PUT", f"/rules/{rule_id}", json=data)

    def delete_rule(self, rule_id: int) -> Tuple[bool, Union[None, str]]:
        return self._request("DELETE", f"/rules/{rule_id}")

    # ==========================================
    # DOMÍNIO: ALERTAS (ALERTS)
    # ==========================================
    def list_alerts(
        self,
        transaction_id: Optional[int] = None,
        rule_id: Optional[int] = None,
        classification: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        params: Dict[str, Any] = {"skip": skip, "limit": limit}
        if transaction_id is not None:
            params["transaction_id"] = transaction_id
        if rule_id is not None:
            params["rule_id"] = rule_id
        if classification and classification != "TODAS":
            params["classification"] = classification
        return self._request("GET", "/alerts", params=params)

    def get_alert(self, alert_id: int) -> Tuple[bool, Union[Dict[str, Any], str]]:
        return self._request("GET", f"/alerts/{alert_id}")


# Instância singleton global do cliente API
api = ApiClient()
