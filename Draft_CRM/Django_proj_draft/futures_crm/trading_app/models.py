from django.db import models
from django.contrib.auth.models import User

class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades')
    symbol = models.CharField(max_length=50)
    type = models.CharField(max_length=5)  # LONG/SHORT
    entry_price = models.DecimalField(max_digits=15, decimal_places=2)
    current_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    leverage = models.PositiveIntegerField(default=1)
    pnl = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pnl_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=6, default='OPEN')  # OPEN/CLOSED
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} ({self.type})"
