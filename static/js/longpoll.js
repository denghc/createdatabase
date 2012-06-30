/**
 * Created by PyCharm.
 * User: denghc
 * Date: 12-4-18
 * Time: 下午4:24
 * To change this template use File | Settings | File Templates.
 */
function getdata(id , num) {
    var ret = "../../news/update";
    ret+='/?id='+ id +'&num=' + num;
    var numtemp  = num
    $.getJSON(ret, function(result)
    {
        $.each(result,function(id,data){
            $('#messagecontent').prepend(data['content'])
            numtemp += 1;
        });
        setTimeout('getdata('+id + ','+ numtemp+')',5000);
    });
}

function seemore(){
    var ret = "../../news/updateold/";
    $.getJSON(ret, function(result)
    {
        $.each(result,function(id,data){
            if(data['content'] != 'none')
            {
                $('#messagecontent').append(data['content']);
            }
            else
            {
                $('#seemoremessages').hide();
            }

        });
    });
}

$(document).ready(function() {
    var ret = "../../news/getbasicmessage/";
    $.getJSON(ret, function(result)
    {
        getdata(result["id"], result["num"]);
    });

});

