# Generated by Django 3.1.5 on 2021-01-29 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meet', '0006_auto_20210128_1611'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='devices',
            options={'ordering': ['-schedule_date'], 'verbose_name': '设备排期管理', 'verbose_name_plural': '设备排期管理'},
        ),
        migrations.AddField(
            model_name='devices',
            name='schedule_date',
            field=models.DateField(default=None, verbose_name='占用日期'),
        ),
        migrations.AddField(
            model_name='devices',
            name='schedule_time',
            field=models.IntegerField(choices=[(0, '0:00'), (1, '1:00'), (2, '2:00'), (3, '3:00'), (4, '4:00'), (5, '5:00'), (6, '6:00'), (7, '7:00'), (8, '8:00'), (9, '9:00'), (10, '10:00'), (11, '11:00'), (12, '12:00'), (13, '13:00'), (14, '14:00'), (15, '15:00'), (16, '16:00'), (17, '17:00'), (18, '18:00'), (19, '19:00'), (20, '20:00'), (21, '21:00'), (22, '22:00'), (23, '23:00')], default=None, verbose_name='占用时间'),
        ),
        migrations.AlterUniqueTogether(
            name='devices',
            unique_together={('schedule_date', 'schedule_time', 'device')},
        ),
    ]