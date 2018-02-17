# my-ctf-xinetd
fast deploy pwn , using docker &amp; ctf_xinted

---

# 致谢
感谢ctf\_xinetd提供的方法：[https://github.com/Eadom/ctf_xinetd](https://github.com/Eadom/ctf_xinetd)

通过包装，使pwn的搭建更加便捷。

# 使用方法

初始目录环境：

```
.
├── deploy.py
└── pwn1
    ├── flag
    └── pwn1
```

`pwn1`为二进制文件的名字，创建相同的文件名名字，结构如上。

---

当前目录执行命令：

```
#usage: ./deploy.py ProjectPath ExposePort LinuxVersion [timeout(120 for default, 0 to cancel timeout)]
./deploy.py pwn1 10001 ubuntu:16.04
./deploy.py pwn1 10001 ubuntu:16.04 60
./deploy.py pwn1 10001 ubuntu:16.04 0
```

---

搭建完成后的文件目录：

```
.
├── ctf_xinetd
│   ├── bin
│   │   ├── flag
│   │   └── pwn1
│   ├── ctf.xinetd
│   ├── Dockerfile
│   └── start.sh
├── deploy.py
├── pwn1
│   ├── flag
│   └── pwn1
└── libc
    ├── libc32.so
    └── libc64.so
```

libc为docker环境中的libc，提供给选手使用。

# END

enjoy :)