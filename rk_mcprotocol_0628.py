import socket

""" 
    元件代碼
    功能敘述	     PLC   元件代碼     進 制
    -------------------------------------------
    輸入	          X	       9C      8進制
    輸出	          Y	       9D      8進制
    內部繼電器        M	       90      10進制
    鎖存繼電器	      L	       92      10進制
    警報器	          F	       93      10進制
    連接繼電器   	  B	       A0      16進制
    數據寄存器	      D	       A8      10進制
    連接寄存器	      W	       B4      16進制
    文件寄存器        R        AF      10進制
    ------------------------------------------- """
    


element_list = [{"M": b'\x90',"L": b'\x92',"F": b'\x93',"D": b'\xA8',"R": b'\xAF'}, {"B": b'\xA0',"W": b'\xB4'},{"X": b'\x9C',"Y": b'\x9D'}]
io_table = { "X" : [8,1024] , "Y" : [8,1024] , "M" : [10,32768] , "L" : [10,32768] , "F" : [10,32768] , "B" : [16,32768] , "D" : [10,8000] , "W" : [16,32768] ,"R" : [10,32768] }
length_limit ={"read_sign_word" : 960 ,"read_sign_Dword" : 480,"write_sign_word" : 960 ,"write_sign_Dword" : 480, "read_bit" : 3584 ,"write_bit" : 3584}
"""              请求目标多点站号                           
     網路編號 请求IO編號  ↓                                              元件   
 副偵頭|  ↓ |PC|   ↓   | ↓ |請求長度| 保 留 |  指令 | 子指令 |起始元件標號|代碼|元件長度|傳送資料| 
b'P\x00\x00\xff\xff\x03\x00\x0e\x00\x00\x00\x01\x14\x01\x00\x08\x00\x00\x9d\x04\x00\x11\x11' 
                                     14  13  12  11  10   9   8   7   6   5   4   3   2   1
                "請求長度"計算範圍→→→ |--------------------共14碼---------------------------| (所以 = x0e)
 """
main_data_byte = {
    "read_word" :b'\x50\x00\x00\xff\xff\x03\x00\x0c\x00\x00\x00\x01\x04\x00\x00',   #指令 0401H  子指令0000H
    "read_bit"  :b'\x50\x00\x00\xff\xff\x03\x00\x0c\x00\x00\x00\x01\x04\x01\x00',   #指令 0401H  子指令0001H
    "write_bit" :b'P\x00\x00\xff\xff\x03\x00\x0c\x00\x00\x00\x01\x14\x01\x00' ,     #指令 1401H  子指令0001H
    "write_word" :b'P\x00\x00\xff\xff\x03\x00\x0c\x00\x00\x00\x01\x14\x00\x00'      #指令 1401H  子指令0000H
}

plc_error_message = {
    "C050" : "通訊數據代碼設置為“ASCII”時,接收了無法轉換為二進制碼的ASCII碼數據。PLC_error = C050(hex)",
    "C051" : "可一次性批量讀寫的最大位軟元件數超出允許範圍。PLC_error = C051(hex)", # OK
    "C052" : "可一次性批量讀寫的最大字軟元件數超出允許範圍。PLC_error = C052(hex)", # OK  當長度小於999
    "C053" : "可一次性隨機讀寫的最大位軟元件數超出允許範圍。PLC_error = C053(hex)",  #(預留)沒使用到隨機指令
    "C054" : "可一次性隨機讀寫的最大字軟元件數超出允許範圍。PLC_error = C054(hex)",  #(預留)沒使用到隨機指令
    "C056" : "超過最大地址的寫入及讀取請求。PLC_error = C056(hex)", #ok
    "C058" : "ASCII-二進制轉換後的請求數據長度與字符區(文本的一部分)的數據數不符。PLC_error = C058(hex)",
    "C059" : "1.命令、子命令的指定有誤。2.是CPU模塊中無法使用的命令、子命令。PLC_error = C059(hex)",
    "C05B" : "CPU模塊無法對指定軟元件進行寫入及讀取。PLC_error = C05B(hex)",
    "C05C" : "請求內容有誤。(以位為單位對字軟元件進行寫入、讀取等)。PLC_error = C05C(hex)",
    "C05F" : "是無法對對象CPU模塊執行的請求。PLC_error = C05F(hex)",
    "C060" : "請求內容有誤。(對位軟元件的數據指定有誤等)。PLC_error = C060(hex)",
    "C061" : "請求數據長度與字符區(文本的一部分)的數據數不符。PLC_error = C061(hex)",
    "C06F" : "通訊數據代碼被設置為“二進制”時,接收了ASCII的請求報文。(本出錯代碼僅登錄出錯履歷，而不返回異常響應)。PLC_error = C06F(hex)",
    "C0D8" : "指定塊數超過範圍。PLC_error = C0D8(hex)",
    "C200" : "遠程口令有誤。PLC_error = C200(hex)",
    "C201" : "通訊所使用的端口處於遠程密碼鎖定狀態。PLC_error = C201(hex)",
    "C204" : "與請求了遠程口令解鎖處理的對方設備不同。PLC_error = C204(hex)",
    "C810" : "遠程密碼有誤。(認證失敗次數為9次以下)。PLC_error = C810(hex)",
    "C815" : "遠程密碼有誤。(認證失敗次數為10次)。PLC_error = C815(hex)",
    "C816" : "遠程密碼認證閉鎖中。PLC_error = C816(hex)"
}

def open_socket(HOST, PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.settimeout(6)  #設定逾時
    return s

def check_user_data_format (headdevice,device_type,length) :
    try :
        headdevice = headdevice.upper()
        if io_table.get(headdevice[0]) and 0 < length <= length_limit[device_type]:  # 判斷headdevice格式是否正確 跟 長度是否有超過上限
            dec_or_hex = io_table.get(headdevice[0]) # [ 幾進制 , 該元件最大地址 ]
            if 0 <= int(headdevice[1:],dec_or_hex[0]) <= dec_or_hex[1]: # 判斷 headdevice 最小~最大地址 
                return  "OK"
            else : 
                return (f" The Value exceeds the upper limit or lower limit , headdevice = '{headdevice}' , lenght = {length}")
        else : 
            return  (f"format error , headdevice = '{headdevice}' , lenght = {length}")
    except (TypeError , ValueError, AttributeError) as e :         
        return  (f"{e.__class__.__name__} - {e},headdevice = {headdevice} , lenght = {length}")
     
def handle_plc_error_message (total_data) :
        int_plc_error_code =  (int.from_bytes (total_data [9:11] , byteorder= "little"))   #將第9~11的byte 轉為 int (異常代碼在第9~11之間位置)
        str_hex_plc_error_code = format(int_plc_error_code ,"X")                           #將int轉為16進制的str 
        return (f'PLC error message = {plc_error_message[str_hex_plc_error_code]}')        

def recv_PLC_data_wirte (s):
    total_data = b''
 
    while len(total_data)  < 11 :
        indata = s.recv(4096)
        total_data += indata    
        
    #表示送給PLC的文報是有錯誤的!(備註:當文報異常時,PLC將返還20個字節) [9:11]是異常代碼
    if len(total_data) == 20 and  total_data[9:11] != b'\x00\x00' :     
        return   handle_plc_error_message (total_data)
    
    return "OK"

def recv_PLC_data_read (s,def_name,data_size,length=None,signed_type=None):
    total_data = b''
    
    while len(total_data) < data_size:
        indata = s.recv(4096)
        total_data += indata
    
        if  len(total_data) == 20 and  total_data[9:11] != b'\x00\x00'  :     
            result = handle_plc_error_message(total_data)
            break
    match def_name :
        case 'read_sign_word' :
            if len(total_data) == data_size :        
                result = word_result_analysis(total_data,signed_type)
        case 'read_sign_Dword' :
            if len(total_data) == data_size :
                result = dword_result_analysis(total_data,signed_type)
        case 'read_bit' :
            if len(total_data) == data_size :
                result = bit_result_analysis(total_data,length)

    return result

def word_result_analysis(word_answer ,word_signed):     #單個word 拆解的function , 適用於 (PLC "D" "W" "R" ) 
    result =[]
    #舉例讀取D0,長度3,實際可讀取D0~2  D0=0 D1=1 D2=2           ▼為收到data數值開始 (在第11位)
    # indata = b'\xd0\x00\x00\xff\xff\x03\x00\x08\x00\x00\x00\x00\x00\x01\x00\x02\x00'
                                                            # (  D0  )(  D1  )(  D2  ) 
    length = int(len(word_answer[11:]) / 2)  #計算資料長度 
                     
    for i in range(length):  #如果"有"正負符號 (-32767~32767)  如果有"無"負符號  (0~65535)   
    
        i = i * 2
        byte_sequence = word_answer[11 + i:11 + i + 2]
        result.append(int.from_bytes(byte_sequence, byteorder='little', signed=word_signed)) 



    
    return result 

def dword_result_analysis(dword_answer ,dword_signed):  #雙個word 拆解的function , 適用於 (PLC "D" "W" "R" ) 
    result =[]
    #舉例讀取D0,長度1,實際可讀取D0~1  D0=0 D1=1                ▼為收到data數值開始 (在第11位)
    # indata = b'\xd0\x00\x00\xff\xff\x03\x00\x08\x00\x00\x00\x00\x00\x01\x00\'
                                                            # (  D0  ~   D1  ) 
    length = int(len(dword_answer[11:]) / 4)  #計算資料長度 
                     
    for i in range(length):  #如果"有"正負符號 (-2147483648~2,147,483,647)  如果有"無"負符號  (0~4294967295)   
    
        i = i * 4
        byte_sequence = dword_answer[11 + i:11 + i + 4]
        result.append(int.from_bytes(byte_sequence, byteorder='little', signed=dword_signed)) 

    return result  

def bit_result_analysis(binary_answer,length):     #單個bit 拆解的function , 適用於 (PLC "M" "L" "F" "b" ) 
    result =[]
    #舉例讀取M0,長度2,實際最大可讀取至M15(總共16bit長度)       ▼為收到data數值開始 (在第11位)
    #indata = b'\xd0\x00\x00\xff\xff\x03\x00\x04\x00\x00\x00\x11\x11\x11\x11' #(s,headdevice = 'm0' , lenght =1))
                                                           #(m0~1)(m2~3)(m4~5)(m6~7)
    #步驟1: 取byte後11data,(例:indata = b'\xff\xff\xff\xff)
    data_str = str(binary_answer[11:])
    #步驟2: 再只取 ("1","0")這些符號
    delete_str = ['1','0'] 
    bin_answer_int =  [ int(i) for i in data_str if i  in delete_str]
    result = bin_answer_int[:length]
   
    
    return result

# def bit_result_analysis(binary_answer):    #單個bit 拆解的function , 適用於 (PLC "M" "L" "F" "b" ) 子指令(\x00\x00) 最大長度7680 (由於是一次16個 所以只能輸入480數值)
    # result =[]                             #!!注意:使用此function記得改成 device_type = "word"  (因為子指令不一樣)
    #舉例讀取M0,長度2,實際最大可讀取至M15(總共16bit長度)       ▼為收到data數值開始 (在第11位)
    #indata = b'\xd0\x00\x00\xff\xff\x03\x00\x04\x00\x00\x00\xff\xff\xff\xff' #(s,headdevice = 'm0' , lenght =1))
                                                            #(m0~15) (m16~31)
    #步驟1: 取byte後11data,(例:indata = b'\xff\xff\xff\xff)
    # data = binary_answer[11:]
    #步驟2: 將11以後data轉為二進制字串,  (例:indata = b'\xff\xff\xff\xff) 
            # {08b}   "0" 表示用零填充。如果格式化的字符串长度不足8位用零填充。  
            #         "8" 表示字符串的总长度，最终结果都会是 8 位。
            #          二進制再透過reversed 反轉 ,不然高低位元會相反
    # bin_answer_str = ''.join(''.join(reversed(f'{byte:08b}')) for byte in data)

    #步驟3: 將二進制字串 轉為 int存入list, 
    # dec_answer_list = [int(i) for i in bin_answer_str]
    # result = dec_answer_list
    
    # return result

def send_full_data_byte (headdevice,length,device_type,data_list=b'') :    #將發送的文報組合  (備註:data_list 有使用到write function,才會觸發)
    
    # 將字串轉為大寫
    headdevice_str = headdevice[0].upper()
    # 拆解 headdevice,拆分為(元件代碼)、(起始元件編號) , 為10進制
    if any(element_list[0].get(headdevice_str,'')) :
        
        # (element_code_byte)元件代碼 
        element_code_byte = element_list[0].get(headdevice_str)
    
        # (start_number_byte)起始元件編號
        start_number_int = int(headdevice[1:6], 10)  #表示只讀取到30000,萬的位數  #10表示10進制
        start_number_byte = start_number_int.to_bytes(3, byteorder="little")

        
    # 拆解 headdevice,拆分為(元件代碼)、(起始元件編號) , 為16進制
    if any(element_list[1].get(headdevice_str,'')) :
        
        # (element_code_byte)元件代碼 
        element_code_byte = element_list[1].get(headdevice_str)
        
        # (start_number_byte)起始元件編號
        start_number_int = int(headdevice[1:6], 16)   #表示只讀取到30000,萬的位數  #16表示16進制
        start_number_byte = start_number_int.to_bytes(3, byteorder="little")
    
    
    # 拆解 headdevice,拆分為(元件代碼)、(起始元件編號) , 為8進制
    if any(element_list[2].get(headdevice_str,'')) :
        
        # (element_code_byte)元件代碼 
        element_code_byte = element_list[2].get(headdevice_str)
        
        # (start_number_byte)起始元件編號
        start_number_int = int(headdevice[1:6], 8)   #表示只讀取到30000,萬的位數  #8表示8進制
        start_number_byte = start_number_int.to_bytes(3, byteorder="little")

        
    #(longth_byte) 將元件長度,轉為byte
    longth_byte = length.to_bytes(2, byteorder='little')  
    
    if data_list == b"" :
        send_full_data_byte = main_data_byte[device_type] + start_number_byte + element_code_byte + longth_byte + data_list
    else :
        send_full_data_byte = main_data_byte[device_type] + start_number_byte + element_code_byte + longth_byte + data_list

        
        send_full_data_list = list(send_full_data_byte)
        request_length = len(send_full_data_byte[9:])
        int_request_length_list = [i for i in request_length.to_bytes(2,byteorder ="little")] 
        send_full_data_list[7:9] = int_request_length_list
        send_full_data_byte = bytes(send_full_data_list)

    return send_full_data_byte

def read_sign_word(s,headdevice , length ,signed_type): 
    device_type = "read_word"
    def_name =  read_sign_word.__name__
    try:
        check_list = check_user_data_format(headdevice,def_name,length)
        if  check_list == "OK" :
            data_size = (length - 1) *2 + 13   #用來計算固定資料長度 當(length=1,字節13)、(length=2,字節15)、(length=960,字節1931)
            outdata = send_full_data_byte(headdevice,length,device_type)
            
            s.send(outdata)
            result = recv_PLC_data_read(s,def_name,data_size,None,signed_type)
 
        else :
            return  check_list
            
    except (Exception, socket.error) as e:
        return f"{e.__class__.__name__} - {e}"

    return result

def read_sign_Dword(s,headdevice , length ,signed_type):  #由於Dword 所以lenght*2 固最大上限為480
    device_type = "read_word"
    def_name =  read_sign_Dword.__name__
    try:
        check_list = check_user_data_format(headdevice,def_name,length)
        if  check_list == "OK" :
            data_size = (length - 1) *4 + 15   #用來計算固定資料長度 當(length=1,字節15)、(length=2,字節19)、(length=480,字節1931)
            outdata = send_full_data_byte(headdevice,length*2,device_type) #會要*2 ,因為是dword的關係
            
            s.send(outdata)
            result = recv_PLC_data_read(s,def_name,data_size,None,signed_type)
 
        else :
            return  check_list
    except (Exception, socket.error) as e:
        return f"{e.__class__.__name__} - {e}"

    return result

def read_bit(s,headdevice , length):
    device_type = "read_bit"
    def_name =  read_bit.__name__
    try:
        check_list = check_user_data_format(headdevice,def_name,length)
        if  check_list == "OK" :    
            data_size = (length - 1 ) //2 + 12     #用來計算固定資料長度 當(length=1,字節12)、(length=2,字節12)、(length=3,字節13)、(length=4,字節13)、(length=3584,字節1803)                                
            outdata = send_full_data_byte(headdevice,length,device_type)
           
            s.send(outdata)
            result = recv_PLC_data_read(s,def_name,data_size,length,None)
 
        else :
            return  check_list
    except (Exception, socket.error) as e:
        return f"{e.__class__.__name__} - {e}"
    return result

def write_bit(s,headdevice,data_list ) :
    device_type = "write_bit"
    def_name =  write_bit.__name__
    
    try:
        check_list = check_user_data_format(headdevice,def_name,len(data_list))
        if  check_list == "OK" : 
            length = len(data_list)
            quotient,remainder = divmod (len(data_list),2)
            byte_length   = quotient + remainder  
            
            if remainder == 0 :                                     #計算"餘"是否為0,因為 若餘數等於0將藉由下面.to_bytes可正常轉為byte
                str_data = "0x" + "".join(map(str,data_list))       #利用前綴0x 加上將list轉為轉字串 ,相加後等於16進的數值
            else :                                                  #如果"餘"不等於0,to_bytes直接轉會導致"值"不對所以補上0的字串
                str_data = "0x" + "".join(map(str,data_list)) + "0" #因為最後會由"長度的文報"來決定最後data大小,所以加上"0"不影響最後結果,0會被忽略不計

            hex_data = int(str_data,16)
            byte_data = hex_data.to_bytes(byte_length, byteorder ="big")
            outdata = send_full_data_byte(headdevice,length,device_type,byte_data)

            s.send(outdata)
            result = recv_PLC_data_wirte(s)
 
        else :
            return check_list
    except (Exception,socket.error) as e:
        return f"{e.__class__.__name__} - {e} "

    return result

def write_sign_word(s,headdevice,data_list ,signed_type ) :
    device_type = "write_word"
    def_name =  write_sign_word.__name__
    
    try:
        check_list = check_user_data_format(headdevice,def_name,len(data_list))
        if  check_list == "OK" :  
            length = len(data_list)
            byte_data = b"".join(i.to_bytes(2, byteorder ="little" ,signed=signed_type ) for i in data_list)
            outdata = send_full_data_byte(headdevice,length,device_type,byte_data)
            
            s.send(outdata)
            result = recv_PLC_data_wirte(s)
 
        else :
            return check_list
    except (Exception,socket.error) as e:
        return f"{e.__class__.__name__} - {e} "

    return result

def write_sign_Dword(s,headdevice,data_list ,signed_type ) :
    device_type = "write_word"
    def_name =  write_sign_Dword.__name__ 
    try:
        check_list = check_user_data_format(headdevice,def_name,len(data_list))
        if  check_list == "OK" :  
            length = len(data_list) *2
            byte_data = b"".join(i.to_bytes(4, byteorder ="little" ,signed=signed_type ) for i in data_list)
            outdata = send_full_data_byte(headdevice,length,device_type,byte_data)
            
            s.send(outdata)
            result = recv_PLC_data_wirte(s)
 
        else :
            return check_list
    except (Exception,socket.error) as e:
        return f"{e.__class__.__name__} - {e} "

    return result