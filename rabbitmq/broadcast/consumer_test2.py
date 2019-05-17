# -*- coding: utf-8 -*-
# @Time     : 2019/5/15 11:36
# @Author   : LEI
# @IDE      : PyCharm
# @PJ_NAME  : mq_test

# sender

import pika,time

'''
消费者比较简单，只需要绑定待消费的队列即可
广播模型中，rabbitmq产生的队列数量与消费者数量相同(10个消费者就是10个(临时)队列)
'''
# 指定远程rabbitmq的用户名密码
username = 'admin'
pwd = 'admin'

# 生成登录凭据
user_pwd = pika.PlainCredentials(username, pwd)

# 连接mq
connection = pika.BlockingConnection(pika.ConnectionParameters('49.4.5.148', credentials=user_pwd))

# 在连接上创建一个频道
channel = connection.channel()

result = channel.queue_declare('',  # 传空字符，会创建一个随机且唯一的队列
                               exclusive=True) # 指定此参数True，则消费者断开连接后此队列自动被删除(这个队列只能被当前消费者使用)
queue_name = result.method.queue
print(f'consumer-2 random and exclusive queue name: {queue_name}')

# 把队列绑定到exchange
channel.queue_bind(exchange='ec1', queue=queue_name)


def callback(ch, method, properties, body): #定义一个回调函数，用来接收生产者发送的消息
    # print(f'channel: {ch} method:{method} prop:{properties} body:{body}')
    print("consume: recv %s" % body)
    # 在这条消息被处理完毕再写ack，而不是在外面写 no_ack=True
    time.sleep(2)
    ch.basic_ack(delivery_tag = method.delivery_tag)

# 设置当前消费者每次最多能取多少条（仅处理完所取的消息后才能再取）
channel.basic_qos(prefetch_count=1)

# 频道绑定待消费的队列
channel.basic_consume(queue=queue_name,
                      on_message_callback=callback)

print('consume start...')
channel.start_consuming()
