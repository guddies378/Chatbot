First Install the Following:
>Python "Python 3.8 or higher"
>Pytorch (https://pytorch.org/get-started/locally/)
>Anaconda (https://www.anaconda.com/download)
>NLTK (https://www.nltk.org)
>CUDA if you have GPU and NVIDIA (https://developer.nvidia.com/cuda-toolkit)

***Anaconda must be in your system environment variables, else it will not work in VSCode***

STEPS: 
> copy the path of "condabin"
> press windows + r
> type edit the system environment variables
> click environment variables 
> in system variables click path
> and put the condabin path
> press ok

***Create a chatbot environment, name it "chatbot-env"***

1. open Anaconda Powershell Prompt

type this
2. conda create --name chatbot-env python=3.x (x is the python version)
3. conda activate chatbot-env
4. conda install Flask torch torchvision nltk
5. python
>>> import nltk
>>> nltk.download('punkt')

6. pip install flask-cors
7. pip install requests
8. pip install Pillow


******************************************************

To Install the chatbot on another computer/server

***"for CPU"***
╰┈➤conda create --name chatbot-env python=3.x (x is the python version)
╰┈➤conda activate <your_environment_name>
╰┈➤pip install flask
╰┈➤python -m flask --version
╰┈➤pip install flask-cors
╰┈➤pip show flask-cors
╰┈➤pip install torch torchvision torchaudio
╰┈➤conda install pytorch torchvision torchaudio cpuonly -c pytorch
╰┈➤python -c "import torch; print(torch.__version__)"
╰┈➤pip install nltk
    >>> import nltk
    >>> nltk.download('punkt')
╰┈➤pip install requests
╰┈➤pip install Pillow

***If GPU is available*** 
╰┈➤conda create --name chatbot-env python=3.x (x is the python version)
╰┈➤conda activate <your_environment_name>
╰┈➤pip install flask
╰┈➤python -m flask --version
╰┈➤pip install flask-cors
╰┈➤pip show flask-cors
╰┈➤pip install torch torchvision torchaudio
╰┈➤conda install pytorch torchvision torchaudio pytorch-cuda=<CUDA_VERSION> -c pytorch -c nvidia
╰┈➤conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
╰┈➤pip install nltk
    >>> import nltk
    >>> nltk.download('punkt')
╰┈➤pip install requests
╰┈➤pip install Pillow

******************************************************

Open this in Anaconda Power shell
╰┈➤cd "Desktop\University Chatbot" (LOCATION)
╰┈➤python app.py
| For the chatbot/server to be active |

***When Updating the "intents.json" file train the Bot on "train.py" file Manually***
***The Bot will not be trained if the Server is Offline***
***admin_dashboard.py and train.py will not run if the app.py is offline***


******************************************************

***To train the Bot***
╰┈➤python train.py

***To run the server***
╰┈➤python app.py

***To run the Admin Dashboard***
╰┈➤python admin_dashboard.py



******************************************************

***Files Description***

app.py: The main Flask application file.
chat.py: Contains the chatbot logic and model loading functions.
train.py: Script to train the chatbot model.
intents.json: Contains the intents and responses for the chatbot.
model.py: Defines the neural network model.
nltk_utils.py: Utility functions for text processing.
admin_dashboard.py: Admin dashboard for managing intents and unanswered questions.
static: Contains static files like CSS and JavaScript.
templates: Contains HTML templates.
models: Contains the trained model file.
unanswered_questions.log: Log file for unanswered questions.
unanswered.json: JSON file for unanswered questions.


***Troubleshooting***

If the chatbot status shows "Offline", ensure that the Flask server is running and accessible at http://127.0.0.1:5000.
Check the browser's developer console for any JavaScript errors.
Check the server logs for any errors when handling requests.

******************************************************

***MongoDB Configuration***

In terminal type: pip install pymongo

Run CMD as Administrator and type:

FISRT: net stop MongoDB 

SECOND: Edit MongoDB Configuration File: Locate the MongoDB configuration file (usually named mongod.cfg or mongod.conf). 
		This file is typically found in the MongoDB installation directory, for example, C:\Program Files\MongoDB\Server\<version>\bin\.

(copy this code)

systemLog:
  destination: file
  path: C:\Program Files\MongoDB\Server\<version>\log\mongod.log
  logAppend: true
storage:
  dbPath: C:\Program Files\MongoDB\Server\<version>\data
net:
  bindIp: 127.0.0.1
  port: 27017
replication:
  replSetName: "rs0"

THIRD: In the CMD Administrator type again "net start MongoDB"

******************************************************

📄 License
© 2026 Mark James F. Manlangit. All Rights Reserved.