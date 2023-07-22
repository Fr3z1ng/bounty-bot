# ENDO Bounty Telegram Bot

## Installation
First, need to install python 3.6 or higher:
```
sudo apt-get install python3.6
```

Make virtual envirovent for project and enter to it:
```
python3.6 -m venv venv
source venv/bin/activate
```

Install requirements:
```
pip install -r requirements.txt
```

Rename `.env.example` file to `.env` and edit with variables:
```
mv .env.example .env && nano .env
```

Install migrations:
```
flask db upgrade
```

Now, you can start your Telegram Bot via command:
```
sh ./boot.sh
```
