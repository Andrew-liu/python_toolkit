# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright 2015
# Time: 2015-6-23 15:32
# Author: Andrew Liu
# Version: v0.2 



# Test
import sys
sys.path.append('../')


import time
import MySQLdb
import core.ALLogger as logging


class MySQLBase(object):
    def __init__(self, hostname, username, passwd, database):
        """
        provide db reconnect function.
        :rtype : None
        :param hostname: db host
        :param username: db user
        :param passwd: db user passwd
        :param database: database
        """
        self.hostname = hostname
        self.username = username
        self.passwd = passwd
        self.database = database
        self.connect = None
        self.cursor = None
        self.dictCursor = None
        self.logger = logging.getLogger()
    
    def __del__(self):
        self.closeDictCursor()
        self.closeCursor()
        self.closeConnection()
        

    def connectDB(self):
        """connect db."""
        # connect.open = 1 if db is connected
        # express that we have't actively call connection.close to close the connection
        # so, add a try-catch to test the connect, 
        # ing will add the cost of time
        if self.connect is not None and self.connect.open == 1:
            pass
        else:
            # link db with three times
            sleep_time = 10
            MAX_RETRY = 3
            try_index = 0
            while try_index < MAX_RETRY:
                try:
                    self.connect = MySQLdb.connect(host=self.hostname, user=self.username, passwd=self.passwd,
                                                   db=self.database)
                    if self.connect is not None and self.connect.open == 1:
                        try_index = MAX_RETRY
                        break
                    else:
                        self.logger.error('connectDB error, host: %s, retry:%d' %(self.hostname, try_index+1))
                        time.sleep(sleep_time)
                except Exception, e:
                    self.logger.exception('connectDB exception, msg: %s, retry:%d' %(e, try_index+1))
                    self.connect = None
                    time.sleep(sleep_time)
                finally:
                    try_index = try_index + 1
            if MAX_RETRY == try_index:
                self.logger.error('connectDB failure, host: %s.' % self.hostname)
                return False
        return True

    # reconnect and sql again 
    def reConnect(self, sql):
        self.closeCursor()
        self.closeDictCursor()
        self.closeConnection()
        if self.tryConnect():
            self.getDictCursor()
            self.dictCursor.execute(sql)

    # wrapper for the connect
    def tryConnect(self):
        sleep_time = 10
        try:  
            self.connect = MySQLdb.connect(host=self.hostname, user=self.username, passwd=self.passwd,
                                                   db=self.database)
        except Exception, e:
            self.logger.exception('reConnectDB exception, msg: %s, retry:%d' %(e, try_index+1))
            self.connect = None
            time.sleep(sleep_time)
            self.connect = MySQLdb.connect(host=self.hostname, user=self.username, passwd=self.passwd,
                                                   db=self.database)
        return True


    def getCursor(self):
        """
        get dict cursor from the connection
        :return: dict cursor if succeed, None for Failed
        """
        if self.connectDB() is False:
            self.logger.error('getCursor error, hostname: %s.' % self.hostname)
            return None
        else:
            if not self.cursor:
                self.cursor = self.connect.cursor()
            return self.cursor

    def getDictCursor(self):
        """
        get dict cursor from the connection
        :return: dict cursor if succeed, None for Failed
        """
        if self.connectDB() is False:
            self.logger.error('getDictCursor error, hostname: %s.' % self.hostname)
            return None
        else:
            if not self.dictCursor:
                self.dictCursor = self.connect.cursor(MySQLdb.cursors.DictCursor)
            return self.dictCursor

    def closeConnection(self):
        if self.connect:
            self.connect.close()
            self.connect = None

    def closeCursor(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None

    def closeDictCursor(self):
        if self.dictCursor:
            self.dictCursor.close()
            self.dictCursor = None
            

    def selectone(self, select_sql):
        """
        user handle exception
        """
        try:
            self.getDictCursor()
            self.dictCursor.execute(select_sql)
        except MySQLdb.OperationalError, e:
            self.logger.warn('connectDB timeout: %s when selectone' % e)
            self.reConnect(select_sql)
        result = self.dictCursor.fetchone()
        self.closeDictCursor()
        return result


    def selectall(self, select_sql):
        """
        user handle exception
        """
        try:
            self.getDictCursor()
            self.dictCursor.execute(select_sql)
        except MySQLdb.OperationalError, e:
            self.logger.warn('connectDB timeout: %s when selectall' % e)
            self.reConnect(select_sql)
        result = self.dictCursor.fetchall()
        self.closeDictCursor()
        return result


    def update(self, update_sql):
        """
        Execute update sql, please commit by yourself after updated
        :param update_sql:
        :return:
        """
        try:
            self.getDictCursor()
            self.dictCursor.execute(update_sql)
            return True
        except MySQLdb.OperationalError, e:
            self.logger.warn('connectDB timeout: %s when update' % e)
            self.reConnect(select_sql)
        except Exception, e:
            self.logger.exception('update exception, sql: %s, msg: %s.' % (update_sql, e))
            self.connect = None
            return False
        finally:
            self.closeDictCursor()

    def commit(self):
        self.connect.commit()

    def close(self):
        self.closeConnection()
