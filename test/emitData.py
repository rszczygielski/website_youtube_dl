from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys


class EmitData:
    def __init__(self, emitName, data):
        self.data = data
        self.emitName = emitName

    @staticmethod
    def getEmitMassage(fullEmit, msgNumber):
        return fullEmit[msgNumber]

    @classmethod
    def initFromMassage(cls, receivedMsg):
        data = receivedMsg[MainYoutubeKeys.ARGS.value][0]
        emitName = receivedMsg[MainYoutubeKeys.NAME.value]
        return cls(emitName, data)
