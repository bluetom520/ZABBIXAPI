#!/usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = 'TT'
import datetime,time

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print now
    d1 = datetime.datetime.now()
    d3 = d1 + datetime.timedelta(hours=-1)
    d3.ctime()
    print d3.strftime("%Y-%m-%d %H:%M:%S")
    print d1 + datetime.timedelta(days=-1)
    print d1 + datetime.timedelta(minutes=-1)

    print d1 + datetime.timedelta(seconds=-1)

