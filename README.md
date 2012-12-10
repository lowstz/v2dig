v2dig
=====

安装
-----------------
```
git clone https://github.com/lowstz/v2dig.git v2dig
cd v2dig
virtualenv ./v2digenv
source v2digenv/bin/activate
pip install -r requirement.txt
```

运行
-----------------
```
python app.py --port=8000
```

部署
-----------------
部署到生产环境的请参考nginx.conf和supervisord.conf两个文件
