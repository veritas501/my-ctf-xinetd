#!/usr/bin/python
#coding=utf8

import os
from os import system
from os import popen
import sys
from time import sleep
if (len(sys.argv) != 4) and (len(sys.argv) != 5):
    print 'usage: %s ProjectPath ExposePort LinuxVersion [timeout(120 for default, 0 to cancel timeout)]' % sys.argv[0]
    exit(0)

dockerfile='''FROM %s

RUN sed -i "s/http:\/\/archive.ubuntu.com/http:\/\/mirrors.163.com/g" /etc/apt/sources.list
RUN sed -i "s/http:\/\/security.ubuntu.com/http:\/\/mirrors.163.com/g" /etc/apt/sources.list
RUN apt-get update && apt-get -y dist-upgrade
RUN apt-get install -y lib32z1 xinetd

RUN useradd -m ctf

COPY ./bin/ /home/ctf/
COPY ./ctf.xinetd /etc/xinetd.d/ctf
COPY ./start.sh /start.sh
RUN echo "Blocked by ctf_xinetd" > /etc/banner_fail

RUN chmod +x /start.sh
RUN chown -R root:ctf /home/ctf
RUN chmod -R 750 /home/ctf
RUN chmod 740 /home/ctf/flag

RUN cp -R /lib* /home/ctf
RUN cp -R /usr/lib* /home/ctf

RUN mkdir /home/ctf/dev
RUN mknod /home/ctf/dev/null c 1 3
RUN mknod /home/ctf/dev/zero c 1 5
RUN mknod /home/ctf/dev/random c 1 8
RUN mknod /home/ctf/dev/urandom c 1 9
RUN chmod 666 /home/ctf/dev/*

RUN mkdir /home/ctf/bin
RUN cp /bin/sh /home/ctf/bin
RUN cp /bin/ls /home/ctf/bin
RUN cp /bin/cat /home/ctf/bin
RUN cp /usr/bin/timeout /home/ctf/bin

WORKDIR /home/ctf

CMD ["/start.sh"]

EXPOSE 9999
''' %sys.argv[3]

startsh='''#!/bin/sh
# Add your startup script

# DO NOT DELETE
/etc/init.d/xinetd start;
sleep infinity;
'''

ctf_xinetd='''service ctf
{
    disable = no
    socket_type = stream
    protocol    = tcp
    wait        = no
    user        = root
    type        = UNLISTED
    port        = 9999
    bind        = 0.0.0.0
    server      = /usr/sbin/chroot
    server_args = --userspec=1000:1000 /home/ctf ./run.sh
    banner_fail = /etc/banner_fail
    # safety options
    per_source    = 5 # the maximum instances of this service per source IP address
    rlimit_cpu    = 3 # the maximum number of CPU seconds that the service may use
    #rlimit_as  = 1024M # the Address Space resource limit for the service
    #access_times = 2:00-9:00 12:00-24:00
}
'''

timeout = 120

if len(sys.argv) == 5:
	timeout = int(sys.argv[4])

if timeout == 0:
	runsh='''
#!/bin/sh
#
exec 2>/dev/null
./%s
''' % sys.argv[1]
else:
	runsh='''
#!/bin/sh
#
exec 2>/dev/null
timeout %d ./%s
''' % (timeout,sys.argv[1])


system('rm -rf ctf_xinetd')
system('rm -rf libc')
system('mkdir ctf_xinetd')
system('mkdir ctf_xinetd/bin')

open('ctf_xinetd/Dockerfile','w').write(dockerfile)
open('ctf_xinetd/ctf.xinetd','w').write(ctf_xinetd)
open('ctf_xinetd/start.sh','w').write(startsh)
open('ctf_xinetd/bin/run.sh','w').write(runsh)

system('cp %s/* ctf_xinetd/bin/'%sys.argv[1])
system('chmod +x ctf_xinetd/bin/%s'%sys.argv[1])
system('chmod +x ctf_xinetd/bin/run.sh')
system('chmod +x ctf_xinetd/start.sh')

if popen("sudo docker images -q %s" % sys.argv[1]).read() == '':
    system('sudo docker build -t "%s" ./ctf_xinetd'%sys.argv[1])
else:
    if_rm = raw_input("\033[0;31mimage already exist, remove or just run it ?[rm/run]\n\033[0m")
    system('sudo docker stop $(sudo docker ps -aq --filter "name=%s")' % sys.argv[1])
    system('sudo docker rm $(sudo docker ps -aq --filter "name=%s")' % sys.argv[1])
    if if_rm == 'rm':
        system('sudo docker rmi $(sudo docker images -q %s)' % sys.argv[1])
        system('sudo docker build -t "%s" ./ctf_xinetd'%sys.argv[1])

sleep(1)
system('sudo docker run --ulimit nproc=1024:2048 -d -p "0.0.0.0:%s:9999" -h "%s" --name="%s" %s'%(sys.argv[2],sys.argv[1],sys.argv[1],sys.argv[1]))


######
system('mkdir libc')
system('sudo docker cp --follow-link %s:lib/x86_64-linux-gnu/libc.so.6 libc/libc64.so'%sys.argv[1])
system('sudo docker cp --follow-link %s:lib32/libc.so.6 libc/libc32.so'%sys.argv[1])

print '''\033[0;32m
============================
||  [+] Deploy finish :)  ||
============================

try nc 0 %s\033[0m
'''%sys.argv[2]
