# chat/models.py
from django.db import models


class FAQ(models.Model):
    question_keyword = models.CharField(max_length=255)  # e.g., "運費"
    answer = models.TextField()  # 回答內容

    def __str__(self):
        return self.question_keyword
