"""Points system core logic — pure Python, no UI dependency."""

from datetime import datetime


# Points awarded per minute of focus time
POINTS_PER_MINUTE = 0.4  # 25 min = 10 points


class PointTransaction:
    """A single points transaction record."""

    def __init__(self, amount: int, reason: str, timestamp: str | None = None):
        self.amount = amount
        self.reason = reason
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "amount": self.amount,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PointTransaction":
        return cls(
            amount=data["amount"],
            reason=data["reason"],
            timestamp=data.get("timestamp"),
        )


class PointsManager:
    """Manages points balance and transaction history."""

    def __init__(self):
        self.balance: int = 0
        self.history: list[PointTransaction] = []

    def add_points(self, amount: int, reason: str):
        """Add points and record the transaction."""
        self.balance += amount
        self.history.append(PointTransaction(amount, reason))

    def award_for_pomodoro(self, duration_minutes: int):
        """Award points for completing a Pomodoro session."""
        points = max(1, round(duration_minutes * POINTS_PER_MINUTE))
        self.add_points(points, f"Completed {duration_minutes}min focus session")

    def get_history(self) -> list[PointTransaction]:
        """Return transaction history, most recent first."""
        return list(reversed(self.history))

    def to_dict(self) -> dict:
        return {
            "balance": self.balance,
            "history": [t.to_dict() for t in self.history],
        }

    def load_from_dict(self, data: dict):
        """Restore state from a dictionary (loaded from storage)."""
        self.balance = data.get("balance", 0)
        self.history = [
            PointTransaction.from_dict(t) for t in data.get("history", [])
        ]
