# -*- coding: utf-8 -*-
# @Time     : 2019/5/15 11:36
# @Author   : LEI
# @IDE      : PyCharm
# @PJ_NAME  : mq_test

import pika
import time

'''
rabbitmq实现的rpc场景中
1. server是一个消费者，且一个rpc server使用一个队列
2. client是一个生产者，发送消息时发送到上面这个队列，
等待server从另一个临时队列中返回数据
使用mq实现rpc需注意几点：
1. rpc服务端是否需要做集群（根据客户端并发量）
2. rpc服务端出现异常，是否要转发给rpc客户端
'''
# 指定远程rabbitmq的用户名密码
username = 'admin'
pwd = 'adminBolaa2019'

# 声明rpc队列
fib_rpc_queue = 'rpc_queue'

# 生成登录凭据
credential = pika.PlainCredentials(username, pwd)

# 连接mq
connection = pika.BlockingConnection(pika.ConnectionParameters('49.4.5.148', 5672, credentials=credential))

# 在连接上创建一个频道
channel = connection.channel()

# 声明这个服务专有的队列
channel.queue_declare(queue='rpc_queue')

# 假设rpc server是返回一个斐波那契数（1,1,2,3,5,8,13,21,34...）
def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

# 消息的处理函数
def on_request(ch, method, props, body):
    n = int(body)

    print(" [.] fib(%s)" % n)
    response = fib(n)

    ch.basic_publish(exchange='', # 为空表示直接发给routing_key同名队列
                     routing_key=props.reply_to,
                     # rpc 请求发来的id再发回去
                     properties=pika.BasicProperties(correlation_id= \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

# 接收消息
channel.basic_qos(prefetch_count=1) # 每次接收1条
# 这个rpc队列是和服务一一对应的
channel.basic_consume(queue=fib_rpc_queue, on_message_callback=on_request)


print(" [x] Awaiting RPC requests")
channel.start_consuming()