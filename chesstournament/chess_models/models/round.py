from django.db import models


class Round(models.Model):
    name = models.CharField(max_length=128)
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True, default=None)
    finish = models.BooleanField(default=False)

    def __str__(self):
        return self.name
