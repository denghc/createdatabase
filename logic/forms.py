#coding=utf-8
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class ManagerLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    advanced_choice = forms.CheckboxInput()

class RegisterForm(forms.Form):
    cardid = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    surepassword = forms.CharField(widget=forms.PasswordInput())
    name = forms.CharField()
    email = forms.EmailField()
    phonenumber =  forms.CharField()
    work = forms.IntegerField()

class LeaveForm(forms.Form):
    leaveday = forms.IntegerField()
    leaveorder = forms.IntegerField()
    reason = forms.CharField()

class  ExchangeForm(forms.Form):
    goalname = forms.CharField()
    myday = forms.IntegerField()
    goalday = forms.IntegerField()
    myorder = forms.IntegerField()
    goalorder = forms.IntegerField()
    reason = forms.CharField()

class  InfoForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    passwordagain = forms.CharField()
    email = forms.EmailField()
    phonenumber = forms.CharField()

class  ReplyExchangeForm(forms.Form):
    ex_id = forms.IntegerField()
    reply = forms.CharField()

class ImportantMessageForm(forms.Form):
    message = forms.CharField()
    ifmanage = forms.CharField()

class NormalMessageForm(forms.Form):
    message = forms.CharField()

class ReplyMessageForm(forms.Form):
    content = forms.CharField()
    id = forms.CharField()

class PhotoForm(forms.Form):
    photo_name = forms.ImageField(label=u"头像")

class EXCELForm(forms.Form):
    excel_name = forms.URLField(label=u"excel文件路径")

class DutyWish(forms.Form):
    b = forms.CharField()

class HatHeadCutForm(forms.Form):
    x1=forms.IntegerField(widget=forms.TextInput(attrs={'size': 4,}))
    y1=forms.IntegerField(widget=forms.TextInput(attrs={'size': 4,}))
    x2=forms.IntegerField(widget=forms.TextInput(attrs={'size': 4,}))
    y2=forms.IntegerField(widget=forms.TextInput(attrs={'size': 4,}))
    w=forms.IntegerField(widget=forms.TextInput(attrs={'size': 4,}))
    h=forms.IntegerField(widget=forms.TextInput(attrs={'size': 4,}))

class NumWishForm(forms.Form):
    minnum = forms.IntegerField()
    maxnum = forms.IntegerField()

class FindPasswordForm(forms.Form):
    id = forms.CharField()
    email = forms.EmailField()

class UploadFileForm(forms.Form):
    file = forms.FileField()



