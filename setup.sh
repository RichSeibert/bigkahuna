if [ ! -d "logs" ]; then
    mkdir logs
fi

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
