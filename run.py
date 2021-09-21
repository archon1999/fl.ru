import os

os.system('cd app && nohup python3.9 manage.py runserver 0.0.0.0:7777 > ../log/server.log &')
os.system('cd parser && nohup python3.9 main.py fl.ru parser > ../log/parser.log &')
os.system('cd bot && nohup python3.9 task_manager.py fl.ru task_manager > ../log/task_manager.log &')
os.system('cd bot && nohup python3.9 main.py fl.ru bot > ../log/bot.log &')
