/**
 * Created by PyCharm.
 * User: denghc
 * Date: 12-2-27
 * Time: 下午2:19
 * To change this template use File | Settings | File Templates.
 */
var Dajax={process:function(b){b==Dajaxice.EXCEPTION?alert("网络异常"):$.each(b,function(b,a){switch(a.cmd){case "alert":alert(a.val);break;case "data":eval(a.fun+"(elem.val);");break;case "as":jQuery.each($(a.id),function(){this[a.prop]=a.val});break;case "addcc":jQuery.each(a.val,function(){$(a.id).addClass(this)});break;case "remcc":jQuery.each(a.val,function(){$(a.id).removeClass(this)});break;case "ap":jQuery.each($(a.id),function(){this[a.prop]+=a.val});
    break;case "pp":jQuery.each($(a.id),function(){this[a.prop]=a.val+this[a.prop]});break;case "clr":jQuery.each($(a.id),function(){this[a.prop]=""});break;case "red":window.setTimeout('window.location="'+a.url+'";',a.delay);break;case "js":eval(a.val);break;case "rm":$(a.id).remove();break;default:alert("Unknown action!")}})}};
(function(c,f){"$:nomunge";c.fn.serializeObject=function(){var a={};c.each(this.serializeArray(),function(g,e){var b=e.name,d=e.value;a[b]=a[b]===f?d:c.isArray(a[b])?a[b].concat(d):[a[b],d]});return a}})(jQuery);