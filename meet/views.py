# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
import json
import datetime
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from meet import models
from meet.form import *
from django.db.models import Q
from django.db.utils import IntegrityError

WEEKDAYS = { '0': '周日',
             '1': '周一',
             '2': '周二',
             '3': '周三',
             '4': '周四',
             '5': '周五',
             '6': '周六'}
def take_md5(content):
    hash = hashlib.md5()    # 创建hash加密实例
    hash.update(content.encode("utf8"))    # hash加密
    result = hash.hexdigest()  # 得到加密结果
    return result


def log_out(request):
    del request.session['user_info']
    return redirect('/')


def login(request):
    """
    用户登录
    """
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            password = take_md5(password)
            user = models.UserInfo.objects.filter(name=name, password=password).first()
            if user:
                request.session['user_info'] = {'id': user.id, 'name': user.name}
                return redirect('/')
            else:
                form.add_error('password', '密码错误')
                return render(request, 'login.html', {'form': form})
        else:
            return render(request, 'login.html', {'form': form})


def reg(request):

    if request.method == "GET":
        form = RegForm()
        return render(request, 'reg.html', {'form': form})
    else:
        form = RegForm(request.POST)
        if form.is_valid():  # 获取表单数据
            name = form.cleaned_data['name']
            namefilter = models.UserInfo.objects.filter(name=name)
            if len(namefilter) > 0:
                form.add_error('name', '该用户名已存在!')
            else:
                password = form.cleaned_data['password']
                password2 = form.cleaned_data['password2']

                if password != password2:
                    form.add_error('password2', '两次输入密码不一致!')
                else:
                    emails = form.cleaned_data['emails']
                    password = take_md5(password)
                    userinfo = models.UserInfo(name=name, password=password, emails=emails)
                    userinfo.save()
                    pass
                    return render(request, 'success.html', {'name': name})
        else:
            return render(request, 'reg.html', {'form': form})
    return render(request, 'reg.html', {'form': form})


def fixpassword(request):
    return HttpResponse('想修改密码,留下你的微信!!!!!!!!!!')


def auth_json(func):
    def inner(request, *args, **kwargs):
        user_info = request.session.get('user_info')
        if not user_info:
            return redirect('/login/')
        return func(request, *args, **kwargs)
    return inner


@auth_json
def index(request):
    """
    会议室预定首页
    :param request:
    :return:
    """
    # 拿到所有的时间段
    time_choices = models.Booking.time_choices
    user_info = request.session.get('user_info')
    name = user_info['name']
    return render(request, 'index.html', {'time_choices': time_choices, 'name': name})


@auth_json
def booking(request):
    """
    获取会议室预定情况以及预定会议室
    :param request:
    :param date:
    :return:
    """
    ret = {'code': 1000, 'msg': None, 'data': None}
    current_date = datetime.datetime.now().date()  # 年月日
    if request.method == "GET":
        try:
            fetch_date = request.GET.get('date')  # 拿到前端传过来的转义过的字符串格式的日期
            fetch_device = request.GET.get('device')
            display = request.GET.get('display')
            if display == 'false':
                display=False
            else:
                display=True
            if not display and not fetch_device and fetch_date:
                fetch_date = datetime.datetime.strptime(fetch_date, '%Y-%m-%d').date()
                booking_info = []
                for i in range(1):
                    booking_date = fetch_date + datetime.timedelta(days=i)
                    weekday = WEEKDAYS[booking_date.strftime('%w')]
                    booking_list = models.Booking.objects.filter(booking_date=booking_date).select_related('room').order_by('booking_date')
                    booking_dict = {}  # 构建方便查询的大字典
                    for item in booking_list:  # item是每一个预定对象
                        if item.booking_time!=None:
                            if item.room_id not in booking_dict:  # 对象的room_id没在字典内
                                booking_dict[item.room_id] = {item.booking_time: {'name': item.user.name, 'date': str(item.booking_date)+' ('+weekday+')', 'task': item.task, 'status': item.status}}
                            else:  # 对象的room_id在字典内
                                if item.booking_time not in booking_dict[item.room_id]:  # 但是还有预定信息没在字典内
                                    booking_dict[item.room_id][item.booking_time] = {'name': item.user.name,'date': str(item.booking_date)+' ('+weekday+')', 'task': item.task, 'status': item.status}
                    room_list = models.MeetingRoom.objects.all()  # 数组【所有房间对象】
                    for room in room_list:
                        if room.id not in booking_dict:
                            continue
                        if booking_dict:
                            temp = [{'text': room.title, 'id':'device','attrs': {'rid': room.id}},{'text':None,'id':'date'}]
                            for choice in models.Booking.time_choices:
                                v = {'text': '', 'attrs': {'time-id': choice[0], 'room-id': room.id}, 'status': None}
                                if room.id in booking_dict and choice[0] in booking_dict[room.id]:  # 说明已有预定信息
                                    if booking_dict[room.id][choice[0]]['task'] != None:
                                        v['text'] = booking_dict[room.id][choice[0]]['name'] +'【'+ booking_dict[room.id][choice[0]]['task'] + '】'# 预订人名
                                        v['status'] = booking_dict[room.id][choice[0]]['status']
                                        temp[1]['text'] = booking_dict[room.id][choice[0]]['date']
                                temp.append(v)
                            booking_info.append(temp)
                        else:
                            ret['msg'] = '没有找到该日期的设备排期'
                ret['data'] = booking_info
            elif not display and fetch_device and not fetch_date:
                booking_info = []
                for i in range(7):
                    booking_date = current_date + datetime.timedelta(days=i)
                    weekday = WEEKDAYS[booking_date.strftime('%w')]
                    try:
                        device_id = models.MeetingRoom.objects.filter(title=fetch_device).first()
                        booking_list = models.Booking.objects.filter(booking_date=booking_date, room_id=device_id.id).order_by('booking_date')
                        booking_dict = {}  # 构建方便查询的大字典
                        for item in booking_list:  # item是每一个预定对象
                            if item.booking_time!=None:
                                if item.room_id not in booking_dict:  # 对象的room_id没在字典内
                                    booking_dict[item.room_id] = {item.booking_time: {'name': item.user.name,'date': str(item.booking_date)+' ('+weekday+')', 'task': item.task, 'status': item.status}}
                                else:  # 对象的room_id在字典内
                                    if item.booking_time not in booking_dict[item.room_id]:  # 但是还有预定信息没在字典内
                                        booking_dict[item.room_id][item.booking_time] = {'name': item.user.name,'date': str(item.booking_date)+' ('+weekday+')', 'task': item.task, 'status': item.status}
                        room_list = models.MeetingRoom.objects.filter(id=device_id.id)  # 数组【所有房间对象】
                        for room in room_list:
                            if booking_dict:
                                temp = [{'text': room.title, 'id': 'device', 'attrs': {'rid': room.id}},{'text':None, 'id':'date'}]
                                for choice in models.Booking.time_choices:
                                    v = {'text': '','id':'data','attrs': {'time-id': choice[0], 'room-id': room.id}, 'status': None}
                                    if room.id in booking_dict and choice[0] in booking_dict[room.id]:  # 说明已有预定信息
                                        if booking_dict[room.id][choice[0]]['task'] != None:
                                            v['text'] = booking_dict[room.id][choice[0]]['name'] +'【'+ booking_dict[room.id][choice[0]]['task'] +'】'  # 预订人名
                                            v['status'] = booking_dict[room.id][choice[0]]['status']
                                            temp[1]['text'] = booking_dict[room.id][choice[0]]['date']
                                    temp.append(v)
                                booking_info.append(temp)
                    except Exception as e:
                        ret['code'] = 400
                        ret['msg']='没有找到相关设备'
                ret['data'] = booking_info
            elif not display and not fetch_device and not fetch_date:
                booking_info = []
                for i in range(50):
                    booking_date = current_date + datetime.timedelta(days=i)
                    weekday = WEEKDAYS[booking_date.strftime('%w')]
                    booking_list = models.Booking.objects.filter(booking_date=booking_date).select_related('room').order_by('booking_date')
                    booking_dict = {}  # 构建方便查询的大字典
                    for item in booking_list:  # item是每一个预定对象
                        if item.booking_time!=None:
                            if item.room_id not in booking_dict:  # 对象的room_id没在字典内
                                booking_dict[item.room_id] = {item.booking_time: {'name': item.user.name, 'date': str(item.booking_date)+' ('+weekday+')', 'task': item.task, 'status': item.status}}
                            else:  # 对象的room_id在字典内
                                if item.booking_time not in booking_dict[item.room_id]:  # 但是还有预定信息没在字典内
                                    booking_dict[item.room_id][item.booking_time] = {'name': item.user.name,'date': str(item.booking_date)+' ('+weekday+')', 'task': item.task, 'status': item.status}
                    room_list = models.MeetingRoom.objects.all()  # 数组【所有房间对象】
                    for room in room_list:
                        if room.id not in booking_dict:
                            continue
                        if booking_dict:
                            temp = [{'text': room.title, 'id':'device','attrs': {'rid': room.id}},{'text':None,'id':'date'}]
                            for choice in models.Booking.time_choices:
                                v = {'text': '','id':'data','attrs': {'time-id': choice[0], 'room-id': room.id},'status':None}
                                if room.id in booking_dict and choice[0] in booking_dict[room.id]:  # 说明已有预定信息
                                    if booking_dict[room.id][choice[0]]['task'] != None:
                                        v['text'] = booking_dict[room.id][choice[0]]['name'] +'【'+ booking_dict[room.id][choice[0]]['task'] + '】'  # 预订人名
                                        v['status'] = booking_dict[room.id][choice[0]]['status']
                                        temp[1]['text'] = booking_dict[room.id][choice[0]]['date']
                                temp.append(v)
                            booking_info.append(temp)
                        else:
                            ret['msg'] = '尚未添加任何设备排期'
                ret['data'] = booking_info
            elif not display and fetch_device and fetch_date:
                booking_date = datetime.datetime.strptime(fetch_date, '%Y-%m-%d').date()
                booking_info = []
                weekday = WEEKDAYS[booking_date.strftime('%w')]
                device_id = models.MeetingRoom.objects.filter(title=fetch_device).first()
                booking_list = models.Booking.objects.filter(booking_date=booking_date,room_id=device_id.id).select_related('room').order_by('booking_date')
                booking_dict = {}  # 构建方便查询的大字典
                for item in booking_list:  # item是每一个预定对象
                    if item.booking_time!=None:
                        if item.room_id not in booking_dict:  # 对象的room_id没在字典内
                            booking_dict[item.room_id] = {item.booking_time: {'name': item.user.name, 'date': str(item.booking_date)+' ('+weekday+')', 'task': item.task, 'status': item.status}}
                        else:  # 对象的room_id在字典内
                            if item.booking_time not in booking_dict[item.room_id]:  # 但是还有预定信息没在字典内
                                booking_dict[item.room_id][item.booking_time] = {'name': item.user.name,'date': str(item.booking_date)+' ('+weekday+')', 'task': item.task, 'status': item.status}
                room_list = models.MeetingRoom.objects.all()  # 数组【所有房间对象】
                for room in room_list:
                    if room.id not in booking_dict:
                        continue
                    if booking_dict:
                        temp = [{'text': room.title, 'id':'device','attrs': {'rid': room.id}},{'text':None,'id':'date'}]
                        for choice in models.Booking.time_choices:
                            v = {'text': '','id':'data','attrs': {'time-id': choice[0], 'room-id': room.id}, 'status': None}
                            if room.id in booking_dict and choice[0] in booking_dict[room.id]:  # 说明已有预定信息
                                if booking_dict[room.id][choice[0]]['task'] != None:
                                    v['text'] = booking_dict[room.id][choice[0]]['name'] +'【'+ booking_dict[room.id][choice[0]]['task'] + '】'  # 预订人名
                                    v['status'] = booking_dict[room.id][choice[0]]['status']
                                    temp[1]['text'] = booking_dict[room.id][choice[0]]['date']
                            temp.append(v)
                        booking_info.append(temp)
                    else:
                        ret['msg'] = '没有找到该日期的设备排期'
                ret['data'] = booking_info
            else:
                booking_info = []
                if fetch_date:
                    fetch_date = datetime.datetime.strptime(fetch_date, '%Y-%m-%d').date()
                else:
                    fetch_date = current_date
                for i in range(7):
                    booking_date = fetch_date + datetime.timedelta(days=i)
                    weekday = WEEKDAYS[booking_date.strftime('%w')]
                    try:
                        device_id = models.MeetingRoom.objects.filter(title=fetch_device).first()
                        booking_list = models.Booking.objects.filter(booking_date=booking_date, room_id=device_id.id).order_by('booking_date')
                        booking_dict = {}  # 构建方便查询的大字典
                        for item in booking_list:  # item是每一个预定对象
                            if item.booking_time!=None:
                                if item.room_id not in booking_dict:  # 对象的room_id没在字典内
                                    booking_dict[item.room_id] = {item.booking_time: {'name': item.user.name,'date': str(item.booking_date)+' ('+weekday+')', 'task': item.task, 'status': item.status}}
                                else:  # 对象的room_id在字典内
                                    if item.booking_time not in booking_dict[item.room_id]:  # 但是还有预定信息没在字典内
                                        booking_dict[item.room_id][item.booking_time] = {'name': item.user.name,'date': str(item.booking_date)+' ('+weekday+')', 'task': item.task, 'status': item.status}
                            else:
                                if item.room_id not in booking_dict:  # 对象的room_id没在字典内
                                    booking_dict[item.room_id] = {item.booking_date:{'name': item.user.name,'task': item.task}}
                                else:  # 对象的room_id在字典内
                                    if item.booking_date not in booking_dict[item.room_id]:  # 但是还有预定信息没在字典内
                                        booking_dict[item.room_id][item.booking_date] ={'name': item.user.name,'task': item.task}
                        room_list = models.MeetingRoom.objects.filter(id=device_id.id)  # 数组【所有房间对象】
                        for room in room_list:
                            if booking_dict:
                                temp = [{'text': room.title, 'id': 'device', 'attrs': {'rid': room.id}},{'text':str(booking_date)+' ('+weekday+')', 'id':'date'}]
                                for choice in models.Booking.time_choices:
                                    if room.id in booking_dict:
                                        if choice[0] in booking_dict[room.id]:  # 说明已有预定信息
                                            v = {'text': '','id':'data','attrs': {'time-id': choice[0], 'room-id': room.id}, 'status': None}
                                            v['text'] = booking_dict[room.id][choice[0]]['name'] +'【'+ booking_dict[room.id][choice[0]]['task'] +'】'  # 预订人名
                                            v['status'] = booking_dict[room.id][choice[0]]['status']
                                            temp[1]['text'] = booking_dict[room.id][choice[0]]['date']
                                        else:
                                            v = {'text': '', 'id':'data','attrs': {'time-id': choice[0], 'room-id': room.id}, 'status': None}
                                        temp.append(v)
                                booking_info.append(temp)
                    except Exception as e:
                        ret['code'] = 401
                        ret['msg']="设备信息获取失败"
                ret['data'] = booking_info
        except Exception as e:
            ret['code'] = 1001
            ret['msg'] = str(e)
            raise e
        return JsonResponse(ret)
    else:
        try:
            if request.POST.get('flag')=='true':
                device_id = request.POST.get('device_id')
                device_name = request.POST.get('device')
                models.MeetingRoom.objects.filter(id=device_id).update(title=device_name)
            else:
                booking_info = json.loads(request.POST.get('data'))
                status = request.POST.get('status')
                for room_id, time_id_list in booking_info['add'].items():
                    if room_id not in booking_info['del']:
                        continue
                    for time_id in list(time_id_list):
                        # 同时点了增加和删除，即用户在选择之后反悔了。。
                        if time_id in booking_info['del'][room_id]:
                            booking_info['del'][room_id].remove(time_id)
                            booking_info['add'][room_id].remove(time_id)

                add_booking_list = []
                for room_id, time_id_list in booking_info['add'].items():
                    for time_id in time_id_list:
                        booking_date = datetime.datetime.strptime(time_id[1], '%Y-%m-%d').date()
                        res = models.Booking.objects.filter(user_id=request.session['user_info']['id'],
                                                      room_id=room_id,
                                                      booking_date=booking_date).first()
                        if status == 'scheduling':
                            if res.booking_time == None:
                                models.Booking.objects.filter(user_id=request.session['user_info']['id'],
                                                          room_id=room_id,
                                                          booking_date=booking_date).update(booking_time=time_id[0],
                                                                                            task=time_id[-1],
                                                                                            status=status)
                            else:
                                obj = models.Booking(
                                    user_id=request.session['user_info']['id'],
                                    room_id=room_id,
                                    booking_time=time_id[0],
                                    booking_date=booking_date,
                                    task=time_id[-1],
                                    status=status)
                                obj.save()
                        if status == 'scheduled':
                            models.Booking.objects.filter(status='scheduling').update(status=status)
                
                remove_booking = Q()
                tmp = list()
                for room_id, time_id_list in booking_info['del'].items():
                    for time_id in time_id_list:
                        booking_date = datetime.datetime.strptime(time_id[1], '%Y-%m-%d').date()
                        temp = Q()
                        temp.connector = 'AND'
                        temp.children.append(('booking_date', booking_date,))
                        temp.children.append(('room_id', room_id,))
                        temp.children.append(('booking_time', time_id[0],))
                        remove_booking.add(temp, 'OR')
                        tmp=[room_id, booking_date]
                if remove_booking:
                    models.Booking.objects.filter(remove_booking).delete()
                    obj = models.Booking(user_id=request.session['user_info']['id'],
                                         room_id=tmp[0],
                                         booking_date=tmp[1])
                    obj.save()
                existed_devices = models.MeetingRoom.objects.all()
                for device in existed_devices:
                    res = models.Booking.objects.filter(room_id=device.id)
                    if not res:
                        models.MeetingRoom.objects.filter(id=device.id).delete()
        except IntegrityError as e:
            ret['code'] = 1011
            ret['msg'] = str(e)
        except Exception as e:
            ret['code'] = 1012
            ret['msg'] = '预定失败：%s' % str(e)
    return JsonResponse(ret)


@auth_json
def addevice(request):
    """
    设备排期
    """
    ret = {'code': 200, 'msg': None, 'data': None}
    user_info = request.session.get('user_info')
    if request.method == 'POST':
        models.Booking.objects.filter(booking_time=None).delete()
        existed_devices = models.MeetingRoom.objects.all()
        for device in existed_devices:
            res = models.Booking.objects.filter(room_id=device.id)
            if not res:
                models.MeetingRoom.objects.filter(id=device.id).delete()
        form = DeviceForm(request.POST)
        if form.is_valid():
            device_name = request.POST.get('device')
            fetch_date = request.POST.get('date')
            fetch_date = datetime.datetime.strptime(fetch_date, '%Y-%m-%d').date()
            try:
                device = models.MeetingRoom(title=device_name)
                device.save()
                device_id = models.MeetingRoom.objects.filter(title=device_name).first()
                is_existed = models.Booking.objects.filter(room_id=device_id.id)
                if not is_existed:
                    for i in range(7):
                        booking_date = fetch_date + datetime.timedelta(days=i)
                        add_device=models.Booking(booking_date=booking_date,
                                                  room_id=device_id.id,
                                                  user_id=request.session['user_info']['id'])
                        add_device.save()
                ret['msg'] = '设备添加成功'
            except Exception as e:
                ret['code'] = 400
                ret['msg'] = '设备已存在'
        return JsonResponse(ret)
    else:
        device_name = request.GET.get('device')
        device_info = models.MeetingRoom.objects.filter(title=device_name).first()
        ret['data'] = device_info.id
        return JsonResponse(ret)
