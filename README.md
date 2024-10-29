## Chat-Agent
A chatbot that can be deployed on WeChat and utilizes COT and React technologies

## 安装各种依赖
cd ./Chat-Agent
sh requirements.sh
pip install -e .

## mongoDB 部署
```bash
    cd ~
    wget https://repo.mongodb.org/apt/ubuntu/dists/jammy/mongodb-org/7.0/multiverse/binary-amd64/mongodb-org-server_7.0.3_amd64.deb
    sudo dpkg -i  mongodb-org-server_7.0.3_amd64.deb
    sudo systemctl enable mongod
    wget https://downloads.mongodb.com/compass/mongodb-compass_1.40.4_amd64.deb
    sudo dpkg -i mongodb-compass_1.40.4_amd64.deb
    # 解决无法启动 bug
    sudo rm /tmp/mongodb-27017.sock
    sudo mkdir -p /data/db
    sudo chown -R `id -u`:`id -g` /data/db
    sudo systemctl start mongod
    sudo systemctl status mongod
    # 修改 /etc/mongod.conf，让其可以远程访问
    # 修改为以下内容，进去改一改对应的部分
    net:
        port: 27017
        bindIp: 0.0.0.0
```

## wxpyit 部署 （单聊能用，但是群聊有问题）
```bash
    # 基于 config-template.py， 创建一个 private_config.py
    python app_on_wxpyit.py
```

## 以下为 ubuntu XYbot 部署, 比较复杂, 但是功能强大
```bash
    # 安装 wine
    sudo dpkg --add-architecture i386
    wget -nc https://dl.winehq.org/wine-builds/winehq.key
    sudo apt-key add winehq.key
    sudo add-apt-repository 'deb https://dl.winehq.org/wine-builds/ubuntu/ lunar main'
    sudo apt-get update
    sudo apt-get install -y wine-stable wine-stable-i386
    sudo apt-get install -y wine64 wine32
    sudo apt-get install -y winehq-stable

    # 下载 WeChatSetup-3.9.10.27.exe
    wget https://github.com/tom-snow/wechat-windows-versions/releases/download/v3.9.10.27/WeChatSetup-3.9.10.27.exe
    wine WeChatSetup-3.9.10.27.exe
```

# 运行
```bash
    # 基于 config-template.py， 创建一个 private_config.py
    python app_on_xybot.py
```

# 后台运行（可选）
```bash
    sh run.sh
```

# vnc docker 部署（可选）
dockerfile
```docker
    # 使用 Ubuntu 24.04 基础镜像
    FROM ubuntu:24.04
    # 更新包列表并安装工具
    RUN apt-get update && apt-get install -y \
        wget \
        curl \
        gnupg \
        software-properties-common \
        git \
        nano \
        sudo
    # 添加 NodeSource 的签名密钥和 PPA 并安装 Node.js LTS 版本
    RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
        apt-get install -y nodejs
    # 安装 Xfce 桌面环境和 VNC 服务器
    RUN apt-get install -y xfce4 xfce4-goodies \
        tightvncserver \
        dbus-x11 \
        x11-xserver-utils
    # 创建新用户并配置密码
    # password 替换为你的 VNC 密码
    RUN useradd -m -s /bin/bash username && echo 'username:password' | chpasswd && \
        usermod -aG sudo username
    # 复制当前文件夹下的 noVNC 文件夹到容器内的 /app 目录
    COPY noVNC /app/noVNC
    RUN ls /app/noVNC/utils
    # 根用户以复制启动脚本
    USER root
    COPY start_vnc.sh /usr/local/bin/start_vnc.sh
    RUN chmod +x /usr/local/bin/start_vnc.sh
    # 设置 VNC 服务器配置
    # password 替换为你的 VNC 密码
    USER username
    ENV USER=username
    RUN mkdir -p /home/username/.vnc && \
        echo "password" | vncpasswd -f > /home/username/.vnc/passwd && \
        chmod 600 /home/username/.vnc/passwd && \
        echo "startxfce4 &" > /home/username/.vnc/xstartup && \
        chmod +x /home/username/.vnc/xstartup
    # 暴露 VNC 端口
    EXPOSE 5901
    # 启动 VNC 服务器和 Xfce
    CMD ["/usr/local/bin/start_vnc.sh"]
```

start_vnc.sh
```bash
    #!/bin/bash
    # 设置环境变量
    export USER=username  # 修改为新用户 username
    export HOME=/home/username  # 修改为新用户的主目录
    # 启动 VNC 服务器并设置显示参数
    vncserver :1 -geometry 1280x800 -depth 24
    # 保持容器运行
    # tail -f /dev/null
    # 8888 是你将暴露给Web浏览器的WebSocket端口，而 localhost:5901 是你的VNC服务器运行的地址和端口。
    /app/noVNC/utils/novnc_proxy --listen 8888 --vnc localhost:5901
```

init.sh
```bash
    # 注意！执行前请先下载 [noVNC](https://github.com/novnc/noVNC) 到当前目录！
    docker build -t ubuntu24.04-nodejs-vnc .
    docker rm -f username
    # 5911 vnc客户端端口，8888 noVNC 网页控制端口
    docker run -d --name username -p 5911:5901 -p 8888:8888 ubuntu24.04-nodejs-vnc
```

# 连接docker命令 (可选)
```bash
    docker run -d --name username \
    -p 5911:5901 -p 8888:8888 \
    --add-host dldir1.qq.com:127.0.0.1 \
    --add-host=host.docker.internal:<填你的宿主机IP> \
    # --gpus all \  # 可选
    ubuntu24.04-nodejs-vnc tail -f /dev/null
```

# vnc 重置脚本 (可选)
```bash
    # 连接不上用这个
    vncserver -list
    vncserver -kill :1
    vncserver -kill :2
    vncserver -kill :3
    sudo rm -rf /tmp/.X1-lock
    sudo sh clean.sh
    vncserver :1
```

# 浏览器 vnc 桌面
http://<你的IP>:8888/vnc.html


# 感谢

https://github.com/HenryXiaoYang/XYBot

https://github.com/fxconfig/wxpyit







