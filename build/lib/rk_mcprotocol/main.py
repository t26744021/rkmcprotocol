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
 
main_data_byte = {
    "read_word" :b'\x50\x00\x00\xff\xff\x03\x00\x0c\x00\x00\x00\x01\x04\x00\x00',   #指令 0401H  子指令0000H
    "read_bit"  :b'\x50\x00\x00\xff\xff\x03\x00\x0c\x00\x00\x00\x01\x04\x01\x00',   #指令 0401H  子指令0001H
    "write_bit" :b'P\x00\x00\xff\xff\x03\x00\x0c\x00\x00\x00\x01\x14\x01\x00' ,     #指令 1401H  子指令0001H
    "write_word" :b'P\x00\x00\xff\xff\x03\x00\x0c\x00\x00\x00\x01\x14\x00\x00'      #指令 1401H  子指令0000H
}

plc_error_message = {
    "C050" : "When the communication data code is set to “ASCII”, ASCII code data which cannot be converted to binary is received. PLC_error = C050(hex)",
    "C051" : "Maximum number of bit devices for which data can be read/written all at once is outside the allowable range. PLC_error = C051(hex)", # OK
    "C052" : "Maximum number of word devices for which data can be read/written all at once is outside the allowable range. PLC_error = C052(hex)", # OK  當長度小於999
    "C053" : "Maximum number of bit devices for which data can be random read/written all at once is outside the allowable range. PLC_error = C053(hex)",  #(預留)沒使用到隨機指令
    "C054" : "Maximum number of word devices for which data can be random read/written all at once is outside the allowable range. PLC_error = C054(hex)",  #(預留)沒使用到隨機指令
    "C056" : "Read or write request exceeds maximum address. PLC_error = C056(hex)", #ok
    "C058" : "Request data length after ASCII-to-binary conversion does not match the number of data in the character section (part of text). PLC_error = C058(hex)",
    "C059" : "1.Error in command or subcommand specification. 2.There is a command or subcommand that cannot be used by the CPU module. PLC_error = C059(hex)",
    "C05B" : "CPU module cannot read or write from/to specified device. PLC_error = C05B(hex)",
    "C05C" : "Error in request contents. (Reading or writing by bit unit for word device, etc.) PLC_error = C05C(hex)",
    "C05F" : "There is a request that cannot be executed for the target CPU module. PLC_error = C05F(hex)",
    "C060" : "Error in request contents. (Error in specification of data for bit device, etc.) PLC_error = C060(hex)",
    "C061" : "Request data length does not match the number of data in the character section (part of text). PLC_error = C061(hex)",
    "C06F" : "When the communication data code is set to Binary, a request message of ASCII is received. (Error history of this error code is registered but no error response is sent.) PLC_error = C06F(hex)",
    "C0D8" : "The number of specified blocks exceeds the range. PLC_error = C0D8(hex)",
    "C200" : "Error in remote password. PLC_error = C200(hex)",
    "C201" : "Locked status of the remote password of the port which is used for communication. PLC_error = C201(hex)",
    "C204" : "Different device requested remote password to be unlocked. PLC_error = C204(hex)",
    "C810" : "Error in remote password. (Authentication failure count is 9 or less.) PLC_error = C810(hex)",
    "C815" : "Error in remote password. (Authentication failure count is 10.) PLC_error = C815(hex)",
    "C816" : "Remote password authentication is locked out. PLC_error = C816(hex)"
}

def open_socket(HOST, PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.settimeout(6)  
    return s

def check_user_data_format (headdevice,device_type,length) :
    try :
        headdevice = headdevice.upper()
        if io_table.get(headdevice[0]) and 0 < length <= length_limit[device_type]: 
            dec_or_hex = io_table.get(headdevice[0]) 
            if 0 <= int(headdevice[1:],dec_or_hex[0]) <= dec_or_hex[1]: 
                return  "OK"
            else : 
                return (f" The Value exceeds the upper limit or lower limit , headdevice = '{headdevice}' , lenght = {length}")
        else : 
            return  (f"format error , headdevice = '{headdevice}' , lenght = {length}")
    except (TypeError , ValueError, AttributeError) as e :         
        return  (f"{e.__class__.__name__} - {e},headdevice = {headdevice} , lenght = {length}")
     
def handle_plc_error_message (total_data) :
        int_plc_error_code =  (int.from_bytes (total_data [9:11] , byteorder= "little"))   
        str_hex_plc_error_code = format(int_plc_error_code ,"X")                           
        return (f'PLC error message = {plc_error_message[str_hex_plc_error_code]}')        

def recv_PLC_data_wirte (s):
    total_data = b''
 
    while len(total_data)  < 11 :
        indata = s.recv(4096)
        total_data += indata    
        
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

def word_result_analysis(word_answer ,word_signed):    
    result =[]     
    length = int(len(word_answer[11:]) / 2)  
                     
    for i in range(length):  
    
        i = i * 2
        byte_sequence = word_answer[11 + i:11 + i + 2]
        result.append(int.from_bytes(byte_sequence, byteorder='little', signed=word_signed)) 

    return result 

def dword_result_analysis(dword_answer ,dword_signed):  
    result =[]
    length = int(len(dword_answer[11:]) / 4)  
                     
    for i in range(length):  
    
        i = i * 4
        byte_sequence = dword_answer[11 + i:11 + i + 4]
        result.append(int.from_bytes(byte_sequence, byteorder='little', signed=dword_signed)) 

    return result  

def bit_result_analysis(binary_answer,length):   
    result =[]

    data_str = str(binary_answer[11:])

    delete_str = ['1','0'] 
    bin_answer_int =  [ int(i) for i in data_str if i  in delete_str]
    result = bin_answer_int[:length]
   
    
    return result

def send_full_data_byte (headdevice,length,device_type,data_list=b'') :    
    

    headdevice_str = headdevice[0].upper()

    if any(element_list[0].get(headdevice_str,'')) :
        

        element_code_byte = element_list[0].get(headdevice_str)
    

        start_number_int = int(headdevice[1:6], 10)  
        start_number_byte = start_number_int.to_bytes(3, byteorder="little")

        

    if any(element_list[1].get(headdevice_str,'')) :
        

        element_code_byte = element_list[1].get(headdevice_str)
        
    
        start_number_int = int(headdevice[1:6], 16)  
        start_number_byte = start_number_int.to_bytes(3, byteorder="little")
    
    
   
    if any(element_list[2].get(headdevice_str,'')) :
        
  
        element_code_byte = element_list[2].get(headdevice_str)
        
 
        start_number_int = int(headdevice[1:6], 8)  
        start_number_byte = start_number_int.to_bytes(3, byteorder="little")

        

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
            data_size = (length - 1) *2 + 13   
            outdata = send_full_data_byte(headdevice,length,device_type)
            
            s.send(outdata)
            result = recv_PLC_data_read(s,def_name,data_size,None,signed_type)
 
        else :
            return  check_list
            
    except (Exception, socket.error) as e:
        return f"{e.__class__.__name__} - {e}"

    return result

def read_sign_Dword(s,headdevice , length ,signed_type):  
    device_type = "read_word"
    def_name =  read_sign_Dword.__name__
    try:
        check_list = check_user_data_format(headdevice,def_name,length)
        if  check_list == "OK" :
            data_size = (length - 1) *4 + 15   
            outdata = send_full_data_byte(headdevice,length*2,device_type) 
            
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
            data_size = (length - 1 ) //2 + 12                                    
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
            
            if remainder == 0 :                                     
                str_data = "0x" + "".join(map(str,data_list))       
            else :                                                  
                str_data = "0x" + "".join(map(str,data_list)) + "0" 

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