#!/usr/bin/python
#coding=utf8

import os
from os import system
import sys

if len(sys.argv) != 4:
	print 'usage: %s ProjectPath ExposePort LinuxVersion' % sys.argv[0]
	exit(0)

dockerfile='''FROM %s

RUN sed -i "s/http:\/\/archive.ubuntu.com/http:\/\/mirrors.tuna.tsinghua.edu.cn/g" /etc/apt/sources.list
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
    # replace helloworld to your program
    server_args = --userspec=1000:1000 /home/ctf ./%s
    banner_fail = /etc/banner_fail
    # safety options
    per_source	= 10 # the maximum instances of this service per source IP address
    rlimit_cpu	= 20 # the maximum number of CPU seconds that the service may use
    #rlimit_as  = 1024M # the Address Space resource limit for the service
    #access_times = 2:00-9:00 12:00-24:00
}
''' % sys.argv[1]

system('rm -rf ctf_xinetd')
system('rm -rf libc')
system('mkdir ctf_xinetd')
system('mkdir ctf_xinetd/bin')

open('ctf_xinetd/Dockerfile','w').write(dockerfile)
open('ctf_xinetd/ctf.xinetd','w').write(ctf_xinetd)
open('ctf_xinetd/start.sh','w').write(startsh)

system('cp %s/* ctf_xinetd/bin/'%sys.argv[1])
system('chmod +x ctf_xinetd/bin/%s'%sys.argv[1])
system('chmod +x ctf_xinetd/start.sh')

system('sudo docker build -t "%s" ./ctf_xinetd'%sys.argv[1])

system('sudo docker run -d -p "0.0.0.0:%s:9999" -h "%s" --name="%s" %s'%(sys.argv[2],sys.argv[1],sys.argv[1],sys.argv[1]))


######
system('mkdir libc')
system('sudo docker cp --follow-link %s:lib/x86_64-linux-gnu/libc.so.6 libc/libc64.so'%sys.argv[1])
system('sudo docker cp --follow-link %s:lib32/libc.so.6 libc/libc32.so'%sys.argv[1])

print '''
============================
||  [+] Deploy finish :)  ||
============================

try nc 0.0.0.0 %s
'''%sys.argv[2]
