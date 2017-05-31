from channels.generic.websockets import JsonWebsocketConsumer


class ChatServer(JsonWebsocketConsumer):
    http_user = True

    def connection_groups(self, **kwargs):
        return [str(self.message.user.id)]

    def connect(self, message, **kwargs):
        self.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass
