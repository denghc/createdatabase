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

function reset_dutywish(){
    for (var i=0; i<dutylist.length; i++)
        dutylist[i].checked = false;
    Dajaxice.RegisterSystem.logic.reset_dutywish(Dajax.process);
}
function updateDutywish() {
    var data = $('#dutywish').serializeObject();
    Dajaxice.RegisterSystem.logic.updateDutywish(Dajax.process, {'form':data});
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
    var data = id;
    if (confirm("确认要删除？")){
        Dajaxice.RegisterSystem.logic.deleateleave(Dajax.process, {'form':data});
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

function transfermessage( message){
    var data = message;
    Dajaxice.RegisterSystem.logic.transfermessage(Dajax.process, {'form':data});
}

function setsumessage(num){
    var n = num;
    switch(n)
    {
        case '1':
            var data = $('#submessageForm1' ).serializeObject();
            break
        case '2':
            var data = $('#submessageForm2' ).serializeObject();
            break
        case '3':
            var data = $('#submessageForm3' ).serializeObject();
            break
        case '4':
            var data = $('#submessageForm4' ).serializeObject();
            break
        case '5':
            var data = $('#submessageForm5' ).serializeObject();
            break
        case '6':
            var data = $('#submessageForm6' ).serializeObject();
            break
        case '7':
            var data = $('#submessageForm7' ).serializeObject();
            break
        case '8':
            var data = $('#submessageForm8' ).serializeObject();
            break
        case '9':
            var data = $('#submessageForm9' ).serializeObject();
            break
        default:
            var data = $('#submessageForm10' ).serializeObject();
    }
    Dajaxice.RegisterSystem.logic.setsumessage(Dajax.process, {'form':data});
}

function uploadPhoto(){
    var data = $('#photo').serializeObject();
    Dajaxice.RegisterSystem.logic.uploadPhoto(Dajax.process, {'form':data});
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
