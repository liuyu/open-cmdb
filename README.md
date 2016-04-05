# 简介

OPEN-CMDB是使用Python、Django、Puppet开发的一套简单的CMDB系统。

# 部署open-cmdb

## 1. 安装依赖:

    要求: python2.7

    #确认python编译包有装, 否则mysql/curl模块可能无法编译:
    yum install python-devel
    yum install libcurl-devel

    pip install -r ./requirements.txt


## 2. 初始化数据库

    # 如果有cmdb库, 先删掉
    # mysql -u root -p -e "DROP DATABASE cmdb;"

    mysql -u root -p -e "CREATE DATABASE cmdb CHARACTER SET='utf8';"

    # 修改 ./local_settings.py 中的数据库密码配置后, 运行:

    python ./manage.py syncdb --noinput
    # python ./manage.py migrate


## 3. 创建管理员账户, 密码建议使用12位字母数字随机串

    python ./manage.py createsuperuser --username=admin --email=admin@example.com


## 4. 运行open-cmdb:

    python ./manage.py runfcgi method=threaded host=127.0.0.1 port=8000

    #如需停止, 请执行:

    kill -9 `ps aux | grep port=8000 | awk '{print $2}'`


## 5. 设置nginx代理8000端口, server配置:

    # 注意 /data/open-cmdb/static/ 目录需要nginx用户可读, 否则访问静态文件会报403.

    server {
        listen   80;
        server_name cmdb.xxxx.com;

        client_max_body_size 2G;

        location / {
            fastcgi_pass 127.0.0.1:8000;
            fastcgi_param PATH_INFO $fastcgi_script_name;
            fastcgi_param REQUEST_METHOD $request_method;
            fastcgi_param QUERY_STRING $query_string;
            fastcgi_param CONTENT_TYPE $content_type;
            fastcgi_param CONTENT_LENGTH $content_length;
            fastcgi_pass_header Authorization;
            fastcgi_intercept_errors off;
            fastcgi_param SERVER_PROTOCOL $server_protocol;
            fastcgi_param SERVER_PORT $server_port;
            fastcgi_param SERVER_NAME $server_name;
        }
        location /static/ {
            root /data/open-cmdb/;
        }
    }
