# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright 2015
# Time: 2015-6-23 15:32
# Author: Andrew Liu
# Version: v0.2 

import logging, sys

# constant variable

DEFAULT_LEAVE = logging.DEBUG
DEFAULT_EMAIL = "1095511964@qq.com"
DEFAULT_FORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


# wrapper logging
class Logger(object):

    def __init__(self, 
                logger=None,
                name=__name__,
                level=DEFAULT_LEAVE,
                fmt=DEFAULT_FORMATTER
                ):
        """init a Logger class
        
        Args : 
            logger: transfer a logger 
            name: set a logger formatter's name
            level: set logging level, default is DEBUG
            fmt: set formatter's format
        """
        if logger is None:
            self.logger = logging.getLogger(name)
        self.formatter = logging.Formatter(fmt)
        self.logger.setLevel(level)

    def enable_file_handler(self,
                            log_file,
                            level=DEFAULT_LEAVE,
                            file_encoding="utf-8"
                            ):
        file_handler = logging.FileHandler(log_file, mode='a', encoding=file_encoding)
        file_handler.setLevel(level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def enable_stream_handler(self,
                              level=DEFAULT_LEAVE):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(stream_handler)

    def enable_smtp_handlder(self,
                             mailhost,
                             to_addr_list,
                             subject="log analysis",
                             from_addr=DEFAULT_EMAIL,
                             level=DEFAULT_EMAIL
                             ):
        """wrapper for SMTPHandler
        
        Args : 
            mailhost: mail server host
            to_addr_list: a list of to email addr string
            subject: a subject string
        """
        smtp_handlder =  logging.handlers.SMTPHandler(mailhost=mailhost, 
                                                      fromaddr=from_addr, 
                                                      toaddrs=to_addr_list, 
                                                      subject=subject
                                                      )
        smtp_handlder.setLevel(level)
        smtp_handlder.setFormatter(self.formatter)
        self.logger.addHandler(smtp_handlder)

    def debug(self, msg, *args):
        if msg:
            self.logger.debug(msg, *args)

    def info(self, msg, *args):
        if msg:
            self.logger.info(msg, *args)

    def warning(self, msg, *args):
        if msg:
            self.logger.warning(msg, *args)

    def error(self, msg, *args):
        if msg:
            self.logger.warning(msg, *args)

    def critical(self, msg, *args):
        if msg:
            self.logger.critical(msg, *args)

    def exception(self, msg, *args):
        if msg:
            self.logger.exception(msg, *args)


class SingletonDecorator(object):

    def __init__(self, cls):
        self._cls = cls
        self._inst = None

    def __call__(self, *args, **kwargs):
        """Over __call__ method. So the instance of this class
        can be called as a function.
        """
        if not self._inst:
            self._inst = self._cls(*args, **kwargs)
        return self._inst

my_logger = SingletonDecorator(Logger)
logger_instance = None
logger_root = None

def setLogger():
    global logger_root
    logger_root = logging.getLogger()
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_FORMATTER)
    console.setFormatter(formatter)
    logger_root.addHandler(console)
    logger_root.setLevel(logging.INFO)
    return logger_root

def getLogger(name=None, formatter=DEFAULT_FORMATTER):
    global logger_instance
    global logger_root
    if logger_instance is not None:
        return logger_instance
    else:
        if name is None:
            if logger_root is None:
                return setLogger()
            else:
                return logger_root
        else:
            logger_instance = Logger(name=name)
            return logger_instance


if __name__ == '__main__':
    mylogger = getLogger(name='test')
    mylogger.enable_stream_handler(logging.DEBUG)
    mylogger.enable_file_handler(sys.argv[1])
    for i in xrange(0, 100):
        mylogger = getLogger(name='test')
        mylogger.debug('debug log: %d' % i)
        mylogger.info('debug log: %d' % i)
        mylogger.warning('debug log: %d' % i)
        mylogger.exception('debug log: %d' % i)
        mylogger.error('debug log: %d' % i)
        mylogger.critical('debug log: %d' % i)

