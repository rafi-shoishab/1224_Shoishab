from django.db import models
from django.contrib.auth.models import User


class AddCash(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cash_entries')
	source = models.CharField(max_length=200)
	datetime = models.DateTimeField(auto_now_add=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	description = models.TextField(blank=True)

	def __str__(self):
		return f"{self.user.username} +{self.amount} ({self.source})"


class Expense(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_entries')
	description = models.CharField(max_length=255)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	datetime = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.user.username} -{self.amount} ({self.description})"
