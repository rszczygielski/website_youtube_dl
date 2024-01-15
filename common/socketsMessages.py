from flask_socketio import emit
from abc import ABC, abstractmethod

class Message(ABC):
    _emitValue = "data"
    # to nie jest interface bo ma zmienną, jeśli nie miałby
    # zmiennej to możnaby nazwać tą klasę interfacem tak to jest klasa abstrakcyjna
    # klasa bazowa to tak która inne klasy dzidziczą ale można stwrzyć jej instancję
    # klasa abstarkcyjna to taka której nie możemy stworzyć instancji tylko dziedziczym
    # interfaceu tez nie możemy zrobić instancji
    # nie powinno się dziedziczyć więcej niż jednej klasy, natomiast interfaców można dzidziczyć niestkończość wynika to z czasu życia zmiennych


    @abstractmethod
    def send(self, data):
        pass

class DownloadMediaFinish(Message):
    _emitTitle = "downloadMediaFinish"

    def send(self, hash):
        emit(self._emitTitle, {self._emitValue: {"HASH": hash}})

    def sendError(self, errorMsg):
        emit(self._emitTitle, {"error": errorMsg})

class MediaInfo(Message):
    _emitTitle = "mediaInfo"

    def send(self, metaData):
        emit(self._emitTitle, {self._emitValue: [metaData]})