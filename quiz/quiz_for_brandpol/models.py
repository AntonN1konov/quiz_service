from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class Question(models.Model):
    test = models.ForeignKey(Test, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    def __str__(self): return self.text[:60]

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    def __str__(self): return self.text[:60]

class Attempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attempts")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="attempts")
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    correct_count = models.PositiveIntegerField(default=0)
    wrong_count = models.PositiveIntegerField(default=0)
    percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    def __str__(self): return f"{self.user} · {self.test}"

class UserAnswer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="user_answers")
    selected = models.ManyToManyField(Answer, blank=True, related_name="selected_in")
    class Meta:
        unique_together = [("attempt","question")]