from django.contrib import admin
from video_schedule.models import Worker

class WorkerAdmin(admin.ModelAdmin):

    list_display = ('ip', 'status', 'info')

admin.site.register(Worker, WorkerAdmin)
