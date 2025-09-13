from django.db import transaction
from .models import Attempt, Question, Answer, UserAnswer

def _evaluate(attempt: Attempt):
    qs = attempt.test.questions.filter(is_active=True)
    total = qs.count(); correct = 0
    for q in qs:
        ua = UserAnswer.objects.filter(attempt=attempt, question=q).first()
        selected = set(ua.selected.values_list("id", flat=True)) if ua else set()
        correct_ids = set(q.answers.filter(is_correct=True).values_list("id", flat=True))
        if selected and selected == correct_ids:
            correct += 1
    attempt.correct_count = correct
    attempt.wrong_count = max(total - correct, 0)
    attempt.percent = round((correct/total*100) if total else 0, 2)

@transaction.atomic
def start_attempt(user, test):
    return Attempt.objects.create(user=user, test=test)

@transaction.atomic
def save_answer(attempt: Attempt, question: Question, answer_ids):
    ua, _ = UserAnswer.objects.get_or_create(attempt=attempt, question=question)
    if answer_ids:
        answers = Answer.objects.filter(question=question, id__in=answer_ids)
        ua.selected.set(answers)
    else:
        ua.selected.clear()
    ua.save()
    return ua

@transaction.atomic
def finish_attempt(attempt: Attempt):
    from django.utils import timezone
    _evaluate(attempt)
    attempt.completed_at = timezone.now()
    attempt.save(update_fields=["correct_count","wrong_count","percent","completed_at"])
