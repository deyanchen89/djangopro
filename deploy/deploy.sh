#!/usr/bin/env bash

DATE=`date +%Y%m%d%H%M%S`

# 前置
# 杀掉 python django
ps aux | grep manage.py | awk '{print$2}' | xargs kill -9

# 关闭 nginx
/etc/init.d/nginx stop

# 步骤1、更新框架、更新用例
GIT_FRAMEWORK_PATH="/home/ubuntu/Code/device_scheduling"
# 确保代码跟远程仓库一样
cd $GIT_FRAMEWORK_PATH && git reset --hard
cd $GIT_FRAMEWORK_PATH && git pull
# 二次确认，防止第一次发现不一样然后更新
cd $GIT_FRAMEWORK_PATH && git reset --hard
cd $GIT_FRAMEWORK_PATH && git pull

# 步骤2、更新配置文件
# 更新 nginx 配置文件，拉起 nginx 服务器
cp "$GIT_FRAMEWORK_PATH/deploy/device_platform.txt" /etc/nginx/sites-available/device_platform.txt
/etc/init.d/nginx start

# 3、开启 python django
/home/ubuntu/Code/device_scheduling/.venv/bin/python /home/ubuntu/Code/device_scheduling/manage.py runserver