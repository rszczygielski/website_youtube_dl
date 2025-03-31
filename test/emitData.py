from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys


class EmitData:
    def __init__(self, emit_name, data):
        self.data = data
        self.emit_name = emit_name

    @staticmethod
    def get_emit_massage(full_emit, msg_number):
        return full_emit[msg_number]

    @classmethod
    def init_from_massage(cls, received_msg):
        data = received_msg[MainYoutubeKeys.ARGS.value][0]
        emit_name = received_msg[MainYoutubeKeys.NAME.value]
        return cls(emit_name, data)
