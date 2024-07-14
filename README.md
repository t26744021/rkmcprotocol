
- **項目名稱**：
    
    Python 使用 Socket 連接 FX5U CPU，實現讀取和寫入功能。

- **支援 PLC**：
    
    FX5U (CPU Ethernet)

- **使用步驟**：

    - **步驟-1:設定PLC環境**：

        IP   : 192.168.1.100<br>
        PORT : 1025 ( TCP )

        ![Example Image](images/p1.png)

    - **步驟-2:安裝 rkmcprotocol**：
        
        Download並安裝rkmcprotocol模組<br>
        例如:C:\Users\Downloads\rkmcprotocol-main>python setup.py install


- **示例**：
    #read from D100 to D110
    wordunits_values = pymc3e.batchread_wordunits(headdevice="D100", readsize=10)
    提供更多詳細的使用示例和應用場景。
