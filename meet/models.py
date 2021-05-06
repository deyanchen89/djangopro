# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class UserInfo(models.Model):
    name = models.CharField(verbose_name='用户姓名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=32)
    emails = models.EmailField(verbose_name='电子邮件', max_length=50, default=None)

    class Meta:
        verbose_name = '用户管理'
        verbose_name_plural = '用户管理'

    def __unicode__(self):
        return self.name


class MeetingRoom(models.Model):
    title = models.CharField(verbose_name='设备名称', max_length=32)

    class Meta:
        verbose_name = '设备管理管理'
        verbose_name_plural = '设备管理'
        unique_together = (
            ('title',)
        )

    def __unicode__(self):
        return self.title


class Booking(models.Model):
    user = models.ForeignKey(verbose_name='用户', to='UserInfo', on_delete=models.CASCADE)
    room = models.ForeignKey(verbose_name='设备名称', to='MeetingRoom', on_delete=models.CASCADE)
    booking_date = models.DateField(verbose_name='预定日期')
    time_choices = (
        (0, '0:00'),
        (1, '1:00'),
        (2, '2:00'),
        (3, '3:00'),
        (4, '4:00'),
        (5, '5:00'),
        (6, '6:00'),
        (7, '7:00'),
        (8, '8:00'),
        (9, '9:00'),
        (10, '10:00'),
        (11, '11:00'),
        (12, '12:00'),
        (13, '13:00'),
        (14, '14:00'),
        (15, '15:00'),
        (16, '16:00'),
        (17, '17:00'),
        (18, '18:00'),
        (19, '19:00'),
        (20, '20:00'),
        (21, '21:00'),
        (22, '22:00'),
        (23, '23:00'),
    )
    booking_time = models.IntegerField(verbose_name='预定时间段', choices=time_choices,null=True)
    task = models.CharField(verbose_name='事务项', max_length=255, default=None, null=True)
    status = models.CharField(verbose_name='事务项', max_length=255, default=None, null=True)
    class Meta:
        verbose_name = '设备排期平台管理'
        verbose_name_plural = '设备排期平台管理'
        # ordering = ['-booking_date']
        # unique_together = (
        #     ('booking_date', 'booking_time', 'room')
        # )

    def __unicode__(self):
        return str(self.booking_date) + '-' + str(self.booking_time) + '-' + self.room.title


