#!/bin/sh

filepath=$(cd "$(dirname "$0")";pwd)
cd $filepath

# start the env as such command: ./run.sh start default | production

export FILE_ENV=$2
LOGDIR='/home/admin/output/py-fileserver/logs'
export LOGDIR=$LOGDIR
ROOT=`pwd`
export PROJECT_DIR=$ROOT

start()
{
    echo 'start ...'
    echo 'start supervisord ...'
    pid=$(pgrep -f "supervisord -c web.conf")
    if [ "x$pid" == "x" ];then
        supervisord -c web.conf
    else
        supervisorctl -c web.conf start all
    fi
    sleep 3
    supervisorctl -c web.conf status
}

stop()
{
    echo 'stop ...'
    pid=$(pgrep -f "supervisord -c web.conf")
    if [ "x$pid" != "x" ];then
        supervisorctl -c web.conf stop all
        supervisorctl -c web.conf shutdown
        sleep 2
    fi
}

init()
{
    echo 'init ...'

    cd /home/admin/py-fileserver/
    mkdir -p /home/admin/output/py-fileserver/log/
    mkdir -p /home/admin/py-fileserver/supervisor
    sudo pip install -r requirements.txt
}


case $1 in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        echo "restart ..."
        stop
        start
        ;;
    status)
        supervisorctl -c web.conf status
        ;;
esac
