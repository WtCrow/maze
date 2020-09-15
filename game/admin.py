from django.contrib import admin
from .models import ScoreRecord


class ScoreRecordAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', 'score')


admin.site.register(ScoreRecord, ScoreRecordAdmin)
