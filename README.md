
- **項目名稱**：
    
    Python 使用 Socket 連接 FX5U CPU，實現"讀取"和"寫入"功能

- **支援 PLC**：
    
    FX5U (CPU Ethernet)

- **使用步驟**：

    - **步驟-1 : 設定PLC環境**

        IP   : 192.168.1.100<br>
        PORT : 1025 ( TCP )

        ![Example Image](images/p1.png)

    - **步驟-2 : 安裝 rkmcprotocol**
        ```python
        python setup.py install
        ```
        Example : C:\Users\Downloads\rkmcprotocol-main>python setup.py install


- **功能**：
 
        **word**: 
         signed 屬性，表示是否需要正/負符號。
            - signed = True :"word" 範圍 -32,768 ~ 32,767
            - signed = False:"word" 範圍 0 ~ 65,535
        
        **Dword**: 
         signed 屬性，表示是否需要正/負符號。
            signed = True :"Dword"  範圍 -2,147,483,648 ~ 2,147,483,647
            signed = False:"Dword"  範圍 0 ~ 4,294,967,295

        **元件清單:**
        各功能請依照指定的“元件清單”的內容執行，否則將會報錯。

        **資料長度:**
        若使用者給予的資料超出範圍，將會報錯。
                                                            FX5U : 出廠默認記憶體範圍
                                                          ( 使用者可自行變更記憶體區塊,所以只介紹默認設定 )
        FUNCTION         元件清單      資料長度             元件清單       資料長度        進制       總點數
        -------------------------------------------| ----------------------------------------------------
        read_sign_word     D0           960        |         X         X0 ~ X1777         8        1024    
                           W0           512        |         Y         Y0 ~ Y1777         8        1024    
                           R0           960        |         M         M0 ~ M7679         10       7680    
                                                   |         B         B0 ~ B0FF          16       256     
        read_sign_Dword    D0           480        |         L         L0 ~ L7679         10       7680    
                           W0           256        |         F         F0 ~ F127          10       128     
                           R0           480        |
                                                   |         D         D0 ~ D7999         10       8000    
        read_bit           X0           1024       |         W         W0 ~ W1FF          16       512     
                           Y0           1024       |         R         R0 ~ R32767        10       32768   
                           M0           3584       |------------------------------------------------------
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
        ---------------------------------------    |
        
    

