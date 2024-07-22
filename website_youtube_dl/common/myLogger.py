from datetime import datetime
from inspect import stack
from flask_socketio import emit
import os

class LoggerClass():
    def __init__(self):
        self.settings()

    def settings(self, showLog_level=True, show_date=True, show_file_name=True, isSave=False, path=os.getcwd(), isEmit=False, emitSkip=[]):
        self.date_bool = show_date
        self.log_level_bool = showLog_level
        self.file_name_bool = show_file_name
        self.isSave = isSave
        self.isEmit = isEmit
        self.emitSkip = emitSkip
        self.path = path + "/log_file_name.log"

    def emit(self, msg):
        if self.isEmit:
            for elem in self.emitSkip:
                if elem in msg:
                    return
            emit("log", msg)

    def time(self):
        return datetime.now().strftime("%Y %m %d %H:%M:%S")

    def file_name(self):
        fileName = stack()[3].filename.split("/")[-1]
        lineNum = stack()[3].lineno
        return f"{fileName}: {lineNum}"

    def arguments(self, arguments):
        printer = ""
        for elem in arguments:
            printer += " " + elem
        return printer

    def get_log(self, log_level, argument):
        log = ""
        if self.date_bool:
            log += self.time() + " "
        if self.file_name_bool:
            log += self.file_name() + " "
        if self.log_level_bool:
            log += log_level + " "
        log += self.arguments(argument)
        return log

    def save_to_file(self, log):
        if self.isSave:
            logFile = open(self.path, "a")
            logFile.write(log)
            logFile.write("\n")
            logFile.close()

    def debug(self, *argument):
        debug = self.get_log("DEBUG", argument)
        print(self.get_log("DEBUG", argument))
        self.save_to_file(debug)
        self.emit(debug)

    def warning(self, *argument):
        warning = self.get_log("WARNING", argument)
        print("\033[93m" + warning,"\033[0m")
        self.save_to_file(warning)
        self.emit(warning)

    def error(self, *argument):
        error = self.get_log("ERROR", argument)
        print("\033[91m" + error,"\033[0m")
        self.save_to_file(error)
        self.emit(error)

Logger = LoggerClass()