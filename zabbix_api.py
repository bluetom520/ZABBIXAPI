#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2
import sys
from urllib2 import URLError
from conf.switch import switch
from conf.INIFILES import read_config
import os
reload(sys)
sys.setdefaultencoding('utf-8')


class zabbixtools:
    def __init__(self, url="http://192.168.1.199/zabbix/api_jsonrpc.php", user="Admin", passwd="zabbix"):
        self.url = url
        self.header = {"Content-Type": "application/json"}
        self.user = user
        self.passwd = passwd
        self.authID = self.user_login()


    def user_login(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "user.login",
                    "params": {
                        "user": self.user,
                        "password": self.passwd,
                        },
                    "id": 0
                    })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            print "Auth Failed, Please Check Your Name And Password:",e.code
        else:
            response = json.loads(result.read())
            result.close()
            authID = response['result']
            return authID

    def get_data(self,data,hostip=""):
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server could not fulfill the request.'
                print 'Error code: ', e.code
            return 0
        else:
            response = json.loads(result.read())
            result.close()
            return response

    def host_get(self,hostid=""):
        #hostip = raw_input("\033[1;35;40m%s\033[0m" % 'Enter Your Check Host:Host_ip :')
        if hostid != "":
            temp = {"hostid": [hostid]}
        else:
            temp = {}

        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                        "output": ["hostid", "name", "status", "host"],
                        "filter": temp,
                        "countOutput": True             #返回结果数量
                        },
                    "auth": self.authID,
                    "id": 1
                })
        res = self.get_data(data)['result']
        return res


    def host_del(self):
        hostip = raw_input("\033[1;35;40m%s\033[0m" % 'Enter Your Check Host:Host_ip :')
        hostid = self.host_get(hostip)
        if hostid == 0:
            print '\t',"\033[1;31;40m%s\033[0m" % "This host cannot find in zabbix,please check it !"
            sys.exit()
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.delete",
                    "params": [{"hostid": hostid}],
                    "auth": self.authID,
                    "id": 1
                })
        res = self.get_data(data)['result']
        if 'hostids' in res.keys():
            print "\t","\033[1;32;40m%s\033[0m" % "Delet Host:%s success !" % hostip
        else:
            print "\t","\033[1;31;40m%s\033[0m" % "Delet Host:%s failure !" % hostip

    def hostgroup_get(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "hostgroup.get",
                    "params": {
                        "output": "extend",
                        "countOutput": True,
                        },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)['result']
        return res

    def template_get(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "template.get",
                    "params": {
                        "output": "extend",
                        "countOutput": True,
                        },

                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)['result']
        return res

    def host_create(self):
        hostip = raw_input("\033[1;35;40m%s\033[0m" % 'Enter your:Host_ip :')
        groupid = raw_input("\033[1;35;40m%s\033[0m" % 'Enter your:Group_id :')
        templateid = raw_input("\033[1;35;40m%s\033[0m" % 'Enter your:Tempate_id :')
        g_list=[]
        t_list=[]
        for i in groupid.split(','):
            var = {}
            var['groupid'] = i
            g_list.append(var)
        for i in templateid.split(','):
            var = {}
            var['templateid'] = i
            t_list.append(var)
        if hostip and groupid and templateid:
            data = json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "host.create",
                        "params": {
                            "host": hostip,
                            "interfaces": [
                                {
                                    "type": 1,
                                    "main": 1,
                                    "useip": 1,
                                    "ip": hostip,
                                    "dns": "",
                                    "port": "10050"
                                }
                            ],
                            "groups": g_list,
                            "templates": t_list,
                    },
                        "auth": self.authID,
                        "id": 1,
                        })
            res = self.get_data(data,hostip)
            if 'result' in res.keys():
                res = res['result']
                if 'hostids' in res.keys():
                    print "\033[1;32;40m%s\033[0m" % "Create host success"
            else:
                print "\033[1;31;40m%s\033[0m" % "Create host failure: %s" % res['error']['data']
        else:
            print "\033[1;31;40m%s\033[0m" % "Enter Error: ip or groupid or tempateid is NULL,please check it !"

    def get_item(self, hostid=""):

        data = json.dumps(
        {
           "jsonrpc": "2.0",
           "method": "item.get",    #extenditem.get["itemids", "key_"]
           "params": {
               "output": "extend",
               # "hostids": hostid,
               "monitored": True,

               # "filter": {
               #     # "status": "0",
               #     "interfaceid":"1"
               # },
               # "search": {
               #   # "key_": "vm*"
               # },
               "countOutput": True            #返回结果数量

           },
            "auth": self.authID,
            "id": 1
        })

        res = self.get_data(data)['result']
        return res
        # if (res !=0) or (len(res) != 0):
        #     print "\033[1;32;40m%s\033[0m" % "Number Of Items: ","\033[1;31;40m%d\033[0m" % len(res)
        #     for item in res:
        #         print"\t","item_id:",item['itemid'],"\t","item_Name:",item['key_'].encode('UTF-8'),"\t","item_name",item['name'].encode('UTF-8'),"\t","value_type",item['value_type']
        # return res

    def get_item_blue(self, hostid, typeid):
        if typeid == 1:
            filter = ["system.uptime", "system.cpu.load[all,avg1]", "vm.memory.size[pused]", "vfs.fs.size[/,pfree]", "vfs.fs.size[C:,pfree]"]
        else:
            filter = ["sysUpTime"]
        data = json.dumps(
        {
           "jsonrpc": "2.0",
           "method": "item.get",    #extenditem.get["itemids", "key_"]
           "params": {
               "output": ["itemids", "key_", "name", "value_type"],
               "hostids": hostid,
               "filter": {
                    "key_": filter
               },
               "search": {
                 # "key_": "vm*"
               },
               "searchByAny": True,
               "searchWildcardsEnabled": True,
           },
            "auth": self.authID,
            "id": 1
        })

        res = self.get_data(data)['result']

        # if (res !=0) or (len(res) != 0):
        #     print "\033[1;32;40m%s\033[0m" % "Number Of Items: ","\033[1;31;40m%d\033[0m" % len(res)
        #     for item in res:
        #         print"\t","item_id:",item['itemid'],"\t","item_Name:",item['key_'].encode('UTF-8'),"\t","item_name",item['name'].encode('UTF-8'),"\t","value_type",item['value_type']
        return res


    def get_value_blue(self, itemid, value_type):
        data = json.dumps(
        {
           "jsonrpc": "2.0",
           "method": "history.get",    #extenditem.get["itemids", "key_"]
           "params": {
               "output": "extend",
                "history":value_type,
               # "hostids": "10110",
                "itemids": itemid,
                "sortfield": "clock",
                "sortorder": "DESC",
                "limit": 1


           },
            "auth": self.authID,
            "id": 1
        })

        res = self.get_data(data)['result']
        return res

    def get_value(self, itemid, value_type):
        data = json.dumps(
        {
           "jsonrpc": "2.0",
           "method": "history.get",    #extenditem.get["itemids", "key_"]
           "params": {
               "output": "extend",
                "history":value_type,
               # "hostids": "10110",
                "itemids": itemid,
                "sortfield":"clock",
               "sortorder": "DESC",
                "limit":10


           },
            "auth": self.authID,
            "id": 1
        })

        res = self.get_data(data)['result']
        # print res
        if (res !=0) or (len(res) != 0):
            print "\033[1;32;40m%s\033[0m" % "Number Of Item_values: ","\033[1;31;40m%d\033[0m" % len(res)
            for item_value in res:
                print"\t","item_id:",item_value['itemid'],"\t","item_value:",item_value['value'].encode('UTF-8')
        return res

def get_path():
    # print sys.argv[0]
    path = os.path.dirname(os.path.abspath(sys.argv[0]))
    # print path
    config_path = path + '/config.ini'
    return config_path


def main():
    test = zabbixtools("http://zabbix.gitcloud.cc/api_jsonrpc.php", user="Admin", passwd="rq071108@")
    # test = zabbixtools()
    # test.template_get()               #模板数
    print test.hostgroup_get()
    # test.host_get()                         ##主机数量
    # test.get_item()                  ## 监控项数量
    # test.get_value("25345", 3)
    # test.host_del()
    #test.host_create()
if __name__ == "__main__":
    # main()
    if len(sys.argv) < 1:
        sys.exit(1)
    config_file_path = get_path()
    web = read_config(config_file_path, 'api', "web")
    user = read_config(config_file_path, 'api', "user")
    passwd = read_config(config_file_path, 'api', "passwd")
    tool = zabbixtools(web, user=user, passwd=passwd)
    for case in switch(sys.argv[1]):
        if case('groups'):
            print tool.hostgroup_get()
            break
        if case('templates'):
            print tool.template_get()
            break
        if case('hosts'):
            print tool.host_get()
            break
        if case('items'):
            print tool.get_item()
            break
        else:
            print "0"

