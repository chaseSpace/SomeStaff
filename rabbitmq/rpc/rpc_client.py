# -*- coding: utf-8 -*-
# @Time     : 2019/5/15 11:36
# @Author   : LEI
# @IDE      : PyCharm
# @PJ_NAME  : mq_test


import pika,time
import uuid

'''
rabbitmq实现的rpc场景中
1. server是一个消费者，且一个rpc server使用一个队列
2. client是一个生产者，发送消息时发送到上面这个队列，
等待server从另一个临时队列中返回数据

使用mq实现rpc需注意几点：
1. rpc服务端是否需要做集群
2. rpc服务端出现异常，是否要转发给rpc客户端
注意：定义rpc类需要按照固定的模式实现，参考下面的FibonacciRpcClient类
主要是self变量，on_response,call方法
'''

# 使用和服务器一样的rpc队列
fib_rpc_queue = 'rpc_queue'

# 指定远程rabbitmq的用户名密码
username = 'admin'
pwd = 'adminBolaa2019'

# 生成登录凭据
user_pwd = pika.PlainCredentials(username, pwd)

# 连接mq
connection = pika.BlockingConnection(pika.ConnectionParameters('49.4.5.148', credentials=user_pwd))

class FibonacciRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('49.4.5.148', credentials=user_pwd))

        self.channel = self.connection.channel()

        # 声明一个随机队列作为存放response的回调队列
        result = self.channel.queue_declare('', exclusive=True)
        self.callback_queue = result.method.queue

        # 消费回调队列（接收rpc response）
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        # response的回调方法
        # 只需要关联id匹配的msg
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        # rpc调用方法
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key=fib_rpc_queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=f'{n}'.encode())

        # 这是一个阻塞调用方法，需要设置一个超时时间
        self.connection.process_data_events(time_limit=1)

        if self.response is not None:
            return int(self.response)
        else:
            raise ValueError('rpc server timeout!')


fibonacci_rpc = FibonacciRpcClient()

print(" [x] Requesting fib(30)")
response = fibonacci_rpc.call(9)
print(" [.] Got %r" % response)