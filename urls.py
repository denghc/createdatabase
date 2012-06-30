from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from logic.views import *

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'RegisterSystem.views.home', name='home'),
    # url(r'^RegisterSystem/', include('RegisterSystem.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index),
    url(r'^index/$', index),
    url(r'^register/',register),
    url(r'^dutywish/', dutywish),
    url(r'^communicate/',requires_login(communicate)),
    url(r'^infomanage/',requires_login(infomanage), name = "infomanage"),
    url(r'^showduty/',requires_login(showduty)),
    url(r'^attendance/',requires_login(attendance)),
    url(r'^changerequest/',requires_login(changerequest)),
    url(r'^status/',requires_login(status)),
    url(r'^page_logout/',page_logout),
    url(r'^findpassword/',findpassword),
    url(r'^news/update/',updatenews),
    url(r'^news/updateold/',updateold),
    url(r'^news/getbasicmessage/',getbasicmessage),
    url(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),

    url(r'^manage_attendance/', requires_login(manage_attendance)),
    url(r'^manage_communicate/', requires_login(manage_communicate)),
    url(r'^manage_sign_in/', requires_login(manage_sign_in)),
    url(r'^manage_status/', requires_login(manage_status)),
    url(r'^manage_infomanage/', requires_login(manage_infomanage), name = "manage_infomanage"),

    url(r'^officer_accreditation/', requires_login(officer_accreditation)),
    url(r'^officer_arrangement/', requires_login(officer_arrangement)),
    url(r'^officer_communication/', requires_login(officer_communication)),
    url(r'^officer_data_managerment/', requires_login(officer_data_managerment)),
    url(r'^officer_infomanage/', requires_login(officer_infomanage)),
    url(r'^officer_new_application/', requires_login(officer_new_application)),
    url(r'^officer_queryInformation/', requires_login(officer_queryInformation)),
    url(r'^officer_selfinfo/', requires_login(officer_selfinfo), name = "officer_selfinfo"),
    url(r'^officer_uploadexcel/', requires_login(officer_uploadexcel), name = "officer_uploadexcel"),
    url(r'^officer_wish/', requires_login(officer_wish)),
    url(r'^officer_wisharrange/', requires_login(officer_wisharrange)),

    url(r'^uploadphoto/', uploadphoto, name= "uploadphoto"),
    url(r'^AllExtendenceExcel/', AllExtendenceExcel, name= "AllExtendenceExcel"),
    url(r'^AllWorkArrangeExcel/', AllWorkArrangeExcel, name= "AllWorkArrangeExcel"),
    url(r'^AllWorkerInfoExcel/', AllWorkerInfoExcel, name= "AllWorkerInfoExcel"),
    url(r'^AllInfoExcel/', AllInfoExcel, name= "AllInfoExcel"),
    url(r'^MyWorkerAttendence/', MyWorkerAttendence, name= "MyWorkerAttendence"),
    url(r'^workerwishExcel/', workerwishExcel, name= "workerwishExcel"),
    url(r'^workwishnumExcel/', workwishnumExcel, name= "workwishnumExcel"),

    url(r'^manager_uploadphoto/', manager_uploadphoto, name= "manager_uploadphoto"),
    url(r'^officer_uploadphoto/', officer_uploadphoto, name= "officer_uploadphoto"),
    url(r'^cutphoto/', cutphoto , name= "cutphoto"),
    url(r'^manager_cutphoto/', manager_cutphoto , name= "manager_cutphoto"),
    url(r'^officer_cutphoto/', officer_cutphoto , name= "officer_cutphoto"),
    #url(r'^manage_attendance/', requires_login(manage_attendance)),
    ##url(r'^manage_communicate/', requires_login(manage_communicate)),
    #url(r'^manage_sign_in/', requires_login(manage_sign_in)),
    #url(r'^manage_status/', requires_login(manage_status)),

)

#urlpatterns += staticfiles_urlpatterns(),

