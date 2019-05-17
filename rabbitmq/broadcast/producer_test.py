# -*- coding: utf-8 -*-
# @Time     : 2019/5/15 11:36
# @Author   : LEI
# @IDE      : PyCharm
# @PJ_NAME  : mq_test

# sender
import pika
import time

'''
在MQ的广播模型中
1. 生产这不需要声明队列，而是使用一个临时随机队列
2. 需要声明使用的exchange
说明：广播模型中，一个(多个)生产者 --> 交换器 --> 多个临时队列（消费者）
(每个消费者一个队列，多个消费者可重复消费同一条消息)
'''
# 指定远程rabbitmq的用户名密码
username = 'admin'
pwd = 'admin'

# 生成登录凭据
credential = pika.PlainCredentials(username, pwd)

# 连接mq
connection = pika.BlockingConnection(pika.ConnectionParameters('49.4.5.148', 5672, credentials=credential))

# 在连接上创建一个频道
channel = connection.channel()

channel.exchange_declare(exchange='ec1',  # 声明交换器名称
                         exchange_type='fanout')  # 交换器类型，消费者必须一致

# 声明(创建)一个队列（反复声明不会报错，但一个队列仍然以名称作为唯一标识）
# 注意第一次创建队列时就应该设置持久化，因为后续不能改这个
# channel.queue_declare(queue='que1',durable=True)


# 将指定的队列和交换器通过 routing_key绑到一起
# channel.queue_bind(exchange='ec1', queue='que1', routing_key='ec1_que1')

# 待发送消息
msg = b'hello world'

# **发送消息**
def produce_msg():
    channel.basic_publish(exchange='ec1',  # 交换机,为空则消息直接发送到与routing-key同名的queue中
                       routing_key='',  # 路由键，交换器根据这个决定转发到哪个queue,当exchange_type=fanout时被忽略
                       body=msg,  # 生产者要发送的消息
                       properties=pika.BasicProperties(
                          delivery_mode=2,  # 设置消息也是持久化，保证MQ重启消息不丢失
                       ))


print(f'produce: {msg}')

n = 3
while n>0:
    print(f'produc... {n}')
    produce_msg()
    time.sleep(1)
    n -= 1

# 关闭mq连接（会关闭连接上的所有channel，
# 关闭前会停止向mq的消息发送操作，已发送至mq的不受影响）
# channel.close()
connection.close()
