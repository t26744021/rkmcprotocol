- **項目名稱**：
    
    Python 連接 FX5U ，實現"讀取"和"寫入"功能

- **支援 PLC**：
    
    FX5U (CPU Ethernet)

- **使用步驟**：

    - **步驟-1 : 設定PLC環境**
        ```python
            IP   : 192.168.1.100
            PORT : 1025 ( TCP )
            Communiaction Data Code : Binary
        ```
        ![Example Image](images/p1.png)

    - **步驟-2 : 安裝 rkmcprotocol**
        ```python
        python setup.py install
        ```
        Example : C:\Users\Downloads\rkmcprotocol-main>python setup.py install


- **功能簡介**：
 

                                                               FX5U : 出廠默認記憶體範圍
                                                       ( 使用者可自行變更記憶體區塊,所以只介紹默認設定 )
        FUNCTION         元件清單      資料長度         元件清單       資料長度        進制       總點數
        -------------------------------------------| --------------------------------------------------
        read_sign_word     D0           960        |      X         X0 ~ X1777        8        1024    
                           W0           512        |      Y         Y0 ~ Y1777        8        1024    
                           R0           960        |      M         M0 ~ M7679        10       7680    
                                                   |      B         B0 ~ B0FF         16       256     
        read_sign_Dword    D0           480        |      L         L0 ~ L7679        10       7680    
                           W0           256        |      F         F0 ~ F127         10       128     
                           R0           480        |
                                                   |      D         D0 ~ D7999        10       8000    
        read_bit           X0           1024       |      W         W0 ~ W1FF         16       512     
                           Y0           1024       |      R         R0 ~ R32767       10       32768   
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
- **指令**：
    ```python  

        # 讀M0 ~ M3583 , 數值 : 0 or 1
        print(mc.read_bit(s,headdevice = 'm0' , length = 3584 ))

        # 讀D0 ~ D959              
        # signed_type=True  數值 : -32,768 ~ 32,767 
        # signed_type=False 數值 :       0 ~ 65,535 
        print(mc.read_sign_word(s,headdevice = 'd0' , length = 960, signed_type=True))

        # 讀(R0,R1) ~ (R958,R959)  
        # signed_type=True  數值 : -2,147,483,648 ~ 2,147,483,647 
        # signed_type=False 數值 :              0 ~ 4,294,967,295       
        print(mc.read_sign_Dword(s,headdevice = 'r0' , length =480 , signed_type=True))
     

        # 寫M0 ~ M3583 , 數值 : 0 or 1
        print(mc.write_bit(s,headdevice = 'm0' , data_list = [1]*3584 )) 

        # 寫D0 ~ D959              
        # signed_type=True  數值 : -32,768 ~ 32,767
        # signed_type=False 數值 :       0 ~ 65,535 
        print(mc.write_sign_word(s,headdevice = 'd0' , data_list = [-999]*960 ,signed_type =True))

        # 寫(R0,R1) ~ (R958,R959)  
        # signed_type=True  數值 : -2,147,483,648 ~ 2,147,483,647 
        # signed_type=False 數值 :              0 ~ 4,294,967,295       
        print(mc.write_sign_Dword(s,headdevice = 'r0' , data_list = [9999999]*480 ,signed_type =True))


    ```
- **範例**：
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

    ˋˋˋ
- **Q&A**：

    - **為何不使用ASCII,而使用Binary**
    
        A : 速度會比較慢<br>
        引用手冊 :2-1<br>
        與利用ASCII代碼的資料進行的通訊相比，利用二進位代碼的資料進行的通訊的通訊資料量僅約為一半，因此能夠縮短通訊時間。<br>

    - **使用Threading會比較快嗎?**

        A : 不會<br>
        引用手冊 : 2-3<br>
        利用SLMP的數據通訊採用半雙工通訊。<br>
        存取CPU模組時，請在相對於前一個指令封包的發送，接收到來自CPU模組側的回應封包後，發送下一個指令封包。<br>
        （在完成回應封包的接收前，不能發送下一個指令封包。）<br>
