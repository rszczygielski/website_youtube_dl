from datetime import datetime
from inspect import stack
import os


class LoggerClass():
    """Custom logger class with configurable output formatting.
    
    Provides logging functionality with options to include date, log level,
    and file name/line number in log messages. Supports console output with
    color coding and optional file logging.
    
    Attributes:
        date_bool (bool): Whether to include date/time in log messages.
        log_level_bool (bool): Whether to include log level in messages.
        file_name_bool (bool): Whether to include file name and line number.
        is_save (bool): Whether to save logs to a file.
        path (str): Path to the log file.
    """
    
    def __init__(self):
        """Initialize LoggerClass with default settings."""
        self.settings()

    def settings(self, show_log_level =True,
                 show_date =True,
                 show_file_name =True,
                 is_save =False,
                 path =os.getcwd()):
        """Configure logger settings.
        
        Args:
            show_log_level (bool, optional): Include log level in messages.
                Defaults to True.
            show_date (bool, optional): Include date/time in messages.
                Defaults to True.
            show_file_name (bool, optional): Include file name and line number.
                Defaults to True.
            is_save (bool, optional): Enable file logging. Defaults to False.
            path (str, optional): Directory path for log file. Defaults to
                current working directory.
        """
        self.date_bool = show_date
        self.log_level_bool = show_log_level
        self.file_name_bool = show_file_name
        self.is_save = is_save
        self.path = path + "/log_file_name.log"

    def time(self):
        """Get current date and time as formatted string.
        
        Returns:
            str: Formatted date/time string (YYYY MM DD HH:MM:SS).
        """
        return datetime.now().strftime("%Y %m %d %H:%M:%S")

    def file_name(self):
        """Get calling file name and line number.
        
        Uses stack inspection to determine the file and line number
        of the code that called the logger method.
        
        Returns:
            str: Formatted string with filename and line number.
        """
        file_name = stack()[3].filename.split("/")[-1]
        line_num = stack()[3].lineno
        return f"{file_name}: {line_num}"

    def arguments(self, arguments):
        """Format arguments into a single string.
        
        Args:
            arguments (tuple): Variable arguments to format.
            
        Returns:
            str: Space-separated string of all arguments.
        """
        printer = ""
        for elem in arguments:
            printer += " " + elem
        return printer

    def get_log(self, log_level, argument):
        """Build formatted log message string.
        
        Args:
            log_level (str): Log level (e.g., "DEBUG", "WARNING", "ERROR").
            argument (tuple): Variable arguments to include in the message.
            
        Returns:
            str: Formatted log message string.
        """
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
        """Save log message to file if file logging is enabled.
        
        Args:
            log (str): Log message to save.
        """
        if self.is_save:
            log_file = open(self.path, "a")
            log_file.write(log)
            log_file.write("\n")
            log_file.close()

    def debug(self, *argument):
        """Log a debug message.
        
        Args:
            *argument: Variable arguments to include in the debug message.
        """
        debug = self.get_log("DEBUG", argument)
        print(self.get_log("DEBUG", argument))
        self.save_to_file(debug)

    def warning(self, *argument):
        """Log a warning message with yellow color.
        
        Args:
            *argument: Variable arguments to include in the warning message.
        """
        warning = self.get_log("WARNING", argument)
        print("\033[93m" + warning, "\033[0m")
        self.save_to_file(warning)

    def error(self, *argument):
        """Log an error message with red color.
        
        Args:
            *argument: Variable arguments to include in the error message.
        """
        error = self.get_log("ERROR", argument)
        print("\033[91m" + error, "\033[0m")
        self.save_to_file(error)


Logger = LoggerClass()
