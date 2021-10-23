import socket
import json
import hashlib
import threading
import struct
import datetime
import random
import uuid

START_TAG = 0
AUTH_CODE = 119812525
CRYPTO_CODE = 0
LOGIN_PACKAGE_CODE = 1
PUSH_NOTIFICATION_PACKAGE_CODE = 3
REQUEST_VIA_INTERVAL_PACKAGE_CODE = 4
ASK_PRIV_LIST_PACKAGE_CODE = 6
OPERATE_ACCOUNT_PACKAGE_CODE = 7
REQUEST_RECENT_PACKAGE_CODE = 10
COUNT_NOTIFICATION_PACKAGE_CODE = 11
#注意 conn目前为全局变量
def thread_listening_socket():
    # bytes_count = 0
    # byte_array = []
    get_bytes_count = 0
    data_size = -1
    buffer_size = 4
    data_id = -1
    while 1:
        # if bytes_count == 4:
        #     print(byte_array)
        #     bytes_str = ""
        #     for byte_bean in byte_array:
        #         bytes_str += byte_bean
        #     # print(struct.unpack('>i',bytes_str.replace("b","").replace("'","")`.encode()))
        #
        #     byte_array.clear()
        #     bytes_count = 0
        res = conn.recv(buffer_size)
        get_bytes_count += 1
        if get_bytes_count == 4 and data_size != -1:
            get_bytes_count = 0
            buffer_size = 4
            print("获得结果："+res.decode())
            data_size = -1
            data_id = -1
        if get_bytes_count == 1:
            data_id = struct.unpack('>i',res)
            print("获得数据包识别码："+str(data_id[0]))
        if get_bytes_count == 2:
            data_size = struct.unpack('>i',res)
            print("获得数据包大小："+str(data_size[0]))

        if get_bytes_count == 3:
            buffer_size = data_size[0]

        # print(struct.unpack('>i',res))
        # byte_array.append(res)
        # bytes_count+=1


def return_message(json_res):
    return json_res

def util_pack_net_package(conn, pack_code, crypto, pack_data):
    print("---pack start---")
    conn.send(pack_code.to_bytes(4,'big'))  #4代表2字节
    print("---sent code---"+str(pack_code))
    conn.send(len(pack_data).to_bytes(4,'big'))
    print("---sent length---"+str(len(pack_data)))
    conn.send(crypto.to_bytes(4,'big'))
    print("---sent crypto---"+str(crypto))
    conn.send(pack_data.encode('utf-8'))
    print("---sent data---"+str(pack_data.encode('utf-8')))
    i = 0
    # while i<4:
    #     if i==3:
    #         print(conn.recv(2048).decode('utf-8', 'ignore'))
    #     else:
    #         print(int.from_bytes(conn.recv(2048), byteorder='big', signed=False))
    #     i+=1

#
def util_token_generate(ori_str):
    hl = hashlib.md5()
    str_rand = str(uuid.uuid4())
    print("生成标准密码学随机字符串"+str_rand)
    hl.update((ori_str+str_rand).encode(encoding='utf-8'))
    return hl.hexdigest()
#
def login_esn(user, psw):
    dict_login_data = {"User": "-1", "Pass": "-1", "Token": "-1"}
    dict_ask_priv_data = {"Priv": "","Token": "-1"}
    dict_login_data["User"] = user
    dict_login_data["Pass"] = psw
    dict_login_data["Token"] = util_token_generate(user+psw)
    login_pack = json.dumps(dict_login_data)
    dict_ask_priv_data["Token"] = util_token_generate(user+psw)
    ask_priv_list_pack = json.dumps(dict_ask_priv_data)
    print(login_pack)
    util_pack_net_package(conn, LOGIN_PACKAGE_CODE, CRYPTO_CODE, login_pack)
    util_pack_net_package(conn, ASK_PRIV_LIST_PACKAGE_CODE, CRYPTO_CODE, ask_priv_list_pack)



def request_via_interval(rfrom, rto, rlim):
    dict_request_data = {"From": "-1", "To": "-1", "Limit": "-1", "Token": "-1"}
    dict_request_data["From"] = rfrom
    dict_request_data["To"] = rto
    dict_request_data["Limit"] = rlim
    dict_request_data["Token"] = util_token_generate(str(rfrom)+str(rto)+str(rlim))
    request_data = json.dumps(dict_request_data)
    util_pack_net_package(conn, REQUEST_VIA_INTERVAL_PACKAGE_CODE, CRYPTO_CODE, request_data)

def request_recent(rlim):
    dict_request_recent_data = {"Limit": "-1", "Token": "-1"}
    dict_request_recent_data["Limit"] = rlim
    dict_request_recent_data["Token"] = util_token_generate(str(rlim))
    request_recent_data = json.dumps(dict_request_recent_data)
    util_pack_net_package(conn, REQUEST_RECENT_PACKAGE_CODE, CRYPTO_CODE, request_recent_data)

def push_notification(target, title, content):
    dict_push_data = {
        "Target":"-1",
        "Time":"-1",
    	"Title":"-1",
	    "Content":"-1",
	    "Token":"-1"
    }
    dict_push_data["Target"] = target
    dict_push_data["Time"] = datetime.datetime.strptime('%Y-%m-%d,%H:%M:%S')
    dict_push_data["Title"] = title
    dict_push_data["Content"] = content
    dict_push_data["Token"] = util_token_generate(content)
    push_data = json.dumps(dict_push_data)
    util_pack_net_package(conn, PUSH_NOTIFICATION_PACKAGE_CODE, CRYPTO_CODE, push_data)

def operate_account(oper_add_or_remove, name, psw, priv, is_kick):
    dict_operate_account_data = {
        "Oper":"-1",
        "Name":"-1",
        "Pass":"-1",
        "Priv":"-1",
        "Kick":"-1",
        "Token":"-1"
    }
    dict_operate_account_data["Oper"] = oper_add_or_remove
    dict_operate_account_data["Name"] = name
    dict_operate_account_data["Pass"] = psw
    dict_operate_account_data["Priv"] = priv
    dict_operate_account_data["Kick"] = is_kick
    dict_operate_account_data["Token"] = util_token_generate(oper+name+psw+priv)
    operate_account_data = json.dumps(dict_operate_account_data)
    util_pack_net_package(conn, OPERATE_ACCOUNT_PACKAGE_CODE, CRYPTO_CODE, operate_account_data)

def count_notification(rfrom, rto):
    dict_count_data = {
    "From":"-1",
    "To":"-1",
    "Token":"-1"}
    dict_count_data["From"] = rfrom
    dict_count_data["To"] = rto
    dict_count_data["Token"] = util_token_generate(rfrom+rto)
    count_data = json.dumps(dict_count_data)
    util_pack_net_package(conn, COUNT_NOTIFICATION_PACKAGE_CODE, CRYPTO_CODE, count_data)


def start_esn(address):
    START_TAG = 1
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(address)
    conn.send(AUTH_CODE.to_bytes(4, 'big'))
    print("获得VersionCode："+str(struct.unpack('>i',conn.recv(1024))[0]))
    threading.Thread(target=thread_listening_socket).start()
    print("connected to server."+str(int.from_bytes(AUTH_CODE.to_bytes(4, 'big'),byteorder='big', signed=True)))

