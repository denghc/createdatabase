#-*- coding:utf-8 –*-

from django.contrib.auth import authenticate, login as auth_login
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from datetime import datetime
from calendar import calendar
from django.core.files import temp
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import Template, Context
import os,uuid,ImageFile,Image
from RegisterSystem.logic.forms import *
from logic.models import *
from logic.dbUpdate import *
from logic.getlist import *
import xlrd
from pyExcelerator import *
from django.core.mail import send_mail
import random,string

def getRandomStr(n):
    a = list(string.ascii_letters)
    random.shuffle(a)
    return ''.join(a[:n])

@dajaxice_register
def login(request, form):
    dajax = Dajax()
    form = LoginForm(form)
    if form.is_valid():
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            workerinfo  = WorkerInfo.objects.get(user = user.id)
            if workerinfo.accept == -1:
                dajax.assign('#msg', 'innerHTML', u'管理员尚未确认')
            else:
                auth_login(request, user)
                workerinfo.if_manager_login = 0
                workerinfo.save()
                url = form.data.get('next', '/')
                dajax.redirect(url)
        else:
            dajax.assign('#msg', 'innerHTML', u'用户名或密码错误')
    else:
        dajax.assign('#msg', 'innerHTML', u'请检查输入格式')
    return dajax.json()

@dajaxice_register
def loginmanager(request, form):
    dajax = Dajax()
    form = ManagerLoginForm(form)
    if form.is_valid():
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        ifmanager = form.data['advanced_choice']
        if user is not None:
            workerinfo  = WorkerInfo.objects.get(user = user.id)
            if workerinfo.accept == -1:
                dajax.assign('#msg', 'innerHTML', u'管理员尚未确认')
            else:
                auth_login(request, user)
                if workerinfo.accept == 1:
                    workerinfo.if_manager_login = 1
                else:
                    workerinfo.if_manager_login = 0
                workerinfo.save()
                url = form.data.get('next', '/')
                dajax.redirect(url)
        else:
            dajax.assign('#msg', 'innerHTML', u'用户名或密码错误')
    else:
        dajax.assign('#msg', 'innerHTML', u'请检查输入格式')
    return dajax.json()

@dajaxice_register
def register(request, form):
    dajax = Dajax()
    form = RegisterForm(form)
    if form.is_valid():
        if form.cleaned_data['password'] == form.cleaned_data['surepassword']:
            userid = User.objects.filter(username=form.cleaned_data['cardid'])
            if len(userid) == 0:
                if form.cleaned_data['work'] == 0:
                    dajax.assign('#msg', 'innerHTML', u'请选择部门')
                else:
                    #dajax.script("alert('4');")
                    user = User.objects.create_user(username = form.cleaned_data['cardid'],
                        email = form.cleaned_data['email'] , password = form.cleaned_data['password'])
                    user.is_staff = True
                    user.save()
                    depa = Department.objects.get(id = form.cleaned_data['work'])
                    userid = User.objects.get(username=form.cleaned_data['cardid'])
                    worker =  WorkerInfo( user = userid ,
                        name = form.cleaned_data['name'] , department = depa,
                        accept = -1, photo_name = "0", photo_thumb = "0",phone = form.cleaned_data['phonenumber'],if_manager_login = 0,
                    )
                    worker.save()
                    currentMessage = CurrentMessage(worker = userid,currentNum = 0,currentMinID = 0,ifaddold = 0)
                    currentMessage.save()
                    dajax.script("$('#open_window').hide();")
                    dajax.script("$('#open_window2').show();")

            else:
                #dajax.script("alert('3');")
                dajax.assign('#msg', 'innerHTML', u'该学号已被注册')
        else:
            #dajax.script("alert('2');")
            dajax.assign('#msg', 'innerHTML', u'两次密码输入不一致')
    else:
        #dajax.script("alert('1');")
        dajax.assign('#msg', 'innerHTML', u'请检查输入格式')
    return dajax.json()

@dajaxice_register
def reset(request):
    dajax = Dajax()
    dajax.redirect("/register/",delay=0)
    return dajax.json()

@dajaxice_register
def findPassword(request,form):
    dajax = Dajax()
    form = FindPasswordForm(form)
    if form.is_valid():
        data = form.cleaned_data
        userids = User.objects.filter(username = data['id'])
        if len(userids) == 1:
            user = User.objects.get(username = data['id'])      #get(username = data['id'])
            if user.email == data['email']: #user['email'] == data['email']:
                newpassword = getRandomStr(8)
                content = u'您在勤工大队网站的密码已经修改为' + newpassword + u'，请尽快登录并修改密码'# + user.password;
                try:
                    send_mail(u'密码找回',content,'',[data['email']])
                    user.set_password(newpassword)
                    user.save()
                    dajax.script("$('#open_window3').hide()")
                    dajax.script("$('#open_window4').show()")
                except Exception:
                    dajax.script("alert('邮件提醒未发送成功')")
            else:
                dajax.script("alert('学号和邮箱不匹配！')")
        else:
            if len(userids) == 0:
                dajax.script("alert('无效的学号！')")
            else:
                dajax.script("alert('系统出现问题，请与管理员联系')")
    else:
        dajax.script("alert('对不起，您的输入格式有误！')")
    return dajax.json()

@dajaxice_register
def retowish(request):
    dajax = Dajax()
    dajax.redirect("/officer_wish/",delay=0)
    return dajax.json()

@dajaxice_register
def retoduty(request):
    dajax = Dajax()
    dajax.redirect("/officer_arrangement/",delay=0)
    return dajax.json()

@dajaxice_register
def recreate(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    schedulelist = Schedule.objects.filter(department = workerinfo.department)
    iffirst = 0
    for item in workerlist:
        workerchoose = WorkerChoose.objects.filter(worker = item.user)
        if(len(workerchoose) > 0):
            workerchoose = WorkerChoose.objects.get(worker = item.user)
            resultcount = 0
            workerstr = u''+ ","+str(workerchoose.worker.id)+ "."
            for item in schedulelist:
                schedulechoose = ScheduleChoose.objects.get(schedule = item)
                if iffirst == 0:
                    schedulechoose.resultworker = u' '
                    schedulechoose.resultworkernum = 0
                    schedulechoose.save()
                num = schedulechoose.chooseworker.find(workerstr)
                if num > 0:
                    if (schedulechoose.resultworkernum < workerchoose.max_worknum) & (resultcount < workerchoose.max_worknum):
                        if schedulechoose.resultworker.find(workerstr) <= 0:
                            schedulechoose.resultworker += workerstr
                            schedulechoose.resultworkernum += 1
                            schedulechoose.save()
                            resultcount += 1
            iffirst = 1
    dajax.redirect("/officer_wisharrange/",delay=0)
    return dajax.json()

@dajaxice_register
def finishwish(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    department_id  = workerinfo.department.id
    order = Department.objects.get(id = department_id).department_worknum
    for i in range(order):
        dutylist = list(Schedule.objects.filter(department = department_id , workorder = i + 1).order_by('day')[:7])
        for item in dutylist:
            chooseworker = ScheduleChoose.objects.get(schedule = item).resultworker
            if chooseworker == None:
                chooseworker = u' '
            item.worker = chooseworker
            item.attendance = chooseworker
            item.save()
    dajax.redirect("/officer_arrangement/",delay=0)
    return dajax.json()

@dajaxice_register
def retowisharrange(request):
    dajax = Dajax()
    dajax.redirect("/officer_wisharrange/",delay=0)
    return dajax.json()

@dajaxice_register
def reset_numwish(request, form):
    dajax = Dajax()
    form = NumWishForm(form)
    if form.is_valid():
        workerchoose = WorkerChoose.objects.get(worker = request.user)
        workerchoose.max_worknum = form.cleaned_data['maxnum']
        workerchoose.min_worknum = form.cleaned_data['minnum']
        workerchoose.save()
        dajax.assign('#msg', 'innerHTML', u'修改成功')
    else:
        dajax.assign('#msg', 'innerHTML', u'请检查输入格式')
    return dajax.json()

@dajaxice_register
def updateDutywish(request , form):
    dajax = Dajax()
    form = DutyWish(form)
    if form.is_valid():
        content = form.cleaned_data['b']
        id = u''
        workerstr = u''+ ","+ str(request.user.id) + "."
        workerchoose = WorkerChoose.objects.get(worker = request.user)
        workerchoose.Worker_WorkLikeNum = 0
        workerinfo = WorkerInfo.objects.get(user = request.user.id)
        department_id  = workerinfo.department.id
        schlist = list(Schedule.objects.filter(department = department_id))
        for item in schlist:
            schechoose = ScheduleChoose.objects.get(schedule = item.id)
            num = schechoose.chooseworker.find(workerstr)
            if(num > 0):
                schechoose.chooseworker = schechoose.chooseworker.replace(workerstr, '')
                schechoose.chooseworkernum -=1
                schechoose.save()
        for ch in content:
            if ch == ',':
                schedulechoose = ScheduleChoose.objects.get(schedule = int(id))
                num = schedulechoose.chooseworker.find(workerstr)
                if(num <= 0):
                    schedulechoose.chooseworker += workerstr
                    schedulechoose.chooseworkernum += 1
                    schedulechoose.save()
                id = u''
                workerchoose.Worker_WorkLikeNum += 1
            else:
                id += ch
        workerchoose.save()
    dajax.redirect("/dutywish/",delay=0)
    return dajax.json()

@dajaxice_register
def getdutys(request):
    dajax = Dajax()
    id  = WorkerInfo.objects.get(user = request.user.id).department.id
    order = Schedule.objects.get(department = id).workorder
    for i in range(order):
        dutylist = list(Schedule.objects.filter(department = id , workorder = i).order_by('workorder')[:7])
        content += get_dutylist(dutylist)
    dajax.append('#dutylist', 'innerHTML', content)
    dajax.script('each();')
    return dajax.json()

@dajaxice_register
def showleave(request):
    dajax = Dajax()
    id_d  = WorkerInfo.objects.get(user = request.user.id).department.id
    order = Department.objects.get(id = id_d).department_worknum
    content = setorder(order)
    dajax.assign('#leaveorder', 'innerHTML', content)
    dajax.script("$('#window_leave').show();")
    dajax.script("$('#window_huanban').hide();")
    return dajax.json()

@dajaxice_register
def showchoosephoto(request):
    dajax = Dajax()
    dajax.script("$('#window_photo').show();")
    return dajax.json()

@dajaxice_register
def reset_dutywish(request):
    dajax = Dajax()
    dajax.script("$('#reset').hide();")
    dajax.script("$('#update').show();")
    return dajax.json()

@dajaxice_register
def showexchange(request):
    dajax = Dajax()
    id_d  = WorkerInfo.objects.get(user = request.user.id).department.id
    order = Department.objects.get(id = id_d).department_worknum
    content = setexchangeorder(order)
    dajax.assign('#exchangeorder', 'innerHTML', content)
    dajax.script("$('#window_huanban').show();")
    dajax.script("$('#window_leave').hide();")
    return dajax.json()

@dajaxice_register
def openreply(request):
    dajax = Dajax()
    unexchange = list(Exchange.objects.filter(passivite_worker = request.user, state = 0))
    if(len(unexchange) > 0):
        latest = unexchange[0]
        iname =  WorkerInfo.objects.get(user = latest.initiative_worker).name
        id = u'<input type="text" name="ex_id" value="%s" style="display:none">'%(latest.id)
        io = u'班次%s' %( latest.iorder)
        po = u'班次%s' %( latest.porder)
        dajax.assign('#i_date', 'innerHTML', latest.itime.date())
        dajax.assign('#i_order', 'innerHTML',io)
        dajax.assign('#p_date', 'innerHTML', latest.ptime.date())
        dajax.assign('#p_order', 'innerHTML',  po)
        dajax.assign('#request_name', 'innerHTML', iname)
        dajax.assign('#exchange_id', 'innerHTML', id)
    else:
        content = u'您无请求！'
        dajax.assign('#request_name', 'innerHTML', content)
    dajax.script("$('#window_leave').show();")
    return dajax.json()

@dajaxice_register
def openearly(request):
    dajax = Dajax()
    early = Early.objects.filter(worker = request.user)
    early_list = list(Early.objects.filter(worker = request.user).order_by('time')[:len(early)])
    content = get_earlylist( request, early_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', content)
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def openovertime(request):
    dajax = Dajax()
    overtime = Overtime.objects.filter(worker = request.user)
    overtime_list = list(Overtime.objects.filter(worker = request.user).order_by('time')[:len(overtime)])
    content = get_overtimelist( request, overtime_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML',"" )
    dajax.assign('#overtimelist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def openleave(request):
    dajax = Dajax()
    leave = Leave.objects.filter(worker = request.user, state = 1)
    leave_list = list(Leave.objects.filter(worker = request.user, state = 1).order_by('time')[:len(leave)])
    content = get_leavelist( request, leave_list)
    dajax.assign('#leavelist', 'innerHTML', content)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML',"" )
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def openabsenteesim(request):
    dajax = Dajax()
    absenteeism = Absenteeism.objects.filter(worker = request.user)
    absenteeism_list = list(Absenteeism.objects.filter(worker = request.user).order_by('time')[:len(absenteeism)])
    content = get_absenteeismlist( request, absenteeism_list)
    dajax.assign('#absenlist', 'innerHTML', content)
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML',"" )
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def openlate(request):
    dajax = Dajax()
    late = Late.objects.filter(worker = request.user)
    late_list = list(Late.objects.filter(worker = request.user).order_by('time')[:len(late)])
    content = get_latelist( request, late_list)
    dajax.assign('#latelist', 'innerHTML', content)
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML',"" )
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def openwork(request):
    dajax = Dajax()
    work = Work.objects.filter(worker = request.user)
    work_list = list(Work.objects.filter(worker = request.user).order_by('time')[:len(work)])
    content = get_worklist( request, work_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', content)
    dajax.assign('#earlylist', 'innerHTML',"" )
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def openexchange(request):
    dajax = Dajax()
    iexchange = Exchange.objects.filter(initiative_worker = request.user, state = 1)
    pexchange = Exchange.objects.filter(passivite_worker = request.user, state = 1)
    iexchange_list = list(Exchange.objects.filter(initiative_worker = request.user, state = 1).order_by('itime')[:len(iexchange)])
    pexchange_list = list(Exchange.objects.filter(passivite_worker  = request.user, state = 1).order_by('ptime')[:len(pexchange)])
    content = get_exchangelist( request, iexchange_list, 0) + get_exchangelist( request, pexchange_list, len(iexchange))
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', content)
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML',"" )
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()


@dajaxice_register
def open_specificleave(request, form):
    dajax = Dajax()
    wor_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            wor_id = id
            id = u''
        else:
            id += ch
    user_worker = User.objects.get(id =  int(wor_id))
    manager = User.objects.get(id = int(id))
    leave = Leave.objects.filter(worker = user_worker, state = 1 ,administrator = manager)
    leave_list = list(Leave.objects.filter(worker = user_worker, state = 1,administrator = manager ).order_by('time')[:len(leave)])
    content = get_manager_leavelist( request, leave_list)
    dajax.assign('#leavelist', 'innerHTML', content)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_specificlate(request, form):
    dajax = Dajax()
    wor_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            wor_id = id
            id = u''
        else:
            id += ch
    user_worker = User.objects.get(id =  int(wor_id))
    manager = User.objects.get(id = int(id))
    late = Late.objects.filter(worker = user_worker, administrator = manager)
    late_list = list(Late.objects.filter(worker = user_worker, administrator = manager).order_by('time')[:len(late)])
    content = get_manager_latelist( request, late_list)
    dajax.assign('#latelist', 'innerHTML', content)
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_specificwork(request, form):
    dajax = Dajax()
    wor_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            wor_id = id
            id = u''
        else:
            id += ch
    user_worker = User.objects.get(id =  int(wor_id))
    manager = User.objects.get(id = int(id))
    work = Work.objects.filter(worker = user_worker, administrator = manager)
    work_list = list(Work.objects.filter(worker = user_worker, administrator = manager).order_by('time')[:len(work)])
    content = get_manager_worklist( request, work_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def open_specificabsenteeism(request, form):
    dajax = Dajax()
    wor_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            wor_id = id
            id = u''
        else:
            id += ch
    user_worker = User.objects.get(id =  int(wor_id))
    manager = User.objects.get(id = int(id))
    absenteeism = Absenteeism.objects.filter(worker = user_worker, administrator = manager)
    absenteeism_list = list(Absenteeism.objects.filter(worker = user_worker, administrator = manager).order_by('time')[:len(absenteeism)])
    content = get_manager_absenteeismlist( request, absenteeism_list)
    dajax.assign('#absenlist', 'innerHTML', content)
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_specificexchange(request, form):
    dajax = Dajax()
    wor_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            wor_id = id
            id = u''
        else:
            id += ch
    user_worker = User.objects.get(id =  int(wor_id))
    manager = User.objects.get(id = int(id))
    i_iexchange = Exchange.objects.filter(initiative_worker = user_worker, iadministrator = manager, state = 1)
    p_iexchange = Exchange.objects.filter(passivite_worker = user_worker, iadministrator = manager, state = 1)
    i_pexchange = Exchange.objects.filter(initiative_worker = user_worker,padministrator = manager, state = 1)
    p_pexchange = Exchange.objects.filter(passivite_worker = user_worker,padministrator = manager, state = 1)
    i_iexchange_list = list(Exchange.objects.filter(initiative_worker = user_worker, iadministrator = manager, state = 1).order_by('itime')[:len(i_iexchange)])
    p_iexchange_list = list(Exchange.objects.filter(passivite_worker = user_worker, iadministrator = manager, state = 1).order_by('ptime')[:len(p_iexchange)])
    i_pexchange_list = list(Exchange.objects.filter(initiative_worker = user_worker,padministrator = manager, state = 1).order_by('ptime')[:len(i_pexchange)])
    p_pexchange_list = list(Exchange.objects.filter(passivite_worker = user_worker,padministrator = manager, state = 1).order_by('ptime')[:len(p_pexchange)])
    content = get_exchangelist( request, i_iexchange_list, 0) + get_exchangelist( request, p_iexchange_list, len(i_iexchange))\
              + get_exchangelist( request, i_pexchange_list, len(i_iexchange) + len(p_iexchange)) + get_exchangelist( request, p_pexchange_list, len(i_iexchange) + len(p_iexchange) + len(i_pexchange))
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', content)
    dajax.assign('#worklist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_specificearly(request, form):
    dajax = Dajax()
    wor_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            wor_id = id
            id = u''
        else:
            id += ch
    user_worker = User.objects.get(id =  int(wor_id))
    manager = User.objects.get(id = int(id))
    early = Early.objects.filter(worker = user_worker, administrator = manager)
    early_list = list(Early.objects.filter(worker = user_worker, administrator = manager).order_by('time')[:len(early)])
    content = get_manager_earlylist( request, early_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def open_specificovertime(request, form):
    dajax = Dajax()
    wor_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            wor_id = id
            id = u''
        else:
            id += ch
    user_worker = User.objects.get(id =  int(wor_id))
    manager = User.objects.get(id = int(id))
    overtime = Overtime.objects.filter(worker = user_worker, administrator = manager)
    overtime_list = list(Overtime.objects.filter(worker = user_worker, administrator = manager).order_by('time')[:len(overtime)])
    content = get_manager_overtimelist( request, overtime_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', content)
    dajax.assign('#earlylist', 'innerHTML', "")
    return dajax.json()

def getdate(day):
    day_time = datetime.date.today()
    if(day_time.weekday() < day):
        date_time = day_time + datetime.timedelta( day - day_time.weekday() - 1)
    else:
        date_time = day_time + datetime.timedelta(6 + day_time.weekday() - day)
    return date_time

@dajaxice_register
def setleave(request , form):
    dajax = Dajax()
    form = LeaveForm(form)
    if form.is_valid():
        dep  = WorkerInfo.objects.get(user = request.user).department
        schedule =  Schedule.objects.get(department = dep ,day = form.cleaned_data['leaveday'], workorder = form.cleaned_data['leaveorder'] )
        worker =schedule.worker
        workerstr = u''+ ","+ str(request.user.id) + "."
        if(worker.find(workerstr) > 0):
            temp = Leave.objects.filter(worker = request.user ,day = form.cleaned_data['leaveday'], workorder = form.cleaned_data['leaveorder'] )
            refuseleave =  Leave.objects.filter(worker = request.user ,day = form.cleaned_data['leaveday'], workorder = form.cleaned_data['leaveorder'],state = -1 )
            workerinfo = WorkerInfo.objects.get(user = request.user)
            if( len(temp) == 0 ):
                date_time = getdate(form.cleaned_data['leaveday'])
                admin = schedule.administrator
                content = request.user.username + u' ' + workerinfo.name + u'向您请假，请假日期%s班次%d ，请尽快登录网页回复。' %(date_time,form.cleaned_data['leaveorder'])
                try:
                    send_mail(u'请假请求',content,'',[admin.email])
                except Exception:
                    dajax.script("alert('提醒邮件未发送成功')")
                leave =Leave(worker = request.user, reason = form.cleaned_data['reason'], day = form.cleaned_data['leaveday'],
                workorder = form.cleaned_data['leaveorder'], time = date_time, state = 0,replyreason = "尚未回复", administrator = schedule.administrator, department = dep )
                leave.save()
                dajax.script("$('#open_window2').show();")
                dajax.script("$('#window_leave').hide();")
            elif (len(refuseleave) > 0):
                date_time = getdate(form.cleaned_data['leaveday'])
                admin = schedule.administrator
                content = request.user.username + u' ' +  workerinfo.name + u'向您请假，请假日期%s班次%d ，请尽快登录网页回复。' %(date_time,form.cleaned_data['leaveorder'])
                try:
                    send_mail(u'请假请求',content,'',[admin.email])
                except Exception:
                    dajax.script("alert('提醒邮件未发送成功')")
                leave =Leave(worker = request.user, reason = form.cleaned_data['reason'], day = form.cleaned_data['leaveday'],
                    workorder = form.cleaned_data['leaveorder'], time = date_time, state = 0,replyreason = "尚未回复", administrator = schedule.administrator, department = dep )
                leave.save()
                dajax.script("$('#open_window2').show();")
                dajax.script("$('#window_leave').hide();")
            else:
                dajax.assign('#leave_msg', 'innerHTML', u'您该班次已请过假！')
        else:
            dajax.assign('#leave_msg', 'innerHTML', u'您该班次无班！')
    else:
        dajax.assign('#leave_msg', 'innerHTML', u'请检查输入格式')
    return dajax.json()

@dajaxice_register
def setexchange(request , form):
    dajax = Dajax()
    form = ExchangeForm(form)
    if form.is_valid():
        dep  = WorkerInfo.objects.get(user = request.user.id).department
        try:
            myschedule =  Schedule.objects.get(department = dep ,day = form.cleaned_data['myday'], workorder = form.cleaned_data['myorder'] )
        except :
            dajax.script("alert('无效的班次！')")
            return dajax.json()
        else:
            worker = myschedule.worker
            print  u'%s;%s;' %(form.cleaned_data['myday'],form.cleaned_data['myorder']) + worker
            workerstr_my = u''+ ","+ str(request.user.id) + "."
            if(worker.find(workerstr_my) > 0):
                goalid = User.objects.get(username=form.cleaned_data['goalname']).id
                workerstr_goal = u''+ ","+ str(goalid) + "."
                goalschedule =  Schedule.objects.get(department = dep ,day = form.cleaned_data['goalday'], workorder = form.cleaned_data['goalorder'] )
                goalworker = goalschedule.worker
                if(worker.find(workerstr_goal)) > 0 :
                    dajax.assign('#exchange_msg', 'innerHTML', u'对方在您班次已有班！')
                    return dajax.json()
                if(goalworker.find(workerstr_my) > 0):
                    dajax.assign('#exchange_msg', 'innerHTML', u'您在对方班次已有班！')
                    return dajax.json()
                mydate = getdate(form.cleaned_data['myday'])
                goaldate =  getdate(form.cleaned_data['goalday'])
                workerinfo = WorkerInfo.objects.get(user = request.user)
                exchange = Exchange.objects.filter(initiative_worker = request.user, passivite_worker = User.objects.get(username=form.cleaned_data['goalname']),
                    iday = form.cleaned_data['myday'],pday = form.cleaned_data['goalday'], iorder = form.cleaned_data['myorder'],
                    porder = form.cleaned_data['goalorder'],  state = 0,
                    itime =mydate, ptime =  goaldate, padministrator =goalschedule.administrator,iadministrator =  myschedule.administrator, department = dep )
                if(len(exchange)>0):
                    dajax.assign('#exchange_msg', 'innerHTML', u'您提交过相同的换班请求，且对方尚未回复！')
                    return dajax.json()
                exchange = Exchange.objects.filter(initiative_worker = request.user, passivite_worker = User.objects.get(username=form.cleaned_data['goalname']),
                    iday = form.cleaned_data['myday'],pday = form.cleaned_data['goalday'], iorder = form.cleaned_data['myorder'],
                    porder = form.cleaned_data['goalorder'],state = 1,
                    itime =mydate, ptime =  goaldate, padministrator =goalschedule.administrator,iadministrator =  myschedule.administrator, department = dep )
                if(len(exchange)>0):
                    dajax.assign('#exchange_msg', 'innerHTML', u'您提交过相同的换班请求，且对方已同意！')
                    return dajax.json()
                if(goalworker.find(workerstr_goal) > 0):
                    content = request.user.username + u' ' +workerinfo.name +u'请求和您换班：\n对方班次：周%s班次%d\n希望换到：周%s班次%d\n原因：  %s' %(form.cleaned_data['myday'],
                                                                                                        form.cleaned_data['myorder'],form.cleaned_data['goalday'],form.cleaned_data['goalorder'],form.cleaned_data['reason']) + u'\n请尽快登录系统回复'
                    try:
                        send_mail(u'换班请求',content,'',[User.objects.get(username=form.cleaned_data['goalname']).email]);
                    except Exception:
                        dajax.script("alert('提醒邮件发送未成功')")
                    exchange = Exchange(initiative_worker = request.user, passivite_worker = User.objects.get(username=form.cleaned_data['goalname']),
                        iday = form.cleaned_data['myday'],pday = form.cleaned_data['goalday'], iorder = form.cleaned_data['myorder'],
                        porder = form.cleaned_data['goalorder'], ireason = form.cleaned_data['reason'], preason = "尚未回复", state = 0,
                        itime =mydate, ptime =  goaldate, padministrator =goalschedule.administrator,iadministrator =  myschedule.administrator, department = dep )
                    exchange.save()
                    dajax.script("$('#open_window3').show();")
                    dajax.script("$('#window_huanban').hide();")
                else:
                    dajax.assign('#exchange_msg', 'innerHTML', u'对方该班次无班！')
            else:
                dajax.assign('#exchange_msg', 'innerHTML', u'您该班次无班！')
    else:
        dajax.assign('#exchange_msg', 'innerHTML', u'请检查输入格式！')
    return dajax.json()

@dajaxice_register
def changeinfo(request , form):
    dajax = Dajax()
    form = InfoForm(form)
    if form.is_valid():
        if form.cleaned_data['password'] == form.cleaned_data['passwordagain']:
            WorkerInfo.objects.filter(user = request.user.id).update(name = form.cleaned_data['username'] ,
                phone = form.cleaned_data['phonenumber'])
            user = User.objects.get(username= request.user.username)
            user.set_password(form.cleaned_data['password'])
            user.save()
            User.objects.filter(id = request.user.id).update( email = form.cleaned_data['email'])
            dajax.script("$('#open_window2').show();")
        else:
            dajax.assign('#msg', 'innerHTML', u'两次密码不一致！')
    else:
        dajax.assign('#msg', 'innerHTML', u'输入格式错误！')
    return dajax.json()

@dajaxice_register
def agreeexchange (request , form):
    dajax = Dajax()
    form = ReplyExchangeForm(form)
    if form.is_valid():
        try:
            send_mail(u'换班成功',u'%s同意用周%d的班次%d和您在周%d的班次%d交换' %(exchange.passivite_worker.username,
                                                              pschedule.day,pschedule.workorder,ischedule.day,ischedule.workorder),'',[exchange.passivite_worker.email])
            send_mail(u'换班成功信息',u'在您所负责的周%d的班次%d上，%s由%s代替' %(pschedule.day,pschedule.workorder,
                                                             exchange.passivite_worker.username,exchange.initiative_worker.username),'',[pschedule.administrator.email])
            send_mail(u'换班成功信息',u'在您所负责的周%d的班次%d上，%s由%s代替' %(ischedule.day,ischedule.workorder,
                                                             exchange.initiative_worker.username,exchange.passivite_worker.username),'',[ischedule.administrator.email])
        except Exception:
            dajax.script("alert('提醒邮件发送未成功')")
        depart = WorkerInfo.objects.get(user = request.user.id).department
        exchange = Exchange.objects.get(id = form.cleaned_data['ex_id'])
        exchange.state = 1
        exchange.preason = form.cleaned_data['reply']
        exchange.save()

        ischedule  = Schedule.objects.get(day = exchange.iday, workorder = exchange.iorder, department = depart)
        att = ischedule.attendance.replace(u',' + str(exchange.initiative_worker.id) + u'.', u',' + str(exchange.passivite_worker.id) + u'.')
        ischedule.attendance = att
        ischedule.save()

        pschedule = Schedule.objects.get(day = exchange.pday, workorder = exchange.porder, department = depart)
        att = ischedule.attendance.replace(u',' + str(exchange.passivite_worker.id) + u'.', u',' + str(exchange.initiative_worker.id) + u'.')
        pschedule.attendance = att
        pschedule.save()
        dajax.redirect("/changerequest/",delay=0)
    else:
        dajax.assign('#msg', 'innerHTML', u'输入格式错误！')
    return dajax.json()

@dajaxice_register
def refuseexchange (request , form):
    dajax = Dajax()
    form = ReplyExchangeForm(form)
    if form.is_valid():
        try:
            send_mail(u'换班失败',u'学号%s不同意您的换班请求。' %(exchange.passivite_worker.username),'',[exchange.passivite_worker.email])
        except Exception:
            dajax.script("alert('提醒邮件发送未成功')")
        Exchange.objects.filter(id = form.cleaned_data['ex_id']).update(state = -1, preason = form.cleaned_data['reply'])
        exchange = Exchange.objects.get(id = form.cleaned_data['ex_id'])
        dajax.redirect("/changerequest/",delay=0)
    else:
        dajax.assign('#msg', 'innerHTML', u'输入格式错误！')
    return dajax.json()

@dajaxice_register
def deleateleave (request , form):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    leave = Leave.objects.get(id = form)
    if leave.state == 1:
        schedule = Schedule.objects.get(day = leave.day, workorder = leave.workorder, department = workerinfo.department)
        schedule.attendance += u','+ str(request.user.id) + u'.'
        schedule.save()
    leave.delete()
    dajax.redirect("/status/",delay=0)
    return dajax.json()

@dajaxice_register
def deleateexchange  (request , form):
    dajax = Dajax()
    exchange = Exchange.objects.get(id = form)
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    depart = workerinfo.department
    if exchange.state == 1:
        ischedule  = Schedule.objects.get(day = exchange.iday, workorder = exchange.iorder, department = depart)
        att = ischedule.attendance.replace( u',' + str(exchange.passivite_worker.id) + u'.', u',' + str(exchange.initiative_worker.id) + u'.')
        ischedule.attendance = att
        ischedule.save()

        pschedule = Schedule.objects.get(day = exchange.pday, workorder = exchange.porder, department = depart)
        att = ischedule.attendance.replace( u',' + str(exchange.initiative_worker.id) + u'.', u',' + str(exchange.passivite_worker.id) + u'.')
        pschedule.attendance = att
        pschedule.save()
    exchange.delete()
    dajax.redirect("/status/",delay=0)
    return dajax.json()

@dajaxice_register
def deleatelate  (request , form):
    dajax = Dajax()
    late = Late.objects.get(id = form)
    late.delete()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    if(workerinfo.accept == 2):
        late = Late.objects.filter(department = workerinfo.department)
        late_list = list(Late.objects.filter(department = workerinfo.department).order_by('time')[:len(late)])
    else:
        late = Late.objects.filter(administrator = request.user)
        late_list = list(Late.objects.filter(administrator = request.user).order_by('time')[:len(late)])
    content = get_manager_latelist( request, late_list)
    dajax.assign('#latelist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def deleatework  (request , form):
    dajax = Dajax()
    work = Work.objects.get(id = form)
    work.delete()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    if(workerinfo.accept == 2):
        work = Work.objects.filter(department = workerinfo.department)
        work_list = list(Work.objects.filter(department = workerinfo.department).order_by('time')[:len(work)])
    else:
        work = Work.objects.filter(administrator = request.user)
        work_list = list(Work.objects.filter(administrator = request.user).order_by('time')[:len(work)])
    content = get_manager_worklist( request, work_list)
    dajax.assign('#worklist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def deleateearly  (request , form):
    dajax = Dajax()
    early = Early.objects.get(id = form)
    early.delete()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    if(workerinfo.accept == 2):
        early = Early.objects.filter(department = workerinfo.department)
        early_list = list(Early.objects.filter(department = workerinfo.department).order_by('time')[:len(early)])
    else:
        early = Early.objects.filter(administrator = request.user)
        early_list = list(Early.objects.filter(administrator = request.user).order_by('time')[:len(early)])
    content = get_manager_earlylist( request, early_list)
    dajax.assign('#earlylist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def deleateovertime  (request , form):
    dajax = Dajax()
    overtime = Overtime.objects.get(id = form)
    overtime.delete()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    if(workerinfo.accept == 2):
        overtime = Overtime.objects.filter(department = workerinfo.department)
        overtime_list = list(Overtime.objects.filter(department = workerinfo.department).order_by('time')[:len(overtime)])
    else:
        overtime = Overtime.objects.filter(administrator = request.user)
        overtime_list = list(Overtime.objects.filter(administrator = request.user).order_by('time')[:len(overtime)])
    content = get_manager_overtimelist( request, overtime_list)
    dajax.assign('#overtimelist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def deleateabsenteeism  (request , form):
    dajax = Dajax()
    absenteeism = Absenteeism.objects.get(id = form)
    absenteeism.delete()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    if(workerinfo.accept == 2):
        absenteeism = Absenteeism.objects.filter(department = workerinfo.department)
        absenteeism_list = list(Absenteeism.objects.filter(department = workerinfo.department).order_by('time')[:len(absenteeism)])
    else:
        absenteeism = Absenteeism.objects.filter(administrator = request.user)
        absenteeism_list = list(Absenteeism.objects.filter(administrator = request.user).order_by('time')[:len(absenteeism)])
    content = get_manager_absenteeismlist( request, absenteeism_list)
    dajax.assign('#absenlist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def deleateleaverecord  (request , form):
    dajax = Dajax()
    leave = Leave.objects.get(id = form)
    leave.delete()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    if(workerinfo.accept == 2):
        leave = Leave.objects.filter(department = workerinfo.department, state = 1)
        leave_list = list(Leave.objects.filter(department = workerinfo.department, state = 1).order_by('time')[:len(leave)])
    else:
        leave = Leave.objects.filter(administrator = request.user, state = 1)
        leave_list = list(Leave.objects.filter(administrator = request.user, state = 1).order_by('time')[:len(leave)])
    content = get_manager_leavelist( request, leave_list)
    dajax.assign('#leavelist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def transfermessage  (request , form):
    dajax = Dajax()
    content = u'<textarea name="message" id="experience_text">%s</textarea>'% (form)
    dajax.assign('#defaultMessage', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def setsumessage  (request , form):
    dajax = Dajax()
    form = ReplyMessageForm(form)
    if form.is_valid():
        dep_id  = WorkerInfo.objects.get(user = request.user.id).department
        message = Message(worker = request.user, createtime = datetime.datetime.now() , content = form.cleaned_data['content'],
            ifSubordinate = 1,superior_id = int(form.cleaned_data['id']), ifImportant = 0,department = dep_id )
        message.save()
        dajax.redirect("/communicate/",delay=0)
    return dajax.json()

@dajaxice_register
def uploadPhoto(request ):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    if workerinfo.if_manager_login == 1 and workerinfo.accept == 1:
        dajax.redirect("/manager_uploadphoto/",delay=0)
    elif workerinfo.accept == 2:
        dajax.redirect("/officer_uploadphoto/",delay=0)
    else:
        dajax.redirect("/uploadphoto/",delay=0)
    return dajax.json()

@dajaxice_register
def signin_normal(request, form):
    dajax = Dajax()
    iffirst = True
    scheduleid = u''
    userid = u''
    for ch in form:
        if ch == ',':
            iffirst = False
        elif iffirst:
            scheduleid += ch
        else:
            userid += ch
    schedule = Schedule.objects.get(id = int(scheduleid))
    attentence = schedule.attendance.replace(','+ userid +'.', '')
    schedule.attendance = attentence
    if len(attentence) <= 3:
        schedule.signindate = datetime.date.today()
        schedule.attendance = schedule.worker
    schedule.save()
    user = User.objects.get(id = int(userid))
    work = Work(worker = user, time = datetime.datetime.today() , reason = u'', day = schedule.day, workorder = schedule.workorder, administrator = schedule.administrator, department = schedule.department)
    work.save()
    dajax.redirect("/manage_sign_in/",delay=0)
    return dajax.json()

@dajaxice_register
def signin_late(request,form):
    dajax = Dajax()
    iffirst = True
    scheduleid = u''
    userid = u''
    for ch in form:
        if ch == ',':
            iffirst = False
        elif iffirst:
            scheduleid += ch
        else:
            userid += ch
    schedule = Schedule.objects.get(id = int(scheduleid))
    attentence = schedule.attendance.replace(','+ userid +'.', '')
    schedule.attendance = attentence
    if len(attentence) <= 3:
        schedule.signindate = datetime.date.today()
        schedule.attendance = schedule.worker
    schedule.save()
    user = User.objects.get(id = int(userid))
    late = Late(worker = user, time = datetime.datetime.today() , reason = u'', day = schedule.day, workorder = schedule.workorder, administrator = schedule.administrator, department = schedule.department)
    late.save()
    work = Work(worker = user, time = datetime.datetime.today() , reason = u'', day = schedule.day, workorder = schedule.workorder, administrator = schedule.administrator, department = schedule.department)
    work.save()
    dajax.redirect("/manage_sign_in/",delay=0)
    return dajax.json()

@dajaxice_register
def signin_finish(request,form):
    dajax = Dajax()
    iffirst = True
    schedule = Schedule.objects.get(id = int(form))
    result = u''
    userid = u''
    ifadd = 0
    for ch in schedule.attendance:
        if (ifadd == 1):
            if (ch == '.'):
                ifadd = 0
                attentence = schedule.attendance.replace(','+ userid +'.', '')
                schedule.attendance = attentence
                if len(attentence) <= 3:
                    schedule.signindate = datetime.date.today()
                    schedule.attendance = schedule.worker
                schedule.save()
                user = User.objects.get(id = int(userid))
                absenteeism = Absenteeism(worker = user, time = datetime.datetime.today(), reason = u'', day = schedule.day, workOrder = schedule.workorder, administrator = schedule.administrator , department = schedule.department)
                absenteeism.save()
            else:
                userid += ch
        else:
            if(ch == ','):
                ifadd = 1
                userid = u''
    dajax.redirect("/manage_sign_in/",delay=0)
    return dajax.json()

@dajaxice_register
def setMessage(request , form):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    dep_id  = workerinfo.department
    if_manage = workerinfo.if_manager_login
    if(len(form) == 1):
        normalform = NormalMessageForm(form)
        if normalform.is_valid():
            if normalform.cleaned_data['message'] == "":
                dajax.assign('#msg', 'innerHTML', u'内容不能为空！')
            else:
                message = Message(worker = request.user, createtime = datetime.datetime.now(), content = normalform.cleaned_data['message'], ifSubordinate = 0,
                    superior_id = 0, ifImportant = 0, department = dep_id)
                message.save()
                if workerinfo.accept == 2:
                    dajax.redirect("/officer_communication/",delay=0)
                elif if_manage == 0:
                    dajax.redirect("/communicate/",delay=0)
                else:
                    dajax.redirect("/manage_communicate/",delay=0)
        else:
            dajax.assign('#msg', 'innerHTML', u'输入格式错误！')
    if(len(form) == 2):
        form = ImportantMessageForm(form)
        if form.is_valid():
            if form.cleaned_data['message'] == "":
                dajax.assign('#msg', 'innerHTML', u'内容不能为空！')
            else:
                message = Message(worker = request.user, createtime = datetime.datetime.now(), content = form.cleaned_data['message'], ifSubordinate = 0,
                    superior_id = 0, ifImportant = 1, department = dep_id)
                message.save()
                if workerinfo.accept == 2:
                    dajax.redirect("/officer_communication/",delay=0)
                elif if_manage == 0:
                    dajax.redirect("/communicate/",delay=0)
                else:
                    dajax.redirect("/manage_communicate/",delay=0)
        else:
            dajax.assign('#msg', 'innerHTML', u'输入格式错误！')
    return dajax.json()

@dajaxice_register
def sureupload(request, form ):
    dajax = Dajax()
    url = form["url"]
    try:
        wk = xlrd.open_workbook(file_contents =  request.FILES["file"].read())
        workerinfo = WorkerInfo.objects.get(user = request.user.id)
        for sh in wk.sheets():
            for i in range(sh.nrows):
                if i > 0 :
                    usercardid = sh.cell_value(i,0)
                    username = sh.cell_value(i,1)
                    userid = User.objects.filter(username=usercardid)
                    if len(userid) == 0:
                        user = User.objects.create_user(username = usercardid,
                            email = "" , password = usercardid)
                        user.is_staff = True
                        user.save()
                        depa = workerinfo.department
                        userid = User.objects.get(username=usercardid)
                        worker =  WorkerInfo( user = userid ,
                            name = username , department = depa,
                            accept = 0, photo_name = "0", photo_thumb = "0",phone = "0",if_manager_login = 0,
                        )
                        worker.save()
                        currentMessage = CurrentMessage(worker = userid,currentNum = 0,currentMinID = 0)
                        currentMessage.save()
                    else:
                        dajax.assign('#msg', 'innerHTML', u'跳过部分已注册学号')
        dajax.assign('#msg', 'innerHTML', u'批量注册成功')
    except:
        dajax.assign('#msg', 'innerHTML', u'文件路径或者格式错误！')
    return dajax.json()

@dajaxice_register
def resetsedule(request , form):
    dajax = Dajax()
    content = u''
    schedule = Schedule.objects.get(id = int(form))
    dutytime =  "(" + str(schedule.starttime.hour) + ":" + str(schedule.starttime.minute)\
                + "--" + str(schedule.endtime.hour) + ":" + str(schedule.endtime.minute) + ")"
    content += u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/><div><span class="sideline">班次设置</span>'\
               u'&nbsp;&nbsp;<span class="week_tag">星期%s</span>&nbsp;&nbsp;<span class="orange">班次%s</span>&nbsp;&nbsp;<span class="orange">%s</span></div>'\
               u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/>'%(schedule.day , schedule.workorder, dutytime )
    content += u'<div id="maincontent3"><table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh2"></td></tr>'
    content += get_workersetlist( schedule.worker, schedule)
    content +=  u'</table><div width="450"><input type="submit" name="modify" value="添加队员" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "addworker_schedule(%s)" /><input type="submit" name="modify" value="完成设置" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "Dajaxice.RegisterSystem.logic.finishresetsed(Dajax.process);" /></div>'%(schedule.id)
    dajax.assign('#setseduleinfo', 'innerHTML', content)
    dajax.assign('#addworker', 'innerHTML', u'')
    return dajax.json()

@dajaxice_register
def resetchoosewish(request , form):
    dajax = Dajax()
    content = u''
    choose = ScheduleChoose.objects.get(id = int(form))
    schedule =choose.schedule
    dutytime =  "(" + str(schedule.starttime.hour) + ":" + str(schedule.starttime.minute)\
                + "--" + str(schedule.endtime.hour) + ":" + str(schedule.endtime.minute) + ")"
    content += u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/><div><span class="sideline">班次设置</span>'\
               u'&nbsp;&nbsp;<span class="week_tag">星期%s</span>&nbsp;&nbsp;<span class="orange">班次%s</span>&nbsp;&nbsp;<span class="orange">%s</span></div>'\
               u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/>'%(schedule.day , schedule.workorder, dutytime )
    content += u'<div id="maincontent3"><table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh2"></td></tr>'
    if choose.resultworker == None:
        choose.resultworker = u' '
        choose.save()
    content += get_workerresultlist( choose)
    content +=  u'</table><div width="450"><input type="submit" name="modify" value="添加队员" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "addworker_result(%s)" /><input type="submit" name="modify" value="完成设置" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "Dajaxice.RegisterSystem.logic.finishresetsed(Dajax.process);" /></div>'%(choose.id)
    dajax.assign('#setseduleinfo', 'innerHTML', content)
    dajax.assign('#addworker', 'innerHTML', u'')
    return dajax.json()

@dajaxice_register
def finishresetsed(request):
    dajax = Dajax()
    dajax.redirect("/officer_arrangement/",delay=0)
    return dajax.json()

@dajaxice_register
def finishresult(request):
    dajax = Dajax()
    dajax.redirect("/officer_wisharrange/",delay=0)
    return dajax.json()

@dajaxice_register
def addsedule(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    w_department  = workerinfo.department
    maxorder = w_department.department_worknum
    for i in range(7):
        newsedule = Schedule(department =  w_department,worker = u' ', day = i + 1, starttime = '2012-01-01 00:00:00',endtime = '2012-01-01 00:00:00',
            workorder = maxorder + 1, attendance = u' ', administrator = request.user,  signindate = '2012-01-01')
        newsedule.save()
        newsedulechoose = ScheduleChoose(schedule =  newsedule, maxworkernum = 0, minworkernum= 0,chooseworker =  u' ',chooseworkernum = 0, resultworker=u' ',resultworkernum = 0,)
        newsedulechoose.save()
    w_department.department_worknum += 1
    w_department.save()
    dajax.redirect("/officer_arrangement/",delay=0)
    return dajax.json()

@dajaxice_register
def deletesedule(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    w_department  = workerinfo.department
    maxorder = w_department.department_worknum
    for i in range(7):
        sedule =  Schedule.objects.filter(department =  w_department, workorder = maxorder,day = i + 1 )
        if(len(sedule) == 1):
            sedule = Schedule.objects.get(department =  w_department, workorder = maxorder,day = i + 1 )
            newsedulechoose = ScheduleChoose.objects.get(schedule =  sedule)
            newsedulechoose.delete()
            sedule.delete()
    w_department.department_worknum -= 1
    w_department.save()
    dajax.redirect("/officer_arrangement/",delay=0)
    return dajax.json()

@dajaxice_register
def changetime(request , form):
    dajax = Dajax()
    order = form["sedule_order"]
    start_time = u'2012-03-13 '+ str(form["starttime"]) + u':00'
    end_time = u'2012-03-13 '+ str(form["endtime"]) + u':00'
    workerinfo = WorkerInfo.objects.get(user  =  request.user)
    schedulelist = list(Schedule.objects.filter(department = workerinfo.department, workorder = int(order)))
    for item in schedulelist:
        item.starttime = start_time
        item.endtime = end_time
        item.save()
    dajax.assign('#msg'+ order, 'innerHTML', u'修改成功！')
    return dajax.json()

@dajaxice_register
def changeworkernum(request , form):
    dajax = Dajax()
    order = form["sedule_order"]
    minnum =  int(form["minnum"])
    maxnum =  int(form["maxnum"])
    workerinfo = WorkerInfo.objects.get(user  =  request.user)
    schedulelist = list(Schedule.objects.filter(department = workerinfo.department, workorder = int(order)))
    for item in schedulelist:
        choose = ScheduleChoose.objects.get(schedule = item)
        choose.maxworkernum = maxnum
        choose.minworkernum = minnum
        choose.save()
    dajax.assign('#msg'+ order, 'innerHTML', u'修改成功！')
    return dajax.json()

@dajaxice_register
def setmanager_schedule (request , form):
    dajax = Dajax()
    sch_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            sch_id = id
            id = u''
        else:
            id += ch
    schedule = Schedule.objects.get(id = int(sch_id))
    user = User.objects.get(id = int(id))
    schedule.administrator = user
    schedule.save()
    content = u''
    dutytime =  "(" + str(schedule.starttime.hour) + ":" + str(schedule.starttime.minute)\
                + "--" + str(schedule.endtime.hour) + ":" + str(schedule.endtime.minute) + ")"
    content += u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/><div><span class="sideline">班次设置</span>'\
               u'&nbsp;&nbsp;<span class="week_tag">星期%s</span>&nbsp;&nbsp;<span class="orange">班次%s</span>&nbsp;&nbsp;<span class="orange">%s</span></div>'\
               u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/>'%(schedule.day , schedule.workorder, dutytime )
    content += u'<div id="maincontent3"><table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh2"></td></tr>'
    content += get_workersetlist( schedule.worker, schedule)
    content +=  u'</table><div width="450"><input type="submit" name="modify" value="添加队员" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "addworker_schedule(%s)" /><input type="submit" name="modify" value="完成设置" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "Dajaxice.RegisterSystem.logic.finishresetsed(Dajax.process);" /></div>'%(schedule.id)
    dajax.assign('#setseduleinfo', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def deleateworker_sche  (request , form):
    dajax = Dajax()
    sch_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            sch_id = id
            id = u''
        else:
            id += ch
    schedule = Schedule.objects.get(id = int(sch_id))
    workerstr = u','+ id + u'.'
    schedule.worker = schedule.worker.replace(workerstr, '')
    schedule.attendance = schedule.attendance.replace(workerstr, '')
    schedule.save()
    content = u''
    dutytime =  "(" + str(schedule.starttime.hour) + ":" + str(schedule.starttime.minute)\
                + "--" + str(schedule.endtime.hour) + ":" + str(schedule.endtime.minute) + ")"
    content += u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/><div><span class="sideline">班次设置</span>'\
               u'&nbsp;&nbsp;<span class="week_tag">星期%s</span>&nbsp;&nbsp;<span class="orange">班次%s</span>&nbsp;&nbsp;<span class="orange">%s</span></div>'\
               u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/>'%(schedule.day , schedule.workorder, dutytime )
    content += u'<div id="maincontent3"><table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh2"></td></tr>'
    content += get_workersetlist( schedule.worker, schedule)
    content +=  u'</table><div width="450"><input type="submit" name="modify" value="添加队员" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "addworker_schedule(%s)" /></div>'%(schedule.id)
    dajax.assign('#setseduleinfo', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def deleateworker_resultsche  (request , form):
    dajax = Dajax()
    sch_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            sch_id = id
            id = u''
        else:
            id += ch
    choose = ScheduleChoose.objects.get(id = int(sch_id))
    schedule = choose.schedule
    workerstr = u','+ id + u'.'
    choose.resultworker = choose.resultworker.replace(workerstr, '')
    choose.save()
    content = u''
    dutytime =  "(" + str(schedule.starttime.hour) + ":" + str(schedule.starttime.minute)\
                + "--" + str(schedule.endtime.hour) + ":" + str(schedule.endtime.minute) + ")"
    content += u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/><div><span class="sideline">班次设置</span>'\
               u'&nbsp;&nbsp;<span class="week_tag">星期%s</span>&nbsp;&nbsp;<span class="orange">班次%s</span>&nbsp;&nbsp;<span class="orange">%s</span></div>'\
               u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/>'%(schedule.day , schedule.workorder, dutytime )
    content += u'<div id="maincontent3"><table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh2"></td></tr>'
    content += get_workerresultlist( choose)
    content +=  u'</table><div width="450"><input type="submit" name="modify" value="添加队员" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "addworker_result(%s)" /></div>'%(choose.id)
    dajax.assign('#setseduleinfo', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def addworker_schresult  (request , form):
    dajax = Dajax()
    sch_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            sch_id = id
            id = u''
        else:
            id += ch
    choose = ScheduleChoose.objects.get(id = int(sch_id))
    schedule = choose.schedule
    workerstr = u','+ id + u'.'
    choose.resultworker += workerstr
    choose.save()
    content = u''
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    content += u'<div id="maincontent3"><div width="400" id="right_table"><div class="sideline">添加新队员</div>'\
               u'<table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh"></td></tr>'
    for item in workerlist:
        if item.accept != 2:
            workerstr = u''+ ","+ str(item.user_id) + "."
            if (choose.resultworker.find(workerstr) <= 0):
                content  += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td><div align="right" >'\
                            u'<input type="submit" name="modify" value="添加" id="modify" onclick = "addworker_schresult(%s, %s)" /></div></td>'\
                            u'</tr>' %(item.name, item.user.username ,choose.id, item.user_id)
    content +=  u'</table></div></div>'
    dajax.assign('#addworker', 'innerHTML', content)
    content = u''
    dutytime =  "(" + str(schedule.starttime.hour) + ":" + str(schedule.starttime.minute)\
                + "--" + str(schedule.endtime.hour) + ":" + str(schedule.endtime.minute) + ")"
    content += u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/><div><span class="sideline">班次设置</span>'\
               u'&nbsp;&nbsp;<span class="week_tag">星期%s</span>&nbsp;&nbsp;<span class="orange">班次%s</span>&nbsp;&nbsp;<span class="orange">%s</span></div>'\
               u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/>'%(schedule.day , schedule.workorder, dutytime )
    content += u'<div id="maincontent3"><table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh2"></td></tr>'
    content += get_workerresultlist( choose)
    content +=  u'</table><div width="450"><input type="submit" name="modify" value="添加队员" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "addworker_result(%s)" /><input type="submit" name="modify" value="完成设置" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "Dajaxice.RegisterSystem.logic.finishresult(Dajax.process);" /></div>'%(schedule.id)
    dajax.assign('#setseduleinfo', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def addworker_sch  (request , form):
    dajax = Dajax()
    sch_id  = u''
    id = ''
    for ch in form:
        if ch == ',':
            sch_id = id
            id = u''
        else:
            id += ch
    schedule = Schedule.objects.get(id = int(sch_id))
    workerstr = u','+ id + u'.'
    schedule.worker += workerstr
    schedule.attendance += workerstr
    schedule.save()
    content = u''
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    content += u'<div id="maincontent3"><div width="400" id="right_table"><div class="sideline">添加新队员</div>'\
               u'<table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh"></td></tr>'
    for item in workerlist:
        if item.accept != 2:
            workerstr = u''+ ","+ str(item.user_id) + "."
            if (schedule.worker.find(workerstr) <= 0):
                content  += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td><div align="right" >'\
                            u'<input type="submit" name="modify" value="添加" id="modify" onclick = "addworker_sch(%s, %s)" /></div></td>'\
                            u'</tr>' %(item.name, item.user.username ,schedule.id, item.user_id)
    content +=  u'</table></div></div>'
    dajax.assign('#addworker', 'innerHTML', content)
    content = u''
    dutytime =  "(" + str(schedule.starttime.hour) + ":" + str(schedule.starttime.minute)\
                + "--" + str(schedule.endtime.hour) + ":" + str(schedule.endtime.minute) + ")"
    content += u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/><div><span class="sideline">班次设置</span>'\
               u'&nbsp;&nbsp;<span class="week_tag">星期%s</span>&nbsp;&nbsp;<span class="orange">班次%s</span>&nbsp;&nbsp;<span class="orange">%s</span></div>'\
               u'<hr align="left" width="850" size="1" noshade="noshade" class="hr"/>'%(schedule.day , schedule.workorder, dutytime )
    content += u'<div id="maincontent3"><table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh2"></td></tr>'
    content += get_workersetlist( schedule.worker, schedule)
    content +=  u'</table><div width="450"><input type="submit" name="bt_addworker" value="添加队员" id="bt_addworker" style="background-color: #f9ad37;'\
                u'"onclick = "addworker_schedule(%s)" /><input type="submit" name="modify" value="完成设置" id="modify" style="background-color: #f9ad37;'\
                u'"onclick = "Dajaxice.RegisterSystem.logic.finishresetsed(Dajax.process);" /></div>'%(schedule.id)
    dajax.assign('#setseduleinfo', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def addworker_schedule  (request, form):
    dajax = Dajax()
    content = u''
    schdule = Schedule.objects.get(id  = int(form))
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    content += u'<div id="maincontent3"><div width="400" id="right_table"><div class="sideline">添加新队员</div>'\
               u'<table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh"></td></tr>'
    for item in workerlist:
        if item.accept != 2:
            workerstr = u''+ ","+ str(item.user_id) + "."
            if (schdule.worker.find(workerstr) <= 0):
                content  += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td><div align="right" >'\
                            u'<input type="submit" name="modify" value="添加" id="modify" onclick = "addworker_sch(%s, %s)" /></div></td>'\
                            u'</tr>' %(item.name, item.user.username ,schdule.id, item.user_id)
    content +=  u'</table></div></div>'
    dajax.assign('#addworker', 'innerHTML', content)

    return dajax.json()

@dajaxice_register
def addworker_result  (request, form):
    dajax = Dajax()
    content = u''
    schdule = ScheduleChoose.objects.get(id  = int(form))
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    content += u'<div id="maincontent3"><div width="400" id="right_table"><div class="sideline">添加新队员</div>'\
               u'<table class="left_float"><tr class="att_name"><td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh"></td></tr>'
    for item in workerlist:
        if item.accept != 2:
            workerstr = u''+ ","+ str(item.user_id) + "."
            if (schdule.resultworker.find(workerstr) <= 0):
                content  += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td><div align="right" >'\
                            u'<input type="submit" name="modify" value="添加" id="modify" onclick = "addworker_schresult(%s, %s)" /></div></td>'\
                            u'</tr>' %(item.name, item.user.username ,schdule.id, item.user_id)
    content +=  u'</table></div></div>'
    dajax.assign('#addworker', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def open_manager_exchange(request):
    dajax = Dajax()
    iexchange = Exchange.objects.filter(iadministrator = request.user, state = 1)
    pexchange = Exchange.objects.filter(padministrator = request.user, state = 1)
    iexchange_list = list(Exchange.objects.filter(iadministrator = request.user, state = 1).order_by('itime')[:len(iexchange)])
    pexchange_list = list(Exchange.objects.filter(padministrator  = request.user, state = 1).order_by('ptime')[:len(pexchange)])
    content = get_manager_exchangelist( request, iexchange_list, 0) + get_manager_exchangelist( request, pexchange_list, len(iexchange))
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', content)
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_manager_leave(request):
    dajax = Dajax()
    leave = Leave.objects.filter(administrator = request.user, state = 1)
    leave_list = list(Leave.objects.filter(administrator = request.user, state = 1).order_by('time')[:len(leave)])
    content = get_manager_leavelist( request, leave_list)
    dajax.assign('#leavelist', 'innerHTML', content)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_manager_absenteesim(request):
    dajax = Dajax()
    absenteeism = Absenteeism.objects.filter(administrator = request.user)
    absenteeism_list = list(Absenteeism.objects.filter(administrator = request.user).order_by('time')[:len(absenteeism)])
    content = get_manager_absenteeismlist( request, absenteeism_list)
    dajax.assign('#absenlist', 'innerHTML', content)
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_manager_late(request):
    dajax = Dajax()
    late = Late.objects.filter(administrator = request.user)
    late_list = list(Late.objects.filter(administrator = request.user).order_by('time')[:len(late)])
    content = get_manager_latelist( request, late_list)
    dajax.assign('#latelist', 'innerHTML', content)
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_manager_work(request):
    dajax = Dajax()
    work = Work.objects.filter(administrator = request.user)
    work_list = list(Work.objects.filter(administrator = request.user).order_by('time')[:len(work)])
    content = get_manager_worklist( request, work_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', content)
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_manager_early(request):
    dajax = Dajax()
    early = Early.objects.filter(administrator = request.user)
    early_list = list(Early.objects.filter(administrator = request.user).order_by('time')[:len(early)])
    content = get_manager_earlylist( request, early_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', content)
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_manager_overtime(request):
    dajax = Dajax()
    overtime = Overtime.objects.filter(administrator = request.user)
    overtime_list = list(Overtime.objects.filter(administrator = request.user).order_by('time')[:len(overtime)])
    content = get_manager_overtimelist( request, overtime_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def open_officer_exchange(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    exchange = Exchange.objects.filter(department = workerinfo.department, state = 1)
    exchange_list = list(Exchange.objects.filter(department = workerinfo.department, state = 1).order_by('itime')[:len(exchange)])
    content = get_manager_exchangelist( request, exchange_list, 0)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', content)
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_leave(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    leave = Leave.objects.filter(department = workerinfo.department, state = 1)
    leave_list = list(Leave.objects.filter(department = workerinfo.department, state = 1).order_by('time')[:len(leave)])
    content = get_manager_leavelist( request, leave_list)
    dajax.assign('#leavelist', 'innerHTML', content)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_absenteesim(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    absenteeism = Absenteeism.objects.filter(department = workerinfo.department)
    absenteeism_list = list(Absenteeism.objects.filter(department = workerinfo.department).order_by('time')[:len(absenteeism)])
    content = get_manager_absenteeismlist( request, absenteeism_list)
    dajax.assign('#absenlist', 'innerHTML', content)
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_late(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    late = Late.objects.filter(department = workerinfo.department)
    late_list = list(Late.objects.filter(department = workerinfo.department).order_by('time')[:len(late)])
    content = get_manager_latelist( request, late_list)
    dajax.assign('#latelist', 'innerHTML', content)
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def searchexcel(request, form):
    dajax = Dajax()
    form = SearchForm(form)
    if form.is_valid():
        startweek = form.cleaned_data['startweek']
        endweek = form.cleaned_data['endweek']
        dajax.script("window.open('/SearchExtendenceExcel/?p1="+str(startweek)+"&p2="+str(endweek) +"')")
    return dajax.json()

@dajaxice_register
def search(request, form):
    dajax = Dajax()
    form = SearchForm(form)
    if form.is_valid():
        startweek = form.cleaned_data['startweek']
        endweek = form.cleaned_data['endweek']
        workerinfo = WorkerInfo.objects.get(user = request.user)
        content = gettotal_searchrecord(request, startweek, endweek)
        dajax.assign('#latelist', 'innerHTML', "")
        dajax.assign('#absenlist', 'innerHTML', "")
        dajax.assign('#leavelist', 'innerHTML', "")
        dajax.assign('#exchangelist', 'innerHTML', "")
        dajax.assign('#worklist', 'innerHTML', content)
        dajax.assign('#earlylist', 'innerHTML', "")
        dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_work(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    work = Work.objects.filter(department = workerinfo.department)
    work_list = list(Work.objects.filter(department = workerinfo.department).order_by('time')[:len(work)])
    content = get_manager_worklist( request, work_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', content)
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_early(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    early = Early.objects.filter(department = workerinfo.department)
    early_list = list(Early.objects.filter(department = workerinfo.department).order_by('time')[:len(early)])
    content = get_manager_earlylist( request, early_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', content)
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_overtime(request):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    overtime = Overtime.objects.filter(department = workerinfo.department)
    overtime_list = list(Overtime.objects.filter(department = workerinfo.department).order_by('time')[:len(overtime)])
    content = get_manager_overtimelist( request, overtime_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def open_officer_specific_exchange(request , form ):
    dajax = Dajax()
    workuser = User.objects.get(id = int(form))
    iexchange = Exchange.objects.filter(initiative_worker = workuser, state = 1)
    pexchange = Exchange.objects.filter(passivite_worker = workuser, state = 1)
    iexchange_list = list(Exchange.objects.filter(initiative_worker = workuser, state = 1).order_by('itime')[:len(iexchange)])
    pexchange_list = list(Exchange.objects.filter(passivite_worker  = workuser, state = 1).order_by('ptime')[:len(pexchange)])
    content= u''
    if(len(iexchange) >0):
        content += get_exchangelist( request, iexchange_list, 0) + get_exchangelist( request, pexchange_list, len(iexchange))
    else:
        content +=  get_exchangelist( request, pexchange_list, 0)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', content)
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_specific_leave(request, form):
    dajax = Dajax()
    workuser = User.objects.get(id = int(form))
    leave = Leave.objects.filter(worker = workuser, state = 1)
    leave_list = list(Leave.objects.filter(worker = workuser, state = 1).order_by('time')[:len(leave)])
    content = get_manager_leavelist( request, leave_list)
    dajax.assign('#leavelist', 'innerHTML', content)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_specific_absenteeism(request, form):
    dajax = Dajax()
    workuser = User.objects.get(id = int(form))
    absenteeism = Absenteeism.objects.filter(worker = workuser)
    absenteeism_list = list(Absenteeism.objects.filter(worker = workuser).order_by('time')[:len(absenteeism)])
    content = get_manager_absenteeismlist( request, absenteeism_list)
    dajax.assign('#absenlist', 'innerHTML', content)
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_specific_late(request, form):
    dajax = Dajax()
    workuser = User.objects.get(id = int(form))
    late = Late.objects.filter(worker = workuser)
    late_list = list(Late.objects.filter(worker = workuser).order_by('time')[:len(late)])
    content = get_manager_latelist( request, late_list)
    dajax.assign('#latelist', 'innerHTML', content)
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_specific_work(request, form):
    dajax = Dajax()
    workuser = User.objects.get(id = int(form))
    work = Work.objects.filter(worker = workuser)
    work_list = list(Work.objects.filter(worker = workuser).order_by('time')[:len(work)])
    content = get_manager_worklist( request, work_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', content)
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_specific_early(request, form):
    dajax = Dajax()
    workuser = User.objects.get(id = int(form))
    early = Early.objects.filter(worker = workuser)
    early_list = list(Early.objects.filter(worker = workuser).order_by('time')[:len(early)])
    content = get_manager_earlylist( request, early_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', content)
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_officer_specific_overtime(request, form):
    dajax = Dajax()
    workuser = User.objects.get(id = int(form))
    overtime = Overtime.objects.filter(worker = workuser)
    overtime_list = list(Overtime.objects.filter(worker = workuser).order_by('time')[:len(overtime)])
    content = get_manager_overtimelist( request, overtime_list)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def open_search_exchange(request , form ):
    dajax = Dajax()
    index = 0
    workerid = u''
    startweek = u''
    endweek = u''
    for ch in form:
        if ch == ',':
            index += 1
        elif index == 0:
            workerid += ch
        elif index == 1:
            startweek += ch
        else:
            endweek += ch
    workuser = User.objects.get(id = int(workerid))
    iexchange = Exchange.objects.filter(initiative_worker = workuser, state = 1)
    pexchange = Exchange.objects.filter(passivite_worker = workuser, state = 1)
    iexchange_list = list(Exchange.objects.filter(initiative_worker = workuser, state = 1).order_by('itime')[:len(iexchange)])
    pexchange_list = list(Exchange.objects.filter(passivite_worker  = workuser, state = 1).order_by('ptime')[:len(pexchange)])
    content = u''
    if(len(iexchange)>0):
        content += get_search_exchangelist( request, iexchange_list, 0, int(startweek), int(endweek)) + get_search_exchangelist( request, pexchange_list, len(iexchange), int(startweek), int(endweek))
    else:
        content +=  get_search_exchangelist( request, pexchange_list, 0, int(startweek), int(endweek))
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', content)
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_search_leave(request, form):
    dajax = Dajax()
    index = 0
    workerid = u''
    startweek = u''
    endweek = u''
    for ch in form:
        if ch == ',':
            index += 1
        elif index == 0:
            workerid += ch
        elif index == 1:
            startweek += ch
        else:
            endweek += ch
    workuser = User.objects.get(id = int(workerid))
    leave = Leave.objects.filter(worker = workuser, state = 1)
    leave_list = list(Leave.objects.filter(worker = workuser, state = 1).order_by('time')[:len(leave)])
    content = get_search_leavelist( request, leave_list,int(startweek), int(endweek))
    dajax.assign('#leavelist', 'innerHTML', content)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_search_absenteeism(request, form):
    dajax = Dajax()
    index = 0
    workerid = u''
    startweek = u''
    endweek = u''
    for ch in form:
        if ch == ',':
            index += 1
        elif index == 0:
            workerid += ch
        elif index == 1:
            startweek += ch
        else:
            endweek += ch
    workuser = User.objects.get(id = int(workerid))
    absenteeism = Absenteeism.objects.filter(worker = workuser)
    absenteeism_list = list(Absenteeism.objects.filter(worker = workuser).order_by('time')[:len(absenteeism)])
    content = get_search_absenteeismlist( request, absenteeism_list,int(startweek), int(endweek))
    dajax.assign('#absenlist', 'innerHTML', content)
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_search_late(request, form):
    dajax = Dajax()
    index = 0
    workerid = u''
    startweek = u''
    endweek = u''
    for ch in form:
        if ch == ',':
            index += 1
        elif index == 0:
            workerid += ch
        elif index == 1:
            startweek += ch
        else:
            endweek += ch
    workuser = User.objects.get(id = int(workerid))
    late = Late.objects.filter(worker = workuser)
    late_list = list(Late.objects.filter(worker = workuser).order_by('time')[:len(late)])
    content = get_search_latelist( request, late_list, int(startweek), int(endweek))
    dajax.assign('#latelist', 'innerHTML', content)
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_search_work(request, form):
    dajax = Dajax()
    index = 0
    workerid = u''
    startweek = u''
    endweek = u''
    for ch in form:
        if ch == ',':
            index += 1
        elif index == 0:
            workerid += ch
        elif index == 1:
            startweek += ch
        else:
            endweek += ch
    workuser = User.objects.get(id = int(workerid))
    work = Work.objects.filter(worker = workuser)
    work_list = list(Work.objects.filter(worker = workuser).order_by('time')[:len(work)])
    content = get_search_worklist( request, work_list, int(startweek), int(endweek))
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', content)
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_search_early(request, form):
    dajax = Dajax()
    index = 0
    workerid = u''
    startweek = u''
    endweek = u''
    for ch in form:
        if ch == ',':
            index += 1
        elif index == 0:
            workerid += ch
        elif index == 1:
            startweek += ch
        else:
            endweek += ch
    workuser = User.objects.get(id = int(workerid))
    early = Early.objects.filter(worker = workuser)
    early_list = list(Early.objects.filter(worker = workuser).order_by('time')[:len(early)])
    startweek =  int(startweek)
    endweek = int(endweek)
    content = get_search_earlylist( request, early_list, startweek, endweek)
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', content)
    dajax.assign('#overtimelist', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def open_search_overtime(request, form):
    dajax = Dajax()
    index = 0
    workerid = u''
    startweek = u''
    endweek = u''
    for ch in form:
        if ch == ',':
            index += 1
        elif index == 0:
            workerid += ch
        elif index == 1:
            startweek += ch
        else:
            endweek += ch
    workuser = User.objects.get(id = int(workerid))
    overtime = Overtime.objects.filter(worker = workuser)
    overtime_list = list(Overtime.objects.filter(worker = workuser).order_by('time')[:len(overtime)])
    content = get_search_overtimelist( request, overtime_list, int(startweek), int(endweek))
    dajax.assign('#latelist', 'innerHTML', "")
    dajax.assign('#absenlist', 'innerHTML', "")
    dajax.assign('#leavelist', 'innerHTML', "")
    dajax.assign('#exchangelist', 'innerHTML', "")
    dajax.assign('#worklist', 'innerHTML', "")
    dajax.assign('#earlylist', 'innerHTML', "")
    dajax.assign('#overtimelist', 'innerHTML', content)
    return dajax.json()


@dajaxice_register
def addovertime(request):
    dajax = Dajax()
    content = u'<table width="500" border="0" align="left" cellspacing="1" id="table8" ><tr>' \
               u'<form name="overtime" id = "overtime" method="post" action="" onsubmit="return false;"><div>'\
               u'<td class="banci">学号<input type="text" name="cardid"  style="max-width: 100px" value=""></td>'\
               u'<td class="banci">班次<input type="text" name="order"  style="max-width: 60px" value=""></td>'\
               u'<td class="banci">加班时长/小时<input type="text" name="hournum"  style="max-width: 60px" value=""></td>'\
              u'<td class="banci">加班原因：<input type="text" name="reason" style="max-width: 500px" value=""></td>'\
              u'<td class="banci"><input name="change" type="submit" class="change" value="提交"  onclick="finishovertime();"/></td>' \
              u'<label id="msg" style="color: red;"></label></div></form></tr></table>'
    dajax.assign('#early_list', 'innerHTML', "")
    dajax.assign('#overtime_list', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def finishovertime(request, form):
    dajax = Dajax()
    goalworker = User.objects.filter(username=form["cardid"])
    if(len(goalworker) <= 0):
        dajax.assign('#msg', 'innerHTML', u'学号不存在！')
    else:
        goalworker = User.objects.get(username=form["cardid"])
        workerinfo = WorkerInfo.objects.get(user = goalworker)
        date = datetime.date.today().weekday() + 1
        schedule = Schedule.objects.filter(day = date, workorder = int(form["order"]), department = workerinfo.department)
        if(len(schedule) <= 0):
            dajax.assign('#msg', 'innerHTML', u'班次不存在！')
        else:
            schedule = Schedule.objects.get(day = date, workorder = int(form["order"]), department = workerinfo.department)
            hour = float(form["hournum"])
            overtime = Overtime(worker =  goalworker,reason = form["reason"], day = date,workorder = form["order"],
                time = datetime.datetime.today(), administrator =  schedule.administrator, department = workerinfo.department, hournum = form["hournum"] )
            overtime.save()
            dajax.assign('#msg', 'innerHTML', u'添加成功！')
    return dajax.json()

@dajaxice_register
def addearly(request):
    dajax = Dajax()
    content = u'<table width="500" border="0" align="left" cellspacing="1" id="table8" ><tr>'\
              u'<form name="early" id ="early"  method="post" action="" onsubmit="return false;"><div>'\
              u'<td class="banci">学号<input type="text" name="cardid"  style="max-width: 100px" value=""></td>'\
              u'<td class="banci">班次<input type="text" name="order"  style="max-width: 60px" value=""></td>'\
              u'<td class="banci">早退时长/小时<input type="text" name="hournum"  style="max-width: 60px" value=""></td>'\
              u'<td class="banci">早退原因：<input type="text" name="reason" style="max-width: 500px" value=""></td>'\
              u'<td class="banci"><input name="change" type="submit" class="change" value="提交"  onclick="finishearly();"/></td>'\
              u'<label id="msg" style="color: red;"></label></div></form></tr></table>'
    dajax.assign('#early_list', 'innerHTML', content)
    dajax.assign('#overtime_list', 'innerHTML', "")
    return dajax.json()

@dajaxice_register
def finishearly(request, form):
    dajax = Dajax()
    goalworker = User.objects.filter(username=form["cardid"])
    if(len(goalworker) <= 0):
        dajax.assign('#msg', 'innerHTML', u'学号不存在！')
    else:
        goalworker = User.objects.get(username=form["cardid"])
        workerinfo = WorkerInfo.objects.get(user = goalworker)
        date = datetime.date.today().weekday() + 1
        schedule = Schedule.objects.filter(day = date, workorder = int(form["order"]), department = workerinfo.department)
        if(len(schedule) <= 0):
            dajax.assign('#msg', 'innerHTML', u'班次不存在！')
        else:
            schedule = Schedule.objects.get(day = date, workorder = int(form["order"]), department = workerinfo.department)
            hour = float(form["hournum"])
            early = Early(worker =  goalworker,reason = form["reason"], day = date,workorder = form["order"],
                time = datetime.datetime.today(), administrator =  schedule.administrator, department = workerinfo.department, hournum = form["hournum"] )
            early.save()
            dajax.assign('#msg', 'innerHTML', u'添加成功！')
    return dajax.json()

@dajaxice_register
def updatelate(request , form):
    dajax = Dajax()
    lateid = form["late_id"]
    content = form["reason_content"]
    late = Late.objects.get(id = lateid)
    late.reason = content
    late.save()
    dajax.assign('#msg'+ str(form["late_id"]), 'innerHTML', u'修改成功')
    return dajax.json()

@dajaxice_register
def updateabsenteeism(request , form):
    dajax = Dajax()
    absenteeismid = form["absenteeism_id"]
    content = form["reason_content"]
    absenteeism = Absenteeism.objects.get(id = absenteeismid)
    absenteeism.reason = content
    absenteeism.save()
    dajax.assign('#msg'+ str(form["absenteeism_id"]), 'innerHTML', u'修改成功')
    return dajax.json()

@dajaxice_register
def updateleave(request , form):
    dajax = Dajax()
    leaveid = form["leave_id"]
    content = form["reason_content"]
    leave = Leave.objects.get(id = leaveid)
    leave.reason = content
    leave.save()
    dajax.assign('#msg'+ str(form["leave_id"]), 'innerHTML', u'修改成功')
    return dajax.json()

@dajaxice_register
def agree_newleave(request , form):
    dajax = Dajax()
    leaveid = form["leave_id"]
    content = form["reason_content"]
    try:
        send_mail('请假批准','您在周%d的班次%d的请假已经被批准' %(leave.day,leave.workorder),'',[leave.worker.email])
    except Exception:
        dajax.script("alert('邮件发送未成功')")
    leave = Leave.objects.get(id = leaveid)
    leave.replyreason = content
    leave.state = 1
    leave.save()
    dajax.redirect("/manage_status/",delay=0)
    return dajax.json()

@dajaxice_register
def refuse_newleave(request , form):
    dajax = Dajax()
    leaveid = form["leave_id"]
    content = form["reason_content"]
    leave = Leave.objects.get(id = leaveid)
    leave.replyreason = content
    leave.state = -1
    try:
        send_mail('请假未获批','您在周%d的班次%d的请假未被批准……' %(leave.day,leave.workorder),'',[leave.worker.email])
    except Exception:
        dajax.script("alert('邮件发送未成功')")
    leave.save()
    dajax.redirect("/manage_status/",delay=0)
    return dajax.json()

@dajaxice_register
def settomanager(request , form):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(id = int(form))
    workerinfo.accept = 1
    workerinfo.save()
    content_manager = u'<table class="left_float"><tr class="att_name">'\
                      u'<td class="att_wh3">负责人姓名</td><td class="att_wh">学号</td><td class="att_wh2">操作</td>'
    content_worker = u'<table class="left_float"><tr class="att_name">'\
                     u'<td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh2">操作</td>'
    workerinfo = WorkerInfo.objects.get(user = request.user)
    oriworkerlist = list(WorkerInfo.objects.filter(department = workerinfo.department , accept = 0))
    managerlist = list(WorkerInfo.objects.filter(department = workerinfo.department , accept = 1))
    for item in oriworkerlist:
        content_worker += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td>'\
                          u'<input type="submit" name="delete" value="设为负责人" id="delete" onclick = "settomanager(%s)"/>'\
                          u'</td></tr>' %(item.name, item.user.username, item.id)
    for item in managerlist:
        content_manager += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td>'\
                           u'<input type="submit" name="delete" value="设为普通队员" id="delete" onclick = "settooridinary(%s)"/>'\
                           u'</td></tr>' %(item.name, item.user.username, item.id)
    content_worker += u'</tr></table>'
    content_manager += u'</tr></table>'
    dajax.assign('#workerset', 'innerHTML', content_manager)
    dajax.assign('#managerser', 'innerHTML', content_worker)
    return dajax.json()

@dajaxice_register
def settooridinary(request , form):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(id = int(form))
    workerinfo.accept = 0
    workerinfo.save()
    content_manager = u'<table class="left_float"><tr class="att_name">'\
                      u'<td class="att_wh3">负责人姓名</td><td class="att_wh">学号</td><td class="att_wh2">操作</td>'
    content_worker = u'<table class="left_float"><tr class="att_name">'\
                     u'<td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh2">操作</td>'
    workerinfo = WorkerInfo.objects.get(user = request.user)
    oriworkerlist = list(WorkerInfo.objects.filter(department = workerinfo.department , accept = 0))
    managerlist = list(WorkerInfo.objects.filter(department = workerinfo.department , accept = 1))
    for item in oriworkerlist:
        content_worker += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td>'\
                          u'<input type="submit" name="delete" value="设为负责人" id="delete" onclick = "settomanager(%s)"/>'\
                          u'</td></tr>' %(item.name, item.user.username, item.id)
    for item in managerlist:
        content_manager += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td>'\
                           u'<input type="submit" name="delete" value="设为普通队员" id="delete" onclick = "settooridinary(%s)"/>'\
                           u'</td></tr>' %(item.name, item.user.username, item.id)
    content_worker += u'</tr></table>'
    content_manager += u'</tr></table>'
    dajax.assign('#workerset', 'innerHTML', content_manager)
    dajax.assign('#managerser', 'innerHTML', content_worker)
    return dajax.json()

@dajaxice_register
def agree_newworker(request , form):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(id = int(form))
    try:
        mailcontent = u'您在勤工大队网站的申请已经通过，欢迎成为大队一员！'
        send_mail(u'队员申请成功',mailcontent,'',[workerinfo.user.email])
    except Exception:
        dajax.script("alert('提醒邮件发送未成功')")
    workerinfo.accept = 0
    workerinfo.save()
    content = u''
    workerinfo = WorkerInfo.objects.get(user = request.user)
    newworkerlist = list(WorkerInfo.objects.filter(department = workerinfo.department , accept = -1))
    if len(newworkerlist) == 0:
        content += u'无新申请队员'
    else:
        content = u'<table class="left_float"><tr class="att_name">'\
                  u'<td class="att_wh3">新队员姓名</td><td class="att_wh">学号</td><td class="att_wh2">操作</td>'
        for item in newworkerlist:
            content += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td>'\
                       u'<input input name="issue" type="submit" id="issue" value="同意" onclick = "agree_newworker(%s)"/>'\
                       u'<input input name="issue" type="submit" id="issue" value="删除" onclick = "refuse_newworker(%s)"/>'\
                       u'</td></tr>' %(item.name, item.user.username, item.id, item.id)
        content += u'</tr></table>'
    dajax.assign('#setnew', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def refuse_newworker(request , form):
    dajax = Dajax()
    mailcontent = u'你在勤工大队网站的申请遇到了一些问题，未能成功，请与管理员联系！'
    send_mail(u'队员申请失败',mailcontent,'zhangty10@gmail.com',[workerinfo.user.email])
    workerinfo = WorkerInfo.objects.get(id = int(form))
    workerinfo.delete()
    content = u''
    workerinfo = WorkerInfo.objects.get(user = request.user)
    newworkerlist = list(WorkerInfo.objects.filter(department = workerinfo.department , accept = -1))
    if len(newworkerlist) == 0:
        content += u'无新申请队员'
    else:
        content = u'<table class="left_float"><tr class="att_name">'\
                  u'<td class="att_wh3">新队员姓名</td><td class="att_wh">学号</td><td class="att_wh2">操作</td>'
        for item in newworkerlist:
            content += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td>'\
                       u'<input input name="issue" type="submit" id="issue" value="同意" onclick = "agree_newworker(%s)"/>'\
                       u'<input input name="issue" type="submit" id="issue" value="删除" onclick = "refuse_newworker(%s)"/>'\
                       u'</td></tr>' %(item.name, item.user.username, item.id, item.id)
        content += u'</tr></table>'
    dajax.assign('#setnew', 'innerHTML', content)
    return dajax.json()

@dajaxice_register
def deleaveworker(request , form):
    dajax = Dajax()
    workerinfo = WorkerInfo.objects.get(id = int(form))
    user = User.objects.get(id = workerinfo.user.id)
    currentMessage = CurrentMessage.objects.filter(worker = user)
    if(len(currentMessage) > 0):
        currentMessage = CurrentMessage.objects.get(worker = user)
        currentMessage.delete()
    department_id  = workerinfo.department.id
    schedule = Schedule.objects.filter(department = department_id)
    workerstr = u''+ ","+str(form)+ "."
    for sch in schedule:
        if(sch.attendance.find(workerstr)>0):
            sch.attendance = sch.attendance.replace(workerstr, '')
        if(sch.worker.find(workerstr)>0):
            sch.worker = sch.worker.replace(workerstr, '')
        if(sch.administrator==user):
            sch.administrator=request.user
        sch.save()
    user.delete()
    workerinfo.delete()
    workerinfo = WorkerInfo.objects.get(user = request.user)
    allworkerlist = list(WorkerInfo.objects.filter(department = workerinfo.department ))
    content = u'<table ><tr class="att_name">'\
              u'<td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh">邮箱</td><td class="att_wh">电话</td><td class="att_wh2">操作</td>'
    for item in allworkerlist:
        content += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td class="att_wh">%s</td><td class="att_wh">%s</td><td>'\
                   u'<input input type="submit"  value="请离队伍" onclick = "deleaveworker(%s)"/>'\
                   u'</td></tr>' %(item.name, item.user.username, item.user.email, item.phone, item.id)
    content += u'</tr></table>'
    dajax.assign('#workermanagelist', 'innerHTML', content)
    return dajax.json()