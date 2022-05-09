# -*- coding: utf-8 -*-
import re
import os.path
from operator import itemgetter


class ExtractLog:

    def __init__(self, filepath="./log/", result_file="./result.tcl"):
        self.filepath = filepath
        self.result_file = result_file

    def returnindex(self,result_data , index):
        for j in range(len(result_data[:index]) - 1, -1, -1):
            pass



    # 处理测试仪
    def createTM(self):
        tmdata = []
        for path, dirlist, filelist in os.walk('./logbak/'):
            for filename in filelist:
                txtname = './logbak/' + filename
                filetype_tm = re.compile('094904.log').findall(filename)
                if filetype_tm:
                    comand = open(txtname, encoding='utf-8')
                    lines = comand.read()
                    tmrequestitem = re.compile(
                        "\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}.\d{1,3}\sINFO.*request:\n{'method':\s'apply_config'.*").findall(lines)
                    for item in tmrequestitem:
                        # 普通流量
                        if re.compile("\'headers'\:\s\[\{'fields\'\:").findall(item):
                            headers_json = ''
                            portload_json = ''
                            frame_size_json = ''
                            payload_fill_json = ''
                            date = re.sub(re.compile('-'), '/',
                                          re.compile('\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}.\d{1,3}').findall(item)[0])
                            headers = re.compile("\[{'fields'.*}],\s*'modifiers'\s*:\s*\[.*]}").findall(item)
                            portload = re.compile("'portLoad':\s*.*'},").findall(item)
                            frame_size = re.compile("'size':\s\[{'percent':.*'}],").findall(item)
                            payload_fill = re.compile("'payload_fill':\s*{.*data':\s*'\d*'}").findall(item)

                            if headers:
                                headers_json = re.sub(re.compile("'"), '"', re.sub(re.compile("\,\s'modifiers':\s*\[.*"), '', headers[0]))
                            if portload:
                                portload_json = re.sub(re.compile("'"), '"', re.sub(re.compile("'portLoad':\s|},"), '', portload[0])) + '}'
                            if frame_size:
                                frame_size_json = re.sub(re.compile("'"), '"', re.sub(re.compile("'size':\s\[|],"), '', frame_size[0]))
                            if payload_fill:
                                payload_fill_json = re.sub(re.compile("'"), '"', re.sub(re.compile("'payload_fill':\s*"), '', payload_fill[0]))

                            stream_json = '[ { "op": "replace", "path": "/headers", "value": [' + headers_json + ', ' + frame_size_json + ', ' + portload_json + ', ' + payload_fill_json + ' ] } ]'
                            if headers_json or portload_json or frame_size_json or payload_fill_json:
                                tmdata.append({
                                    'sysname': 'TM',
                                    'dut': 'TM',
                                    'viewlist_num': 199,
                                    'viewlist': 'None',
                                    'time': date,
                                    'config': stream_json
                                })
                        # 建立邻居流量
                        if re.compile("{'emulator': {'devices': .*").findall(item):
                            pass

        comand.close()
        return tmdata

    # 返回字典中value对应的key，如果不存在返回空list
    def getdictkey(self, mydict, value):
        keylist = []
        for k, v in mydict.items():
            if v == value:
                keylist.append(k)
        return keylist

    # 获取log名称中相关信息
    def gettclname(self, modename='no_modename', topo_name='no_topo_name'):
        for path, dirlist, filelist in os.walk(self.filepath):
            for filename in filelist:
                txtname = self.filepath + filename
                filetype_l = re.compile('.log').findall(filename)
                filetype_t = re.compile('.topo').findall(filename)
                if filetype_l:
                    if re.compile("_.*_").findall(filename):
                        modename = re.sub(re.compile('_'), "",
                                      re.compile("_.*_").findall(filename)[0])
                if filetype_t:
                    topo_name = filename
        return modename, topo_name

    # 处理日志
    def disposelog(self):
        result_data = []
        print_data = []
        configreturn = []
        partten_norule = "\[\d{4}(?:-|\/|.)\d{1,2}(?:-|\/|.)\d{1,2}\s\d{1,2}\:\d{1,2}\:\d{1,2}\]\s.*"
        patten_allitem = re.compile("\[\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}]\s[<\[]{1}.*[>\]]{1}.*")
        patten_sysnameitem = re.compile("[<\[>\]]{1}")
        partten_print = re.compile(
            '%[A-Za-z]*\s*\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}:\d{1,3}\s\d{4}\s.*')
        partten_mainitem = re.compile("\[\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}]\s[<\[]{1}\S*[>\]]{1}")
        for path, dirlist, filelist in os.walk(self.filepath):
            for filename in filelist:
                txtname = self.filepath + '/' + filename
                filetype_l = re.compile('.log').findall(filename)
                if filetype_l:
                    comand = open(txtname, encoding='utf-8')
                    lines = comand.read()
                    logbufferitem = re.compile(".*;\sCommand\sis\s.*").findall(lines)
                    # logbufferitem = re.compile("\[\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}]\s%.*;\sCommand\sis\s.*").findall(lines)
                    logbufferlist = []
                    for logbuffer in logbufferitem:
                        logbufferlist.append(
                            ' '.join(re.sub(re.compile(".*;\sCommand\sis\s"), "", logbuffer).split()))
                    noruleItem = re.compile(partten_norule).findall(lines)
                    allItem = patten_allitem.findall(lines)
                    sysName_f = re.compile("^[A-Za-z0-9\-]*").findall(filename)
                    sysName = re.sub(patten_sysnameitem, '', re.sub(re.compile(
                        "\[\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}]"), "", partten_mainitem.findall(allItem[1])[0]))
                    for item in noruleItem:
                        incSysname = patten_allitem.findall(item)
                        printItem = partten_print.findall(item)
                        date = re.sub(re.compile('[\[\]]{1}'), "", re.compile(
                            "\[\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}]").findall(
                            item)[
                            0])
                        if not printItem:
                            if incSysname:
                                allItem_1 = re.sub(partten_mainitem, "",
                                                   incSysname[0])
                                if allItem_1:
                                    ques_item = re.compile('\?').findall(allItem_1)
                                    if not ques_item:
                                        if logbufferlist:
                                            if ' '.join(allItem_1.split()) in logbufferlist:
                                                viewlist = re.sub(
                                                    re.compile('[\[<>\]]{1}'), '',
                                                    re.compile(
                                                        '[<\[]{1}.*[>\]]{1}').findall(
                                                        re.sub(re.compile(
                                                            "\[\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}]"),
                                                            '', item))[0]).split("-")
                                                if re.compile(
                                                        '[\[]{1}.*[]]{1}').findall(
                                                    re.sub(re.compile(
                                                        "\[\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}]"),
                                                        '', item)):
                                                    # print(viewlist)
                                                    result_data.append({
                                                        'sysname': sysName,
                                                        'dut': sysName_f[0],
                                                        'viewlist_num': 1,
                                                        'viewlist': viewlist,
                                                        'time': date,
                                                        'config': allItem_1
                                                    })
                                                else:
                                                    result_data.append({
                                                        'sysname': sysName,
                                                        'dut': sysName_f[0],
                                                        'viewlist_num': 0,
                                                        'viewlist': viewlist,
                                                        'time': date,
                                                        'config': allItem_1
                                                    })
                                            # 此逻辑为不在logbuffer中命令
                                            else:
                                                continue
                                        # 此逻辑为没有logbuffer相关命令行
                                        else:
                                            print('Log Winthout Logbuffer Config')
                                            viewlist = re.sub(
                                                re.compile('[\[<>\]]{1}'), '',
                                                re.compile(
                                                    '[<\[]{1}.*[>\]]{1}').findall(
                                                    re.sub(re.compile(
                                                        "\[\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}]"),
                                                        '', item))[0]).split("-")
                                            # print(viewlist)
                                            if re.compile(
                                                    '[\[]{1}.*[]]{1}').findall(
                                                re.sub(re.compile(
                                                    "\[\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}]"),
                                                    '', item)):
                                                # print(viewlist)
                                                result_data.append({
                                                    'sysname': sysName,
                                                    'dut': sysName_f[0],
                                                    'viewlist_num': 1,
                                                    'viewlist': viewlist,
                                                    'time': date,
                                                    'config': allItem_1
                                                })
                                            else:
                                                result_data.append({
                                                    'sysname': sysName,
                                                    'dut': sysName_f[0],
                                                    'viewlist_num': 0,
                                                    'viewlist': viewlist,
                                                    'time': date,
                                                    'config': allItem_1
                                                })
                                    # 保留，此逻辑为带？联想命令行
                                    else:
                                        continue
                                else:
                                    continue
                            # 不带视图日志操作
                            else:
                                mainItem = re.sub(
                                    re.compile(
                                        '\[\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}]\s'),
                                    "",
                                    item)
                                bashItem = re.compile('^[$#]{1}').findall(mainItem)
                                if bashItem:
                                    bashconfig = re.sub(re.compile('[$#]{1}\s'),
                                                        "", mainItem)
                                    if re.sub(re.compile('[$#]{1}'),
                                              "", mainItem):
                                        result_data.append({
                                            'sysname': sysName,
                                            'dut': sysName_f[0],
                                            'viewlist_num': 99,
                                            'viewlist': ['bash'],
                                            'time': date,
                                            'config': bashconfig
                                        })
                                # 保留，此逻辑为命令行返回的信息
                                else:
                                    configreturn.append({
                                        'sysname': sysName,
                                        'dut': sysName_f[0],
                                        'viewlist_num': 98,
                                        'viewlist': ['configreturn'],
                                        'time': date,
                                        'config': mainItem
                                    })
                                    continue
                        # 保留，此逻辑为打印信息
                        else:
                            print_data.append({
                                'sysname': sysName,
                                'dut': sysName_f[0],
                                'viewlist_num': 99,
                                'viewlist': ['print'],
                                'time': date,
                                'config': printItem[0]
                            })
                    comand.close()
        result_data.sort(key=itemgetter('time'))
        print_data.sort(key=itemgetter('time'))
        # print(result_data)
        # print(configreturn)
        return result_data, print_data, configreturn

    # 处理topo
    def dealtopo(self):
        link_dir = {}
        ip_dir = {}
        ipv6_dir = {}
        dut = ''
        for path, dirlist, filelist in os.walk(self.filepath):
            for filename in filelist:
                txtname = self.filepath + filename
                filetype_t = re.compile('.topo').findall(filename)
                if filetype_t:
                    comand = open(txtname, encoding='utf-8')
                    lines = comand.read()
                    link_item = re.compile('MAP:.*').findall(lines)
                    link_ip = re.compile('rtentry:.*').findall(lines)
                    link_ipv6 = re.compile('rtentryv6=.*').findall(lines)
                    if link_item:
                        for link in link_item:
                            link_list_temp = link.split(':')[1].split(',')
                            for list in link_list_temp:
                                map_temp = list.split()
                                port_temp = {}
                                for map_t in map_temp:
                                    dut_m = re.compile('^' + map_temp[0]).findall(map_t)
                                    if dut_m:
                                        link_dir[map_t] = {}
                                        dut = map_t
                                    else:
                                        mapping_list = map_t.split('-')
                                        port_temp.update(
                                            {mapping_list[0]: mapping_list[1]})
                                        link_dir[dut] = port_temp
                    if link_ip:
                        for ip in link_ip:
                            linkip_list_temp = ip.split(':')[1].split(',')
                            for list in linkip_list_temp:
                                map_temp = list.split()
                                port_temp = {}
                                dut = map_temp[0]
                                for map_t in map_temp:
                                    if re.compile('PORT').findall(map_t):
                                        mapping_list = map_t.split('-')
                                        port_temp.update(
                                            {dut: mapping_list[0]})
                                        ip_dir[mapping_list[1]] = port_temp
                    if link_ipv6:
                        for ip in link_ipv6:
                            linkip_list_temp = ip.split('=')[1].split(',')
                            for list in linkip_list_temp:
                                map_temp = list.split()
                                port_temp = {}
                                dut = map_temp[0]
                                for map_t in map_temp:
                                    if re.compile('PORT').findall(map_t):
                                        mapping_list = map_t.split('-')
                                        port_temp.update(
                                            {dut: mapping_list[0]})
                                        ipv6_dir[mapping_list[1]] = port_temp
                    comand.close()
        return link_dir, ip_dir, ipv6_dir

    # 处处理命令行回显数据
    def configreturn(self, config, time):
        result_data, print_data, configreturn = self.disposelog()
        returnconfig = ''
        id = 1
        returnconfig_dir = {}
        for value in result_data:
            configreturn.append(value)
        configreturn.sort(key=itemgetter('time'))
        # print(configreturn)
        for index_temp, config_temp in enumerate(configreturn):
            if config == config_temp.get('config') and time == config_temp.get('time'):
                index_next = index_temp + 1
                for index_temp_n, config_temp_n in enumerate(configreturn[index_next:]):
                    if config_temp_n.get('viewlist_num') != 98:
                        index_next_r = index_temp_n + index_next
                        configreturn_temp = configreturn[index_next:index_next_r]
                        for k in configreturn_temp:
                            returnconfig = returnconfig + '\n' + k.get('config')
                        returnconfig_dir[id] = returnconfig
                        returnconfig = ''
                        id = id + 1
                        break
                    if config_temp_n == len(configreturn) - 1:
                        configreturn_temp = configreturn[index_next:]
                        for k in configreturn_temp:
                            returnconfig = returnconfig + '\n' + k.get('config')
                        returnconfig_dir[id] = returnconfig
                        returnconfig = ''
                        id = id + 1
                        break
        return returnconfig_dir

    #将配置数据ip对照topo转换
    def transip(self, result_data, ip_dir, ipv6_dir, link_dir):
        result_data_ip = []
        # ip_dir ={}
        # ipv6_dir = {}
        # link_dir = {}
        if ip_dir or ipv6_dir:
            for k in result_data:
                dut_1 = k.get('dut')
                config = k.get('config')
                config_t = ''
                if ip_dir:
                    if re.compile('\d+.\d+.\d+.\d+').findall(k.get('config')):
                        ip_list = re.compile('\d+.\d+.\d+.\d+').findall(k.get('config'))
                        # 获取dut和接口映射
                        # ip_list_t = ip_dir.get(k.get('dut')).values()
                        for ip in ip_list:
                            if ip in ip_dir:
                                dir = ip_dir.get(ip)
                                for dut_4, port_4 in dir.items():
                                    dut = dut_4
                                    port = port_4
                                config_t = re.sub(re.compile(ip), '$addr({dut},{port})'.format(dut=dut, port=port), config)
                if ipv6_dir:
                    ipv6list = []
                    for ipv6, cont in ipv6_dir.items():
                        ipv6list.append(ipv6)
                        for ipv6_t in ipv6list:
                            dir_v6 = ipv6_dir.get(ipv6_t)
                            if re.compile(ipv6_t).findall(k.get('config')):
                                for dut_6, port_6 in dir_v6.items():
                                    dut = dut_6
                                    port = port_6
                                if config_t:
                                    config_t = re.sub(re.compile(ipv6_t), '$addr6({dut},{port})'.format(dut=dut, port=port), config_t)
                                else:
                                    config_t = re.sub(re.compile(ipv6_t), '$addr6({dut},{port})'.format(dut=dut, port=port), config)

                if link_dir:
                    if dut_1 in link_dir:
                        portdir = link_dir.get(dut_1)
                        intlist = portdir.values()
                        for int in intlist:
                            if re.compile(int).findall(''.join(k.get('config').split())):
                                port_1 = self.getdictkey(portdir,int)
                                if config_t:
                                    config_t = re.sub(re.compile(int), ' $intf({dut},{port}) '.format(dut=dut_1, port=port_1[0]), ''.join(config_t.split()))
                                else:
                                    config_t = re.sub(re.compile(int), ' $intf({dut},{port}) '.format(dut=dut_1, port=port_1[0]), ''.join(config.split()))
                if config_t:
                    result_data_ip.append({
                        'sysname': k.get('sysname'),
                        'dut': k.get('dut'),
                        'viewlist_num': k.get('viewlist_num'),
                        'viewlist': k.get('viewlist'),
                        'time': k.get('time'),
                        'config': config_t
                    })
                else:
                    result_data_ip.append({
                        'sysname': k.get('sysname'),
                        'dut': k.get('dut'),
                        'viewlist_num': k.get('viewlist_num'),
                        'viewlist': k.get('viewlist'),
                        'time': k.get('time'),
                        'config': k.get('config')
                    })

        else:
            result_data_ip = result_data
        result_data_ip.sort(key=itemgetter('time'))
        return result_data_ip


    # 整理log
    def deallogbak(self):
        result_data, print_data, configreturn = self.disposelog()
        link_dir, ip_dir, ipv6_dir = self.dealtopo()
        result_data = self.transip(result_data, ip_dir,ipv6_dir,link_dir)
        config_data = []
        dutlist = []
        checkdatelist = []
        checknumlist = []
        checklist = []
        tempconfig_data = {}
        id = 1
        configdate = ''
        if result_data:
            for i, k in enumerate(result_data):
                viewlist = k.get('viewlist')
                date = k.get('time')
                dut = k.get('dut')
                '''
                check类型配置：check_num = 0 为command check
                check_num = 1 为ping check
                check_num = 2 为packet-capture抓包check
                check_num = 3 为dir查看文件check
                check_num = 4 为tracert查看文件check
                check_num = 5 为校验debug信息
                '''
                disItem = re.compile("^dis").findall(k.get("config").lstrip())
                includecheck = re.compile("include").findall(k.get("config"))
                ping_check = re.compile('^ping').findall(k.get('config').lstrip())
                tracert_check = re.compile('tracert').findall(k.get('config'))
                iproot_check = re.compile('peer').findall(k.get('config'))
                capture_check = re.compile('^packet-capture interface').findall(' '.join(k.get('config').split()))
                dir_check = re.compile('^dir').findall(k.get('config').lstrip())
                debug_check = re.compile('^debug').findall(k.get('config').lstrip())

                # 确定是否为check项
                if disItem or ping_check or capture_check or dir_check or tracert_check or debug_check:
                    # display 显示类信息流程处理
                    if disItem:
                        if re.compile("include").findall(k.get("config")) or re.compile("exclude").findall(k.get("config")):
                            dutlist.append(dut)
                            checkdatelist.append(date)
                            checknumlist.append(0)
                            checklist.append(k.get('config'))
                        # display不带include命令处理逻辑
                        # else:
                        #     dutlist.append(dut)
                        #     checkdatelist.append(date)
                        #     checknumlist.append(99)
                        #     checklist.append(k.get('config'))
                    if dir_check:
                        if re.compile("include").findall(k.get("config")) or re.compile("exclude").findall(k.get("config")):
                            dutlist.append(dut)
                            checkdatelist.append(date)
                            checknumlist.append(3)
                            checklist.append(k.get('config'))
                    if capture_check:
                        dutlist.append(dut)
                        checkdatelist.append(date)
                        checknumlist.append(2)
                        checklist.append(k.get('config'))
                    if ping_check:
                        dutlist.append(dut)
                        checkdatelist.append(date)
                        checknumlist.append(1)
                        checklist.append(k.get('config'))
                    if tracert_check:
                        dutlist.append(dut)
                        checkdatelist.append(date)
                        checknumlist.append(4)
                        checklist.append(k.get('config'))
                    if debug_check:
                        dutlist.append(dut)
                        checkdatelist.append(date)
                        checknumlist.append(5)
                        checklist.append(k.get('config'))
                # 非check配置逻辑
                else:
                    if checklist:
                        if tempconfig_data:
                            config_data.append({
                                'step': id,
                                'dut': dutlist,
                                'check_num': checknumlist,
                                'checkdate': checkdatelist,
                                'configdate': configdate,
                                'check': checklist,
                                'config_num': 0,
                                'config': tempconfig_data
                            })
                            tempconfig_data = {}
                            dutlist = []
                            checkdatelist = []
                            checknumlist = []
                            checklist = []
                            id = id + 1
                        else:
                            config_data.append({
                                'step': id,
                                'dut': dutlist,
                                'check_num': checknumlist,
                                'checkdate': checkdatelist,
                                'check': checklist
                            })
                            dutlist = []
                            checkdatelist = []
                            checknumlist = []
                            checklist = []
                            id = id + 1
                    configdate = date
                    if (k.get("dut")) in tempconfig_data:
                        # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                        tempconfig_data[k.get("dut")] = tempconfig_data[k.get("dut")] + '\n' + k.get('config')
                    else:
                        tempconfig_data[k.get("dut")] = k.get("config")
                    # 判断topo图中是否是存在接口映射
                    # if link_dir.get(k.get('dut')):
                    #     # 获取dut和接口映射
                    #     int_list = link_dir.get(k.get('dut')).values()
                    #     if viewlist[-1] in int_list:
                    #         int = self.getdictkey(link_dir.get(k.get('dut')),
                    #                               viewlist[-1])
                    #         for j in range(len(result_data[:i]) - 1, -1, -1):
                    #             if result_data[j].get('dut') == result_data[i].get('dut'):
                    #                 # 判断是不是和上条配置同一视图
                    #                 if result_data[j].get('viewlist')[-1] == viewlist[-1]:
                    #                     if re.compile('^dis').findall(result_data[j].get('config')):
                    #                         if (k.get("dut")) in tempconfig_data:
                    #                             # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                    #                             tempconfig_data[k.get("dut")] = \
                    #                                 tempconfig_data[k.get("dut")] + '\n' + 'int $intf(' + k.get('dut') + ',' + int[0] + ')' + '\n' + k.get(
                    #                                     'config')
                    #                             break
                    #                         else:
                    #                             tempconfig_data[k.get("dut")] = 'int $intf(' + k.get('dut') + ',' + int[0] + ')' + '\n' + k.get("config")
                    #                             break
                    #
                    #                     else:
                    #                         if (k.get("dut")) in tempconfig_data:
                    #                             # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                    #                             tempconfig_data[k.get("dut")] = \
                    #                                 tempconfig_data[k.get("dut")] + '\n' + k.get('config')
                    #                             break
                    #                         else:
                    #                             tempconfig_data[k.get("dut")] = k.get("config")
                    #                             break
                    #                 else:
                    #                     if (k.get("dut")) in tempconfig_data:
                    #                         # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                    #                         tempconfig_data[k.get("dut")] = \
                    #                             tempconfig_data[k.get("dut")] + '\n' + 'int $intf(' + k.get('dut') + ',' + int[0] + ')' + '\n' + k.get(
                    #                                 'config')
                    #                         break
                    #                     else:
                    #                         tempconfig_data[k.get("dut")] = 'int $intf(' + k.get('dut') + ',' + int[0] + ')' + '\n' + k.get("config")
                    #                         break
                    #     else:
                    #         if (i + 1) == len(result_data):
                    #             if (k.get("dut")) in tempconfig_data:
                    #                 # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                    #                 tempconfig_data[k.get("dut")] = \
                    #                     tempconfig_data[k.get("dut")] + '\n' + k.get('config')
                    #             else:
                    #                 tempconfig_data[k.get("dut")] = k.get("config")
                    #         else:
                    #             for i_t, l in enumerate(result_data[i + 1:]):
                    #                 if i_t == len(result_data[i + 1:]):
                    #                     if (k.get("dut")) in tempconfig_data:
                    #                         # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                    #                         tempconfig_data[k.get("dut")] = \
                    #                             tempconfig_data[k.get("dut")] + '\n' + k.get('config')
                    #                         break
                    #                     else:
                    #                         tempconfig_data[k.get("dut")] = k.get("config")
                    #                         break
                    #                 if l.get('dut') == result_data[i].get('dut'):
                    #                     if l.get('viewlist')[-1] in int_list:
                    #                         break
                    #                     else:
                                            # if (k.get("dut")) in tempconfig_data:
                                            #     # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                                            #     tempconfig_data[k.get("dut")] = \
                                            #         tempconfig_data[k.get("dut")] + '\n' + k.get('config')
                                            #     break
                                            # else:
                                            #     tempconfig_data[k.get("dut")] = k.get("config")
                                            #     break

                    # topo不存在dut映射
                    # else:
                    #     if (k.get("dut")) in tempconfig_data:
                    #         # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                    #         tempconfig_data[k.get("dut")] = tempconfig_data[k.get("dut")] + '\n' + k.get('config')
                    #     else:
                    #         tempconfig_data[k.get("dut")] = k.get("config")

            if checklist:
                if tempconfig_data:
                    config_data.append({
                        'step': id,
                        'dut': dutlist,
                        'check_num': checknumlist,
                        'checkdate': checkdatelist,
                        'configdate': configdate,
                        'check': checklist,
                        'config_num': 0,
                        'config': tempconfig_data
                    })
                    tempconfig_data = {}
                    dutlist = []
                    checkdatelist = []
                    checknumlist = []
                    checklist = []
                    id = id + 1
                else:
                    config_data.append({
                        'step': id,
                        'dut': dutlist,
                        'check_num': checknumlist,
                        'checkdate': checkdatelist,
                        'check': checklist
                    })
                    dutlist = []
                    checkdatelist = []
                    checknumlist = []
                    checklist = []
                    id = id + 1
            # print(config_data)
            if tempconfig_data:
                for key, value in tempconfig_data.items():
                    dutlist.append(dut)
                config_data.append({
                        'step': id,
                        'dut': dutlist,
                        'check_num': [99],
                        'check': ['none'],
                        'config_num': 0,
                        'config': tempconfig_data
                    })
                id = id + 1
        else:
            print('If no log meets requirements, check logs in the path')
        return config_data

    # 整理log
    def deallog(self):
        result_data, print_data, configreturn = self.disposelog()
        link_dir, ip_dir = self.dealtopo()
        config_data = []
        tempconfig_data = {}
        id = 1
        if result_data:
            for k in result_data:
                viewlist = k.get('viewlist')
                '''
                check类型配置：check_num = 0 为command check
                check_num = 1 为ping check
                '''
                disItem = re.compile("display").findall(k.get("config"))
                includecheck = re.compile("include").findall(k.get("config"))
                ping_check = re.compile('ping').findall(k.get('config'))
                iproot_check = re.compile('peer').findall(k.get('config'))
                # 判断命令行下发视图是不是一级视图
                if not (len(viewlist) == 1):
                    # 判断是否为check_num为0
                    if len(disItem) and len(includecheck):
                        if (k.get("dut")) in tempconfig_data:
                            config_data.append({
                                'step': id,
                                'dut': k.get("dut"),
                                'check_num': 0,
                                'check': k.get("config"),
                                'config_num': 0,
                                'config': tempconfig_data
                            })
                            tempconfig_data = {}
                            id = id + 1
                        else:
                            config_data.append({
                                'step': id,
                                'dut': k.get("dut"),
                                'check_num': 0,
                                'check': k.get("config")
                            })
                            id = id + 1
                    # 判断是否为ping check
                    elif len(ping_check) != 0:
                        if (k.get("dut")) in tempconfig_data:
                            config_data.append({
                                'step': id,
                                'dut': k.get("dut"),
                                'check_num': 1,
                                'check': k.get("config"),
                                'config_num': 0,
                                'config': tempconfig_data
                            })
                            tempconfig_data = {}
                            id = id + 1
                        else:
                            config_data.append({
                                'step': id,
                                'dut': k.get("dut"),
                                'check_num': 1,
                                'check': k.get("config")
                            })
                            id = id + 1
                    else:
                        if link_dir.get(k.get('dut')):
                            int_list = link_dir.get(k.get('dut')).values()
                            for index, view in enumerate(viewlist):
                                if view in int_list:
                                    int = self.getdictkey(link_dir.get(k.get('dut')),
                                                          view)
                                    if (k.get("dut")) in tempconfig_data:
                                        # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                                        tempconfig_data[k.get("dut")] = \
                                            tempconfig_data[k.get("dut")] + '\n' + 'int $l2intf(' + k.get('dut') + ',' + int[0] + ')' + '\n' + k.get('config')
                                    else:
                                        tempconfig_data[k.get("dut")] = 'int $l2intf(' + k.get('dut') + ',' + int[0] + ')' + '\n' + k.get("config")
                                elif index == (len(viewlist) - 1):
                                    if (k.get("dut")) in tempconfig_data:
                                        # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                                        tempconfig_data[k.get("dut")] = \
                                            tempconfig_data[k.get("dut")] + '\n' + k.get('config')
                                    else:
                                        tempconfig_data[k.get("dut")] = k.get("config")
                                else:
                                    continue
                        else:
                            if (k.get("dut")) in tempconfig_data:
                                # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                                tempconfig_data[k.get("dut")] = tempconfig_data[k.get("dut")] + '\n' + k.get('config')
                            else:
                                tempconfig_data[k.get("dut")] = k.get("config")
                else:
                    if len(disItem) and len(includecheck):
                        if (k.get("dut")) in tempconfig_data:
                            config_data.append({
                                'step': id,
                                'dut': k.get("dut"),
                                'check_num': 0,
                                'check': k.get("config"),
                                'config_num': 0,
                                'config': tempconfig_data
                            })
                            tempconfig_data = {}
                            id = id + 1
                        else:
                            config_data.append({
                                'step': id,
                                'dut': k.get("dut"),
                                'check_num': 0,
                                'check': k.get("config")
                            })
                            id = id + 1
                    elif len(ping_check) != 0:
                        if (k.get("dut")) in tempconfig_data:
                            config_data.append({
                                'step': id,
                                'dut': k.get("dut"),
                                'check_num': 1,
                                'check': k.get("config"),
                                'config_num': 0,
                                'config': tempconfig_data
                            })
                            tempconfig_data = {}
                            id = id + 1
                        else:
                            config_data.append({
                                'step': id,
                                'dut': k.get("dut"),
                                'check_num': 1,
                                'check': k.get("config")
                            })
                            id = id + 1
                    else:
                        if (k.get("dut")) in tempconfig_data:
                            # if tempconfig_data.has_key('DUT' + index):   #python2.7用法
                            tempconfig_data[k.get("dut")] = tempconfig_data[k.get("dut")] + '\n' + k.get('config')
                        else:
                            tempconfig_data[k.get("dut")] = k.get("config")
            if tempconfig_data:
                for key, value in tempconfig_data.items():
                    config_data.append({
                        'step': id,
                        'dut': key,
                        'check_num': 99,
                        'config_num': 0,
                        'config': {key: value}
                    })
                    id = id + 1
            # print(config_data)
        else:
            print('If no log meets requirements, check logs in the path')
        return config_data

    # 生成tcl
    def creattcl(self):
        config_data = self.deallogbak()
        modeName, topo_name = self.gettclname()
        result_file_o = open(self.result_file, mode='w+')
        header = '<TESTCASE_BEGIN>\n<TESTCASE_HEADER_BEGIN>\n    <TITLE>      "执行用例自动化生成脚本"\n    <INDEX>      "执行编号"\n    <LEVEL>      "2"\n    <WEIGHT>     "4"\n    <MODULE>     "{mode}"\n    <TYPE>       "FUN"\n    <AUTHOR>     "Automatic Generation"\n    <LIMITATION> "CmwV7Device"\n    <VERSION> "2.1"\n    <DESIGN> "log自动化脚本"\n    <SOURCE> "{topo}"\n<TESTCASE_HEADER_END>\n\n<TESTCASE_DEVICE_MAP_BEGIN>\n\n<TESTCASE_DEVICE_MAP_END>\n'.format(
            mode=modeName, topo=topo_name
        )
        ender = '\n<TESTCASE_END>'
        result_file_o.write(header)
        '''
        将config_data遍历组织成测试步骤
        '''
        for j in config_data:
            temp_step = j.get('step')
            temp_dut = j.get('dut')
            temp_check = j.get('check')
            temp_check_num = j.get('check_num')
            temp_check_date = j.get('checkdate')
            # if j.has_key('config'):  #python2.7用法
            if 'config' in j:
                temp_config = j.get('config')  # 返回是字典
                step = '\n<STEP> "step {step}" {{\n'.format(step=temp_step)
                result_file_o.write(step)
                for key in temp_config:
                    configlist = temp_config.get(key).split('\n')
                    temp_setconfig = ''
                    for setconfig in configlist:
                        #  将install封装成tcl函数
                        if re.compile('install').findall(setconfig):
                            setconfig_list = setconfig.split()
                            installconfig = 'setInstallActivate'
                            if temp_setconfig:
                                config = '{DUT} Config "\n{temconfig}	"\n'.format(
                                    DUT=key, temconfig=temp_setconfig)
                                result_file_o.write(config)
                                temp_setconfig = ''
                                for index, value in enumerate(setconfig_list):
                                    if value == "boot":
                                        installconfig = installconfig + '-bootfile' + setconfig_list[index + 1]
                                    if value == "system":
                                        installconfig = installconfig + '-systemfile' + setconfig_list[index + 1]
                                    if value == "feature":
                                        installconfig = installconfig + '-featurefile' + setconfig_list[index + 1]
                                    if value == "patch":
                                        installconfig = installconfig + '-patchfile' + setconfig_list[index + 1]
                                    if value == "slot":
                                        installconfig = installconfig + '-slot' + setconfig_list[index + 1]
                                    if value == "chassis":
                                        installconfig = installconfig + '-chassis' + setconfig_list[index + 1]
                                    if value == "test":
                                        installconfig = installconfig + '-testFlag' + '1'
                                config = '  {DUT} Config "\n{temconfig}	"\n'.format(
                                    DUT=key, temconfig=installconfig)
                                result_file_o.write(config)
                            else:
                                for index, value in enumerate(setconfig_list):
                                    if value == "boot":
                                        installconfig = installconfig + '-bootfile' + setconfig_list[index + 1]
                                    if value == "system":
                                        installconfig = installconfig + '-systemfile' + setconfig_list[index + 1]
                                    if value == "feature":
                                        installconfig = installconfig + '-featurefile' + setconfig_list[index + 1]
                                    if value == "patch":
                                        installconfig = installconfig + '-patchfile' + setconfig_list[index + 1]
                                    if value == "slot":
                                        installconfig = installconfig + '-slot' + setconfig_list[index + 1]
                                    if value == "chassis":
                                        installconfig = installconfig + '-chassis' + setconfig_list[index + 1]
                                    if value == "test":
                                        installconfig = installconfig + '-testFlag' + '1'
                                config = '{DUT} Config "\n{temconfig}	"\n'.format(
                                    DUT=key, temconfig=installconfig)
                                result_file_o.write(config)
                        else:
                            temp_setconfig = temp_setconfig + '\n' + '      ' + setconfig
                    if temp_setconfig:
                        config = '  {DUT} Config "\n{temconfig}	"\n'.format(
                            DUT=key, temconfig=temp_setconfig)
                        result_file_o.write(config)
            if temp_check:
                for index, value in enumerate(temp_check):
                    if temp_check_num[index] == 0:
                        if re.compile("include").findall(value):
                            include = re.sub(re.compile(".*\s*\|\s*include\s*"), "", value)
                            tempinclude_check = re.sub(re.compile("\s*\|\s*include\s*.*"), "",
                                                       value)
                            if re.compile('".*"').findall(include):
                                check = '\n	<CHECK> description "check {step}"\n	<CHECK> type custom\n	<CHECK> args  {{  \n	    {DUT} Config "return"\n	    {DUT1} CheckConfig -command "{allItem_1}" -include {include}  -checkreturn configreturn\n    }}\n	<CHECK> repeat 1 -interval 5 \n    <CHECK> whenfailed {{PUTSINFO "$configreturn"}}\n    <CHECK> \n'.format(
                                    step=temp_step, DUT=temp_dut[index], DUT1=temp_dut[index],
                                    allItem_1=tempinclude_check, include=include)
                            else:
                                check = '\n	<CHECK> description "check {step}"\n	<CHECK> type custom\n	<CHECK> args  {{  \n	    {DUT} Config "return"\n	    {DUT1} CheckConfig -command "{allItem_1}" -include "{include}"  -checkreturn configreturn\n    }}\n	<CHECK> repeat 1 -interval 5 \n    <CHECK> whenfailed {{PUTSINFO "$configreturn"}}\n    <CHECK> \n'.format(
                                    step=temp_step, DUT=temp_dut[index], DUT1=temp_dut[index],
                                    allItem_1=tempinclude_check, include=include)
                            result_file_o.write(check)
                        if re.compile("exclude").findall(value):
                            exclude = re.sub(re.compile(".*\s*\|\s*exclude\s*"), "", value)
                            tempexclude_check = re.sub(re.compile("\s*\|\s*exclude\s*.*"), "",
                                                       value)
                            if re.compile('".*"').findall(exclude):
                                check = '\n	<CHECK> description "check {step}"\n	<CHECK> type custom\n	<CHECK> args  {{  \n	    {DUT} Config "return"\n	    {DUT1} CheckConfig -command "{allItem_1}" -include {include}  -checkreturn configreturn\n    }}\n	<CHECK> repeat 1 -interval 5 \n    <CHECK> whenfailed {{PUTSINFO "$configreturn"}}\n    <CHECK> \n'.format(
                                    step=temp_step, DUT=temp_dut[index], DUT1=temp_dut[index],
                                    allItem_1=tempexclude_check, include=exclude)
                            else:
                                check = '\n	<CHECK> description "check {step}"\n	<CHECK> type custom\n	<CHECK> args  {{  \n	    {DUT} Config "return"\n	    {DUT1} CheckConfig -command "{allItem_1}" -include "{include}"  -checkreturn configreturn\n    }}\n	<CHECK> repeat 1 -interval 5 \n    <CHECK> whenfailed {{PUTSINFO "$configreturn"}}\n    <CHECK> \n'.format(
                                    step=temp_step, DUT=temp_dut[index], DUT1=temp_dut[index],
                                    allItem_1=tempexclude_check, include=exclude)
                            result_file_o.write(check)
                    elif temp_check_num[index] == 1:
                        dest_ip = re.sub('ping', '', value)
                        pinglist =  dest_ip.split()
                        ip = pinglist[-1]
                        for i ,v in enumerate(pinglist):
                            if v == '-a':
                                ip = ip + " -source " +pinglist[i+1]
                        check = '\n	<CHECK> description "check {step}"\n	<CHECK> type ping\n	<CHECK> object {DUT} \n	<CHECK> expect -negative 100\n	 <CHECK> args "{dest_ip}"\n	 <CHECK> repeat 3 -interval 5 \n	      <CHECK> \n'.format(
                            step=temp_step, DUT=temp_dut[index],
                            dest_ip=ip)
                        result_file_o.write(check)
                    elif temp_check_num[index] == 2:
                        include = re.sub(re.compile(".*\s*\|\s*include\s*"), "", value)
                        check_1 = re.sub(re.compile("\s\|\sinclude\s.*"), "",
                                            value)
                        check = '\n	<CHECK> description "check {step}"\n	<CHECK> type custom\n	<CHECK> args  {{  \n	    {DUT} Config "return"\n	    {DUT1} CheckConfig -command "{allItem_1}" -include "{include}"  -checkreturn configreturn\n    }}\n	<CHECK> repeat 1 -interval 5 \n    <CHECK> whenfailed {{PUTSINFO "$configreturn"}}\n    <CHECK> \n'.format(
                            step=temp_step, DUT=temp_dut[index], DUT1=temp_dut[index],
                            allItem_1=check_1, include=include)
                        result_file_o.write(check)
                    elif temp_check_num[index] == 3:
                        if re.compile("include").findall(value):
                            include = re.sub(re.compile(".*\s*\|\s*include\s*"), "", value)
                            tempinclude_check = re.sub(re.compile("\s\|\sinclude\s.*"), "",
                                                       value)
                            check = '\n	<CHECK> description "check {step}"\n	<CHECK> type custom\n	<CHECK> args  {{  \n	    {DUT} Config "return"\n	    {DUT1} CheckConfig -command "{allItem_1}" -include "{include}"  -checkreturn configreturn\n    }}\n	<CHECK> repeat 1 -interval 5 \n    <CHECK> whenfailed {{PUTSINFO "$configreturn"}}\n    <CHECK> \n'.format(
                                step=temp_step, DUT=temp_dut[index], DUT1=temp_dut[index],
                                allItem_1=tempinclude_check, include=include)
                            result_file_o.write(check)
                        if re.compile("exclude").findall(value):
                            exclude = re.sub(re.compile(".*\s*\|\s*exclude\s*"), "", value)
                            tempexclude_check = re.sub(re.compile("\s\|\sexclude\s.*"), "",
                                                       value)
                            check = '\n	<CHECK> description "check {step}"\n	<CHECK> type custom\n	<CHECK> args  {{  \n	    {DUT} Config "return"\n	    {DUT1} CheckConfig -command "{allItem_1}" -exclude "{exclude}"  -checkreturn configreturn\n }}\n	<CHECK> repeat 1 -interval 5 \n    <CHECK> whenfailed {{PUTSINFO "$configreturn"}}\n	      <CHECK> \n'.format(
                                step=temp_step, DUT=temp_dut[index], DUT1=temp_dut[index],
                                allItem_1=tempexclude_check, exclude=exclude)
                            result_file_o.write(check)
                    elif temp_check_num[index] == 4:
                        dest_tracert = re.sub(re.compile('tracert'), '', value)
                        check = '\n	<CHECK> description "check {step}"\n	<CHECK> type custom\n	<CHECK> args  {{  \n	    {DUT} Config "return"\n	    set a [{DUT1} executeTracert -target "{allItem_1}"] \n    return $a\n    }}\n	<CHECK> repeat 1 -interval 5 \n    <CHECK> whenfailed {{PUTSINFO "$a"}}\n    <CHECK>\n'.format(
                            step=temp_step, DUT=temp_dut[index], DUT1=temp_dut[index],
                            allItem_1=dest_tracert, include=include)
                        result_file_o.write(check)
                    elif temp_check_num[index] == 5:
                        check = '\n	<CHECK> description "check {step}"\n	<CHECK> type custom\n	<CHECK> args  {{  \n	    {DUT} Config "return\n         undo debugging  all\n         t  d \n         t m"\n		{DUT1} Send "{value}"\n		{DUT2} ClearBuffer\n		after 10000\n		set res2 [{DUT3} GetBuffer]\n		 if {{[string first "$config" $res2]!=-1}} {{\n				return 1\n		}} else {{\n			  return 0	\n      }}\n    }}\n	<CHECK> repeat 1 -interval 5 \n    <CHECK> whenfailed {{PUTSINFO "$a"}}\n    <CHECK> \n'.format(
                            step=temp_step, DUT=temp_dut[index], DUT1=temp_dut[index], DUT2=temp_dut[index], DUT3=temp_dut[index],value=value)
                        result_file_o.write(check)
                    # elif temp_check_num[index] == 99:
                    #     check = '}'
                    #     result_file_o.write(check)
                    if index==len(temp_check)-1:
                        check = '}'
                        result_file_o.write(check)
        result_file_o.write(ender)
        result_file_o.close()


    def generatenetconftcl(self):
        result_data, print_data, configreturn = self.disposelog()
        modeName, topo_name = self.gettclname()
        result_file_o = open(self.result_file, mode='w+')
        header = 'SET_RUNNING_PARAM if_address 1 open_mode 1\n<TESTCASE_BEGIN>\n<TESTCASE_HEADER_BEGIN>\n    <TITLE>      "自动化生成脚本"\n    <INDEX>      "x.x.x"\n    <LEVEL>      "2"\n    <WEIGHT>     "4"\n    <MODULE>     "{mode}"\n    <TYPE>       "NETCONF"\n    <AUTHOR>     "Automatic Generation"\n    <LIMITATION> "CmwV7Device"\n    <VERSION>    "2.1"\n    <DESIGN>     "netconf自动化脚本"\n    <SOURCE>     "{topo}"\n<TESTCASE_HEADER_END>\n\n<TESTCASE_DEVICE_MAP_BEGIN>\n\n<TESTCASE_DEVICE_MAP_END>\n'.format(
            mode=modeName, topo=topo_name)
        xmlhellorpc = '"<hello xmlns=\\"urn:ietf:params:xml:ns:netconf:base:1.0\\"><capabilities><capability>urn:ietf:params:netconf:base:1.0</capability></capabilities></hello>\]\]>\]\]>"'
        xmlcloserpc = '"<rpc message-id=\\"100\\" xmlns=\\"urn:ietf:params:xml:ns:netconf:base:1.0\\"><close-session/></rpc>\]\]>\]\]>"'
        preconfig = '\tset xmlhello ' + xmlhellorpc + '\n\tset xmlclose ' + xmlcloserpc + '\n\tDUT1 Config "netconf ssh server enable\n\tline vty 0 63\n\tauthentication-mode none\n\tuser-role network-admin\n\tidle-timeout 0 0\n\tquit\n\tpassword-recovery enable\n\tundo password-control composition enable\n\tpassword-control length 4\n\tundo password-control complexity user-name check\n\tlocal-user admin class manage\n\tpassword simple admin\n\tservice-type ssh telnet http https\n\tauthorization-attribute user-role network-admin\n\tauthorization-attribute user-role network-operator\n\tquit\n\tquit"\n\tOpenTerm -name netconf -type telnet -addr $addr(DUT1,PORT1) -port 23\n\tafter 3000\n\n\n\t##########部分对象须提前命令行配置的请在此处下发############\n\tDUT1 Config ""\n\n'
        ender = '\n<TESTCASE_END>'
        stepstart = '<STEP> "验证netconf功能" {\n'
        stepend = "}\n"

        # 拼接脚本头和预配置
        result_file_o.write(header)
        result_file_o.write(preconfig)
        result_file_o.write(stepstart)

        # 获取模块名  表名
        for line in print_data:
            temp = line.get("config")
            if re.match('.*XML_REQUEST.*', temp) != None and re.match('.*operation="merge".*', temp) != None:
                rpcxmltemp = re.findall('<rpc.*rpc>', temp)
                rpcxml = "".join(rpcxmltemp)

                startindex = rpcxml.index('"merge"><')
                endindex = rpcxml.index("></top>")
                tmp = rpcxml[startindex:endindex].split("></")
                feature = tmp[-1]
                tablename = tmp[-2]

            else:
                continue

        # 将print_data遍历 组织成测试步骤
        for line in print_data:
            temp = line.get("config")
            if re.match('.*XML_REQUEST.*', temp) != None:
                checkend = "\n}\n<CHECK>\n"

                # 拼装check
                if re.match('.*<get>.*', temp) != None:
                    checkstart = '<CHECK> description "' + feature + '/' + tablename + ' get表操作"\n<CHECK> type custom\n<CHECK> args {\n'
                    rpcxmltemp = re.findall('<rpc.*rpc>', temp)
                    rpcxml = "".join(rpcxmltemp)
                    result_file_o.write(checkstart)

                    # 目前针对数字　字符　范围内的列值
                    sublist = re.compile('>[1-9a-zA-Z]+<').findall(rpcxml)
                    # c count t1 t2 ...都是作为中间变量 l lenth
                    c = 1
                    for i in sublist:
                        t1 = re.findall(">[1-9a-zA-Z]+<", i)
                        t2 = t1[-1]
                        l = len(t2)
                        t3 = t2[1:l - 1]

                        rpcxml = re.sub(re.compile(i), ">$part_{c}<".format(c=c), rpcxml, 1)
                        t4 = "part_{c}".format(c=c)
                        c = c + 1
                        result_file_o.write("\tset " + t4 + " " + t3 + "\n")

                    c = c - 1
                    list1 = "set lst " + '"' + "合法值 " + "$part_{c}".format(c=c) + " 非法值" + '"'
                    rpcxml = rpcxml.replace("$part_{c}".format(c=c), "$pass").replace('"', '\\"')

                    checkbody1 = "\n\t" + list1 + "\n\tset i 0\n\tset lenth [expr [llength $lst]-1]\n\n\tfor { set i $i } { $i <= $lenth } { incr i }  {\n\t\tset pass [lindex $lst $i]"

                    checkbody2 = '\n\t\tif {$i==0} {\n\t\t\tset getrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody3 = '\n\t\tif {$i==1} {\n\t\t\tset getrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody4 = '\n\t\tif {$i==2} {\n\t\t\tset getrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'

                    checkbody5 = '\n\t}\n\texpr $i == [expr $lenth+1]'

                    result_file_o.write(str(checkbody1))
                    result_file_o.write(str(checkbody2))
                    result_file_o.write(str(checkbody3))
                    result_file_o.write(str(checkbody4))
                    result_file_o.write(str(checkbody5))
                    result_file_o.write(checkend)
                    result_file_o.write("\n\n\n")

                elif re.match('.*<get-bulk>.*', temp) != None:
                    checkstart = '<CHECK> description "' + feature + '/' + tablename + ' get-bulk表操作"\n<CHECK> type custom\n<CHECK> args {\n'
                    rpcxmltemp = re.findall('<rpc.*rpc>', temp)
                    rpcxml = "".join(rpcxmltemp)
                    result_file_o.write(checkstart)

                    # 目前针对数字　字符　范围内的列值
                    sublist = re.compile('>[1-9a-zA-Z]+<').findall(rpcxml)
                    # c count t1 t2 ...都是作为中间变量 l lenth
                    c = 1
                    for i in sublist:
                        t1 = re.findall(">[1-9a-zA-Z]+<", i)
                        t2 = t1[-1]
                        l = len(t2)
                        t3 = t2[1:l - 1]

                        rpcxml = re.sub(re.compile(i), ">$part_{c}<".format(c=c), rpcxml, 1)
                        t4 = "part_{c}".format(c=c)
                        c = c + 1
                        result_file_o.write("\tset " + t4 + " " + t3 + "\n")

                    c = c - 1
                    list1 = "set lst " + '"' + "合法值 " + "$part_{c}".format(c=c) + " 非法值" + '"'
                    rpcxml = rpcxml.replace("$part_{c}".format(c=c), "$pass").replace('"', '\\"')

                    checkbody1 = "\n\t" + list1 + "\n\tset i 0\n\tset lenth [expr [llength $lst]-1]\n\n\tfor { set i $i } { $i <= $lenth } { incr i }  {\n\t\tset pass [lindex $lst $i]"

                    checkbody2 = '\n\t\tif {$i==0} {\n\t\t\tset getbulkrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getbulkrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody3 = '\n\t\tif {$i==1} {\n\t\t\tset getbulkrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getbulkrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody4 = '\n\t\tif {$i==2} {\n\t\t\tset getbulkrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getbulkrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'

                    checkbody5 = '\n\t}\n\texpr $i == [expr $lenth+1]'

                    result_file_o.write(str(checkbody1))
                    result_file_o.write(str(checkbody2))
                    result_file_o.write(str(checkbody3))
                    result_file_o.write(str(checkbody4))
                    result_file_o.write(str(checkbody5))

                    result_file_o.write(checkend)
                    result_file_o.write("\n\n\n")

                elif re.match('.*<get-config>.*', temp) != None:
                    checkstart = '<CHECK> description "' + feature + '/' + tablename + ' get-config表操作"\n<CHECK> type custom\n<CHECK> args {\n'
                    rpcxmltemp = re.findall('<rpc.*rpc>', temp)
                    rpcxml = "".join(rpcxmltemp)
                    result_file_o.write(checkstart)

                    # 目前针对数字　字符　范围内的列值
                    sublist = re.compile('>[1-9a-zA-Z]+<').findall(rpcxml)
                    # c count t1 t2 ...都是作为中间变量 l lenth
                    c = 1
                    for i in sublist:
                        t1 = re.findall(">[1-9a-zA-Z]+<", i)
                        t2 = t1[-1]
                        l = len(t2)
                        t3 = t2[1:l - 1]

                        rpcxml = re.sub(re.compile(i), ">$part_{c}<".format(c=c), rpcxml, 1)
                        t4 = "part_{c}".format(c=c)
                        c = c + 1
                        result_file_o.write("\tset " + t4 + " " + t3 + "\n")

                    c = c - 1
                    list1 = "set lst " + '"' + "合法值 " + "$part_{c}".format(c=c) + " 非法值" + '"'
                    rpcxml = rpcxml.replace("$part_{c}".format(c=c), "$pass").replace('"', '\\"')

                    checkbody1 = "\n\t" + list1 + "\n\tset i 0\n\tset lenth [expr [llength $lst]-1]\n\n\tfor { set i $i } { $i <= $lenth } { incr i }  {\n\t\tset pass [lindex $lst $i]"

                    checkbody2 = '\n\t\tif {$i==0} {\n\t\t\tset getconfigrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getconfigrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody3 = '\n\t\tif {$i==1} {\n\t\t\tset getconfigrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getconfigrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody4 = '\n\t\tif {$i==2} {\n\t\t\tset getconfigrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getconfigrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'

                    checkbody5 = '\n\t}\n\texpr $i == [expr $lenth+1]'

                    result_file_o.write(str(checkbody1))
                    result_file_o.write(str(checkbody2))
                    result_file_o.write(str(checkbody3))
                    result_file_o.write(str(checkbody4))
                    result_file_o.write(str(checkbody5))

                    result_file_o.write(checkend)
                    result_file_o.write("\n\n\n")

                elif re.match('.*<get-bulk-config>.*', temp) != None:
                    checkstart = '<CHECK> description "' + feature + '/' + tablename + ' get-bulk-config表操作"\n<CHECK> type custom\n<CHECK> args {\n'
                    rpcxmltemp = re.findall('<rpc.*rpc>', temp)
                    rpcxml = "".join(rpcxmltemp)
                    result_file_o.write(checkstart)

                    # 目前针对数字　字符　范围内的列值
                    sublist = re.compile('>[1-9a-zA-Z]+<').findall(rpcxml)
                    # c count t1 t2 ...都是作为中间变量 l lenth
                    c = 1
                    for i in sublist:
                        t1 = re.findall(">[1-9a-zA-Z]+<", i)
                        t2 = t1[-1]
                        l = len(t2)
                        t3 = t2[1:l - 1]

                        rpcxml = re.sub(re.compile(i), ">$part_{c}<".format(c=c), rpcxml, 1)
                        t4 = "part_{c}".format(c=c)
                        c = c + 1
                        result_file_o.write("\tset " + t4 + " " + t3 + "\n")

                    c = c - 1
                    list1 = "set lst " + '"' + "合法值 " + "$part_{c}".format(c=c) + " 非法值" + '"'
                    rpcxml = rpcxml.replace("$part_{c}".format(c=c), "$pass").replace('"', '\\"')

                    checkbody1 = "\n\t" + list1 + "\n\tset i 0\n\tset lenth [expr [llength $lst]-1]\n\n\tfor { set i $i } { $i <= $lenth } { incr i }  {\n\t\tset pass [lindex $lst $i]"

                    checkbody2 = '\n\t\tif {$i==0} {\n\t\t\tset getbulkconfigrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getbulkconfigrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody3 = '\n\t\tif {$i==1} {\n\t\t\tset getbulkconfigrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getbulkconfigrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody4 = '\n\t\tif {$i==2} {\n\t\t\tset getbulkconfigrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $getbulkconfigrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "<data></data>" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'

                    checkbody5 = '\n\t}\n\texpr $i == [expr $lenth+1]'

                    result_file_o.write(str(checkbody1))
                    result_file_o.write(str(checkbody2))
                    result_file_o.write(str(checkbody3))
                    result_file_o.write(str(checkbody4))
                    result_file_o.write(str(checkbody5))

                    result_file_o.write(checkend)
                    result_file_o.write("\n\n\n")

                elif re.match('.*operation="merge".*', temp) != None:
                    checkstart = '<CHECK> description "' + feature + '/' + tablename + ' merge表操作"\n<CHECK> type custom\n<CHECK> args {\n'
                    rpcxmltemp = re.findall('<rpc.*rpc>', temp)
                    rpcxml = "".join(rpcxmltemp)
                    result_file_o.write(checkstart)

                    # 目前针对数字　字符　范围内的列值
                    sublist = re.compile('>[1-9a-zA-Z]+<').findall(rpcxml)
                    # c count t1 t2 ...都是作为中间变量 l lenth
                    c = 1
                    for i in sublist:
                        t1 = re.findall(">[1-9a-zA-Z]+<", i)
                        t2 = t1[-1]
                        l = len(t2)
                        t3 = t2[1:l - 1]

                        rpcxml = re.sub(re.compile(i), ">$part_{c}<".format(c=c), rpcxml, 1)
                        t4 = "part_{c}".format(c=c)
                        c = c + 1
                        result_file_o.write("\tset " + t4 + " " + t3 + "\n")

                    c = c - 1
                    list1 = "set lst " + '"' + "合法值 " + "$part_{c}".format(c=c) + " 非法值" + '"'
                    rpcxml = rpcxml.replace("$part_{c}".format(c=c), "$pass").replace('"', '\\"')

                    checkbody1 = "\n\t" + list1 + "\n\tset i 0\n\tset lenth [expr [llength $lst]-1]\n\n\tfor { set i $i } { $i <= $lenth } { incr i }  {\n\t\tset pass [lindex $lst $i]"

                    checkbody2 = '\n\t\tif {$i==0} {\n\t\t\tset mergegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $mergegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody3 = '\n\t\tif {$i==1} {\n\t\t\tset mergegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $mergegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody4 = '\n\t\tif {$i==2} {\n\t\t\tset mergegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $mergegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'

                    checkbody5 = '\n\t}\n\texpr $i == [expr $lenth+1]'

                    result_file_o.write(str(checkbody1))
                    result_file_o.write(str(checkbody2))
                    result_file_o.write(str(checkbody3))
                    result_file_o.write(str(checkbody4))
                    result_file_o.write(str(checkbody5))

                    result_file_o.write(checkend)
                    result_file_o.write("\n\n\n")

                elif re.match('.*operation="create".*', temp) != None:
                    checkstart = '<CHECK> description "' + feature + '/' + tablename + ' create表操作"\n<CHECK> type custom\n<CHECK> args {\n'
                    rpcxmltemp = re.findall('<rpc.*rpc>', temp)
                    rpcxml = "".join(rpcxmltemp)
                    result_file_o.write(checkstart)

                    # 目前针对数字　字符　范围内的列值
                    sublist = re.compile('>[1-9a-zA-Z]+<').findall(rpcxml)
                    # c count t1 t2 ...都是作为中间变量 l lenth
                    c = 1
                    for i in sublist:
                        t1 = re.findall(">[1-9a-zA-Z]+<", i)
                        t2 = t1[-1]
                        l = len(t2)
                        t3 = t2[1:l - 1]

                        rpcxml = re.sub(re.compile(i), ">$part_{c}<".format(c=c), rpcxml, 1)
                        t4 = "part_{c}".format(c=c)
                        c = c + 1
                        result_file_o.write("\tset " + t4 + " " + t3 + "\n")

                    c = c - 1
                    list1 = "set lst " + '"' + "合法值 " + "$part_{c}".format(c=c) + " 非法值" + '"'
                    rpcxml = rpcxml.replace("$part_{c}".format(c=c), "$pass").replace('"', '\\"')

                    checkbody1 = "\n\t" + list1 + "\n\tset i 0\n\tset lenth [expr [llength $lst]-1]\n\n\tfor { set i $i } { $i <= $lenth } { incr i }  {\n\t\tset pass [lindex $lst $i]"

                    checkbody2 = '\n\t\tif {$i==0} {\n\t\t\tset creategrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $creategrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody3 = '\n\t\tif {$i==1} {\n\t\t\tset creategrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $creategrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody4 = '\n\t\tif {$i==2} {\n\t\t\tset creategrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $creategrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "Configuration already exists." $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'

                    checkbody5 = '\n\t}\n\texpr $i == [expr $lenth+1]'

                    result_file_o.write(str(checkbody1))
                    result_file_o.write(str(checkbody2))
                    result_file_o.write(str(checkbody3))
                    result_file_o.write(str(checkbody4))
                    result_file_o.write(str(checkbody5))

                    result_file_o.write(checkend)
                    result_file_o.write("\n\n\n")

                elif re.match('.*operation="replace".*', temp) != None:
                    checkstart = '<CHECK> description "' + feature + '/' + tablename + ' replace表操作"\n<CHECK> type custom\n<CHECK> args {\n'
                    rpcxmltemp = re.findall('<rpc.*rpc>', temp)
                    rpcxml = "".join(rpcxmltemp)
                    result_file_o.write(checkstart)

                    # 目前针对数字　字符　范围内的列值
                    sublist = re.compile('>[1-9a-zA-Z]+<').findall(rpcxml)
                    # c count t1 t2 ...都是作为中间变量 l lenth
                    c = 1
                    for i in sublist:
                        t1 = re.findall(">[1-9a-zA-Z]+<", i)
                        t2 = t1[-1]
                        l = len(t2)
                        t3 = t2[1:l - 1]

                        rpcxml = re.sub(re.compile(i), ">$part_{c}<".format(c=c), rpcxml, 1)
                        t4 = "part_{c}".format(c=c)
                        c = c + 1
                        result_file_o.write("\tset " + t4 + " " + t3 + "\n")

                    c = c - 1
                    list1 = "set lst " + '"' + "合法值 " + "$part_{c}".format(c=c) + " 非法值" + '"'
                    rpcxml = rpcxml.replace("$part_{c}".format(c=c), "$pass").replace('"', '\\"')

                    checkbody1 = "\n\t" + list1 + "\n\tset i 0\n\tset lenth [expr [llength $lst]-1]\n\n\tfor { set i $i } { $i <= $lenth } { incr i }  {\n\t\tset pass [lindex $lst $i]"

                    checkbody2 = '\n\t\tif {$i==0} {\n\t\t\tset replacegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $replacegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody3 = '\n\t\tif {$i==1} {\n\t\t\tset replacegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $replacegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody4 = '\n\t\tif {$i==2} {\n\t\t\tset replacegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $replacegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'

                    checkbody5 = '\n\t}\n\texpr $i == [expr $lenth+1]'

                    result_file_o.write(str(checkbody1))
                    result_file_o.write(str(checkbody2))
                    result_file_o.write(str(checkbody3))
                    result_file_o.write(str(checkbody4))
                    result_file_o.write(str(checkbody5))

                    result_file_o.write(checkend)
                    result_file_o.write("\n\n\n")

                elif re.match('.*operation="delete".*', temp) != None:
                    checkstart = '<CHECK> description "' + feature + '/' + tablename + ' delete表操作"\n<CHECK> type custom\n<CHECK> args {\n'
                    rpcxmltemp = re.findall('<rpc.*rpc>', temp)
                    rpcxml = "".join(rpcxmltemp)

                    result_file_o.write(checkstart)

                    # 目前针对数字　字符　范围内的列值
                    sublist = re.compile('>[1-9a-zA-Z]+<').findall(rpcxml)
                    # c count t1 t2 ...都是作为中间变量 l lenth
                    c = 1
                    for i in sublist:
                        t1 = re.findall(">[1-9a-zA-Z]+<", i)
                        t2 = t1[-1]
                        l = len(t2)
                        t3 = t2[1:l - 1]

                        rpcxml = re.sub(re.compile(i), ">$part_{c}<".format(c=c), rpcxml, 1)
                        t4 = "part_{c}".format(c=c)
                        c = c + 1
                        result_file_o.write("\tset " + t4 + " " + t3 + "\n")

                    c = c - 1
                    list1 = "set lst " + '"' + "合法值 " + "$part_{c}".format(c=c) + " 非法值" + '"'
                    rpcxml = rpcxml.replace("$part_{c}".format(c=c), "$pass").replace('"', '\\"')

                    checkbody1 = "\n\t" + list1 + "\n\tset i 0\n\tset lenth [expr [llength $lst]-1]\n\n\tfor { set i $i } { $i <= $lenth } { incr i }  {\n\t\tset pass [lindex $lst $i]"

                    checkbody2 = '\n\t\tif {$i==0} {\n\t\t\tset deletegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $deletegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody3 = '\n\t\tif {$i==1} {\n\t\t\tset deletegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $deletegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody4 = '\n\t\tif {$i==2} {\n\t\t\tset deletegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $deletegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "Configuration does not exist." $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'

                    checkbody5 = '\n\t}\n\texpr $i == [expr $lenth+1]'

                    result_file_o.write(str(checkbody1))
                    result_file_o.write(str(checkbody2))
                    result_file_o.write(str(checkbody3))
                    result_file_o.write(str(checkbody4))
                    result_file_o.write(str(checkbody5))

                    result_file_o.write(checkend)
                    result_file_o.write("\n\n\n")

                elif re.match('.*operation="remove".*', temp) != None:
                    checkstart = '<CHECK> description "' + feature + '/' + tablename + ' remove表操作"\n<CHECK> type custom\n<CHECK> args {\n'
                    rpcxmltemp = re.findall('<rpc.*rpc>', temp)
                    rpcxml = "".join(rpcxmltemp)
                    result_file_o.write(checkstart)

                    # 目前针对数字　字符　范围内的列值
                    sublist = re.compile('>[1-9a-zA-Z]+<').findall(rpcxml)
                    # c count t1 t2 ...都是作为中间变量 l lenth
                    c = 1
                    for i in sublist:
                        t1 = re.findall(">[1-9a-zA-Z]+<", i)
                        t2 = t1[-1]
                        l = len(t2)
                        t3 = t2[1:l - 1]

                        rpcxml = re.sub(re.compile(i), ">$part_{c}<".format(c=c), rpcxml, 1)
                        t4 = "part_{c}".format(c=c)
                        c = c + 1
                        result_file_o.write("\tset " + t4 + " " + t3 + "\n")

                    c = c - 1
                    list1 = "set lst " + '"' + "合法值 " + "$part_{c}".format(c=c) + " 非法值" + '"'
                    rpcxml = rpcxml.replace("$part_{c}".format(c=c), "$pass").replace('"', '\\"')

                    checkbody1 = "\n\t" + list1 + "\n\tset i 0\n\tset lenth [expr [llength $lst]-1]\n\n\tfor { set i $i } { $i <= $lenth } { incr i }  {\n\t\tset pass [lindex $lst $i]"

                    checkbody2 = '\n\t\tif {$i==0} {\n\t\t\tset removegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $removegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody3 = '\n\t\tif {$i==1} {\n\t\t\tset removegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $removegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'
                    checkbody4 = '\n\t\tif {$i==2} {\n\t\t\tset removegrpc ' + '"' + rpcxml + "\]\]>\]\]>" + '"' + '\n\t\t\ttsend3  netconf "xml"\n\t\t\t<WAIT> 3\n\t\t\ttsend3  netconf -t 3000  $xmlhello\n\t\t\t<WAIT> 3\n\t\t\ttclear netconf\n\t\t\ttsend3  netconf -t 3000  $removegrpc\n\t\t\t<WAIT> 3\n\t\t\tset res [tget netconf]\n\n\t\t\t#请根据实际情况调整检查内容\n\t\t\tif {[string first "ok" $res] != -1} {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tcontinue\n\t\t\t} else {\n\t\t\t\ttsend3  netconf -t 1000 $xmlclose\n\t\t\t\t<WAIT> 3\n\t\t\t\tbreak\n\t\t\t}\n\t\t}'

                    checkbody5 = '\n\t}\n\texpr $i == [expr $lenth+1]'

                    result_file_o.write(str(checkbody1))
                    result_file_o.write(str(checkbody2))
                    result_file_o.write(str(checkbody3))
                    result_file_o.write(str(checkbody4))
                    result_file_o.write(str(checkbody5))

                    result_file_o.write(checkend)
                    result_file_o.write("\n\n\n")

        # 拼接脚本尾　
        result_file_o.write(stepend)
        result_file_o.write(ender)
        result_file_o.close()



