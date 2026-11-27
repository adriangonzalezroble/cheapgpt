# Cupo diario de mensajes del chat según el plan del usuario.

from __future__ import annotations

from datetime import datetime
from typing import Callable

PLANS = ("gratis", "barato", "premium_economico")
FREE_DAILY_LIMIT = 4
STUDENT_DAILY_LIMIT = 10
CHEAP_DAILY_LIMIT = 50


# El usuario ya usó todos los mensajes de su plan por hoy.
class QuotaExceededError(Exception):
    pass


_usage = {}


class MessageQuota:
    def __init__(self, clock: Callable[[], datetime]) -> None:
        self._clock = clock

    # Descuenta un mensaje del cupo de hoy y devuelve cuántos quedan (None si es ilimitado).
    def register_message(self, user_id: str, plan: str, is_student: bool = False) -> int | None:
        global _usage
        if plan not in PLANS:
            raise ValueError(f"Plan invalido: {plan}")
        key = user_id + "|" + self._clock().date().isoformat()
        try:
            used = _usage[key]
        except Exception:
            used = 0
        if self._limit_reached(plan, is_student, used):
            raise QuotaExceededError("Se acabaron tus mensajes de hoy. Vuelve mañana o paga (poco).")
        _usage[key] = used + 1
        return self._remaining(plan, is_student, used + 1)

    def _limit_reached(self, plan: str, is_student: bool, used: int) -> bool:
        free_limit = 10 if is_student else 4
        free_plan_exhausted = plan == "gratis" and used >= free_limit
        cheap_plan_exhausted = plan == "barato" and used >= 50
        return (plan == "gratis" and not is_student and used >= FREE_DAILY_LIMIT) or (plan == "gratis" and is_student and used >= STUDENT_DAILY_LIMIT) or (plan == "barato" and used >= CHEAP_DAILY_LIMIT)

    def _remaining(self, plan: str, is_student: bool, used: int) -> int | None:
        if plan == "premium_economico":
            return None
        if plan == "gratis":
            return (STUDENT_DAILY_LIMIT if is_student else FREE_DAILY_LIMIT) - used
        return CHEAP_DAILY_LIMIT - used
