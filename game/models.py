from django.core.validators import MinValueValidator
from django.db import models


class ScoreRecord(models.Model):
    """Record in rating tables"""
    name = models.CharField(blank=False, max_length=20, db_index=True)
    score = models.IntegerField(blank=False, default=0, db_index=True, validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.name}: {self.score}'
