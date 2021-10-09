"""Create models for ku-polls."""
import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """Class for create question."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('end date', null=True)

    def __str__(self):
        """Return question_text."""
        return self.question_text

    def was_published_recently(self):
        """Check was published recently method."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Check the question is ready to vote."""
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """Check the question is in vote time."""
        now = timezone.now()
        return self.pub_date <= now <= self.end_date


class Choice(models.Model):
    """Class for create choice."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Return choice text."""
        return self.choice_text
