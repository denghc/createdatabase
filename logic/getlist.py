__author__ = 'denghc'
#-*- coding: UTF-8 -*-
from datetime import datetime
from django.core.urlresolvers import reverse
from RegisterSystem.logic.models import *
from django.contrib.auth.models import User
import time
import os,uuid,ImageFile,Image
from RegisterSystem.settings import MEDIA_ROOT, USERPHOTO_ABS_PATH, USERPHOTO_VIR_PATH
import datetime

def get_name(workerstr, add_id):
    result = u''
    id = u''
    ifadd = 0
    for str in workerstr:
        if (ifadd == 1):
            if (str == '.'):
                ifadd = 0
                workerinfo = WorkerInfo.objects.filter(user = int(id))
                if(len(workerinfo) == 1):
                    if int(id) == int(add_id):
                            result += WorkerInfo.objects.get(user = int(id)).name
                            result += u'（负责人）'
                    else:
                            result += WorkerInfo.objects.get(user = int(id)).name
                    result += " , "
            else:
                id += str
        else:
            if(str == ','):
                ifadd = 1
                id = u''
    return result

def get_wishname(workerstr):
    result = u''
    id = u''
    ifadd = 0
    if workerstr != None:
        for str in workerstr:
            if (ifadd == 1):
                if (str == '.'):
                    ifadd = 0
                    workerinfo = WorkerInfo.objects.filter(user = int(id))
                    if(len(workerinfo) == 1):
                        result += WorkerInfo.objects.get(user = int(id)).name
                        result += " , "
                else:
                    id += str
            else:
                if(str == ','):
                    ifadd = 1
                    id = u''
    return result

def get_wishlist( id, wishlist):
    if not wishlist:
        return ''
    result = u''
    iffirst = 1
    for item in wishlist:
        dutytime =  "(" + str(item.starttime.hour) + ":" + str(item.starttime.minute)\
                    + "--" + str(item.endtime.hour) + ":" + str(item.endtime.minute) + ")"
        chooseworker = ScheduleChoose.objects.get(schedule = item).chooseworker
        workerstr = u''+ ","+str(id)+ "."
        num = chooseworker.find(workerstr)
        if(iffirst == 1):
            if num > 0:
                result += u'<tr><td class="banci"><li>班次%s</li><li>%s</li></td><td class="myduties"><li>' \
                        u' <input type="checkbox" name="dutylist" id="dutylist" checked = true value = "%s"' \
                        u' onclick="(this.checked)?b.value=b.value+ \'%s,\':b.value=b.value.replace(\'%s,\',\'\')"/>' \
                        u'</li></td>'% (item.workorder, dutytime, item.workorder, item.id , item.id)
            else:
                result += u'<tr><td class="banci"><li>班次%s</li><li>%s</li></td><td class="myduties"><li>'\
                          u' <input type="checkbox" name="dutylist" id="dutylist" value = "%s"' \
                          u' onclick="(this.checked)?b.value=b.value+ \'%s,\':b.value=b.value.replace(\'%s,\',\'\')"/>' \
                          u'</li></td>'% (item.workorder, dutytime,  item.workorder, item.id ,  item.id )
            iffirst = 0
        else:
            if num > 0:
                result += u'<td class="myduties"><li><input type="checkbox" name="dutylist" id="dutylist" checked = true value = "%s" ' \
                          u'onclick="(this.checked)?b.value=b.value+\'%s,\':b.value=b.value.replace(\'%s,\',\'\')" />' \
                          u'</li></td>'% ( item.workorder, item.id ,  item.id)
            else:
                result +=u'<td class="myduties"><li><input type="checkbox" name="dutylist" id="dutylist" value ="%s" ' \
                         u'onclick="(this.checked)?b.value=b.value+\'%s,\':b.value=b.value.replace(\'%s,\',\'\')"/>' \
                         u'</li></td>'% ( item.workorder, item.id ,   item.id )

    result += u'</tr>'
    return result

def get_dutylist( id, dutylist):
    if not dutylist:
        return ''
    result = u''
    iffirst = 1
    for item in dutylist:
        dutytime =  "(" + str(item.starttime.hour) + ":" + str(item.starttime.minute)\
                    + "--" + str(item.endtime.hour) + ":" + str(item.endtime.minute) + ")"
        workerstr = u''+ ","+str(id)+ "."
        num = item.attendance.find(workerstr)
        if(iffirst == 1):
            result += u'<tr><td class="banci"><li>班次%s</li><li>%s</li>' \
                      u'</td>'% (item.workorder, dutytime)
            if num > 0 :
                result += u'<td class="myduties"><li>%s</li><li>' \
                      u'</li></td>' % (get_name(item.attendance, item.administrator.id))
            else:
                result += u'<td><li>%s</li><li></li>'\
                          u'</td>'% (get_name(item.attendance, item.administrator.id))
            iffirst = 0
        else:
            if num > 0:
                result += u'<td class="myduties"><li>%s</li><li>'\
                          u'</li></td>' % (get_name(item.attendance, item.administrator.id))
            else:
                result += u'<td><li>%s</li><li></li>'\
                          u'</td>'% (get_name(item.attendance, item.administrator.id))
    result += u'</tr>'
    return result

def get_officerdutylist( id, dutylist):
    if not dutylist:
        return ''
    result = u''
    iffirst = 1
    for item in dutylist:
        starttime =  str(item.starttime.hour) + ":" + str(item.starttime.minute)
        endtime =   str(item.endtime.hour) + ":" + str(item.endtime.minute)
        workerstr = u''+ ","+str(id)+ "."
        num = item.attendance.find(workerstr)
        if(iffirst == 1):
            result += u'<tr><td class="banci"><form name="dutytime%s" method="post" action="" id= "dutytime%s" onsubmit="return false;"><div><li>班次%s</li><li><input type="text" name="sedule_order" style="display: none" value="%s" >上班时间：<input type="text" name="starttime"  style="max-width: 60px" value="%s"  >'\
                      u'下班时间：<input type="text" name="endtime" style="max-width: 60px" value="%s" ></li>' \
                      u'<li><input name="change" type="submit" class="change" value="提交"  onclick="changetime(%s);"/>' \
                      u'<label id="msg%s" style="color: red;"></label></li></div></form></td>'% (item.workorder, item.workorder, item.workorder,item.workorder,starttime,  endtime , item.workorder, item.workorder)
            if num > 0 :
                result += u'<td class="myduties"><li><a href="javascript:void(0);" onclick="javascript:resetsedule(%s)">设置</a></li><li>'\
                          u'%s</li></td>' % ( item.id, get_name(item.attendance, item.administrator.id))
            else:
                result += u'<td><li><a href="javascript:void(0);" onclick="javascript:resetsedule(%s)">设置</a></li><li>'\
                          u'%s</li></td>' % ( item.id, get_name(item.attendance, item.administrator.id))
            iffirst = 0
        else:
            if num > 0:
                result += u'<td class="myduties"><li><a href="javascript:void(0);" onclick="javascript:resetsedule(%s)">设置</a></li><li>'\
                          u'%s</li></td>' % ( item.id, get_name(item.attendance, item.administrator.id))
            else:
                result += u'<td><li><a href="javascript:void(0);" onclick="javascript:resetsedule(%s)">设置</a></li><li>'\
                          u'%s</li></td>' % ( item.id, get_name(item.attendance, item.administrator.id))
    result += u'</tr>'
    return result

def get_wishresultlist(dutylist):
    result = u''
    iffirst = 1
    for item in dutylist:
        wishresult  = ScheduleChoose.objects.get(schedule = item)
        if(iffirst == 1):
            result += u'<tr><td class="banci"><form name="dutytime%s" method="post" action="" id= "dutytime%s" onsubmit="return false;"><div><li>班次%s</li>' \
                      u'<li><input type="text" name="sedule_order" style="display: none" value="%s" >' \
                      u'最少人数：<input type="text" name="minnum"  style="max-width: 60px" value="%s"  >'\
                      u'最多人数：<input type="text" name="maxnum" style="max-width: 60px" value="%s" ></li>'\
                      u'<li><input name="change" type="submit" class="change" value="提交"  onclick="changeworkernum(%s);"/>'\
                      u'<label id="msg%s" style="color: red;"></label></li></div></form></td>'% (item.workorder, item.workorder, item.workorder,item.workorder, str(wishresult.minworkernum),  str(wishresult.maxworkernum),item.workorder,item.workorder )
            result += u'<td><li><a href="javascript:void(0);" onclick="javascript:resetchoosewish(%s)">设置</a></li><li>'\
                     u'%s</li></td>' % ( wishresult.id, get_wishname(wishresult.resultworker))
            iffirst = 0
        else:
             result += u'<td><li><a href="javascript:void(0);" onclick="javascript:resetchoosewish(%s)">设置</a></li><li>'\
                          u'%s</li></td>' % ( wishresult.id, get_wishname(wishresult.resultworker))
    result += u'</tr>'
    return result

def get_officerwishlist(  dutylist):
    result = u''
    iffirst = 1
    for item in dutylist:
        chooose = ScheduleChoose.objects.get(schedule = item)
        starttime =  str(item.starttime.hour) + ":" + str(item.starttime.minute)
        endtime =   str(item.endtime.hour) + ":" + str(item.endtime.minute)
        if(iffirst == 1):
            result += u'<tr><td class="banci"><form name="dutytime%s" method="post" action="" id= "dutytime%s" onsubmit="return false;"><div><li>班次%s</li><li><input type="text" name="sedule_order" style="display: none" value="%s" >上班时间：<input type="text" name="starttime"  style="max-width: 60px" value="%s"  >'\
                      u'下班时间：<input type="text" name="endtime" style="max-width: 60px" value="%s" ></li>' \
                      u'</div></form></td>'% (item.workorder, item.workorder, item.workorder,item.workorder,starttime,  endtime )
            result += u'<td><li>%s</li></td>' % ( get_wishname(chooose.chooseworker))
            iffirst = 0
        else:
            result += u'<td><li>%s</li></td>' % (get_wishname(chooose.chooseworker))
    result += u'</tr>'
    return result

def get_numlist( workerlist):
    result = u''
    for item in workerlist:
        choose =  WorkerChoose.objects.filter(worker = item)
        if(len(choose) > 0 ):
            choose = WorkerChoose.objects.get(worker = item)
            result += u'<tr><td>%s</td><td>%s</td><td>%s</td>' \
                      u'<td>%s</td>' % (item.user.username, item.name, choose.min_worknum, choose.max_worknum)
            result += u'</tr>'
    return result

def get_Newleavelist(leave):
    if not leave:
        return ''
    else:
        result = u''
        Now_state = u''
        for item in leave:
            if (item.time.date() >= datetime.date.today()):
                if item.state == 0:
                    Now_state = u'尚未回复'
                if item.state == 1:
                    Now_state = u'已同意'
                if item.state == -1:
                    Now_state = u'已拒绝'
                result += u'<tr class="att_number"><td class="time_wh">%s</td>' \
                          u'<td class="duty_wh">班次%s</td><td class="reason_wh3">%s	</td>' \
                          u'<td class="status_yes">%s</td><td class="duty_reply">%s</td>' \
                          u'<td class="reply_button"><input name="revoke" type="submit" class="revoke" value="撤销请假" onclick="deleateleave(%s);" />' \
                          u'</tr>' %(item.time.date(),item.workorder,item.reason,Now_state, item.replyreason, "'"+ str(item.id) + "'" )
    return  result

def get_Newexchangelist(exchange):
    if not exchange:
        return ''
    else:
        result = u''
        Now_state = u''
        for item in exchange:
            if (item.itime.date() >= datetime.date.today() ):
                if(item.ptime.date() >= datetime.date.today()):
                    if item.state == 0:
                        Now_state = u'尚未回复'
                    if item.state == 1:
                        Now_state = u'已同意'
                    if item.state == -1:
                        Now_state = u'已拒绝'
                    pname = WorkerInfo.objects.get(user = item.passivite_worker).name
                    result += u'<tr class="att_number"><td class="time_wh">%s</td><td class="time_wh">%s</td>' \
                              u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>' \
                              u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>' \
                              u'<td class="duty_wh">%s</td><td class="reason_wh4">%s</td>' \
                              u'<td class="status_yes">%s</td><td class="duty_reply1">%s</td>' \
                              u'<td class="reply_button"><input name="revoke" type="submit" class="revoke" value="撤销换班" onclick="deleateexchange(%s);"  />' \
                              u'</tr>' %(item.itime.date(),item.ptime.date() , item.iday, item.iorder, item.pday, item.porder,pname , item.ireason, Now_state, item.preason, "'"+ str(item.id) + "'")
    return  result

def gettotal_managerrecord(request):
    result = u'<hr align="left" width="750" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">历史记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table5" >'\
             u'<tr class="att_name"><td class="time_wh">学号</td><td class="time_wh">姓名</td>'\
             u'<td class="time_wh">请假记录</td><td class="time_wh">旷工记录</td><td class="time_wh">迟到记录</td><td class="time_wh">' \
             u'换班记录</td><td class="time_wh">工时记录</td><td class="time_wh">早退记录</td><td class="time_wh">加班记录</td></tr>'
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    for item in workerlist:
        early = Early.objects.filter(administrator = request.user, worker = item.user)
        overtime = Overtime.objects.filter(administrator = request.user, worker = item.user)
        overhourtotal = 0.0
        earlyhourtotal = 0.0
        for over in overtime:
            overhourtotal += over.hournum
        for ear in early:
            earlyhourtotal += ear.hournum
        leave = Leave.objects.filter(administrator = request.user, state = 1, worker = item.user)
        absenteeism = Absenteeism.objects.filter(administrator = request.user , worker = item.user)
        late = Late.objects.filter(administrator = request.user, worker = item.user)
        i_iexchange = Exchange.objects.filter(iadministrator = request.user, state = 1, initiative_worker = item.user)
        p_iexchange = Exchange.objects.filter(padministrator = request.user, state = 1,  initiative_worker = item.user)
        i_pexchange = Exchange.objects.filter(iadministrator = request.user, state = 1, passivite_worker = item.user)
        p_pexchange = Exchange.objects.filter(padministrator = request.user, state = 1,  passivite_worker = item.user)
        num_total = len(i_iexchange) + len(p_iexchange) + len(i_pexchange) + len(p_pexchange)
        work = Work.objects.filter( worker = item.user)
        if(len(leave) != 0 or len(absenteeism) != 0 or len(late) != 0 or num_total!=0 or len(work)!=0 or len(early) != 0 or len(overtime) != 0):
            result += u'<tr class="att_number"><td class="time_wh">%s</td><td class="time_wh">%s</td>'%(item.user.username,item.name)
            if(len(leave) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_specificleave(%s , %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , request.user.id , len(leave))
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%(len(leave))
            if(len(absenteeism) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_specificabsenteeism(%s , %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , request.user.id , len(absenteeism))
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%(len(absenteeism))
            if(len(late) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_specificlate(%s , %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , request.user.id ,  len(late))
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( len(late))
            if(num_total != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_specificexchange(%s , %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , request.user.id ,  num_total)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( num_total)
            if(len(work) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_specificwork(%s , %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , request.user.id ,  len(work))
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( len(work))
            if(len(early) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_specificearly(%s , %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , request.user.id ,  earlyhourtotal)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( earlyhourtotal)
            if(len(overtime) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_specificovertime(%s , %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , request.user.id ,  overhourtotal)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( overhourtotal)

    result += u'</table></div>'
    return result

def get_startdate(startweek):
    if(startweek == 1):
        a = '2012-9-10'
    elif(startweek==2):
        a = '2012-9-17'
    elif(startweek==3):
        a = '2012-9-24'
    elif(startweek==4):
        a = '2012-10-1'
    elif(startweek==5):
        a = '2012-10-8'
    elif(startweek==6):
        a = '2012-10-15'
    elif(startweek==7):
        a = '2012-10-22'
    elif(startweek==8):
        a = '2012-10-29'
    elif(startweek==9):
        a = '2012-11-5'
    elif(startweek==10):
        a = '2012-11-12'
    elif(startweek==11):
        a = '2012-11-19'
    elif(startweek==12):
        a = '2012-11-26'
    elif(startweek==13):
        a = '2012-12-3'
    elif(startweek==14):
        a = '2012-12-10'
    elif(startweek==15):
        a = '2012-12-17'
    elif(startweek==16):
        a = '2012-12-24'
    elif(startweek==17):
        a = '2012-12-31'
    elif(startweek==18):
        a = '2013-1-7'
    b = datetime.datetime.strptime(a,'%Y-%m-%d')
    return b

def get_enddate(endweek):
    if(endweek == 1):
        a = '2012-9-16'
    elif(endweek==2):
        a = '2012-9-23'
    elif(endweek==3):
        a = '2012-9-30'
    elif(endweek==4):
        a = '2012-10-7'
    elif(endweek==5):
        a = '2012-10-14'
    elif(endweek==6):
        a = '2012-10-21'
    elif(endweek==7):
        a = '2012-10-28'
    elif(endweek==8):
        a = '2012-10-4'
    elif(endweek==9):
        a = '2012-11-11'
    elif(endweek==10):
        a = '2012-11-18'
    elif(endweek==11):
        a = '2012-11-25'
    elif(endweek==12):
        a = '2012-11-2'
    elif(endweek==13):
        a = '2012-12-9'
    elif(endweek==14):
        a = '2012-12-16'
    elif(endweek==15):
        a = '2012-12-23'
    elif(endweek==16):
        a = '2012-12-30'
    elif(endweek==17):
        a = '2012-12-6'
    elif(endweek==18):
        a = '2013-1-13'
    b = datetime.datetime.strptime(a,'%Y-%m-%d')
    return b

def gettotal_searchrecord(request, startweek, endweek):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">历史记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table5" >'\
             u'<tr class="att_name"><td class="time_wh">学号</td><td class="time_wh">姓名</td>'\
             u'<td class="time_wh">请假记录</td><td class="time_wh">旷工记录</td><td class="time_wh">迟到记录</td>'\
             u'<td class="time_wh">换班记录</td><td class="time_wh">工时记录</td><td class="time_wh">早退记录</td><td class="time_wh">加班记录</td></tr>'
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    startdate = get_startdate(startweek).date()
    enddate= get_enddate(endweek).date()
    for item in workerlist:
        early = Early.objects.filter(worker = item.user )
        overtime = Overtime.objects.filter(worker = item.user)
        overhourtotal = 0.0
        earlyhourtotal = 0.0
        for over in overtime:
            if(over.time.date()>=startdate and over.time.date()<=enddate):
                overhourtotal += over.hournum
        for ear in early:
            if(ear.time.date()>=startdate and ear.time.date()<=enddate):
                earlyhourtotal += ear.hournum
        leave = Leave.objects.filter( state = 1, worker = item.user)
        absenteeism = Absenteeism.objects.filter(worker = item.user)
        late = Late.objects.filter(worker = item.user)
        iexchange = Exchange.objects.filter( state = 1, initiative_worker = item.user)
        pexchange = Exchange.objects.filter( state = 1, passivite_worker = item.user)
        work = Work.objects.filter(worker = item.user)
        num_work = 0
        num_leave =0
        num_late = 0
        num_absenteeism = 0
        num_iexchange = 0
        num_pexchange = 0
        for lea in leave:
            if(lea.time.date()>=startdate and lea.time.date()<=enddate):
                num_leave += 1
        for la in late:
            if(la.time.date()>=startdate and la.time.date()<=enddate):
                num_late += 1
        for wo in work:
            if(wo.time.date()>=startdate and wo.time.date()<=enddate):
                num_work += 1
        for ab in absenteeism:
            if(ab.time.date()>=startdate and ab.time.date()<=enddate):
                num_absenteeism += 1
        for ie in iexchange:
            if(ie.itime.date()>=startdate and ie.itime.date()<=enddate):
                num_iexchange += 1
        for pe in pexchange:
            if(pe.ptime.date()>=startdate and pe.ptime.date()<=enddate):
                num_pexchange += 1
        num_total = num_iexchange + num_pexchange
        if(num_leave != 0 or num_absenteeism != 0 or num_late != 0 or num_total!=0 or num_work != 0  or num_work != 0 or overhourtotal != 0 or earlyhourtotal != 0):
            result += u'<tr class="att_number"><td class="time_wh">%s</td><td class="time_wh">%s</td>'%(item.user.username,item.name)
            if(num_leave != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_search_leave(%s, %s, %s )" '\
                          u'style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , startweek, endweek , num_leave)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%(num_leave)
            if(num_absenteeism != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_search_absenteeism(%s, %s, %s)" '\
                          u'style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , startweek, endweek ,  num_absenteeism)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%(num_absenteeism)
            if(num_late != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_search_late(%s, %s, %s )" '\
                          u'style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id ,   startweek, endweek , num_late)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( num_late)
            if(num_total != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_search_exchange(%s, %s, %s)" '\
                          u'style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , startweek, endweek ,  num_total)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( num_total)
            if(num_work != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_search_work(%s, %s, %s)" '\
                          u'style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id ,  startweek, endweek , num_work)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( num_work)
            if(earlyhourtotal != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_search_early(%s , %s, %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id ,  startweek, endweek , earlyhourtotal)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( earlyhourtotal)
            if(overhourtotal != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_search_overtime(%s , %s, %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id ,  startweek, endweek , overhourtotal)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( overhourtotal)
    result += u'</table></div>'
    return result

def gettotal_officerrecord(request):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">历史记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table5" >'\
             u'<tr class="att_name"><td class="time_wh">学号</td><td class="time_wh">姓名</td>'\
             u'<td class="time_wh">请假记录</td><td class="time_wh">旷工记录</td><td class="time_wh">迟到记录</td>' \
             u'<td class="time_wh">换班记录</td><td class="time_wh">工时记录</td><td class="time_wh">早退记录</td><td class="time_wh">加班记录</td></tr>'
    workerinfo = WorkerInfo.objects.get(user = request.user)
    workerlist = WorkerInfo.objects.filter(department = workerinfo.department)
    for item in workerlist:
        early = Early.objects.filter(worker = item.user)
        overtime = Overtime.objects.filter(worker = item.user)
        overhourtotal = 0.0
        earlyhourtotal = 0.0
        for over in overtime:
            overhourtotal += over.hournum
        for ear in early:
            earlyhourtotal += ear.hournum
        leave = Leave.objects.filter( state = 1, worker = item.user)
        absenteeism = Absenteeism.objects.filter(worker = item.user)
        late = Late.objects.filter(worker = item.user)
        iexchange = Exchange.objects.filter( state = 1, initiative_worker = item.user)
        pexchange = Exchange.objects.filter( state = 1, passivite_worker = item.user)
        num_total = len(iexchange) +  len(pexchange)
        work = Work.objects.filter(worker = item.user)
        if(len(leave) != 0 or len(absenteeism) != 0 or len(late) != 0 or num_total!=0 or len(work) != 0  or len(early) != 0 or len(overtime) != 0):
            result += u'<tr class="att_number"><td class="time_wh">%s</td><td class="time_wh">%s</td>'%(item.user.username,item.name)
            if(len(leave) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_officer_specific_leave(%s )" ' \
                          u'style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id  , len(leave))
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%(len(leave))
            if(len(absenteeism) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_officer_specific_absenteeism(%s)" ' \
                          u'style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id ,  len(absenteeism))
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%(len(absenteeism))
            if(len(late) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_officer_specific_late(%s )" ' \
                          u'style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id ,   len(late))
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( len(late))
            if(num_total != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_officer_specific_exchange(%s)" ' \
                          u'style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id ,  num_total)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( num_total)
            if(len(work) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_officer_specific_work(%s )" '\
                          u'style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id ,   len(work))
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( len(work))
            if(len(early) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_officer_specific_early(%s , %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , request.user.id ,  earlyhourtotal)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( earlyhourtotal)
            if(len(overtime) != 0):
                result += u'<td class="time_wh"><a href="javascript:void(0);" onclick="open_officer_specific_overtime(%s , %s)" style="text-decoration: none" target="_blank" >%s</a></td>' %(item.user_id , request.user.id , overhourtotal)
            else:
                result +=  u'<td class="time_wh">%s</a></td>'%( overhourtotal)
    result += u'</table></div>'
    return result

def get_exchangelist(request,exchangelist , num):
    if(num == 0):
        result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/>' \
                 u' <div id="qingjia_list"><div class="window_title">换班记录</div><div class="clear_float"></div>' \
                 u'<table width="727" border="0" align="left" cellspacing="1" id="table6" ><tr class="att_name">' \
                 u'<td class="code_wh">编号</td><td class="time_wh">我的时间</td>' \
                 u'<td class="time_wh">对方时间</td><td class="duty_wh">我的班次</td>' \
                 u'<td class="duty_wh">对方班次</td><td class="duty_wh">对方姓名</td>' \
                 u'<td class="reason_wh1">换班原因</td><td class="reason_wh1">换班回复</td></tr>'
        iffirst = 1
    else:
        result = u''
        iffirst = 0
    sum = num
    for item in exchangelist:
        sum += 1
        iname = WorkerInfo.objects.get(user = item.initiative_worker).name
        pname = WorkerInfo.objects.get(user = item.passivite_worker).name
        if (item.initiative_worker == request.user):
            result += u'<tr class="att_number"><td class="code_wh"> %s</td>' \
                      u'<td class="time_wh">%s</td><td class="time_wh">%s</td>' \
                      u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>' \
                      u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>' \
                      u'<td class="duty_wh">%s</td><td class="reason_wh1">%s</td>' \
                      u'<td class="reason_wh1">%s</td></tr>'%(sum ,item.itime.date(), item.ptime.date(),
                      item.iday,item.iorder,item.pday, item.porder, pname,"(" +iname + ") :" + item.ireason, "("+pname + ") :" +item.preason)
        else:
            result += u'<tr class="att_number"><td class="code_wh"> %s</td>'\
                      u'<td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                      u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>'\
                      u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>'\
                      u'<td class="duty_wh">%s</td><td class="reason_wh1">%s</td>'\
                      u'<td class="reason_wh1">%s</td></tr>'%(sum , item.ptime.date(), item.itime.date(),
                      item.pday,item.porder,item.iday, item.iorder, iname,"(" +iname + "):" + item.ireason, "("+pname + ") :"+item.preason)
    if iffirst == 0:
        result += u'</table></div>'
    return result

def get_latelist(request, latelist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> ' \
             u'<div id="qingjia_list"><div class="window_title">迟到记录</div><div class="clear_float"></div>' \
             u'<table width="300" border="0" align="left" cellspacing="1" id="table5" >' \
             u'<tr class="att_name"><td class="code_wh">编号</td><td class="time_wh">迟到时间</td>' \
             u'<td class="time_wh">迟到班次</td><td class="reason_wh1">迟到原因</td></tr>'
    sum = 0
    for item in latelist:
        sum += 1
        result += u'<tr class="att_number"><td class="code_wh">%s</td>' \
                  u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>' \
                  u'<td class="reason_wh1">%s</td></tr>'%(sum , item.time.date(), item.day, item.workorder,item.reason)
    result += u'</table></div>'
    return result

def get_worklist(request, worklist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">工时记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table5" >'\
             u'<tr class="att_name"><td class="code_wh">编号</td><td class="time_wh">上班时间</td>'\
             u'<td class="time_wh">上班班次</td><td class="reason_wh1">附加说明</td></tr>'
    sum = 0
    for item in worklist:
        sum += 1
        result += u'<tr class="att_number"><td class="code_wh">%s</td>'\
                  u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                  u'<td class="reason_wh1">%s</td></tr>'%(sum , item.time.date(), item.day, item.workorder,item.reason)
    result += u'</table></div>'
    return result

def get_earlylist(request, earlylist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">早退记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table5" >'\
             u'<tr class="att_name"><td class="code_wh">工时/小时</td><td class="time_wh">上班时间</td>'\
             u'<td class="time_wh">上班班次</td><td class="reason_wh1">附加说明</td></tr>'
    for item in earlylist:
        result += u'<tr class="att_number"><td class="code_wh">%s</td>'\
                  u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                  u'<td class="reason_wh1">%s</td></tr>'%(item.hournum , item.time.date(), item.day, item.workorder,item.reason)
    result += u'</table></div>'
    return result

def get_overtimelist(request, overtimelist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">加班记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table5" >'\
             u'<tr class="att_name"><td class="code_wh">工时/小时</td><td class="time_wh">上班时间</td>'\
             u'<td class="time_wh">上班班次</td><td class="reason_wh1">附加说明</td></tr>'
    for item in overtimelist:
        result += u'<tr class="att_number"><td class="code_wh">%s</td>'\
                  u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                  u'<td class="reason_wh1">%s</td></tr>'%(item.hournum , item.time.date(), item.day, item.workorder,item.reason)
    result += u'</table></div>'
    return result

def get_search_exchangelist(request,exchangelist , num, startweek, endweek):
    if(num == 0):
        result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/>'\
                 u' <div id="qingjia_list"><div class="window_title">换班记录</div><div class="clear_float"></div>'\
                 u'<table width="727" border="0" align="left" cellspacing="1" id="table6" ><tr class="att_name">'\
                 u'<td class="code_wh">编号</td><td class="time_wh">我的时间</td>'\
                 u'<td class="time_wh">对方时间</td><td class="duty_wh">我的班次</td>'\
                 u'<td class="duty_wh">对方班次</td><td class="duty_wh">对方姓名</td>'\
                 u'<td class="reason_wh1">换班原因</td><td class="reason_wh1">换班回复</td></tr>'
        iffirst = 1
    else:
        result = u''
        iffirst = 0
    sum = num
    startdate = get_startdate(startweek).date()
    enddate= get_enddate(endweek).date()
    for item in exchangelist:
        iname = WorkerInfo.objects.get(user = item.initiative_worker).name
        pname = WorkerInfo.objects.get(user = item.passivite_worker).name
        if (item.initiative_worker == request.user):
            if(item.itime.date()>=startdate and item.itime.date()<=enddate):
                sum += 1
                result += u'<tr class="att_number"><td class="code_wh"> %s</td>'\
                          u'<td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                          u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>'\
                          u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>'\
                          u'<td class="duty_wh">%s</td><td class="reason_wh1">%s</td>'\
                          u'<td class="reason_wh1">%s</td></tr>'%(sum ,item.itime.date(), item.ptime.date(),
                                                                  item.iday,item.iorder,item.pday, item.porder, pname,"(" +iname + ") :" + item.ireason, "("+pname + ") :" +item.preason)
        else:
            if(item.ptime.date()>=startdate and item.ptime.date()<=enddate):
                sum += 1
                result += u'<tr class="att_number"><td class="code_wh"> %s</td>'\
                          u'<td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                          u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>'\
                          u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>'\
                          u'<td class="duty_wh">%s</td><td class="reason_wh1">%s</td>'\
                          u'<td class="reason_wh1">%s</td></tr>'%(sum , item.ptime.date(), item.itime.date(),
                                                                  item.pday,item.porder,item.iday, item.iorder, iname,"(" +iname + "):" + item.ireason, "("+pname + ") :"+item.preason)
    if iffirst == 0:
        result += u'</table></div>'
    return result

def get_search_latelist(request, latelist, startweek, endweek ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">迟到记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table3" >'\
             u'<tr class="att_name"><td class="code_wh">编号</td><td class="time_wh">学号</td><td class="time_wh">姓名</td><td class="time_wh">迟到时间</td>'\
             u'<td class="time_wh">迟到班次</td><td class="reason_wh1">迟到原因</td><td class="time_wh">删除操作</td></tr>'
    sum = 0
    startdate = get_startdate(startweek).date()
    enddate= get_enddate(endweek).date()
    for item in latelist:
        if(item.time.date()>=startdate and item.time.date()<=enddate):
            sum += 1
            workerinfo = WorkerInfo.objects.get(user = item.worker)
            result += u'<tr class="att_number"><td class="code_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                      u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                      u'<form name="updatelate%s" method="post" action="" id= "updatelate%s" onsubmit="return false;"><td class="reason_wh1">'\
                      u'<input type="text" name="late_id" style="display: none" value="%s" >'\
                      u'<input type="text" name="reason_content" maxlength="20" value="%s" id="cardid" class="text-input">'\
                      u'<input type="submit" value="提交" onclick="updatelate(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                      u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleatelate(%s)"  />'\
                      u'</td></tr>'%(sum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workorder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result

def get_search_worklist(request, worklist, startweek, endweek ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">工时记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table3" >'\
             u'<tr class="att_name"><td class="code_wh">编号</td><td class="time_wh">学号</td><td class="time_wh">姓名</td><td class="time_wh">上班时间</td>'\
             u'<td class="time_wh">上班班次</td><td class="reason_wh1">附加说明</td><td class="time_wh">删除操作</td></tr>'
    sum = 0
    startdate = get_startdate(startweek).date()
    enddate= get_enddate(endweek).date()
    for item in worklist:
        if(item.time.date()>=startdate and item.time.date()<=enddate):
            sum += 1
            workerinfo = WorkerInfo.objects.get(user = item.worker)
            result += u'<tr class="att_number"><td class="code_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                      u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                      u'<form name="updatelate%s" method="post" action="" id= "updatelate%s" onsubmit="return false;"><td class="reason_wh1">'\
                      u'<input type="text" name="late_id" style="display: none" value="%s" >'\
                      u'<input type="text" name="reason_content" maxlength="20" value="%s" id="cardid" class="text-input">'\
                      u'<input type="submit" value="提交" onclick="updatelate(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                      u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleatework(%s)"  />'\
                      u'</td></tr>'%(sum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workorder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result

def get_search_earlylist(request, earlylist, startweek, endweek ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">早退记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table3" >'\
             u'<tr class="att_number"><td class="time_wh">工时/小时</td><td class="time_wh">学号</td><td class="time_wh">姓名</td><td class="time_wh">上班时间</td>'\
             u'<td class="time_wh">上班班次</td><td class="reason_wh1">附加说明</td><td class="time_wh">删除操作</td></tr>'
    startdate = get_startdate(startweek).date()
    enddate= get_enddate(endweek).date()
    for item in earlylist:
        if(item.time.date()>=startdate and item.time.date()<=enddate):
            workerinfo = WorkerInfo.objects.get(user = item.worker)
            result += u'<tr class="att_number"><td class="time_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                      u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                      u'<form name="updatelate%s" method="post" action="" id= "updatelate%s" onsubmit="return false;"><td class="reason_wh1">'\
                      u'<input type="text" name="late_id" style="display: none" value="%s" >'\
                      u'<input type="text" name="reason_content" maxlength="20" value="%s" id="cardid" class="text-input">'\
                      u'<input type="submit" value="提交" onclick="updatelate(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                      u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleateearly(%s)"  />'\
                      u'</td></tr>'%(item.hournum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workorder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result

def get_search_overtimelist(request, overtimelist , startweek, endweek):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">加班记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table3" >'\
             u'<tr class="att_number"><td class="time_wh">工时/小时</td><td class="time_wh">学号</td><td class="time_wh">姓名</td><td class="time_wh">上班时间</td>'\
             u'<td class="time_wh">上班班次</td><td class="reason_wh1">附加说明</td><td class="time_wh">删除操作</td></tr>'
    startdate = get_startdate(startweek).date()
    enddate= get_enddate(endweek).date()
    for item in overtimelist:
        if(item.time.date()>=startdate and item.time.date()<=enddate):
            workerinfo = WorkerInfo.objects.get(user = item.worker)
            result += u'<tr class="att_number"><td class="time_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                      u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                      u'<form name="updatelate%s" method="post" action="" id= "updatelate%s" onsubmit="return false;"><td class="reason_wh1">'\
                      u'<input type="text" name="late_id" style="display: none" value="%s" >'\
                      u'<input type="text" name="reason_content" maxlength="20" value="%s" id="cardid" class="text-input">'\
                      u'<input type="submit" value="提交" onclick="updatelate(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                      u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleateovertime(%s)"  />'\
                      u'</td></tr>'%(item.hournum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workorder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
        result += u'</table></div>'
    return result

def get_search_leavelist(request,leavelist  , startweek, endweek):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">请假记录</div><div class="clear_float">'\
             u'</div><table width="300" border="0" align="left" cellspacing="1" id="table3" >'\
             u'<tr class="att_name"><td class="code_wh">编号</td><td class="time_wh">学号</td><td class="time_wh">姓名</td>'\
             u'<td class="time_wh">请假时间</td><td class="time_wh">请假班次</td>'\
             u'<td class="reason_wh">请假原因</td><td class="time_wh">删除操作</td></tr>'
    sum = 0
    startdate = get_startdate(startweek).date()
    enddate= get_enddate(endweek).date()
    for item in leavelist:
        if(item.time.date()>=startdate and item.time.date()<=enddate):
            sum += 1
            workerinfo = WorkerInfo.objects.get(user = item.worker)
            result += u'<tr class="att_number"><td class="code_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                      u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                      u'<form name="updateleave%s" method="post" action="" id= "updateleave%s" onsubmit="return false;"><td class="reason_wh1">'\
                      u'<input type="text" name="leave_id" style="display: none" value="%s" >'\
                      u'<input type="text" name="reason_content" maxlength="10" value="%s" id="cardid" class="text-input">'\
                      u'<input type="submit" value="提交" onclick="updateleave(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                      u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleateleave(%s)"  />'\
                      u'</td></tr>'%(sum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workorder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result

def get_search_absenteeismlist(request,absenteeismlist , startweek, endweek ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">旷工记录</div><div class="clear_float"></div>'\
             u'<table width="726" border="0" align="left" cellspacing="1" id="table3" ><tr class="att_name">'\
             u'<td class="code_wh">编号</td><td class="time_wh">学号</td><td class="time_wh">姓名</td><td class="time_wh">旷工时间</td>'\
             u'<td class="time_wh">旷工班次</td><td class="reason_wh1">旷工原因</td><td class="time_wh">删除操作</td></tr>'
    sum = 0
    startdate = get_startdate(startweek).date()
    enddate= get_enddate(endweek).date()
    for item in absenteeismlist:
        if(item.time.date()>=startdate and item.time.date()<=enddate):
            sum += 1
            workerinfo = WorkerInfo.objects.get(user = item.worker)
            result += u'<tr class="att_number"><td class="code_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                      u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                      u'<form name="updateabsenteeism%s" method="post" action="" id= "updateabsenteeism%s" onsubmit="return false;"><td class="reason_wh1">'\
                      u'<input type="text" name="absenteeism_id" style="display: none" value="%s" >'\
                      u'<input type="text" name="reason_content" maxlength="10" value="%s" id="cardid" class="text-input">'\
                      u'<input type="submit" value="提交" onclick="updateabsenteeism(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                      u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleateabsenteeism(%s)"  />'\
                      u'</td></tr>'%(sum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workOrder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result

def setorder(order):
    result = u''
    if(order > 0):
        for i in range(order):
            if i == 0:
                result += u'<p class="reg_ul_p1">班次</p> <p class="reg_ul_p2">' \
                          u'<select name="leaveorder" id="leaveorder">' \
                          u'<option value="1" selected="selected">1</option>'
            else:
                result += u' <option value="%s">%s</option>'%(i + 1, i + 1 )
    result += u'</select></p>'
    return result

def setexchangeorder(order):
    if not order:
        return ''
    result = u''
    if(order > 0):
        for i in range(order):
            if i == 0:
                result += u'<p class="reg_ul_p1">本人班次</p> <p class="reg_ul_p2">'\
                          u'<select name="myorder" id="myorder">'\
                          u'<option value="1" selected="selected">1</option>'
            else:
                result += u' <option value="%s">%s</option>'%(i + 1, i + 1 )
    result += u'</select></p>'
    if(order > 0):
        for i in range(order):
            if i == 0:
                result += u'<p class="reg_ul_p1">对方班次</p> <p class="reg_ul_p2">'\
                          u'<select name="goalorder" id="goalorder">'\
                          u'<option value="1" selected="selected">1</option>'
            else:
                result += u' <option value="%s">%s</option>'%(i + 1, i + 1 )
    result += u'</select></p>'
    return result

def get_leavelist(request,leavelist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">请假记录</div><div class="clear_float">'\
             u'</div><table width="300" border="0" align="left" cellspacing="1" id="table5" >'\
             u'<tr class="att_name"><td class="code_wh">编号</td>'\
             u'<td class="time_wh">请假时间</td><td class="time_wh">请假班次</td>'\
             u'<td class="reason_wh">请假原因</td></tr>'
    sum = 0
    for item in leavelist:
        sum += 1
        result += u'<tr class="att_number"><td class="code_wh">%s</td><td class="time_wh">%s</td>' \
                  u'<td class="duty_wh">星期%s 班次%s</td><td class="reason_wh">%s</td>' \
                  u'</tr>'%(sum , item.time.date(),item.day, item.workorder, item.reason)
    result += u'</table></div>'
    return result

def get_absenteeismlist(request,absenteeismlist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">旷工记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table4" ><tr class="att_name">'\
             u'<td class="code_wh">编号</td><td class="time_wh">旷工时间</td>'\
             u'<td class="time_wh">旷工班次</td><td class="reason_wh1">旷工原因</td></tr>'
    sum = 0
    for item in absenteeismlist:
        sum += 1
        result += u'<tr class="att_number"><td class="code_wh">%s</td><td class="time_wh">%s</td>'\
                  u'<td class="time_wh">星期%s 班次%s</td><td class="reason_wh">%s</td>'\
                  u'</tr>'%(sum , item.time.date(),item.day, item.workOrder, item.reason)
    result += u'</table></div>'
    return result

def get_unexchangelist(request, unexchange_list ):
    result = u''
    for item in unexchange_list:
        iname = WorkerInfo.objects.get(user = item.initiative_worker).name
        result += u'<tr class="att_number"><td class="duty_wh">%s</td>' \
                  u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>' \
                  u'<td class="time_wh">%s</td><td class="time_wh">%s</td><td class="duty_wh"><li class="font_grey">星期%s</li>' \
                  u'<li>班次%s</li></td><td class="reason_wh2">%s</td><td class="reply_button">' \
                  u'</tr>'%(iname ,item.iday, item.iorder, item.itime.date(),item.ptime.date(),item.pday, item.porder, item.ireason)
    return result

def get_noticelist(request, noticelist ):
    result = u''
    num = 0
    for item in noticelist:
        if num <= 7:
            userinfo = User.objects.get(id =  item.worker.id)
            workerinfo = WorkerInfo.objects.get(user = userinfo)
            name = workerinfo.name
            photo = workerinfo.photo_thumb
            if photo == "0":
                src = "images/css/avatar35.png"
            else:
                src = os.path.join( USERPHOTO_VIR_PATH,photo)
            result += u'<div class="boardinfo_details"><div id="avatar_photo2"><img src="%s" /></div><ul>' \
                      u'<li>%s: <span class="boardinfo_words">%s</span></li>' \
                      u'<li class="fontsize_12"><span class="boardinfo_words">%s</span> <input name="issue" type="submit" value="转发" onclick="transfermessage(%s);"  /></li></ul></div>' \
                    u'<hr align="left" width="540" size="1" noshade="noshade" class="info_hr"/>'% (src ,
                name ,item.content, item.createtime, "'" + name + ":" + item.content + "'")
            num += 1
    return result

def get_messagelist(request, message , num ):
    result = u''
    userinfo = User.objects.get(id =  message.worker.id)
    workerinfo = WorkerInfo.objects.get(user = userinfo)
    name = workerinfo.name
    photo = workerinfo.photo_thumb
    if photo == "0":
        src = "images/css/avatar35.png"
    else:
        src = os.path.join( USERPHOTO_VIR_PATH,photo)
    result += u'<div class="boardinfo_details"><div id="avatar_photo2"><img src="%s" /></div><ul>' \
              u'<li>%s : <span class="boardinfo_words">%s</span></li>' \
              u'<li class="fontsize_12"><span class="boardinfo_words">%s</span> ' \
              u'<input name="issue" type="submit" value="转发" onclick="transfermessage(%s);" >' \
              u'<input name="issue" type="submit" value="评论" onclick="setsumessage(%s);" >' \
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
        result += u'<li class="communicate_reply"><div id="avatar_photo2">' \
                  u'<img src="%s" /></div><ul>' \
                  u'<li>%s : <span class="boardinfo_words">%s</span></li>' \
                  u'<li class="fontsize_12">%s</li></ul></li>' \
                  u'<hr align="left" width="597" size="1" noshade="noshade" class="info_hr1"/>'%( src, name, item.content ,item.createtime )
    result += u'<form name="submessageForm%s" method="post" action="" id= "submessageForm%s" onsubmit="return false;">' \
              u'<div class="reply_info"><textarea name="content" class="reply_textarea"></textarea>' \
              u'<textarea name="id" class="reply_textarea" style="display: none" >%s</textarea>' \
              u'</div></ul></div></form>' \
              u'<hr align="left" width="662" size="1" noshade="noshade" class="info_hr2"/>'% ( num , num ,message.id )
    return result

def getsign_in(userid , schedule):
    result = u''
    workerinfo = WorkerInfo.objects.filter(user = userid)
    if(len(workerinfo) == 1):
        workerinfo = WorkerInfo.objects.get(user = userid)
        result += u'<tr class="att_number"><td class="att_name att_wh">%s</td> ' \
                  u'<td class="att_name att_wh"><input name="signin" type="submit" class="refuse" value="签到" onclick = "signin_normal(%s);" />' \
                  u'<input name="signin" type="submit" class="refuse" value="迟到" onclick = "signin_late(%s);"/> </td>' \
                  u'<td class="reply_button1"></td></tr>'%(workerinfo.name, str(schedule.id) + ","+ str(userid), str(schedule.id) + ","+ str(userid))
    return result

def get_AttentenceList(schedule):
    id = u''
    ifadd = 0
    dutytime =  "(" + str(schedule.starttime.hour) + ":" + str(schedule.starttime.minute)\
                + "--" + str(schedule.endtime.hour) + ":" + str(schedule.endtime.minute) + ")"
    result = u'<table width="200" border="0" align="left" cellspacing="1" ><tr><td>今天是%s</td><td> 星期%s</td> <td></td> <td width = "250"></td></tr><tr><td>本班次上班时间：%s </td><td>班次： %s</td><td></td><td width = "250"></td></tr></table>' \
             u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> ' \
             u'<table width="200" border="0" align="left" cellspacing="1" id="table7" ><tr class="att_name"><td class="duty_wh">队员</td>' \
             u'<td class="duty_wh"><input name="signin_button" type="submit" id = "signin_button" value="完成签到" onclick = "signin_finish(%s);" /></td>' \
             u'<td class="reply_button1"></td></tr>' %(datetime.datetime.now().date(), datetime.datetime.now().weekday() + 1,dutytime, schedule.workorder,  str(schedule.id))
    for ch in schedule.attendance:
        if (ifadd == 1):
            if (ch == '.'):
                ifadd = 0
                result += getsign_in(int(id),schedule)
            else:
                id += ch
        else:
            if(ch == ','):
                ifadd = 1
                id = u''
    result += u'</table>'
    return result

def get_worerlist_from_str(workerstr):
    result = list()
    id = u''
    ifadd = 0
    for str in workerstr:
        if (ifadd == 1):
            if (str == '.'):
                ifadd = 0
                result.append(WorkerInfo.objects.get(user = int(id)))
            else:
                id += str
        else:
            if(str == ','):
                ifadd = 1
                id = u''
    return result

def get_workersetlist(str, schedule):
    result = u''
    workerinfolist = get_worerlist_from_str(str)
    for item in workerinfolist:
        if(item.user == schedule.administrator):
            if item.accept == 1:
                result += u'<tr><td class="att_wh">%s(负责人)</td><td class="num_wh">%s</td><td><div width="850" align="right" ><input type="submit" name="delete" value="设为负责人" id="delete" onclick = "setmanager_schedule(%s,%s)"/>'\
                          u'<input type="submit" name="modify" value="删除" id="modify" onclick = "deleateworker_sche(%s,%s)" /></div></td>'\
                          u'</tr>' %(item.name, item.user.username,schedule.id, item.user.id,schedule.id, item.user.id)
            else:
                result += u'<tr><td class="att_wh">%s(负责人)</td><td class="num_wh">%s</td><td><div width="850" align="right" >'\
                          u'<input type="submit" name="modify" value="删除" id="modify" onclick = "deleateworker_sche(%s,%s)" /></div></td>'\
                          u'</tr>' %(item.name, item.user.username,schedule.id, item.user.id)
        else:
            if item.accept == 1:
                result += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td><div width="850" align="right" ><input type="submit" name="delete" value="设为负责人" id="delete" onclick = "setmanager_schedule(%s,%s)"/>'\
                           u'<input type="submit" name="modify" value="删除" id="modify" onclick = "deleateworker_sche(%s,%s)" /></div></td>' \
                           u'</tr>' %(item.name, item.user.username ,schedule.id, item.user.id,schedule.id, item.user.id)
            else:
                result += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td><div width="850" align="right" >'\
                          u'<input type="submit" name="modify" value="删除" id="modify" onclick = "deleateworker_sche(%s,%s)" /></div></td>'\
                          u'</tr>' %(item.name, item.user.username ,schedule.id, item.user.id)
    return result

def get_workerresultlist(choose):
    result = u''
    workerinfolist = get_worerlist_from_str(choose.resultworker)
    for item in workerinfolist:
        result += u'<tr><td class="att_wh">%s</td><td class="num_wh">%s</td><td><div width="850" align="right" >'\
                        u'<input type="submit" name="modify" value="删除" id="modify" onclick = "deleateworker_resultsche(%s,%s)" /></div></td>'\
                         u'</tr>' %(item.name, item.user.username ,choose.id, item.user.id)
    return result

def get_manager_exchangelist(request,exchangelist , num):
    if(num == 0):
        result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/>'\
                 u' <div id="qingjia_list"><div class="window_title">换班记录</div><div class="clear_float"></div>'\
                 u'<table width="727" border="0" align="left" cellspacing="1" id="table6" ><tr class="att_name">'\
                 u'<td class="code_wh">编号</td><td class="time_wh">我的时间</td>'\
                 u'<td class="time_wh">对方时间</td><td class="duty_wh">我的班次</td>'\
                 u'<td class="duty_wh">对方班次</td><td class="duty_wh">对方姓名</td>'\
                 u'<td class="reason_wh1">换班原因</td><td class="reason_wh1">换班回复</td></tr>'
        iffirst = 1
    else:
        result = u''
        iffirst = 0
    sum = num
    for item in exchangelist:
        sum += 1
        iname = WorkerInfo.objects.get(user = item.initiative_worker).name
        pname = WorkerInfo.objects.get(user = item.passivite_worker).name
        if (item.initiative_worker == request.user):
            result += u'<tr class="att_number"><td class="code_wh"> %s</td>'\
                      u'<td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                      u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>'\
                      u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>'\
                      u'<td class="duty_wh">%s</td><td class="reason_wh1">%s</td>'\
                      u'<td class="reason_wh1">%s</td></tr>'%(sum ,item.itime.date(), item.ptime.date(),
                                                              item.iday,item.iorder,item.pday, item.porder, pname,"(" +iname + ") :" + item.ireason, "("+pname + ") :" +item.preason)
        else:
            result += u'<tr class="att_number"><td class="code_wh"> %s</td>'\
                      u'<td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                      u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>'\
                      u'<td class="duty_wh"><li class="font_grey">星期%s</li><li>班次%s</li></td>'\
                      u'<td class="duty_wh">%s</td><td class="reason_wh1">%s</td>'\
                      u'<td class="reason_wh1">%s</td></tr>'%(sum , item.ptime.date(), item.itime.date(),
                                                              item.pday,item.porder,item.iday, item.iorder, iname,"(" +iname + "):" + item.ireason, "("+pname + ") :"+item.preason)
    if iffirst == 0:
        result += u'</table></div>'
    return result

def get_manager_latelist(request, latelist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">迟到记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table3" >'\
             u'<tr class="att_name"><td class="code_wh">编号</td><td class="time_wh">学号</td><td class="time_wh">姓名</td><td class="time_wh">迟到时间</td>'\
             u'<td class="time_wh">迟到班次</td><td class="reason_wh1">迟到原因</td><td class="time_wh">删除操作</td></tr>'
    sum = 0
    for item in latelist:
        sum += 1
        workerinfo = WorkerInfo.objects.get(user = item.worker)
        result += u'<tr class="att_number"><td class="code_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                  u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                  u'<form name="updatelate%s" method="post" action="" id= "updatelate%s" onsubmit="return false;"><td class="reason_wh1">' \
                  u'<input type="text" name="late_id" style="display: none" value="%s" >' \
                  u'<input type="text" name="reason_content" maxlength="20" value="%s" id="cardid" class="text-input">' \
                  u'<input type="submit" value="提交" onclick="updatelate(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>' \
                  u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleatelate(%s)"  />' \
                  u'</td></tr>'%(sum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workorder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result

def get_manager_worklist(request, worklist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">工时记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table3" >'\
             u'<tr class="att_name"><td class="code_wh">编号</td><td class="time_wh">学号</td><td class="time_wh">姓名</td><td class="time_wh">上班时间</td>'\
             u'<td class="time_wh">上班班次</td><td class="reason_wh1">附加说明</td><td class="time_wh">删除操作</td></tr>'
    sum = 0
    for item in worklist:
        sum += 1
        workerinfo = WorkerInfo.objects.get(user = item.worker)
        result += u'<tr class="att_number"><td class="code_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                  u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                  u'<form name="updatelate%s" method="post" action="" id= "updatelate%s" onsubmit="return false;"><td class="reason_wh1">'\
                  u'<input type="text" name="late_id" style="display: none" value="%s" >'\
                  u'<input type="text" name="reason_content" maxlength="20" value="%s" id="cardid" class="text-input">'\
                  u'<input type="submit" value="提交" onclick="updatelate(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                  u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleatework(%s)"  />'\
                  u'</td></tr>'%(sum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workorder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result

def get_manager_overtimelist(request, overtimelist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">加班记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table3" >'\
             u'<tr class="att_number"><td class="time_wh">工时/小时</td><td class="time_wh">学号</td><td class="time_wh">姓名</td><td class="time_wh">上班时间</td>'\
             u'<td class="time_wh">上班班次</td><td class="reason_wh1">附加说明</td><td class="time_wh">删除操作</td></tr>'
    for item in overtimelist:
        workerinfo = WorkerInfo.objects.get(user = item.worker)
        result += u'<tr class="att_number"><td class="time_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                  u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                  u'<form name="updatelate%s" method="post" action="" id= "updatelate%s" onsubmit="return false;"><td class="reason_wh1">'\
                  u'<input type="text" name="late_id" style="display: none" value="%s" >'\
                  u'<input type="text" name="reason_content" maxlength="20" value="%s" id="cardid" class="text-input">'\
                  u'<input type="submit" value="提交" onclick="updatelate(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                  u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleateovertime(%s)"  />'\
                  u'</td></tr>'%(item.hournum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workorder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result

def get_manager_earlylist(request, earlylist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">早退记录</div><div class="clear_float"></div>'\
             u'<table width="300" border="0" align="left" cellspacing="1" id="table3" >'\
             u'<tr class="att_number"><td class="time_wh">工时/小时</td><td class="time_wh">学号</td><td class="time_wh">姓名</td><td class="time_wh">上班时间</td>'\
             u'<td class="time_wh">上班班次</td><td class="reason_wh1">附加说明</td><td class="time_wh">删除操作</td></tr>'
    for item in earlylist:
        workerinfo = WorkerInfo.objects.get(user = item.worker)
        result += u'<tr class="att_number"><td class="time_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                  u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                  u'<form name="updatelate%s" method="post" action="" id= "updatelate%s" onsubmit="return false;"><td class="reason_wh1">'\
                  u'<input type="text" name="late_id" style="display: none" value="%s" >'\
                  u'<input type="text" name="reason_content" maxlength="20" value="%s" id="cardid" class="text-input">'\
                  u'<input type="submit" value="提交" onclick="updatelate(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                  u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleateearly(%s)"  />'\
                  u'</td></tr>'%(item.hournum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workorder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result

def get_manager_leavelist(request,leavelist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">请假记录</div><div class="clear_float">'\
             u'</div><table width="300" border="0" align="left" cellspacing="1" id="table3" >'\
             u'<tr class="att_name"><td class="code_wh">编号</td><td class="time_wh">学号</td><td class="time_wh">姓名</td>'\
             u'<td class="time_wh">请假时间</td><td class="time_wh">请假班次</td>'\
             u'<td class="reason_wh">请假原因</td><td class="time_wh">删除操作</td></tr>'
    sum = 0
    for item in leavelist:
        sum += 1
        workerinfo = WorkerInfo.objects.get(user = item.worker)
        result += u'<tr class="att_number"><td class="code_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                  u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                  u'<form name="updateleave%s" method="post" action="" id= "updateleave%s" onsubmit="return false;"><td class="reason_wh1">'\
                  u'<input type="text" name="leave_id" style="display: none" value="%s" >'\
                  u'<input type="text" name="reason_content" maxlength="10" value="%s" id="cardid" class="text-input">'\
                  u'<input type="submit" value="提交" onclick="updateleave(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                  u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleateleave(%s)"  />'\
                  u'</td></tr>'%(sum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workorder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result

def get_manager_absenteeismlist(request,absenteeismlist ):
    result = u'<hr align="left" width="724" size="1" noshade="noshade" class="hr"/> '\
             u'<div id="qingjia_list"><div class="window_title">旷工记录</div><div class="clear_float"></div>'\
             u'<table width="726" border="0" align="left" cellspacing="1" id="table3" ><tr class="att_name">'\
             u'<td class="code_wh">编号</td><td class="time_wh">学号</td><td class="time_wh">姓名</td><td class="time_wh">旷工时间</td>'\
             u'<td class="time_wh">旷工班次</td><td class="reason_wh1">旷工原因</td><td class="time_wh">删除操作</td></tr>'
    sum = 0
    for item in absenteeismlist:
        sum += 1
        workerinfo = WorkerInfo.objects.get(user = item.worker)
        result += u'<tr class="att_number"><td class="code_wh">%s</td><td class="time_wh">%s</td><td class="time_wh">%s</td>'\
                  u'<td class="time_wh">%s</td><td class="duty_wh">星期%s 班次%s</td>'\
                  u'<form name="updateabsenteeism%s" method="post" action="" id= "updateabsenteeism%s" onsubmit="return false;"><td class="reason_wh1">'\
                  u'<input type="text" name="absenteeism_id" style="display: none" value="%s" >'\
                  u'<input type="text" name="reason_content" maxlength="10" value="%s" id="cardid" class="text-input">'\
                  u'<input type="submit" value="提交" onclick="updateabsenteeism(%s);"  /><label id="msg%s" style="color: red;"></label></td></form>'\
                  u'<td class="duty_wh"> <input name="qingjia" type="submit" id="qingjia" value="删除" onclick="deleateabsenteeism(%s)"  />'\
                  u'</td></tr>'%(sum ,item.worker.username, workerinfo.name, item.time.date(), item.day, item.workOrder, item.id, item.id, item.id, item.reason ,item.id, item.id, item.id)
    result += u'</table></div>'
    return result