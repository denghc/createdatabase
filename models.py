#-*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Department(models.Model):
    department_mame = models.CharField(max_length=50)
    department_worknum = models.IntegerField()

class WorkerInfo(models.Model):
    # In news feeds, like, reply need to be loaded dynamically,
    # thus we have to store the original object
    user = models.ForeignKey(User, unique=True)
    name = models.CharField(max_length=50)
    department = models.ForeignKey(Department)
    accept =  models.IntegerField() #-1 0 1 2
    phone = models.CharField(max_length=50)
    photo_name = models.CharField(u"图片路径",max_length=255)
    photo_thumb = models.CharField(u"图片缩略图",max_length=255)
    if_manager_login =  models.IntegerField()

    def __unicode__(self):
        return self.name


class WorkerChoose(models.Model):
    worker = models.ForeignKey(User, unique=True)
    max_worknum = models.IntegerField()
    min_worknum = models.IntegerField()
    Worker_WorkLikeNum = models.IntegerField()

class Absenteeism(models.Model):
    worker = models.ForeignKey(User ,related_name='+')
    reason = models.TextField()
    day = models.IntegerField()
    workOrder = models.IntegerField()
    administrator = models.ForeignKey(User ,related_name='+')
    time = models.DateTimeField()
    department = models.ForeignKey(Department ,related_name='+')

class Exchange(models.Model):
    initiative_worker =  models.ForeignKey(User ,related_name='+')
    passivite_worker = models.ForeignKey(User ,related_name='+')
    iday =  models.IntegerField()
    pday =  models.IntegerField()
    iorder =  models.IntegerField()
    porder =  models.IntegerField()
    ireason = models.TextField()
    preason = models.TextField()
    state=  models.IntegerField()
    itime = models.DateTimeField()
    ptime = models.DateTimeField()
    padministrator = models.ForeignKey(User ,related_name='+')
    iadministrator = models.ForeignKey(User ,related_name='+')
    department = models.ForeignKey(Department ,related_name='+')

class Work(models.Model):
    worker = models.ForeignKey(User  ,related_name='+' )
    time = models.DateTimeField()
    reason = models.TextField()
    day = models.IntegerField()
    workorder = models.IntegerField()
    administrator = models.ForeignKey(User ,related_name='+')
    department = models.ForeignKey(Department ,related_name='+')

class Late(models.Model):
    worker = models.ForeignKey(User  ,related_name='+' )
    time = models.DateTimeField()
    reason = models.TextField()
    day = models.IntegerField()
    workorder = models.IntegerField()
    administrator = models.ForeignKey(User ,related_name='+')
    department = models.ForeignKey(Department ,related_name='+')

class Leave(models.Model):
    worker = models.ForeignKey(User ,related_name='+')
    reason = models.TextField()
    day = models.IntegerField()
    workorder = models.IntegerField()
    time = models.DateTimeField()
    replyreason = models.TextField()
    administrator = models.ForeignKey(User ,related_name='+')
    state = models.IntegerField()
    department = models.ForeignKey(Department ,related_name='+')

class Early(models.Model):
    worker = models.ForeignKey(User ,related_name='+')
    reason = models.TextField()
    day = models.IntegerField()
    workorder = models.IntegerField()
    time = models.DateTimeField()
    administrator = models.ForeignKey(User ,related_name='+')
    department = models.ForeignKey(Department ,related_name='+')
    hournum = models.FloatField()

class Overtime(models.Model):
    worker = models.ForeignKey(User ,related_name='+')
    reason = models.TextField()
    day = models.IntegerField()
    workorder = models.IntegerField()
    time = models.DateTimeField()
    administrator = models.ForeignKey(User ,related_name='+')
    department = models.ForeignKey(Department ,related_name='+')
    hournum = models.FloatField()

class Message(models.Model):
    worker = models.ForeignKey(User ,related_name='+')
    createtime = models.DateTimeField()
    content = models.TextField()
    ifSubordinate = models.IntegerField()
    superior_id = models.IntegerField()
    ifImportant = models.IntegerField()
    department = models.ForeignKey(Department)

class Schedule(models.Model):
    department =  models.ForeignKey(Department ,related_name='+')
    worker = models.TextField()
    day = models.IntegerField()
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    workorder = models.IntegerField()
    attendance = models.TextField()
    administrator = models.ForeignKey(User ,related_name='+')
    signindate = models.DateField()

class ScheduleChoose(models.Model):
    #department =  models.ForeignKey(Department ,related_name='+')
    schedule =  models.ForeignKey(Schedule, unique=True  ,related_name='+')
    maxworkernum = models.IntegerField()
    minworkernum= models.IntegerField()
    chooseworker =  models.TextField()
    chooseworkernum =  models.IntegerField()
    resultworker  =  models.TextField(null=True)
    resultworkernum =  models.IntegerField()

class Photo(models.Model):
    photo_name=models.CharField(u"图片路径",max_length=255)
    photo_thumb=models.CharField(u"图片缩略图",max_length=255)

class CurrentMessage(models.Model):
    worker = models.ForeignKey(User ,related_name='+')
    currentNum =  models.IntegerField()
    currentMinID =  models.IntegerField()
    ifaddold = models.IntegerField()