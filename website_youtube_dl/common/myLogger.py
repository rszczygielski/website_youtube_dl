from datetime import datetime
from inspect import stack
import os


class LoggerClass():
    def __init__(self):
        self.settings()

    def settings(self, show_log_level =True,
                 show_date =True,
                 show_file_name =True,
                 is_save =False,
                 path =os.getcwd()):
        self.date_bool = show_date
        self.log_level_bool = show_log_level
        self.file_name_bool = show_file_name
        self.is_save = is_save
        self.path = path + "/log_file_name.log"

    def time(self):
        return datetime.now().strftime("%Y %m %d %H:%M:%S")

    def file_name(self):
        file_name = stack()[3].filename.split("/")[-1]
        line_num = stack()[3].lineno
        return f"{file_name}: {line_num}"

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
        if self.is_save:
            log_file = open(self.path, "a")
            log_file.write(log)
            log_file.write("\n")
            log_file.close()

    def debug(self, *argument):
        debug = self.get_log("DEBUG", argument)
        print(self.get_log("DEBUG", argument))
        self.save_to_file(debug)

    def warning(self, *argument):
        warning = self.get_log("WARNING", argument)
        print("\033[93m" + warning, "\033[0m")
        self.save_to_file(warning)

    def error(self, *argument):
        error = self.get_log("ERROR", argument)
        print("\033[91m" + error, "\033[0m")
        self.save_to_file(error)


Logger = LoggerClass()
