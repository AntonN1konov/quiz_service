from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Test, Question, Answer, Attempt, UserAnswer

class AnswerInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors): return
        total = correct = 0
        for form in self.forms:
            if form.cleaned_data.get("DELETE"): continue
            if not form.cleaned_data: continue
            total += 1
            if form.cleaned_data.get("is_correct"): correct += 1
        if total > 0 and correct == 0:
            raise ValidationError("Хотя бы один правильный ответ обязателен.")
        if total > 0 and correct == total:
            raise ValidationError("Не все варианты могут быть правильными.")

class AnswerInline(admin.TabularInline):
    model = Answer
    formset = AnswerInlineFormSet
    fields = ("text","is_correct","order")
    extra = 2

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("id","title","is_active","created_at")
    list_filter = ("is_active",)
    search_fields = ("title",)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id","test","text","is_active","order")
    list_filter = ("is_active","test")
    inlines = [AnswerInline]

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id","user","test","started_at","completed_at","correct_count","wrong_count","percent")

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("id","attempt","question")
    filter_horizontal = ("selected",)