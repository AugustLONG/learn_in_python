# coding:utf-8

from flask import Flask
from flask import request
from flask import render_template

from user_data import *
app=Flask(__name__)

@app.route('/')
def index():
    return '<a href="/login">LOGIN</a> &nbsp&nbsp&nbsp&nbsp <a href="/sign">SIGN</a>'


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        userdata=request.form.to_dict()

