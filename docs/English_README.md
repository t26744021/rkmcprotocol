- **Project Name**：
    
    Python Connect to FX5U for "Read" and Write Functions

- **Support PLC**：
    
    FX5U (CPU Ethernet)

- **How to use ?**：

    - **Step-1 : Configure PLC**
        ```python
            IP   : 192.168.1.100
            PORT : 1025 ( TCP )
            Communiaction Data Code : Binary
        ```
        ![Example Image](../images/p1.png)

    - **Step-2 : Install rkmcprotocol ( Windows )**
        ```python
        pip install dist/rk_mcprotocol-0.0.2-py3-none-any.whl
        ```
        Example : C:\Users\Downloads\rkmcprotocol-main>pip install dist/rk_mcprotocol-0.0.2-py3-none-any.whl

    - **Step-2 : Install / Uninstall rkmcprotocol ( Raspberr PI OS 64-bit )**
        ```python
        pip install dist/rk_mcprotocol-0.0.2-py3-none-any.whl --break-system-packages
        ```
        ```python
        pip uninstall rk_mcprotocol --break-system-packages
        ```
        Example : rk@raspberrypi:~/rkmcprotocol $ pip install dist/rk_mcprotocol-0.0.2-py3-none-any.whl --break-system-packages<br>

        Example : rk@raspberrypi:~/rkmcprotocol $ pip uninstall rk_mcprotocol --break-system-packages<br>        

- **Function Overview**：
 

                                                               FX5U : Default Memory Range
                                                  ( User can change memory blocks , so only default settings are introduced )
        Function       Device Code     Length         Device Code     Points    CarrySystem  Max.Points
        -------------------------------------------| --------------------------------------------------
        read_sign_word     D0           960        |      X         X0 ~ X1777      OCT       1024    
                           W0           512        |      Y         Y0 ~ Y1777      OCT       1024    
                           R0           960        |      M         M0 ~ M7679      DEC       7680    
                                                   |      B         B0 ~ B0FF       HEX       256     
        read_sign_Dword    D0           480        |      L         L0 ~ L7679      DEC       7680    
                           W0           256        |      F         F0 ~ F127       DEC       128     
                           R0           480        |
                                                   |      D         D0 ~ D7999      DEC       8000    
        read_bit           X0           1024       |      W         W0 ~ W1FF       HEX       512     
                           Y0           1024       |      R         R0 ~ R32767     DEC       32768   
                           M0           3584       |----------------------------------------------------
                           B0           256        |
                           L0           3584       |
                           F0           128        |
                                                   |
        write_sign_word    D0           960        |
                           W0           512        |
                           R0           960        |
                                                   |
        write_sign_Dword   D0           480        |
                           W0           256        | 
                           R0           480        |
                                                   |
        write_bit          X0           1024       |
                           Y0           1024       |
                           M0           3584       |
                           B0           256        |
                           L0           3584       |
                           F0           128        |                
        -------------------------------------------|
- **Commands**：
    ```python  

        # Read M0 ~ M3583 , Value : 0 or 1
        print(mc.read_bit(s,headdevice = 'm0' , length = 3584 ))

        # Read D0 ~ D959              
        # signed_type=True  Value : -32,768 ~ 32,767 
        # signed_type=False Value :       0 ~ 65,535 
        print(mc.read_sign_word(s,headdevice = 'd0' , length = 960, signed_type=True))

        # Read (R0,R1) ~ (R958,R959)  
        # signed_type=True  Value : -2,147,483,648 ~ 2,147,483,647 
        # signed_type=False Value :              0 ~ 4,294,967,295       
        print(mc.read_sign_Dword(s,headdevice = 'r0' , length =480 , signed_type=True))
     

        # Write M0 ~ M3583 , Value : 0 or 1
        print(mc.write_bit(s,headdevice = 'm0' , data_list = [1]*3584 )) 

        # Write D0 ~ D959              
        # signed_type=True  Value : -32,768 ~ 32,767
        # signed_type=False Value :       0 ~ 65,535 
        print(mc.write_sign_word(s,headdevice = 'd0' , data_list = [-999]*960 ,signed_type =True))

        # Write (R0,R1) ~ (R958,R959)  
        # signed_type=True  Value : -2,147,483,648 ~ 2,147,483,647 
        # signed_type=False Value :              0 ~ 4,294,967,295       
        print(mc.write_sign_Dword(s,headdevice = 'r0' , data_list = [9999999]*480 ,signed_type =True))


    ```
- **Example**：
    ```python  
        import rk_mcprotocol as mc
        import time
        
        HOST = '192.168.1.100'
        PORT = 1025
        s = mc.open_socket(HOST,PORT) 
 
        while True :
            st = time.time()
            
            print(mc.read_bit(s,headdevice = 'm0' , length = 3584 ))   
            print(mc.read_sign_word(s,headdevice = 'd0' , length = 960, signed_type=False))
            print(mc.read_sign_Dword(s,headdevice = 'r0' , length =480 , signed_type=True))      
            print(mc.write_bit(s,headdevice = 'm0' , data_list = [1]*3584 )) 
            print(mc.write_sign_word(s,headdevice = 'd0' , data_list = [-999]*960 ,signed_type =True))
            print(mc.write_sign_Dword(s,headdevice = 'r0' , data_list = [9999999]*480 ,signed_type =True))
        
            et = time.time()
            elapsed = et -st
            time.sleep(1)  
            
            print (f' elapsed time = {elapsed}')

    
- **Q&A**：

    - **Why use Binary instead of ASCII for communication ?**
    
        A : ASCII is slower<br>
        Reference : MELSEC iQ-F FX5 User's Manual (SLMP) Page 12 :<br>
        When using binary codes , the communcation time will decrease since the amount of communication dreduced by approximately half comparing to using ASCII codes 。<br>

    - **Does using Threading make it faster ?**

        A : No<br>
        Reference : MELSEC iQ-F FX5 User's Manual (SLMP) Page 13 :<br>
            Data communication using SLMP communication is executed in half-duplex communication。<br>
            To access the Ethernet-equipped module, send the next command message after receiving a response message for the
            preceding command message from the Ethernet-equipped module。<br>
            (Until the receiving of the response message is completed, the next command message cannot be sent.)<br>
 