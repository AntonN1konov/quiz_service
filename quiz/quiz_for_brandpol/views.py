from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from .models import Test, Question, Attempt
from .services import start_attempt, save_answer, finish_attempt
from django.views.generic import ListView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required



@login_required
def start_test(request, test_id):
    test = get_object_or_404(Test, id=test_id, is_active=True)
    return render(request, "quiz_for_brandpol/question.html", {"test": test})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")  # после регистрации сразу на главную
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class AttemptHistoryView(ListView):
    model = Attempt
    template_name = "quiz_for_brandpol/attempts_history.html"
    context_object_name = "attempts"
    paginate_by = 20  # опционально

    def get_queryset(self):
        return (Attempt.objects
                .filter(user=self.request.user)
                .select_related("test")
                .order_by("-started_at"))


@method_decorator(login_required, name="dispatch")
class HomeView(ListView):
    model = Test
    queryset = Test.objects.filter(is_active=True).order_by("id")
    template_name = "quiz_for_brandpol/home.html"
    context_object_name = "tests"


@method_decorator(login_required, name="dispatch")
class StartTestView(View):
    def post(self, request, test_id):
        test = get_object_or_404(Test, id=test_id, is_active=True)
        attempt = start_attempt(request.user, test)
        first_q = test.questions.filter(is_active=True).order_by("order","id").first()
        return redirect("qfb_question", attempt_id=attempt.id, question_id=first_q.id)

    # чтобы было удобно тестировать — разрешим старт и GET-ом
    def get(self, request, test_id):
        return self.post(request, test_id)

@method_decorator(login_required, name="dispatch")
class QuestionView(View):
    template_name = "quiz_for_brandpol/question.html"

    def get(self, request, attempt_id, question_id):
        attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
        question = get_object_or_404(Question, id=question_id, test=attempt.test, is_active=True)

        ids = list(
            attempt.test.questions
            .filter(is_active=True)
            .order_by("order", "id")
            .values_list("id", flat=True)
        )
        i = ids.index(question.id)            # 0-based
        index = i + 1                         # 1-based
        total = len(ids)
        percent = int(index / total * 100) if total else 0
        prev_id = ids[i - 1] if i > 0 else None
        next_id = ids[i + 1] if i < total - 1 else None

        ctx = {
            "attempt": attempt,
            "question": question,
            "prev_id": prev_id,
            "next_id": next_id,
            "index": index,
            "total": total,
            "percent": percent,
        }
        return render(request, self.template_name, ctx)

    def post(self, request, attempt_id, question_id):
        attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
        question = get_object_or_404(Question, id=question_id, test=attempt.test, is_active=True)

        selected = [int(x) for x in request.POST.getlist("answers")]
        save_answer(attempt, question, selected)

        ids = list(
            attempt.test.questions
            .filter(is_active=True)
            .order_by("order", "id")
            .values_list("id", flat=True)
        )
        i = ids.index(question.id)
        is_last = (i == len(ids) - 1)
        next_id = None if is_last else ids[i + 1]

        if "finish" in request.POST or is_last:
            finish_attempt(attempt)
            return redirect("qfb_result", attempt_id=attempt.id)

        return redirect("qfb_question", attempt_id=attempt.id, question_id=next_id)


@method_decorator(login_required, name="dispatch")
class ResultView(View):
    template_name = "quiz_for_brandpol/result.html"
    def get(self, request, attempt_id):
        attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
        return render(request, self.template_name, {"attempt": attempt})
