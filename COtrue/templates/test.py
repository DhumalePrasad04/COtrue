from flask import Flask,render_template
import requests
import _json

app=Flask(__name__)

@app.route("/")
def index():
    return "hello world"
if __name__=="__main__":
    app.run()