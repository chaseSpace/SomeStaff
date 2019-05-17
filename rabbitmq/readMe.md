
### RabbitMQ可以实现以下几个队列模型或功能 

#### 1. 简单分发模型  
    多个消费者共享同一队列，一条消息在全局不能被重复消费  
    具体实现：  
    a. 生产者声明队列、exchange以及绑定关系  
    b. 每个消费者声明待消费的队列即可  

#### 2. 广播模型  
    多个消费者可消费同一条消息，同一个消费者不能消费同一条消息  
    具体实现：  
    a. 生产者仅声明exchange，然后发布消息时指定exchange即可  
    b. 每个消费者声明一个专属且唯一的队列供自己使用，并绑定上面的exchange  

#### 3. exchange_type = `fanout`  
    这种方式可以实现广播模型，在于如何使用  
    具体实现：  
    a. 生产者声明队列A和B和exchange-A(type='fanout')绑定，通过不同的routing-key。  
    b. 两个消费者，分别声明上面两个队列为待消费队列  
    c. 生产者发布1条消息，指定exchange=A, routing-key='xxx',这时两个消费者都应该从两个队列中收到同一条消息。  

#### 4. exchange_type = `direct`  
    基于routing-key的精确匹配模型  
    具体实现:  
    a. 生产者声明两个队列、1个exchange，通过不同routing-key将他们绑定  
    b. 多个消费者声明不同的待消费队列  
    c. 生产者发送消息到不同routing-key，然后每个消费者都能收到消息对应的消息。  

#### 5. exchange_type = `topic`  
    基于routing-key的通配符匹配模型  
    具体实现:  
    a. 生产者声明一个队列 ，1个exchange(type=topic)，使用两个不同的routing-key绑定它们：  
        mylog.level.info 和 mylog.level.warning  
    b. 消费者声明这个队列为待消费队列  
    c. 生产者发送第一条消息routing-key="mylog.level.*"，第二条routing-key="mylog.#",  
        结果是这两条消息都会发送到上面的队列被消费者消费。  
#### 6. rpc  
    使用rabbitmq实现rpc  
