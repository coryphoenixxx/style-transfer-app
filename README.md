# STYLE TRANSFER APP
This is an asynchronous dual application (**web** + **Telegram bot**) for stylization images.

Neural Network made on the basis of [this research article](https://arxiv.org/pdf/1812.02342.pdf).

## Video Presentation
[![Video Presentation](https://i.ibb.co/mJj89Yc/1.jpg)](https://www.youtube.com/watch?v=_1MibTVd-T0 "Video Presentation")

### Requirements:
* Python 3.7+;
* CUDA *(optional)*;
  
Tested on **Windows 8.1/10 + GTX 1080** and **UBUNTU 20.04.3 LTS (CPU only)**

### Local usage:
* Сlone: `git clone https://github.com/coryphoenixxx/style-transfer-app.git <your_project_dir>`;
* Create virtual environment: `python -m venv venv`;
* Activate it: 
  
  `<your_project_dir>\venv\Scripts\activate.bat` *(Windows)*;
  
  or `source venv/bin/activate` *(Linux)*;
* Install requirements: `pip install -r requirements.txt`;
* If your video card supports **CUDA** then: `pip install torch==1.10.0+cu113 torchvision==0.11.1+cu113 torchaudio===0.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html`

    else: `pip install torch torchvision torchaudio`;
* Create telegram bot with [@BotFather](https://t.me/BotFather) -> `/newbot` and set your token in *config.py* for **API_TOKEN** parameter;
* Get your telegram id from [@getmyid_bot](https://t.me/getmyid_bot) and set it in *config.py* for **ADMIN_ID** parameter;
* Run: `python __main__.py`;

If everything OK then **"App started."** and **"Bot started.**" appear in python console and your Telegram client respectively.  

* Open `http://localhost:8080/` in your browser for interaction with the web part or press `/start` in your Telegram client for interaction with the bot part.
* *(Optional)* For weak video card maybe you should reduce the **MAX_IMAGE_SIZE** parameter in *config.py*, but this will affect the quality of the stylization.
* *(Optional)* You can add your images in **content_presets** or **style_presets** folders. But limit it to a 100 images per folder for the correct keyboard display in the bot.

### Train pipeline:
You may to train the network from scratch or continue training. For this you should:
* Download datasets:
  * e.g. for [content](http://images.cocodataset.org/zips/train2017.zip) and put all images to `train_images/content`;
  * e.g. for [style](https://www.kaggle.com/c/painter-by-numbers/data) *(test.zip + train.zip)* and put all images to `train_images/style`;
* Set your personal parameters in *config.py*;
* Run: `python train.py`;
  

### Tech Stack:
* pytorch;
* aiohttp;
* aiogram;
* HTML/CSS/JS;



