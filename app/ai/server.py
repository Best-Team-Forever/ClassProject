from flask import Flask
import subprocess

app = Flask(__name__)


@app.route('/')
def hello_world():
    subprocess.Popen('python3 /python-docker/predict.py an_image', shell=True)
    f = open("/data/images/result.txt", "r")
    result = f.read()
    f.close()
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
