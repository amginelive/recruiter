from channels.routing import route_class

from chat.consumers import ChatServer

routes = [
    route_class(ChatServer, path=r'^/$')
]
