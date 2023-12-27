from django.db import models


# Create your models here.
class TeamSentiment(models.Model):
    team_name = models.CharField(max_length=255)
    avg_compound_score = models.FloatField()

    def __str__(self):
        return self.team_name
