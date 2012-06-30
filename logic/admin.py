__author__ = 'denghc'
from django.contrib import admin
from RegisterSystem.logic.models import *

admin.site.register(WorkerInfo)
admin.site.register(WorkerChoose)
admin.site.register(Absenteeism)
admin.site.register(Department)
admin.site.register(Exchange)
admin.site.register(Late)
admin.site.register(Message)
admin.site.register(Schedule)
admin.site.register(ScheduleChoose)
admin.site.register(Leave)