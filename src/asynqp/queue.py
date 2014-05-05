import asyncio


class Queue(object):
    """
    A queue is a collection of messages, which new messages can be delivered to via an exchange,
    and messages can be consumed from by an application.

    Attributes:
        queue.name: the name of the queue
        queue.durable: if True, the queue will be re-created when the broker restarts
        queue.exclusive: if True, the queue is only accessible over one channel
        queue.auto_delete: if True, the queue will be deleted when its last consumer is removed

    Methods:
        queue.bind(exchange, routing_key): Bind a queue to an exchange. This method is a coroutine.
    """
    def __init__(self, channel, loop, sender, name, durable, exclusive, auto_delete):
        self.channel = channel
        self.loop = loop
        self.sender = sender
        self.name = name
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete

    @asyncio.coroutine
    def bind(self, exchange, routing_key):
        """
        Bind a queue to an exchange, with the supplied routing key.
        This action 'subscribes' the queue to the routing key; the precise meaning of this
        varies with the exchange type.
        This method is a coroutine.

        Arguments:
            exchange: the exchange to bind to
            routing_key: the routing key under which to bind

        Return value:
            The newly created binding object
        """
        self.channel.queue_bind_future = fut = asyncio.Future(loop=self.loop)
        self.sender.send_QueueBind(self.name, exchange.name, routing_key)
        yield from fut
        return QueueBinding(self, exchange)

    @asyncio.coroutine
    def get(self, *, no_ack=False):
        """
        Synchronously get a message from the queue.
        This method is a coroutine.

        Arguments:
            no_ack: if True, the broker does not require acknowledgement of receipt of the message.
                    default: False

        Return value:
            an instance of asynqp.Message, or None if there were no messages on the queue.
        """
        self.channel.basic_get_future = asyncio.Future(loop=self.loop)
        self.sender.send_BasicGet(self.name, no_ack)
        result = yield from self.channel.basic_get_future
        return result


class QueueBinding(object):
    def __init__(self, queue, exchange):
        self.queue = queue
        self.exchange = exchange