from website_youtube_dl.common.youtubeLogKeys import YoutubeVariables

class EmitData:
    def __init__(self, emitName, data):
        self.data = data
        self.emitName = emitName

    @staticmethod
    def getEmitMassage(fullEmit, msgNumber):
        return fullEmit[msgNumber]

    @classmethod
    def initFromMassage(cls, receivedMsg):
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        return cls(emitName, data)