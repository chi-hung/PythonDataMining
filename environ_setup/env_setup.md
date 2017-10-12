# 準備深度學習環境

本筆記的目標為安裝以下軟體
```bash
1. Ubuntu 16.04 LTS
2. NVIDIA Display Driver 384.66
3. NVIDIA CUDA ToolKit 8
4. NVIDIA cuDNN 6
5. Docker-ce
6. NVIDIA-Docker
```
步驟如下：
1. 下載[Ubuntu 16.04 LTS server](http://ftp.ubuntu-tw.org/mirror/ubuntu-releases/16.04.3/ubuntu-16.04.3-server-amd64.iso) (或[Ubuntu 16.04 LTS Desktop](http://releases.ubuntu.com/16.04.3/ubuntu-16.04.3-desktop-amd64.iso?_ga=2.79702615.1542122037.1505967108-763877899.1501350163))，並將其燒錄成光碟(或[製作成USB開機碟](https://unetbootin.github.io/))後，用其開機並開始安裝Ubuntu。
    * #### 注意： Server版本預設沒有桌面環境。若桌面環境是必要的，則可待安裝Server版本後，於[步驟8](#桌面環境)加裝桌面環境即可。
        #### 另外，你亦可選擇直接安裝帶有桌面環境的Desktop版本。此情形適用於Server版本的一些功能對你來說為非必要(諸如：Software RAID的配置)。
    
2. 開機時選擇安裝Ubuntu，並且依照安裝提示，將Ubuntu安裝好。其中鍵盤配置，硬碟分割區配置等，若沒特殊需求，則遵從Ubuntu的安裝建議即可。

3. 安裝好Ubuntu後，重新開機。開機成功後，輸入安裝時所設定的帳號和密碼，即可登入終端機界面。
    * #### 注意： 若你安裝的是桌面版，則可於輸入帳號密碼，登入桌面後，按鍵盤上的```ctrl+alt+t```, 以啟動視窗內的終端機介面。
    於終端機界面，鍵入```sudo -i```並再次輸入密碼，以進入管理員(root)模式。於該模式下，我們才有權限進行接下來的系統環境設定。進入root模式後，輸入
    ```
    wget https://raw.githubusercontent.com/chi-hung/PythonTutorial/master/environ_setup/drvPreInstall.sh
    wget https://raw.githubusercontent.com/chi-hung/PythonTutorial/master/environ_setup/drvInstall.sh
    wget https://raw.githubusercontent.com/chi-hung/PythonTutorial/master/environ_setup/dockerInstall.sh
    ```
    將三個用於安裝系統的批次檔下載下來。
    
    其中，*[drvPreInstall.sh](https://github.com/chi-hung/PythonTutorial/blob/master/environ_setup/drvPreInstall.sh)* 將協助我們關閉Nouveau Display Driver，以便我們將其替換為NVIDIA的Display Driver。
    
    * 註： Nouveau Display Driver是Ubuntu內建的開源顯示驅動，用於驅動NVIDIA的顯示卡。若是開機時kernel有載入此驅動，則我們須重啟kernel並停止該驅動的載入，否則將會無法正常安裝NVIDIA的顯示驅動。
    
    接著，*[drvInstall.sh](https://github.com/chi-hung/PythonTutorial/blob/master/environ_setup/drvInstall.sh)* 將幫助我們安裝[NVIDIA Display Driver](http://www.nvidia.com/Download/index.aspx), [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)以及[cuDNN library](https://developer.nvidia.com/cudnn)。
    
    最後，*[dockerInstall.sh](https://github.com/chi-hung/PythonTutorial/blob/master/environ_setup/dockerInstall.sh)* 除了將安裝[Docker](https://www.docker.com/what-docker)和[NVIDIA-Docker](https://github.com/NVIDIA/nvidia-docker)外，也會去[Dockerhub](http://dockerhub.com/)抓取一些深度學習相關的docker image。
    
4. 準備開始安裝驅動等軟體。首先，我們須把Nouveau Display Driver關閉，並重新啟動kernel。於root模式下，輸入
    ```bash
    bash drvPreInstall.sh
    ```
    即可。註：此步驟將重新啟動電腦。

5. 重新啟動後，關閉lightdm login manager
    * #### 注意： 若您有安裝桌面環境則需要進行以下步驟。若無，請跳至第六步。
    ```bash
    sudo service lightdm stop    # 停止 login manager
    ```
    接著，按```ctrl+alt+F2```切換至terminal 2，輸入
    ```bash
    sudo init 3    # 進入文字模式
    sudo -i        # 得到管理員權限，以便之後利用管理員權限來安裝軟體。
    ```
    以便接下來使用管理員權限來安裝軟體。
5. 安裝NVIDIA Display Driver, NVIDIA CUDA Toolkit以及cuDNN。於root模式下鍵入
    ```bash
    bash drvInstall.sh
    ```
    即可完成安裝。接著，我們要驗證驅動是否有順利安裝。輸入
    ```bash
    nvidia-smi
    ```
    看是否有顯示NVIDIA GPU的當前狀態資訊。您應該於終端機得到類似於下圖的資訊
    ![img_nvsmi](https://i.imgur.com/hjWwGee.png)

    接著，順便看NVCC (NVidia Cuda Compiler driver)有沒有正確安裝。於終端機輸入
    ```bash
    /usr/local/cuda/bin/nvcc -V
    ```
    後，若無發生錯誤，則應該會看到類同於以下資訊
    ```bash
    nvcc: NVIDIA (R) Cuda compiler driver
    Copyright (c) 2005-2016 NVIDIA Corporation
    Built on Tue_Jan_10_13:22:03_CST_2017
    Cuda compilation tools, release 8.0, V8.0.61
    ```
    其顯示我們所安裝的CUDA版本為8.0。
    
    最後，若```nvidia-smi```和```nvcc -V```的輸出皆正常，則表示驅動和CUDA Toolkit應該已有正常安裝。如此，我們可進行下一步。
5. 接著，於root模式下鍵入以下指令，以安裝Docker, NVIDIA-Docker。安裝完畢後，此批次檔亦會下載一些用於深度學習的Docker image諸如Caffe, Digits, CNTK, Tensorflow和Keras。
    ```bash
    bash dockerInstall.sh
    ```
    安裝完畢後，我們要驗證Docker以及NVIDIA-Docker是否運作正常。輸入
    ```bash
    nvidia-docker run --rm nvidia/cuda nvidia-smi
    ```
    後，若有跳出NVIDIA GPU的當前狀態資訊，則表示Docker和NVIDIA-Docker已正常安裝。
    
    * #### 注意：若您有桌面環境，且已成功安裝各軟體，則可輸入```reboot```重新開機，以便回到桌面環境去使用。
<div id='桌面環境'>
    
8. 安裝桌面環境
     * #### 注意：若您是Ubuntu伺服器版本，想要加裝桌面環境，則可以執行此步驟。而若您不需要桌面，或是你已經安裝了Ubuntu桌面版本，則可跳過此步驟。
     
     若前述步驟皆無任何錯誤訊息，則可輸入以下指令安裝桌面環境
    ```bash
    apt-get install -y ubuntu-desktop
    ```
    安裝結束後，輸入
    ```bash
    reboot
    ```
    重新開機，看桌面環境是否有正常顯示。
    
7. 啟動Jupyter Notebook
 
    於終端機內輸入
    ```bash
    sudo nvidia-docker run -it --rm -p 9999:8888 --name keras -v ~/:/notebooks:cached honghu/keras:latest-gpu-py3
    ```
    看能否利用NVIDIA-Docker來啟動一個含有Keras, Tensorflow, Scikit-Learn, OpenCV的深度學習環境。
    
    啟用此Docker container時，container內的Jupyter Notebook會啟動。Jupyter Notebook預設使用container內的port ```8888```來讓使用者透過瀏覽器連線，並預設讓使用者進入container內的```/notebooks```資料夾。
    
    而由於port ```8888```以及資料夾```/notebooks```皆位於container端，其於host端並無法看到，故我們想要將container的port ```8888```導出至host端，並且將container的資料夾```/notebooks```掛載於host端。
    
    以上指令輸入時，我們已經利用```-v```，將docker container內的```/notebooks```資料夾導至host端的```~/```(使用者家目錄)。並且利用```-p```，將container的port ```8888```導出至host端的port ```9999```。故，此container正常啟動後，我們應可以於host端，透過port ```9999```使用Jupyter Notebook。

    指令輸入後，若出現以下畫面
    ![img_runkeras](https://i.imgur.com/saF0bqP.png)
則代表Jupyter Notebook已正常啟動。於上圖內，我們可發現token為```560f6b9dd05f4112d341fcba3032a22e5db2c8ae7335cc20```。其為用於登入container內Jupyter Notebook的密碼。將其複製下來，並於host端開啟瀏覽器，貼上以下網址
    ```bash
    http://localhost:9999/?token=560f6b9dd05f4112d341fcba3032a22e5db2c8ae7335cc20
    ```
    您即可使用container內的Jupyter Notebook。
     * 註1：以上網址中```?token=xxx```的```xxx```須改成您所看到的token，因為安全性的關係，token為亂數產生，故你的token應和我的不同。
     * 註2：若您是Ubuntu伺服器版本，則因為沒有瀏覽器的關係，無法從本地端開啟瀏覽器直接連接至本地端。此時，須利用內網另外一台有瀏覽器的電腦，開啟瀏覽器連接至```http://host_ip:9999/?token=my_token```。其中，```host_ip```為此jupyter notebook server的ip, ```my_token```為該server啟動後給予的token。
    
    最後，若登入Jupyter Notebook順利，則可於該軟體內新增一個Python3筆記本，於其中輸入
    ```bash
    import tensorflow
    import keras
    import cv2
    ```
    來測試我們會用到的套件是否能夠順利匯入，如下圖
    ![img_importPackages](https://i.imgur.com/SojFkGM.png)
    以上，若執行後並無出現錯誤訊息，則此深度學習環境大致設立完畢。