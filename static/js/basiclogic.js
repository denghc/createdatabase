/**
 * Created by PyCharm.
 * User: denghc
 * Date: 12-2-27
 * Time: 下午9:47
 * To change this template use File | Settings | File Templates.
 */
function login() {
    var data = $('#login_form').serializeObject() ;
    if (advanced_choice.checked)
    {
        Dajaxice.RegisterSystem.logic.loginmanager(Dajax.process, {'form':data});
    }
    else
    {
        Dajaxice.RegisterSystem.logic.login(Dajax.process, {'form':data});
    }
}

function register() {
    var data = $('#registrationForm').serializeObject();
    Dajaxice.RegisterSystem.logic.register(Dajax.process, {'form':data});
}
function findPassword()
{
    var data = $('#findpasswordForm').serializeObject();
    Dajaxice.RegisterSystem.logic.findPassword(Dajax.process,{'form':data});
}

function reset_dutywish(){
    for (var i=0; i<dutylist.length; i++)
        dutylist[i].checked = false;
    Dajaxice.RegisterSystem.logic.reset_dutywish(Dajax.process);
}
function updateDutywish() {
    var data = $('#dutywish').serializeObject();
    Dajaxice.RegisterSystem.logic.updateDutywish(Dajax.process, {'form':data});
}
function reset_numwish() {
    var data = $('#wishnum').serializeObject();
    Dajaxice.RegisterSystem.logic.reset_numwish(Dajax.process, {'form':data});
}
function showduty(){
    var data = $('#registrationForm').serializeObject();
    Dajaxice.RegisterSystem.logic.register(Dajax.process, {'form':data});
}

function setleave(){
    var data = $('#leaveForm').serializeObject();
    Dajaxice.RegisterSystem.logic.setleave(Dajax.process, {'form':data});
}

function setexchange(){
    var data = $('#huanbanForm').serializeObject();
    Dajaxice.RegisterSystem.logic.setexchange(Dajax.process, {'form':data});
}

function changeinfo(){
    var data = $('#infoForm').serializeObject();
    Dajaxice.RegisterSystem.logic.changeinfo(Dajax.process, {'form':data});
}

function agreeexchange(){
    var data = $('#replyexchangeForm').serializeObject();
    Dajaxice.RegisterSystem.logic.agreeexchange(Dajax.process, {'form':data});
}

function refuseexchange(){
    var data = $('#replyexchangeForm').serializeObject();
    Dajaxice.RegisterSystem.logic.refuseexchange(Dajax.process, {'form':data});
}

function deleateleave( id){
    if (confirm("确认要删除？")){
        Dajaxice.RegisterSystem.logic.deleateleave(Dajax.process, {'form':id});
    }
}

function sureupload(){
    if (confirm("是否批量导入为队员？")){
        var data = $('#uploadexcel').serializeObject();
        Dajaxice.RegisterSystem.logic.sureupload(Dajax.process, {'form':data});
    }
}

function signin_normal(scheduleid, workerid ){
    Dajaxice.RegisterSystem.logic.signin_normal(Dajax.process,  {'form': scheduleid +','+ workerid})
}
function signin_late(scheduleid, workerid){
    Dajaxice.RegisterSystem.logic.signin_late(Dajax.process,  {'form': scheduleid +','+ workerid})
}
function signin_finish(scheduleid){
    if (confirm("未签到的将被记录为旷工，确定签到完成？")){
        Dajaxice.RegisterSystem.logic.signin_finish(Dajax.process,  {'form': scheduleid})
    }
}

function setmessage(){
    var data = $('#messangeForm').serializeObject();
    Dajaxice.RegisterSystem.logic.setMessage(Dajax.process, {'form':data});
}

function deleateexchange( id){
    var data = id;
    if (confirm("确认要删除？")){
        Dajaxice.RegisterSystem.logic.deleateexchange(Dajax.process, {'form':data});
    }
}

function deleatelate( id){
    var data = id;
    if (confirm("删除后不保存此记录，确认要删除？")){
        Dajaxice.RegisterSystem.logic.deleatelate(Dajax.process, {'form':data});
    }
}

function deleatework( id){
    var data = id;
    if (confirm("删除后不保存此记录，确认要删除？")){
        Dajaxice.RegisterSystem.logic.deleatework(Dajax.process, {'form':data});
    }
}

function deleateearly( id){
    var data = id;
    if (confirm("删除后不保存此记录，确认要删除？")){
        Dajaxice.RegisterSystem.logic.deleateearly(Dajax.process, {'form':data});
    }
}

function deleateovertime( id){
    var data = id;
    if (confirm("删除后不保存此记录，确认要删除？")){
        Dajaxice.RegisterSystem.logic.deleateovertime(Dajax.process, {'form':data});
    }
}
function deleateabsenteeism( id){
    var data = id;
    if (confirm("删除后不保存此记录，确认要删除？")){
        Dajaxice.RegisterSystem.logic.deleateabsenteeism(Dajax.process, {'form':data});
    }
}

function deleateleave( id){
    var data = id;
    if (confirm("删除后不保存此记录，确认要删除？")){
        Dajaxice.RegisterSystem.logic.deleateleaverecord(Dajax.process, {'form':data});
    }
}
function transfermessage( message){
    var data = message;
    Dajaxice.RegisterSystem.logic.transfermessage(Dajax.process, {'form':data});
}

function resetsedule(id){
    Dajaxice.RegisterSystem.logic.resetsedule(Dajax.process, {'form':id});
}
function resetchoosewish(id){
    Dajaxice.RegisterSystem.logic.resetchoosewish(Dajax.process, {'form':id});
}
function deletesedule(){
    if (confirm("删除最后一班班次所有相关数据？")){
    Dajaxice.RegisterSystem.logic.deletesedule(Dajax.process);
    }
}

function changetime(id){
    var data = $('#dutytime'+id).serializeObject();
    Dajaxice.RegisterSystem.logic.changetime(Dajax.process, {'form':data});
}
function changeworkernum(id){
    var data = $('#dutytime'+id).serializeObject();
    Dajaxice.RegisterSystem.logic.changeworkernum(Dajax.process, {'form':data});
}
function updatelate(id){
    var data = $('#updatelate'+id).serializeObject();
    Dajaxice.RegisterSystem.logic.updatelate(Dajax.process, {'form':data});
}
function updateabsenteeism(id){
    var data = $('#updateabsenteeism'+id).serializeObject();
    Dajaxice.RegisterSystem.logic.updateabsenteeism(Dajax.process, {'form':data});
}
function updateleave(id){
    var data = $('#updateleave'+id).serializeObject();
    Dajaxice.RegisterSystem.logic.updateleave(Dajax.process, {'form':data});
}
function finishaddwork(){
    var data = $('#work').serializeObject();
    Dajaxice.RegisterSystem.logic.finishaddwork(Dajax.process, {'form':data});
}
function finishovertime(){
    var data = $('#overtime').serializeObject();
    Dajaxice.RegisterSystem.logic.finishovertime(Dajax.process, {'form':data});
}

function search(){
    var data = $('#searchForm').serializeObject();
    Dajaxice.RegisterSystem.logic.search(Dajax.process, {'form':data});
}

function searchexcel(){
    var data = $('#searchForm').serializeObject();
    Dajaxice.RegisterSystem.logic.searchexcel(Dajax.process, {'form':data});
}

function finishearly(){
    var data = $('#early').serializeObject();
    Dajaxice.RegisterSystem.logic.finishearly(Dajax.process, {'form':data});
}
function setsumessage(num){
    var data = $('#submessageForm'+ num ).serializeObject();
    Dajaxice.RegisterSystem.logic.setsumessage(Dajax.process, {'form':data});
}

function uploadPhoto(){
    var data = $('#photo').serializeObject();
    Dajaxice.RegisterSystem.logic.uploadPhoto(Dajax.process, {'form':data});
}

function setmanager_schedule(schid, userid){
    var data = schid + "," + userid
    Dajaxice.RegisterSystem.logic.setmanager_schedule(Dajax.process, {'form':data});
}
function deleateworker_sche(schid, userid){
    var data = schid + "," + userid
    Dajaxice.RegisterSystem.logic.deleateworker_sche(Dajax.process, {'form':data});
}
function deleateworker_resultsche(schid, userid){
    var data = schid + "," + userid
    Dajaxice.RegisterSystem.logic.deleateworker_resultsche(Dajax.process, {'form':data});
}
function addworker_sch(schid, userid){
    var data = schid + "," + userid
    Dajaxice.RegisterSystem.logic.addworker_sch(Dajax.process, {'form':data});
}
function addworker_schresult(schid, userid){
    var data = schid + "," + userid
    Dajaxice.RegisterSystem.logic.addworker_schresult(Dajax.process, {'form':data});
}

function addworker_schedule(schid){
    Dajaxice.RegisterSystem.logic.addworker_schedule(Dajax.process, {'form':schid});
}

function addworktime_schedule(schid){
    if (confirm("给该实际班次的队员批量补录1工时？")){
        Dajaxice.RegisterSystem.logic.addworktime_schedule(Dajax.process, {'form':schid});
    }
}
function resetattendance(schid){
    if (confirm("将实际上班表同步为固定排班表（清除请假，换班等）？")){
        Dajaxice.RegisterSystem.logic.resetattendance(Dajax.process, {'form':schid});
    }
}

function addworker_result(schid){
    Dajaxice.RegisterSystem.logic.addworker_result(Dajax.process, {'form':schid});
}

function open_specificleave(worker_id, manager_id){
    var data = worker_id + "," + manager_id
    Dajaxice.RegisterSystem.logic.open_specificleave(Dajax.process, {'form':data});
}
function open_specificlate(worker_id, manager_id){
    var data = worker_id + "," + manager_id
    Dajaxice.RegisterSystem.logic.open_specificlate(Dajax.process, {'form':data});
}
function open_specificabsenteeism(worker_id, manager_id){
    var data = worker_id + "," + manager_id
    Dajaxice.RegisterSystem.logic.open_specificabsenteeism(Dajax.process, {'form':data});
}
function open_specificexchange(worker_id, manager_id){
    var data = worker_id + "," + manager_id
    Dajaxice.RegisterSystem.logic.open_specificexchange(Dajax.process, {'form':data});
}
function open_specificwork(worker_id, manager_id){
    var data = worker_id + "," + manager_id
    Dajaxice.RegisterSystem.logic.open_specificwork(Dajax.process, {'form':data});
}
function open_specificearly(worker_id, manager_id){
    var data = worker_id + "," + manager_id
    Dajaxice.RegisterSystem.logic.open_specificearly(Dajax.process, {'form':data});
}
function open_specificovertime(worker_id, manager_id){
    var data = worker_id + "," + manager_id
    Dajaxice.RegisterSystem.logic.open_specificovertime(Dajax.process, {'form':data});
}

function open_officer_specific_leave(worker_id){
    Dajaxice.RegisterSystem.logic.open_officer_specific_leave(Dajax.process, {'form':worker_id});
}
function open_officer_specific_late(worker_id){
    Dajaxice.RegisterSystem.logic.open_officer_specific_late(Dajax.process, {'form':worker_id});
}
function open_officer_specific_absenteeism(worker_id){
    Dajaxice.RegisterSystem.logic.open_officer_specific_absenteeism(Dajax.process, {'form':worker_id});
}
function open_officer_specific_exchange(worker_id){
    Dajaxice.RegisterSystem.logic.open_officer_specific_exchange(Dajax.process, {'form':worker_id});
}
function open_officer_specific_work(worker_id){
    Dajaxice.RegisterSystem.logic.open_officer_specific_work(Dajax.process, {'form':worker_id});
}
function open_officer_specific_early(worker_id){
    Dajaxice.RegisterSystem.logic.open_officer_specific_early(Dajax.process, {'form':worker_id});
}
function open_officer_specific_overtime(worker_id){
    Dajaxice.RegisterSystem.logic.open_officer_specific_overtime(Dajax.process, {'form':worker_id});
}


function open_search_leave(worker_id, startweek, endweek){
    Dajaxice.RegisterSystem.logic.open_search_leave(Dajax.process, {'form':worker_id +','+ startweek+','+ endweek});
}
function open_search_late(worker_id, startweek, endweek){
    Dajaxice.RegisterSystem.logic.open_search_late(Dajax.process, {'form':worker_id +','+ startweek+','+ endweek});
}
function open_search_absenteeism(worker_id, startweek, endweek){
    Dajaxice.RegisterSystem.logic.open_search_absenteeism(Dajax.process, {'form':worker_id +','+ startweek+','+ endweek});
}
function open_search_exchange(worker_id, startweek, endweek){
    Dajaxice.RegisterSystem.logic.open_search_exchange(Dajax.process, {'form':worker_id +','+ startweek+','+ endweek});
}
function open_search_work(worker_id, startweek, endweek){
    Dajaxice.RegisterSystem.logic.open_search_work(Dajax.process, {'form':worker_id +','+ startweek+','+ endweek});
}

function open_search_early(worker_id, startweek, endweek){
    Dajaxice.RegisterSystem.logic.open_search_early(Dajax.process, {'form':worker_id +','+ startweek+','+ endweek});
}
function open_search_overtime(worker_id, startweek, endweek){
    Dajaxice.RegisterSystem.logic.open_search_overtime(Dajax.process, {'form':worker_id +','+ startweek+','+ endweek});
}

function settomanager(worker_id){
    Dajaxice.RegisterSystem.logic.settomanager(Dajax.process, {'form':worker_id});
}
function settooridinary(worker_id){
    Dajaxice.RegisterSystem.logic.settooridinary(Dajax.process, {'form':worker_id});
}
function agree_newworker(worker_id){
    Dajaxice.RegisterSystem.logic.agree_newworker(Dajax.process, {'form':worker_id});
}
function refuse_newworker(worker_id){
    if (confirm("将会注销该用户？")){
    Dajaxice.RegisterSystem.logic.refuse_newworker(Dajax.process, {'form':worker_id});
    }
}
function deleaveworker(worker_id){
    if (confirm("将会注销该用户？")){
        Dajaxice.RegisterSystem.logic.deleaveworker(Dajax.process, {'form':worker_id});
    }
}
function agree_newleave(leave_id){
    if (confirm("确定批准请假？")){
    var data = $('#leavereply'+ leave_id ).serializeObject();
    Dajaxice.RegisterSystem.logic.agree_newleave(Dajax.process, {'form':data});
    }
}
function refuse_newleave(leave_id){
    if (confirm("确定拒绝请假？")){
    var data = $('#leavereply'+ leave_id ).serializeObject();
    Dajaxice.RegisterSystem.logic.refuse_newleave(Dajax.process, {'form':data});
    }
}
function finishwish(){
    if (confirm("将会提交为班次安排？")){
        Dajaxice.RegisterSystem.logic.finishwish(Dajax.process);
    }
}

function seemore(){

}

$(function () {
    $('#hidewindow_photo').click(function(){
        $('#window_photo').hide();
    });

    $('#hidewindow_leave').click(function(){
        $('#window_leave').hide();
    });

    $('#hidewindow_huanban').click(function(){
        $('#window_huanban').hide();
    });

    $('#hidereply_exchange').click(function(){
        $('#window_leave').hide();
    });

    $('#openleave').click(function(){
        Dajaxice.RegisterSystem.logic.openleave(Dajax.process);
    });

    $('#openabsenteesim').click(function(){
        Dajaxice.RegisterSystem.logic.openabsenteesim(Dajax.process);
    });

    $('#openlate').click(function(){
        Dajaxice.RegisterSystem.logic.openlate(Dajax.process);
    });

    $('#openexchange').click(function(){
        Dajaxice.RegisterSystem.logic.openexchange(Dajax.process);
    });

    $('#openwork').click(function(){
        Dajaxice.RegisterSystem.logic.openwork(Dajax.process);
    });

    $('#openearly').click(function(){
        Dajaxice.RegisterSystem.logic.openearly(Dajax.process);
    });

    $('#openovertime').click(function(){
        Dajaxice.RegisterSystem.logic.openovertime(Dajax.process);
    });

    $('#open_manager_leave').click(function(){
        Dajaxice.RegisterSystem.logic.open_manager_leave(Dajax.process);
    });

    $('#open_manager_absenteesim').click(function(){
        Dajaxice.RegisterSystem.logic.open_manager_absenteesim(Dajax.process);
    });

    $('#open_manager_late').click(function(){
        Dajaxice.RegisterSystem.logic.open_manager_late(Dajax.process);
    });

    $('#open_manager_exchange').click(function(){
        Dajaxice.RegisterSystem.logic.open_manager_exchange(Dajax.process);
    });

    $('#open_manager_work').click(function(){
        Dajaxice.RegisterSystem.logic.open_manager_work(Dajax.process);
    });

    $('#open_manager_early').click(function(){
        Dajaxice.RegisterSystem.logic.open_manager_early(Dajax.process);
    });

    $('#open_manager_overtime').click(function(){
        Dajaxice.RegisterSystem.logic.open_manager_overtime(Dajax.process);
    });

    $('#open_officer_leave').click(function(){
        Dajaxice.RegisterSystem.logic.open_officer_leave(Dajax.process);
    });

    $('#open_officer_absenteesim').click(function(){
        Dajaxice.RegisterSystem.logic.open_officer_absenteesim(Dajax.process);
    });

    $('#open_officer_late').click(function(){
        Dajaxice.RegisterSystem.logic.open_officer_late(Dajax.process);
    });

    $('#open_officer_exchange').click(function(){
        Dajaxice.RegisterSystem.logic.open_officer_exchange(Dajax.process);
    });

    $('#open_officer_work').click(function(){
        Dajaxice.RegisterSystem.logic.open_officer_work(Dajax.process);
    });

    $('#open_officer_early').click(function(){
        Dajaxice.RegisterSystem.logic.open_officer_early(Dajax.process);
    });

    $('#open_officer_overtime').click(function(){
        Dajaxice.RegisterSystem.logic.open_officer_overtime(Dajax.process);
    });

});

function preview(img, selection) {
    if (!selection.width || !selection.height)
        return;

    var scaleX = 100 / selection.width;
    var scaleY = 100 / selection.height;

    $('#preview img').css({
        width: Math.round(scaleX * 300),
        height: Math.round(scaleY * 300),
        marginLeft: -Math.round(scaleX * selection.x1),
        marginTop: -Math.round(scaleY * selection.y1)
    });

    $('#id_x1').val(selection.x1);
    $('#id_y1').val(selection.y1);
    $('#id_x2').val(selection.x2);
    $('#id_y2').val(selection.y2);
    $('#id_w').val(selection.width);
    $('#id_h').val(selection.height);
}

$(function (){
    $('#id_x1').val(100);
    $('#id_y1').val(100);
    $('#id_x2').val(200);
    $('#id_y2').val(200);
    $('#id_w').val(100);
    $('#id_h').val(100);
    $('#photo').imgAreaSelect({ aspectRatio: '1:1', handles: true,
        fadeSpeed: 200, minHeight:100,minWidth:100,onSelectChange: preview,
        x1: 100, y1: 100, x2: 200, y2: 200
    });
});


