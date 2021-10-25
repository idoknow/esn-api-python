import socket
import json
import hashlib
import threading
import struct
import datetime
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


# 注意 conn目前为全局变量
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
            __debug("获得结果：" + res.decode())
            data_size = -1
            data_id = -1
        if get_bytes_count == 1:
            data_id = struct.unpack('>i', res)
            __debug("获得数据包识别码：" + str(data_id[0]))
        if get_bytes_count == 2:
            data_size = struct.unpack('>i', res)
            __debug("获得数据包大小：" + str(data_size[0]))

        if get_bytes_count == 3:
            buffer_size = data_size[0]

        # print(struct.unpack('>i',res))
        # byte_array.append(res)
        # bytes_count+=1


def return_message(json_res):
    return json_res


# Send NetPackage in a blocked way.
def sendNetPackageBlocked(conn, pack_code, crypto, pack_data):
    __debug("---pack start---")
    conn.send(pack_code.to_bytes(4, 'big'))  # 4代表2字节
    __debug("---sent code---" + str(pack_code))
    conn.send(len(pack_data).to_bytes(4, 'big'))
    __debug("---sent length---" + str(len(pack_data)))
    conn.send(crypto.to_bytes(4, 'big'))
    __debug("---sent crypto---" + str(crypto))
    conn.send(pack_data.encode('utf-8'))
    __debug("---sent data---" + str(pack_data.encode('utf-8')))
    i = 0
    # while i<4:
    #     if i==3:
    #         print(conn.recv(2048).decode('utf-8', 'ignore'))
    #     else:
    #         print(int.from_bytes(conn.recv(2048), byteorder='big', signed=False))
    #     i+=1


#
def randToken(plain_text):
    hl = hashlib.md5()
    str_rand = str(uuid.uuid4())
    __debug("generating token:" + str_rand)
    hl.update((plain_text + str_rand).encode(encoding='utf-8'))
    return hl.hexdigest()


#
def login(user, password):
    dict_login_data = {"User": "-1", "Pass": "-1", "Token": "-1"}
    dict_ask_priv_data = {"Priv": "", "Token": "-1"}
    dict_login_data["User"] = user
    dict_login_data["Pass"] = password
    dict_login_data["Token"] = randToken(user + password)
    login_pack = json.dumps(dict_login_data)
    dict_ask_priv_data["Token"] = randToken(user + password)
    ask_priv_list_pack = json.dumps(dict_ask_priv_data)
    __debug("login_pack:" + login_pack)
    sendNetPackageBlocked(conn, LOGIN_PACKAGE_CODE, CRYPTO_CODE, login_pack)
    sendNetPackageBlocked(conn, ASK_PRIV_LIST_PACKAGE_CODE, CRYPTO_CODE, ask_priv_list_pack)


def requestNotification(rfrom, rto, limit):
    dict_request_data = {"From": rfrom, "To": rto, "Limit": limit,
                         "Token": randToken(str(rfrom) + str(rto) + str(limit))}
    request_data = json.dumps(dict_request_data)
    sendNetPackageBlocked(conn, REQUEST_VIA_INTERVAL_PACKAGE_CODE, CRYPTO_CODE, request_data)


def requestRecent(limit):
    dict_request_recent_data = {"Limit": limit, "Token": randToken(str(limit))}
    request_recent_data = json.dumps(dict_request_recent_data)
    sendNetPackageBlocked(conn, REQUEST_RECENT_PACKAGE_CODE, CRYPTO_CODE, request_recent_data)


def pushNotification(target, title, content):
    dict_push_data = {"Target": target, "Time": datetime.datetime.strptime('%Y-%m-%d,%H:%M:%S'), "Title": title,
                      "Content": content, "Token": randToken(content)}
    push_data = json.dumps(dict_push_data)
    sendNetPackageBlocked(conn, PUSH_NOTIFICATION_PACKAGE_CODE, CRYPTO_CODE, push_data)


def addAccount(name, password, privilege):
    __operateAccount("add", name, password, privilege, "False")


def removeAccount(name, kick):
    __operateAccount("remove", name, "", "", kick)


def __operateAccount(op, name, password, privilege, kick):
    dict_operate_account_data = {"Oper": op, "Name": name, "Pass": password, "Priv": privilege, "Kick": kick,
                                 "Token": randToken(op + name + password + privilege)}
    operate_account_data = json.dumps(dict_operate_account_data)
    sendNetPackageBlocked(conn, OPERATE_ACCOUNT_PACKAGE_CODE, CRYPTO_CODE, operate_account_data)


def countNotification(rfrom, rto):
    dict_count_data = {"From": rfrom, "To": rto, "Token": randToken(rfrom + rto)}
    count_data = json.dumps(dict_count_data)
    sendNetPackageBlocked(conn, COUNT_NOTIFICATION_PACKAGE_CODE, CRYPTO_CODE, count_data)


def connect(address):
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(address)
    conn.send(AUTH_CODE.to_bytes(4, 'big'))
    __debug("ProtocolVersionCode：" + str(struct.unpack('>i', conn.recv(1024))[0]))
    threading.Thread(target=thread_listening_socket).start()
    __debug("connected to server." + str(int.from_bytes(AUTH_CODE.to_bytes(4, 'big'), byteorder='big', signed=True)))


debugMode = False


def __debug(message):
    if debugMode:
        print(message)
