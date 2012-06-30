# Create your views here.
#-*- coding: UTF-8 -*-
from django.http import  HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.simple import direct_to_template
from django.contrib.auth.views import logout
from RegisterSystem.logic.getlist import *
import os,uuid,ImageFile,Image
from RegisterSystem.logic.forms import *
from RegisterSystem.settings import  USERPHOTO_ABS_PATH, USERPHOTO_VIR_PATH
from django.contrib import messages
import datetime
import xlrd
import json
import codecs
import csv
from excel_response import ExcelResponse

def requires_login(view):
    def new_view(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/index/')
        return view(request, *args, **kwargs)
    return new_view

def getifhaswork(request):
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    day_today = datetime.datetime.now().weekday() + 1
    schedule = list(Schedule.objects.filter(department = workerinfo.department, day = day_today))
    result = 0
    for item  in schedule:
        workerstr = u''+ ","+str(request.user.id)+ "."
        num = item.attendance.find(workerstr)
        if num > 0:
            result += 1
    return result

def index(request):
    if request.user.is_authenticated():
        department_id  = WorkerInfo.objects.get(user = request.user.id).department.id
        order = Department.objects.get(id = department_id).department_worknum
        pexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
        content = u''
        workerinfo  = WorkerInfo.objects.get(user = request.user)
        leave = Leave.objects.filter(administrator = request.user, state = 1)
        absenteeism = Absenteeism.objects.filter(administrator = request.user)
        late = Late.objects.filter(administrator = request.user)
        i_ma_exchange = Exchange.objects.filter(iadministrator = request.user, state = 1)
        p_ma_exchange = Exchange.objects.filter(padministrator = request.user, state = 1)
        num_total = len(i_ma_exchange) + len(p_ma_exchange)
        new_leave = Leave.objects.filter(administrator = request.user, state = 0)
        leave_officer = Leave.objects.filter(department = workerinfo.department, state = 1)
        absenteeism_officer = Absenteeism.objects.filter(department = workerinfo.department,)
        late_officer = Late.objects.filter(department = workerinfo.department,)
        exchang_officer = Exchange.objects.filter(department = workerinfo.department, state = 1)
        num_total_officer = len(exchang_officer)
        newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
        for i in range(order):
            dutylist = list(Schedule.objects.filter(department = department_id , workorder = i + 1).order_by('day')[:7])
            content += get_dutylist( request.user.id, dutylist)
        currentMessage = CurrentMessage.objects.get(worker = request.user)
        if currentMessage.ifaddold  == 1:
            currentMessage.ifaddold  = 0
            currentMessage.save()
        if workerinfo.accept == 2:
            content_oficer = gettotal_officerrecord(request)
            work  = Work.objects.filter(department = workerinfo.department)
            early = Early.objects.filter(department = workerinfo.department)
            overtime = Overtime.objects.filter(department = workerinfo.department)
            overhourtotal = 0.0
            earlyhourtotal = 0.0
            for over in overtime:
                overhourtotal += over.hournum
            for ear in early:
                earlyhourtotal += ear.hournum
            return render_to_response('officer/officer_infomanage.html', {
                'newworkernum':len(newworkerlist),
                'num_leave': len(leave_officer),
                'num_absenteesim': len(absenteeism_officer),
                'num_late': len(late_officer),
                'num_exchange' : num_total_officer,
                'num_work' : len(work),
                'workername':request.user.get_profile().name,
                'cardid':request.user,
                'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
                'latelist':content_oficer,
                'num_early': earlyhourtotal,
                'num_overtime': overhourtotal
                }, context_instance=RequestContext(request))
        elif(workerinfo.if_manager_login == 1 and workerinfo.accept == 1):
            content_list = gettotal_managerrecord(request)
            work  = Work.objects.filter(administrator = request.user)
            early = Early.objects.filter(administrator = request.user)
            overtime = Overtime.objects.filter(administrator = request.user)
            overhourtotal = 0.0
            earlyhourtotal = 0.0
            for over in overtime:
                overhourtotal += over.hournum
            for ear in early:
                earlyhourtotal += ear.hournum
            return render_to_response('manager/manage_attendance.html', {
                'num_leave': len(leave),
                'num_absenteesim': len(absenteeism),
                'num_late': len(late),
                'num_exchange' : num_total,
                'num_worktime': len(work),
                'workername':request.user.get_profile().name,
                'cardid':request.user,
                'latelist':content_list,
                'num_newleave':len(new_leave),
                'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
                'num_early': earlyhourtotal,
                'num_overtime': overhourtotal
                }, context_instance=RequestContext(request))
        else:
            return render_to_response('ordinary/showduty.html', {
                'workername':request.user.get_profile().name,
                'cardid':request.user,
                'dutylist': content,
                'new_num':len(pexchange),
                'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
                }, context_instance=RequestContext(request))

    return render_to_response('ordinary/index.html', {
        'next': request.REQUEST.get('next', '')
    }, context_instance=RequestContext(request))

def register(request):
    return direct_to_template(request, '../templates/ordinary/register.html')

def dutywish(request):
    pexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    department_id  = WorkerInfo.objects.get(user = request.user.id).department.id
    order = Department.objects.get(id = department_id).department_worknum
    content = u''
    workerchoose = WorkerChoose.objects.filter(worker = request.user)
    if(len(workerchoose) == 0):
        workerchoose = WorkerChoose(worker =  request.user, max_worknum = 0, min_worknum = 0, Worker_WorkLikeNum = 0)
        workerchoose.save()
    workerchoose = WorkerChoose.objects.get(worker = request.user)
    for i in range(order):
        dutylist = list(Schedule.objects.filter(department = department_id , workorder = i + 1).order_by('day')[:7])
        content += get_wishlist( request.user.id, dutylist)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('ordinary/dutywish.html', {
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'new_num':len(pexchange),
        'minnum':workerchoose.min_worknum,
        'maxnum':workerchoose.max_worknum,
        'wishlist':content,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
    }, context_instance=RequestContext(request))

def communicate(request):
    pexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    noticelist = Message.objects.filter( department = workerinfo.department, ifImportant = 1).order_by('-createtime')
    messagelist =  Message.objects.filter( department = workerinfo.department, ifSubordinate = 0, ifImportant = 0).order_by('-createtime')
    if(len(messagelist) > 10):
        messagelist =  Message.objects.filter( department = workerinfo.department,ifSubordinate = 0, ifImportant = 0).order_by('-createtime')[:10]
    notice_content = get_noticelist(request, noticelist)
    messagelist_content = u''
    num = 1
    min = -1
    for item in messagelist:
        messagelist_content += get_messagelist(request, item,  num)
        if min == -1:
            min = item.id
        elif min > item.id:
            min = item.id
        num += 1
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 0:
        currentMessage.currentNum = num
        currentMessage.currentMinID = min
        currentMessage.save()
    managenotice = u''
    name = u''
    if workerinfo.accept == 0 :
        name = u'<span>%s</span>'%(workerinfo.name )
        managenotice = u''
    if workerinfo.accept == 1 :
        name = u'<span>%s</span><span id="name_tag" >负责人</span>'%(workerinfo.name)
        managenotice = u'<input name="ifmanage" type="checkbox" id="checkbox"  />' \
                       u'<label for="fuzeren" id="commu_help"  >以负责人身份发表' \
                       u'<span class="font_grey" >（将同步到公告栏）</span></label>'
    if workerinfo.photo_name == "0":
        path = "images/css/avatar80.png"
    else:
        path = os.path.join( USERPHOTO_VIR_PATH,workerinfo.photo_thumb)
    return render_to_response('ordinary/communicate.html', {
        'workername':workerinfo.name,
        'cardid':request.user.get_profile().name,
        'new_num':len(pexchange),
        'getname' : name,
        'managenotice' : managenotice,
        'noticelist' : notice_content,
        'defaultMessage': u'<textarea name="message" id="experience_text">说些什么吧？</textarea>',
        'messagelist': messagelist_content,
        'vir_path':path,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
    }, context_instance=RequestContext(request))

def infomanage(request):
    pexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    department_id  = workerinfo.department.id
    de_name = Department.objects.get(id = department_id).department_mame
    if workerinfo.photo_name == "0":
        path = "images/css/avatar80.png"
    else:
        path = os.path.join( USERPHOTO_VIR_PATH,workerinfo.photo_name)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('ordinary/infomanage.html', {
        'workername':request.user.get_profile().name,
        'card_id': request.user,
        'user_name':workerinfo.name,
        'user_password': u'',
        'user_passwordagain': u'',
        'user_email':request.user.email,
        'user_phonenumber':workerinfo.phone,
        'department':de_name,
        'new_num':len(pexchange),
        'vir_path':path,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
    }, context_instance=RequestContext(request))

def showduty(request):
    pexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    department_id  = workerinfo.department.id
    order = Department.objects.get(id = department_id).department_worknum
    content = u''
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    for i in range(order):
        dutylist = list(Schedule.objects.filter(department = department_id , workorder = i + 1).order_by('day')[:7])
        content += get_dutylist( request.user.id, dutylist)
    if(workerinfo.if_manager_login == 1 and workerinfo.accept == 1):
        return render_to_response('manager/manager_attendance.html', {
            'workername':request.user.get_profile().name,
            'cardid':request.user,
            }, context_instance=RequestContext(request))
    else:
        return render_to_response('ordinary/showduty.html', {
            'workername':request.user.get_profile().name,
            'cardid':request.user,
            'dutylist': content,
            'new_num':len(pexchange),
            'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
            }, context_instance=RequestContext(request))

def attendance(request):
    leave = Leave.objects.filter(worker = request.user, state = 1)
    absenteeism = Absenteeism.objects.filter(worker = request.user)
    late = Late.objects.filter(worker = request.user)
    unexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    iexchange = Exchange.objects.filter(initiative_worker = request.user, state = 1)
    pexchange = Exchange.objects.filter(passivite_worker = request.user, state = 1)
    num_total = len(iexchange) + len(pexchange)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    work = Work.objects.filter(worker = request.user)
    early = Early.objects.filter(worker = request.user)
    overtime = Overtime.objects.filter(worker = request.user)
    overhourtotal = 0.0
    earlyhourtotal = 0.0
    for item in overtime:
        overhourtotal += item.hournum
    for item in early:
        earlyhourtotal += item.hournum
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('ordinary/attendance.html', {
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'num_leave': len(leave),
        'num_absenteesim': len(absenteeism),
        'num_late': len(late),
        'num_exchange' : num_total,
        'num_work':len(work),
        'new_num':len(unexchange),
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        'num_early': earlyhourtotal,
        'num_overtime': overhourtotal
    }, context_instance=RequestContext(request))

def changerequest(request):
    unexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    unexchange_list = list(Exchange.objects.filter(passivite_worker = request.user, state = 0).order_by('ptime')[:len(unexchange)])
    content = get_unexchangelist( request, unexchange_list)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('ordinary/changerequest.html', {
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'new_num':len(unexchange),
        'exchrequest_list': content,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
    }, context_instance=RequestContext(request))

def status(request):
    unexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    leave = Leave.objects.filter(worker = request.user )
    iexchange = Exchange.objects.filter(initiative_worker = request.user )
    content = u''
    content_exchange = u''
    if(len(leave) > 0 ):
        content += get_Newleavelist(leave)
    if(len(iexchange) > 0 ):
        content_exchange += get_Newexchangelist(iexchange)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('ordinary/status.html', {
        'newleavelist' : content,
        'newexchangelist' : content_exchange,
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'new_num':len(unexchange),
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
    }, context_instance=RequestContext(request))

def jsonMessagesByID(request, mid):
    ret = {}
    result = u''
    message = Message.objects.get(id = mid)
    workerinfo = WorkerInfo.objects.get(user = message.worker)
    photo = workerinfo.photo_thumb
    if photo == "0":
        src = "images/css/avatar35.png"
    else:
        src = os.path.join( USERPHOTO_VIR_PATH,photo)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    num = currentMessage.currentNum
    name = workerinfo.name
    result += u'<div class="boardinfo_details"><div id="avatar_photo2"><img src="%s" /></div><ul>'\
              u'<li>%s : <span class="boardinfo_words">%s</span></li>'\
              u'<li class="fontsize_12"><span class="boardinfo_words">%s</span> '\
              u'<input name="issue" type="submit" value="转发" onclick="transfermessage(%s);" >'\
              u'<input name="issue" type="submit" value="评论" onclick="setsumessage(%s);" >'\
              u'</li> '%(src ,name , message.content,message.createtime ,
                         "'" + name + ":" + message.content + "'", "'" + str(num) + "'")
    sumessagelist = Message.objects.filter(superior_id = message.id, ifSubordinate = 1)
    for item in sumessagelist:
        userinfo = User.objects.get(id =  item.worker.id)
        workerinfo = WorkerInfo.objects.get(user = userinfo)
        name =workerinfo.name
        photo = workerinfo.photo_thumb
        if photo == "0":
            src = "images/css/avatar35.png"
        else:
            src = os.path.join( USERPHOTO_VIR_PATH,photo)
        result += u'<li class="communicate_reply"><div id="avatar_photo2">'\
                  u'<img src="%s" /></div><ul>'\
                  u'<li>%s : <span class="boardinfo_words">%s</span></li>'\
                  u'<li class="fontsize_12">%s</li></ul></li>'\
                  u'<hr align="left" width="597" size="1" noshade="noshade" class="info_hr1"/>'%( src, name, item.content ,item.createtime )
    result += u'<form name="submessageForm%s" method="post" action="" id= "submessageForm%s" onsubmit="return false;">'\
              u'<div class="reply_info"><textarea name="content" class="reply_textarea"></textarea>'\
              u'<textarea name="id" class="reply_textarea" style="display: none" >%s</textarea>'\
              u'</div></ul></div></form>'\
              u'<hr align="left" width="662" size="1" noshade="noshade" class="info_hr2"/>'% ( num , num ,message.id )
    currentMessage.currentNum = num + 1
    currentMessage.ifaddold = 1
    currentMessage.save()
    ret['content'] = result
    return ret

def updatenews(request):
    departmentid = int(request.GET['id'])
    num = int(request.GET['num'])
    messageslist = list(Message.objects.filter(department = departmentid,ifImportant = 0, ifSubordinate = 0)[num:])
    result = []
    for item in messageslist:
        result.append(jsonMessagesByID(request, item.id))
    content = json.dumps(result)
    return HttpResponse(content)

def updateold(request):
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    num = currentMessage.currentNum
    minid = currentMessage.currentMinID
    workerinfo = WorkerInfo.objects.get(user = request.user)
    result = []
    currentnum = 0
    minid -= 1
    if minid > 0:
        while(currentnum < 10):
            message = Message.objects.filter(id = minid, department = workerinfo.department, ifImportant = 0, ifSubordinate = 0)
            if(len(message) == 1):
                message = Message.objects.get(id = minid, department = workerinfo.department, ifImportant = 0, ifSubordinate = 0)
                result.append(jsonMessagesByID(request, message.id))
                currentnum += 1
            minid -= 1
            if minid < 1:
                currentMessage = CurrentMessage.objects.get(worker = request.user)
                currentMessage.currentMinID = minid
                currentMessage.currentNum = num + currentnum
                currentMessage.ifaddold = 1
                currentMessage.save()
                ret = {}
                ret['content'] = u'none'
                result.append(ret)
                content = json.dumps(result)
                return HttpResponse(content)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    currentMessage.currentMinID = minid
    currentMessage.currentNum = num + currentnum
    currentMessage.ifaddold = 1
    currentMessage.save()
    ret = {}
    ret['content'] = u'none'
    result.append(ret)
    content = json.dumps(result)
    return HttpResponse(content)

def getbasicmessage(request):
    departmentid = WorkerInfo.objects.get(user = request.user).department.id
    result = {}
    result['id'] = departmentid
    result['num'] = len(list(Message.objects.filter(department = departmentid,ifImportant = 0, ifSubordinate = 0)))
    result = json.dumps(result)
    return HttpResponse(result)

def page_logout(request):
    logout(request)
    return HttpResponseRedirect( '/')

def findpassword(request):
    return render_to_response('ordinary/findpassword.html', {
        }, context_instance=RequestContext(request))

def manage_attendance(request):
    leave = Leave.objects.filter(administrator = request.user, state = 1)
    absenteeism = Absenteeism.objects.filter(administrator = request.user)
    late = Late.objects.filter(administrator = request.user)
    iexchange = Exchange.objects.filter(iadministrator = request.user, state = 1)
    pexchange = Exchange.objects.filter(padministrator = request.user, state = 1)
    num_total = len(iexchange) + len(pexchange)
    content = gettotal_managerrecord(request)
    new_leave = Leave.objects.filter(administrator = request.user, state = 0)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    work  = Work.objects.filter(administrator = request.user)
    early = Early.objects.filter(administrator = request.user)
    overtime = Overtime.objects.filter(administrator = request.user)
    overhourtotal = 0.0
    earlyhourtotal = 0.0
    for item in overtime:
        overhourtotal += item.hournum
    for item in early:
        earlyhourtotal += item.hournum
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('manager/manage_attendance.html', {
        'num_leave': len(leave),
        'num_absenteesim': len(absenteeism),
        'num_late': len(late),
        'num_exchange' : num_total,
        'num_worktime': len(work),
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'latelist':content,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        'num_newleave': len(new_leave),
        'num_early' : earlyhourtotal,
        'num_overtime': overhourtotal
    }, context_instance=RequestContext(request))

def manage_communicate(request):
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    noticelist = Message.objects.filter( department = workerinfo.department, ifImportant = 1).order_by('-createtime')
    messagelist =  Message.objects.filter( department = workerinfo.department, ifSubordinate = 0, ifImportant = 0).order_by('-createtime')
    if(len(messagelist) > 10):
        messagelist =  Message.objects.filter( department = workerinfo.department,ifSubordinate = 0, ifImportant = 0).order_by('-createtime')[:10]
    notice_content = get_noticelist(request, noticelist)
    messagelist_content = u''
    num = 1
    min = -1
    for item in messagelist:
        messagelist_content += get_messagelist(request, item,  num)
        if min == -1:
            min = item.id
        elif min > item.id:
            min = item.id
        num += 1
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 0:
        currentMessage.currentNum = num
        currentMessage.currentMinID = min
        currentMessage.save()
    managenotice = u''
    name = u''
    if workerinfo.accept == 0 :
        name = u'<span>%s</span>'%(workerinfo.name )
        managenotice = u''
    if workerinfo.accept == 1 :
        name = u'<span>%s</span><span id="name_tag" >负责人</span>'%(workerinfo.name)
        managenotice = u'<input name="ifmanage" type="checkbox" id="checkbox"  />'\
                       u'<label for="fuzeren" id="commu_help"  >以负责人身份发表'\
                       u'<span class="font_grey" >（将同步到公告栏）</span></label>'
    if workerinfo.photo_name == "0":
        path = "images/css/avatar80.png"
    else:
        path = os.path.join( USERPHOTO_VIR_PATH,workerinfo.photo_thumb)
    new_leave = Leave.objects.filter(administrator = request.user, state = 0)
    return render_to_response('manager/manage_communicate.html', {
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        'getname' : name,
        'managenotice' : managenotice,
        'noticelist' : notice_content,
        'defaultMessage': u'<textarea name="message" id="experience_text">说些什么吧？</textarea>',
        'messagelist': messagelist_content,
        'vir_path':path,
        'num_newleave': len(new_leave),
        }, context_instance=RequestContext(request))

def manage_sign_in(request):
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    schedulelist = list(Schedule.objects.filter(department = workerinfo.department, administrator = request.user, day = datetime.datetime.now().weekday() +1 ))
    content = u''
    for item in schedulelist:
        if (item.starttime.hour < datetime.datetime.now().hour  or(item.starttime.hour == datetime.datetime.now().hour and item.starttime.minute <= datetime.datetime.now().minute ))\
           and ( item.endtime.hour > datetime.datetime.now().hour or (item.endtime.hour == datetime.datetime.now().hour and item.endtime.minute > datetime.datetime.now().minute) ):
            if item.signindate == datetime.date.today():
                content = u'该时间段班次已签到完毕！'
            else:
                content += get_AttentenceList(item)
    if content == u'':
        content = u'该时间段您无需组织签到！'
    new_leave = Leave.objects.filter(administrator = request.user, state = 0)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('manager/manage_sign_in.html', {
        'signin_list': content,
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        'num_newleave': len(new_leave),
    }, context_instance=RequestContext(request))

def manage_status(request):
    new_leave = Leave.objects.filter(administrator = request.user, state = 0)
    content = u''
    if len(new_leave) == 0:
        content = u'您无需要回复的请假条。'
    else:
        new_leavelist = list(Leave.objects.filter(administrator = request.user, state = 0))
        content += u'<table width="200" border="0" align="left" cellspacing="1" id="table3" ><tr class="att_name"><td class="time_wh">姓名</td>'\
                   u'<td class="duty_wh">学号</td><td class="time_wh">时间</td><td class="duty_wh">班次</td><td class="reason_wh3">请假原因</td>'\
                   u'<td class="reason_wh3">回复</td><td class="duty_wh"></td><td class="duty_wh"></td></tr>'
        for item in new_leavelist:
            workerinfo = WorkerInfo.objects.get(user = item.worker)
            content += u'<tr class="att_number"><td class="time_wh">%s</td><td class="duty_wh">%s</td>' \
                       u'<td class="time_wh">%s</td><td class="duty_wh">班次%s</td><td class="reason_wh3">%s</td>' \
                       u'<td class="reason_wh3"><form name="leavereply%s" method="post" action="" id= "leavereply%s" onsubmit="return false;">' \
                       u'<input type="text" name="leave_id" style="display: none" value="%s" >' \
                       u'<input type="text" name="reason_content" maxlength="20" value="%s" id="cardid" class="text-input">' \
                       u'</form></td><td class="duty_wh"><input name="agree" type="submit" class="refuse" value="批准" onclick = "agree_newleave(%s);" /></td><td class="duty_wh">' \
                       u'<input name="refuse" type="submit" class="refuse" value="拒绝" onclick = "refuse_newleave(%s);" /></td></tr>' \
                       u'</table>' %(workerinfo.name, item.worker.username, item.time.date(), item.workorder, item.reason, item.id, item.id, item.id, item.replyreason,  item.id, item.id )
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('manager/manage_status.html', {
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        'num_newleave': len(new_leave),
        'newleavelist': content,
    }, context_instance=RequestContext(request))

def manage_infomanage(request):
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    department_id  = workerinfo.department.id
    de_name = Department.objects.get(id = department_id).department_mame
    if workerinfo.photo_name == "0":
        path = "images/css/avatar80.png"
    else:
        path = os.path.join( USERPHOTO_VIR_PATH,workerinfo.photo_name)
    new_leave = Leave.objects.filter(administrator = request.user, state = 0)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('manager/manage_infomanage.html', {
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        'user_name':workerinfo.name,
        'user_password': u'',
        'user_passwordagain': u'',
        'user_email':request.user.email,
        'user_phonenumber':workerinfo.phone,
        'department':de_name,
        'vir_path':path,
        'num_newleave': len(new_leave),
        }, context_instance=RequestContext(request))

def uploadphoto(request):
    template_var={}
    form=PhotoForm()
    unexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    if request.method=="POST":
        form = PhotoForm(request.POST.copy(),request.FILES)
        if form.is_valid():
            file=request.FILES.get("photo_name",None)
            if file:
                p=ImageFile.Parser()
                for c in file.chunks():
                    p.feed(c)
                img=p.close()
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                if img.size[0]>img.size[1]:
                    offset=int(img.size[0]-img.size[1])/2
                    img=img.crop((offset,0,int(img.size[0]-offset),img.size[1]))
                else:
                    offset=int(img.size[1]-img.size[0])/2
                    img=img.crop((0,offset,img.size[0],(img.size[1]-offset)))
                img.thumbnail((300, 300))
                file_name="%s.jpg"%str(uuid.uuid1())
                img.save(os.path.join(USERPHOTO_ABS_PATH,file_name),"JPEG",quality=100)
                p=Photo.objects.create(photo_name=file_name)
                p.save()
                workerinfo = WorkerInfo.objects.filter(user = request.user.id)
                workerinfo.update(photo_name = file_name)
                return HttpResponseRedirect(reverse("cutphoto"))
    template_var["form"]=form
    template_var["workername"] = request.user.get_profile().name
    template_var["cardid"] = request.user
    template_var["new_num"] = len(unexchange)
    template_var["whetherwork"] = u'有 '+ str(getifhaswork(request)) + u' '
    return render_to_response('ordinary/uploadphoto.html',template_var, context_instance=RequestContext(request))

def manager_uploadphoto(request):
    template_var={}
    form=PhotoForm()
    if request.method=="POST":
        form = PhotoForm(request.POST.copy(),request.FILES)
        if form.is_valid():
            file=request.FILES.get("photo_name",None)
            if file:
                p=ImageFile.Parser()
                for c in file.chunks():
                    p.feed(c)
                img=p.close()
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                if img.size[0]>img.size[1]:
                    offset=int(img.size[0]-img.size[1])/2
                    img=img.crop((offset,0,int(img.size[0]-offset),img.size[1]))
                else:
                    offset=int(img.size[1]-img.size[0])/2
                    img=img.crop((0,offset,img.size[0],(img.size[1]-offset)))
                img.thumbnail((300, 300))
                file_name="%s.jpg"%str(uuid.uuid1())
                img.save(os.path.join(USERPHOTO_ABS_PATH,file_name),"JPEG",quality=100)
                p=Photo.objects.create(photo_name=file_name)
                p.save()
                workerinfo = WorkerInfo.objects.filter(user = request.user.id)
                workerinfo.update(photo_name = file_name)
                return HttpResponseRedirect(reverse("manager_cutphoto"))
    new_leave = Leave.objects.filter(administrator = request.user, state = 0)
    template_var["num_newleave"] = len(new_leave)
    template_var["form"]=form
    template_var["workername"] = request.user.get_profile().name
    template_var["cardid"] = request.user
    template_var["whetherwork"] = u'有 '+ str(getifhaswork(request)) + u' '
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('manager/manage_uploadphoto.html',template_var, context_instance=RequestContext(request))

def officer_uploadphoto(request):
    template_var={}
    form=PhotoForm()
    if request.method=="POST":
        form = PhotoForm(request.POST.copy(),request.FILES)
        if form.is_valid():
            file=request.FILES.get("photo_name",None)
            if file:
                p=ImageFile.Parser()
                for c in file.chunks():
                    p.feed(c)
                img=p.close()
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                if img.size[0]>img.size[1]:
                    offset=int(img.size[0]-img.size[1])/2
                    img=img.crop((offset,0,int(img.size[0]-offset),img.size[1]))
                else:
                    offset=int(img.size[1]-img.size[0])/2
                    img=img.crop((0,offset,img.size[0],(img.size[1]-offset)))
                img.thumbnail((300, 300))
                file_name="%s.jpg"%str(uuid.uuid1())
                img.save(os.path.join(USERPHOTO_ABS_PATH,file_name),"JPEG",quality=100)
                p=Photo.objects.create(photo_name=file_name)
                p.save()
                workerinfo = WorkerInfo.objects.filter(user = request.user.id)
                workerinfo.update(photo_name = file_name)
                return HttpResponseRedirect(reverse("officer_cutphoto"))
    workerinfo = WorkerInfo.objects.get(user = request.user)
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    template_var["newworkernum"]=len(newworkerlist)
    template_var["form"]=form
    template_var["workername"] = request.user.get_profile().name
    template_var["cardid"] = request.user
    template_var["whetherwork"] = u'有 '+ str(getifhaswork(request)) + u' '
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_uploadphoto.html',template_var, context_instance=RequestContext(request))

def cutphoto(request):
    template_var={}
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    photo = Photo.objects.get(photo_name = workerinfo.photo_name)
    id = photo.id
    p = get_object_or_404(Photo,pk=int(id))
    unexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    if not p.photo_name:
        messages.info(request,u"请先上传图片！")
        return HttpResponseRedirect(reverse("uploadphoto"))
    template_var["vir_path"]=os.path.join( USERPHOTO_VIR_PATH,p.photo_name)
    form=HatHeadCutForm()
    if request.method=='POST':
        form=HatHeadCutForm(request.POST)
        if form.is_valid():
            try:
                img=Image.open(os.path.join( USERPHOTO_ABS_PATH,p.photo_name))
            except IOError:
                messages.info(request,u"读取文件错误！")
            data=form.cleaned_data
            img=img.crop((data["x1"],data["y1"],data["x2"],data["y2"]))
            img.thumbnail((150, 150))
            file_name="%s_%s"%(os.path.splitext(p.photo_name)[0],"_50_50.jpg")
            img.save(os.path.join( USERPHOTO_ABS_PATH,file_name),"JPEG",quality=100)
            p.photo_thumb=file_name
            p.save()
            workerinfo = WorkerInfo.objects.filter(user = request.user.id)
            workerinfo.update(photo_thumb = file_name)
            return HttpResponseRedirect(reverse("infomanage"))
        else:
            messages.info(request,u"请剪切后 再保存！")
    template_var["form"]=form
    template_var["workername"]=request.user.get_profile().name
    template_var["cardid"]=request.user
    template_var["new_num"] = len(unexchange)
    template_var["whetherwork"] = u'有 '+ str(getifhaswork(request)) + u' '
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold = 0
        currentMessage.save()
    return render_to_response('ordinary/cutphoto.html',template_var, context_instance=RequestContext(request))

def manager_cutphoto(request):
    template_var={}
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    photo = Photo.objects.get(photo_name = workerinfo.photo_name)
    id = photo.id
    p = get_object_or_404(Photo,pk=int(id))
    if not p.photo_name:
        messages.info(request,u"请先上传图片！")
        return HttpResponseRedirect(reverse("manager_uploadphoto"))
    template_var["vir_path"]=os.path.join( USERPHOTO_VIR_PATH,p.photo_name)
    form=HatHeadCutForm()
    if request.method=='POST':
        form=HatHeadCutForm(request.POST)
        if form.is_valid():
            try:
                img=Image.open(os.path.join( USERPHOTO_ABS_PATH,p.photo_name))
            except IOError:
                messages.info(request,u"读取文件错误！")
            data=form.cleaned_data
            img=img.crop((data["x1"],data["y1"],data["x2"],data["y2"]))
            img.thumbnail((150, 150))
            file_name="%s_%s"%(os.path.splitext(p.photo_name)[0],"_50_50.jpg")
            img.save(os.path.join( USERPHOTO_ABS_PATH,file_name),"JPEG",quality=100)
            p.photo_thumb=file_name
            p.save()
            workerinfo = WorkerInfo.objects.filter(user = request.user.id)
            workerinfo.update(photo_thumb = file_name)
            return HttpResponseRedirect(reverse("manage_infomanage"))
        else:
            messages.info(request,u"请剪切后 再保存！")
    new_leave = Leave.objects.filter(administrator = request.user, state = 0)
    template_var["num_newleave"] = len(new_leave)
    template_var["form"]=form
    template_var["workername"]=request.user.get_profile().name
    template_var["cardid"]=request.user
    template_var["whetherwork"] = u'有 '+ str(getifhaswork(request)) + u' '
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('manager/manage_cutphoto.html',template_var, context_instance=RequestContext(request))

def officer_cutphoto(request):
    template_var={}
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    photo = Photo.objects.get(photo_name = workerinfo.photo_name)
    id = photo.id
    p = get_object_or_404(Photo,pk=int(id))
    unexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    if not p.photo_name:
        messages.info(request,u"请先上传图片！")
        return HttpResponseRedirect(reverse("officer_uploadphoto"))
    template_var["vir_path"]=os.path.join( USERPHOTO_VIR_PATH,p.photo_name)

    form=HatHeadCutForm()
    if request.method=='POST':
        form=HatHeadCutForm(request.POST)
        if form.is_valid():
            try:
                img=Image.open(os.path.join( USERPHOTO_ABS_PATH,p.photo_name))
            except IOError:
                messages.info(request,u"读取文件错误！")
            data=form.cleaned_data
            img=img.crop((data["x1"],data["y1"],data["x2"],data["y2"]))
            img.thumbnail((150, 150))
            file_name="%s_%s"%(os.path.splitext(p.photo_name)[0],"_50_50.jpg")
            img.save(os.path.join( USERPHOTO_ABS_PATH,file_name),"JPEG",quality=100)
            p.photo_thumb=file_name
            p.save()
            workerinfo = WorkerInfo.objects.filter(user = request.user.id)
            workerinfo.update(photo_thumb = file_name)
            return HttpResponseRedirect(reverse("officer_selfinfo"))
        else:
            messages.info(request,u"请剪切后 再保存！")
    workerinfo = WorkerInfo.objects.get(user = request.user)
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    template_var["newworkernum"]=len(newworkerlist)
    template_var["form"]=form
    template_var["workername"]=request.user.get_profile().name
    template_var["cardid"]=request.user
    template_var["whetherwork"] = u'有 '+ str(getifhaswork(request)) + u' '
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_cutphoto.html',template_var, context_instance=RequestContext(request))

def officer_accreditation(request):
    content_manager = u'<table class="left_float"><tr class="att_name">' \
                     u'<td class="att_wh3">负责人姓名</td><td class="att_wh">学号</td><td class="att_wh2">操作</td>'
    content_worker= u'<table class="left_float"><tr class="att_name">' \
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
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_accreditation.html', {
        'newworkernum': len(newworkerlist),
        'workerset':content_manager,
        'managerser':content_worker,
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
    }, context_instance=RequestContext(request))

def officer_arrangement(request):
    workerinfo = WorkerInfo.objects.get(user = request.user)
    department_id  = workerinfo.department.id
    order = Department.objects.get(id = department_id).department_worknum
    content = u''
    for i in range(order):
        dutylist = list(Schedule.objects.filter(department = department_id , workorder = i + 1).order_by('day')[:7])
        content += get_officerdutylist( request.user.id, dutylist)
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_arrangement.html', {
        'newworkernum': len(newworkerlist),
        'showdutylist':content,
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
    }, context_instance=RequestContext(request))

def officer_wish(request):
    workerinfo = WorkerInfo.objects.get(user = request.user)
    department_id  = workerinfo.department.id
    order = Department.objects.get(id = department_id).department_worknum
    content = u''
    for i in range(order):
        dutylist = list(Schedule.objects.filter(department = department_id , workorder = i + 1).order_by('day')[:7])
        content += get_officerwishlist( dutylist)
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    workerlist = WorkerInfo.objects.filter(department = department_id)
    numcontent = get_numlist(workerlist)
    return render_to_response('officer/officer_wish.html', {
        'newworkernum': len(newworkerlist),
        'showwishlist':content,
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'numdutylist':numcontent,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        }, context_instance=RequestContext(request))

def officer_wisharrange(request):
    workerinfo = WorkerInfo.objects.get(user = request.user)
    department_id  = workerinfo.department.id
    order = Department.objects.get(id = department_id).department_worknum
    content = u''
    for i in range(order):
        dutylist = list(Schedule.objects.filter(department = department_id , workorder = i + 1).order_by('day')[:7])
        content += get_wishresultlist(dutylist)
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_wisharrange.html', {
        'newworkernum': len(newworkerlist),
        'showdutylist':content,
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        }, context_instance=RequestContext(request))

def officer_communication(request):
    pexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    noticelist = Message.objects.filter( department = workerinfo.department, ifImportant = 1).order_by('-createtime')
    messagelist =  Message.objects.filter( department = workerinfo.department, ifSubordinate = 0, ifImportant = 0).order_by('-createtime')
    if(len(messagelist) > 10):
        messagelist =  Message.objects.filter( department = workerinfo.department,ifSubordinate = 0, ifImportant = 0).order_by('-createtime')[:10]
    notice_content = get_noticelist(request, noticelist)
    messagelist_content = u''
    num = 1
    min = -1
    for item in messagelist:
        messagelist_content += get_messagelist(request, item,  num)
        if min == -1:
            min = item.id
        elif min > item.id:
            min = item.id
        num += 1
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 0:
        currentMessage.currentNum = num
        currentMessage.currentMinID = min
        currentMessage.save()
    managenotice = u''
    name = u''
    if workerinfo.accept == 0 :
        name = u'<span>%s</span>'%(workerinfo.name )
        managenotice = u''
    if workerinfo.accept == 1 :
        name = u'<span>%s</span><span id="name_tag" >负责人</span>'%(workerinfo.name)
        managenotice = u'<input name="ifmanage" type="checkbox" id="checkbox"  />'\
                       u'<label for="fuzeren" id="commu_help"  >以负责人身份发表'\
                       u'<span class="font_grey" >（将同步到公告栏）</span></label>'
    elif  workerinfo.accept == 2 :
        name = u'<span>%s</span><span id="name_tag" >队委</span>'%(workerinfo.name)
        managenotice = u'<input name="ifmanage" type="checkbox" id="checkbox"  />'\
                       u'<label for="fuzeren" id="commu_help"  >以负责人身份发表'\
                       u'<span class="font_grey" >（将同步到公告栏）</span></label>'
    if workerinfo.photo_name == "0":
        path = "images/css/avatar80.png"
    else:
        path = os.path.join( USERPHOTO_VIR_PATH,workerinfo.photo_thumb)
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    return render_to_response('officer/officer_communication.html', {
        'newworkernum': len(newworkerlist),
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        'getname' : name,
        'managenotice' : managenotice,
        'noticelist' : notice_content,
        'defaultMessage': u'<textarea name="message" id="experience_text">说些什么吧？</textarea>',
        'messagelist': messagelist_content,
        'vir_path':path,
        }, context_instance=RequestContext(request))

def officer_data_managerment(request):
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_data_managerment.html', {
        'newworkernum': len(newworkerlist),
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
    }, context_instance=RequestContext(request))

def officer_infomanage(request):
    workerinfo = WorkerInfo.objects.get(user = request.user)
    leave = Leave.objects.filter(department = workerinfo.department, state = 1)
    absenteeism = Absenteeism.objects.filter(department = workerinfo.department,)
    late = Late.objects.filter(department = workerinfo.department,)
    exchange = Exchange.objects.filter(department = workerinfo.department, state = 1)
    num_total = len(exchange)
    content = gettotal_officerrecord(request)
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    work = Work.objects.filter(department =  workerinfo.department)
    early = Early.objects.filter(department =  workerinfo.department)
    overtime = Overtime.objects.filter(department =  workerinfo.department)
    overhourtotal = 0.0
    earlyhourtotal = 0.0
    for item in overtime:
        overhourtotal += item.hournum
    for item in early:
        earlyhourtotal += item.hournum
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_infomanage.html', {
        'newworkernum': len(newworkerlist),
        'num_leave': len(leave),
        'num_absenteesim': len(absenteeism),
        'num_late': len(late),
        'num_exchange' : num_total,
        'num_work': len(work),
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        'latelist':content,
        'num_early' : earlyhourtotal,
        'num_overtime': overhourtotal
    }, context_instance=RequestContext(request))

def officer_new_application(request):
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
                              u'<input input name="issue" type="submit" id="issue" value="同意" onclick = "agree_newworker(%s)"/>' \
                              u'<input input name="issue" type="submit" id="issue" value="删除" onclick = "refuse_newworker(%s)"/>'\
                              u'</td></tr>' %(item.name, item.user.username, item.id, item.id)
        content += u'</tr></table>'
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_new_application.html', {
        'newworkernum': len(newworkerlist),
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        'setnew':content,
    }, context_instance=RequestContext(request))

def officer_queryInformation(request):
    workerinfo = WorkerInfo.objects.get(user = request.user)
    allworkerlist = list(WorkerInfo.objects.filter(department = workerinfo.department ))
    content = u'<table ><tr class="att_name">'\
              u'<td class="att_wh3">队员姓名</td><td class="att_wh">学号</td><td class="att_wh">邮箱</td><td class="att_wh">电话</td><td class="att_wh2">操作</td>'
    for item in allworkerlist:
        if(item.accept != 2):
            content += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td class="att_wh">%s</td><td class="att_wh">%s</td><td>'\
                       u'<input input type="submit"  value="请离队伍" onclick = "deleaveworker(%s)"/>'\
                       u'</td></tr>' %(item.name, item.user.username, item.user.email, item.phone, item.id)
    content += u'</tr></table>'
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_queryInformation.html', {
        'workermanagelist':content,
        'newworkernum': len(newworkerlist),
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
    }, context_instance=RequestContext(request))

def officer_selfinfo(request):
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    department_id  = workerinfo.department.id
    de_name = Department.objects.get(id = department_id).department_mame
    unexchange = Exchange.objects.filter(passivite_worker = request.user, state = 0)
    if workerinfo.photo_name == "0":
        path = "images/css/avatar80.png"
    else:
        path = os.path.join( USERPHOTO_VIR_PATH,workerinfo.photo_name)
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_selfinfo.html', {
        'newworkernum': len(newworkerlist),
        'workername':request.user.get_profile().name,
        'cardid':request.user,
        'whetherwork':u'有 '+ str(getifhaswork(request)) + u' ',
        'user_name':workerinfo.name,
        'user_password': u'',
        'user_passwordagain': u'',
        'user_email':request.user.email,
        'user_phonenumber':workerinfo.phone,
        'department':de_name,
        'vir_path':path,
        }, context_instance=RequestContext(request))

def officer_uploadexcel(request):
    template_var={}
    template_var["msg"]="*请确认是xls文件（一二列分别为学号和姓名)"
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        template_var["form"]=form
        if form.is_valid():
            try:
                wk = xlrd.open_workbook(file_contents =  request.FILES["file"].read())
                content = u''
                content += u'<tr><td>学号</td><td>姓名</td><td></td>'\
                           u'<td><input type="text" name="url"  value="%s" id="url" style="display: none"></td></tr>'%("temp.xls")
                for sh in wk.sheets():
                    for i in range(sh.nrows):
                        if i > 0 :
                            content += u'<tr><td>%s</td><td>%s</td><td></td></tr>' %(sh.cell_value(i,0),sh.cell_value(i,1) )
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
                                    accept = 0, photo_name = "0", photo_thumb = "0",phone = "0",if_manager_login = 0)
                                worker.save()
                                currentMessage = CurrentMessage(worker = userid,currentNum = 0,currentMinID = 0, ifaddold = 0)
                                currentMessage.save()
                            else:
                                template_var["msg"]="跳过部分已注册学号！"
                template_var["msg"]="批量注册成功！"
                template_var["show_excel"] = content
            except:
                template_var["msg"]="文件路径或格式出错！"
    workerinfo = WorkerInfo.objects.get(user = request.user.id)
    newworkerlist = WorkerInfo.objects.filter(department = workerinfo.department , accept = -1)
    template_var["newworkernum"]=len(newworkerlist)
    template_var["workername"] = request.user.get_profile().name
    template_var["cardid"] = request.user
    template_var["whetherwork"] = u'有 '+ str(getifhaswork(request)) + u' '
    currentMessage = CurrentMessage.objects.get(worker = request.user)
    if currentMessage.ifaddold  == 1:
        currentMessage.ifaddold  = 0
        currentMessage.save()
    return render_to_response('officer/officer_uploadexcel.html',template_var, context_instance=RequestContext(request))

def AllExtendenceExcel(request):
    response = HttpResponse(mimetype='text/csv')
    response.write('\xEF\xBB\xBF')
    response['Content-Disposition'] = 'attachment; filename=出勤记录.csv'
    writer = csv.writer(response)
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    name = u'姓名'
    id = u'学号'
    leave= u'请假次数'
    absenteeism = u'旷工次数'
    late = u'迟到次数'
    exchange = u'换班次数'
    writer.writerow([ id.encode('GBK'), name.encode('GBK'),leave.encode('GBK'),absenteeism.encode('GBK'),late.encode('GBK'),exchange.encode('GBK')])
    for item in workerlist:
        leave = Leave.objects.filter( state = 1, worker = item.user)
        absenteeism = Absenteeism.objects.filter(worker = item.user)
        late = Late.objects.filter(worker = item.user)
        iexchange = Exchange.objects.filter( state = 1, initiative_worker = item.user)
        pexchange = Exchange.objects.filter( state = 1, passivite_worker = item.user)
        num_total = len(iexchange) +  len(pexchange)
        name = u'%s'%(item.name)
        name = name.encode('GBK')
        if(len(leave) != 0 or len(absenteeism) != 0 or len(late) != 0 or num_total!=0):
            writer.writerow([item.user.username , name, str(len(leave)), str(len(absenteeism)) , str(len(late)), str(num_total)])
    return response

def AllWorkArrangeExcel(request):
    response = HttpResponse(mimetype='text/csv')
    response.write('\xEF\xBB\xBF')
    response['Content-Disposition'] = 'attachment; filename=班次安排.csv'
    writer = csv.writer(response)
    workerinfo = WorkerInfo.objects.get(user = request.user)
    num =  workerinfo.department.department_worknum
    worknum = u'班次'
    time = u'时间段'
    mon = u'星期一'
    tue = u'星期二'
    wed = u'星期三'
    thu = u'星期四'
    fri = u'星期五'
    sat = u'星期六'
    sun = u'星期日'
    writer.writerow([ worknum.encode('GBK'), time.encode('GBK'),mon.encode('GBK'),tue.encode('GBK'),wed.encode('GBK'),thu.encode('GBK'),fri.encode('GBK'),sat.encode('GBK'),sun.encode('GBK')])
    for i in range(num):
        schedulelist = Schedule.objects.filter(department = workerinfo.department,workorder = i + 1)
        worknum = str(i)
        for item in schedulelist:
            if(item.day == 1):
                time = str(item.starttime.hour) + ":" + str(item.starttime.minute)+ "--"+str(item.endtime.hour) + ":" + str(item.endtime.minute)
                mon = get_name(item.worker, item.administrator.id)
            elif(item.day == 2):
                tue = get_name(item.worker, item.administrator.id)
            elif(item.day == 3):
                wed = get_name(item.worker, item.administrator.id)
            elif(item.day == 4):
                thu = get_name(item.worker, item.administrator.id)
            elif(item.day == 5):
                fri = get_name(item.worker, item.administrator.id)
            elif(item.day == 6):
                sat = get_name(item.worker, item.administrator.id)
            elif(item.day == 7):
                sun = get_name(item.worker, item.administrator.id)
        writer.writerow([ worknum.encode('GBK'), time.encode('GBK'),mon.encode('GBK'),tue.encode('GBK'),wed.encode('GBK'),thu.encode('GBK'),fri.encode('GBK'),sat.encode('GBK'),sun.encode('GBK')])
    return response

def AllWorkerInfoExcel(request):
    response = HttpResponse(mimetype='text/csv')
    response.write('\xEF\xBB\xBF')
    response['Content-Disposition'] = 'attachment; filename=队员信息.csv'
    writer = csv.writer(response)
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    name = u'姓名'
    id = u'学号'
    email= u'邮箱'
    phonenum = u'电话'
    writer.writerow([ id.encode('GBK'), name.encode('GBK'),email.encode('GBK'),phonenum.encode('GBK')])
    for item in workerlist:
        name = item.name.encode('GBK')
        email = item.user.email.encode('GBK')
        phonenum = item.phone
        writer.writerow([item.user.username , name, email, phonenum])
    return response

def AllInfoExcel(request):
    response = HttpResponse(mimetype='text/csv')
    response.write('\xEF\xBB\xBF')
    response['Content-Disposition'] = 'attachment; filename=队员信息及出勤记录.csv'
    writer = csv.writer(response)
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    name = u'姓名'
    id = u'学号'
    email= u'邮箱'
    phonenum = u'电话'
    leave= u'请假次数'
    absenteeism = u'旷工次数'
    late = u'迟到次数'
    exchange = u'换班次数'
    writer.writerow([ id.encode('GBK'), name.encode('GBK'),email.encode('GBK'),phonenum.encode('GBK'),leave.encode('GBK'),absenteeism.encode('GBK'),late.encode('GBK'),exchange.encode('GBK')])
    for item in workerlist:
        name = item.name.encode('GBK')
        email = item.user.email.encode('GBK')
        phonenum = item.phone
        leave = Leave.objects.filter( state = 1, worker = item.user)
        absenteeism = Absenteeism.objects.filter(worker = item.user)
        late = Late.objects.filter(worker = item.user)
        iexchange = Exchange.objects.filter( state = 1, initiative_worker = item.user)
        pexchange = Exchange.objects.filter( state = 1, passivite_worker = item.user)
        num_total = len(iexchange) +  len(pexchange)
        writer.writerow([item.user.username , name, email, phonenum,  str(len(leave)), str(len(absenteeism)) , str(len(late)), str(num_total)])
    return response

def MyWorkerAttendence(request):
    response = HttpResponse(mimetype='text/csv')
    response.write('\xEF\xBB\xBF')
    response['Content-Disposition'] = 'attachment; filename=负责班次队员出勤记录.csv'
    writer = csv.writer(response)
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    name = u'姓名'
    id = u'学号'
    leave= u'请假次数'
    absenteeism = u'旷工次数'
    late = u'迟到次数'
    exchange = u'换班次数'
    writer.writerow([ id.encode('GBK'), name.encode('GBK'),leave.encode('GBK'),absenteeism.encode('GBK'),late.encode('GBK'),exchange.encode('GBK')])
    for item in workerlist:
        leave = Leave.objects.filter(administrator = request.user, state = 1, worker = item.user)
        absenteeism = Absenteeism.objects.filter(administrator = request.user, worker = item.user)
        late = Late.objects.filter(administrator = request.user, worker = item.user)
        i_ma_exchange = Exchange.objects.filter(iadministrator = request.user, state = 1, initiative_worker = item.user)
        p_ma_exchange = Exchange.objects.filter(padministrator = request.user, state = 1, passivite_worker = item.user)
        num_total = len(i_ma_exchange) + len(p_ma_exchange)
        name = item.name.encode('GBK')
        if(len(leave) != 0 or len(absenteeism) != 0 or len(late) != 0 or num_total!=0):
            writer.writerow([item.user.username , name, str(len(leave)), str(len(absenteeism)) , str(len(late)), str(num_total)])
    return response

def workerwishExcel(request):
    response = HttpResponse(mimetype='text/csv')
    response.write('\xEF\xBB\xBF')
    response['Content-Disposition'] = 'attachment; filename=队员志愿表.csv'
    writer = csv.writer(response)
    workerinfo = WorkerInfo.objects.get(user = request.user)
    num =  workerinfo.department.department_worknum
    worknum = u'班次'
    time = u'时间段'
    mon = u'星期一'
    tue = u'星期二'
    wed = u'星期三'
    thu = u'星期四'
    fri = u'星期五'
    sat = u'星期六'
    sun = u'星期日'
    writer.writerow([ worknum.encode('GBK'), time.encode('GBK'),mon.encode('GBK'),tue.encode('GBK'),wed.encode('GBK'),thu.encode('GBK'),fri.encode('GBK'),sat.encode('GBK'),sun.encode('GBK')])
    for i in range(num):
        schedulelist = Schedule.objects.filter(department = workerinfo.department,workorder = i + 1)
        worknum = str(i)
        for item in schedulelist:
            choose = ScheduleChoose.objects.get(schedule = item)
            if(item.day == 1):
                time = str(item.starttime.hour) + ":" + str(item.starttime.minute)+ "--"+str(item.endtime.hour) + ":" + str(item.endtime.minute)
                mon = get_wishname(choose.chooseworker)
            elif(item.day == 2):
                tue = get_wishname(choose.chooseworker)
            elif(item.day == 3):
                wed = get_wishname(choose.chooseworker)
            elif(item.day == 4):
                thu = get_wishname(choose.chooseworker)
            elif(item.day == 5):
                fri = get_wishname(choose.chooseworker)
            elif(item.day == 6):
                sat = get_wishname(choose.chooseworker)
            elif(item.day == 7):
                sun = get_wishname(choose.chooseworker)
        writer.writerow([ worknum.encode('GBK'), time.encode('GBK'),mon.encode('GBK'),tue.encode('GBK'),wed.encode('GBK'),thu.encode('GBK'),fri.encode('GBK'),sat.encode('GBK'),sun.encode('GBK')])
    return response

def workwishnumExcel(request):
    response = HttpResponse(mimetype='text/csv')
    response.write('\xEF\xBB\xBF')
    response['Content-Disposition'] = 'attachment; filename=队员志愿班次数量表.csv'
    writer = csv.writer(response)
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    name = u'姓名'
    id = u'学号'
    email= u'最少班次'
    phonenum = u'最多班次'
    writer.writerow([ id.encode('GBK'), name.encode('GBK'),email.encode('GBK'),phonenum.encode('GBK')])
    for item in workerlist:
        name = item.name.encode('GBK')
        choose =  WorkerChoose.objects.filter(worker = item)
        if(len(choose) > 0 ):
            choose = WorkerChoose.objects.get(worker = item)
            min_num = choose.min_worknum
            max_num = choose.max_worknum
            writer.writerow([item.user.username , name, min_num, max_num])
    return response
