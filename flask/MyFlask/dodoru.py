# coding:utf-8

from flask import Flask
from flask import request
from flask import render_template

import flask

import os

import user
import problem

# user_db_file = 'user.db.txt'
# message_db_file = 'message.db.txt'
# problem_db_file = 'problem.db.txt'

# 创建一个存取数据的文本文件
# from user import
# 因为这样可以使你的程序更加易读，也可以避免名称的冲突
app = Flask(__name__)


@app.route('/')
def index():
    name = request.cookies.get('username')
    # return '<a href="/login">LOGIN</a> &nbsp&nbsp&nbsp&nbsp <a href="/sign">SIGN</a>'
    return render_template('index.html', username=name)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        userdata = request.form.to_dict()
        # 载入数据库，遍历对比登录信息，当然，这个过程应该写成一个函数放到user.py里，这里就会清爽干净很多
        print 'login - userdata : ', userdata
        # 这里可以调试debug 的时候看看有没有正确把login 里面的用户信息传送进来
        users = user.load()
        for ur in users:
            # if userdata['user_name'] == u['user_name'] and userdata['password'] == u['password1']:
            if userdata['name'] == ur["name"]:
                # user_exist=True
                if userdata['password'] == ur['password']:
                    print "login ok.\(^o^)/"
                    # set cookies
                    response = flask.make_response(flask.redirect(flask.url_for('problems')))
                    response.set_cookie('username', ur['name'])
                    return response
                else:
                    return '<h1> password is not suit for the username. </h1>'
                    # 因为这里返回去查看是否存在用户名没多大用处，所以一般网站都只是显示“用户名和密码不匹配”
                    # 当然，可以设置一个 user_exist 来判定是否存在该用户
    return render_template('login.html')


@app.route('/sign', methods=['POST', 'GET'])
def sign():
    if request.method == 'POST':
        userdata = request.form.to_dict()
        print 'sign - userdata : ', userdata
        # user.save(userdata)
        # 把新注册用户写入数据库（在实际中，会利用js 在页面里过滤不合法的 用户名和密码，然后直接把数据放进去）
        # users = user.load(user_db_file)
        users = user.load()
        for ur in users:
            if userdata['name'] == ur['name']:
                return '<h1> User name already exists </h1>'
            if len(userdata['name']) <= 2:
                return '<h1> User name should be more than 2 bytes.</h2>'
                # 应该弹出 提示框

        if userdata['password1'] == userdata['password']:
            del userdata['password1']
            # 两个密码相同，只需要存一个好了，所以把另一个删掉
            user.save(userdata)
            return '<h1> sign OK </h1>'
        else:
            return '<h1>前后密码不匹配，请重新输入密码</h1>'
            # 应该弹出 提示框
    return render_template('sign.html')


# 名字和 user.py 冲突了
# @app.route('/user/<name>')
# def user(name):
# return render_template('user.html')

@app.route('/settings/<name>', methods=['POST', 'GET'])
def settings(name):
    username = request.cookies.get('username')

    if username == name:
        users_data = user.load()
        url = '/settings/' + str(name)
        if request.method == 'POST':
            user_passwords = request.form.to_dict()
            if user_passwords['password1'] == user_passwords['password2']:
                for ur in users_data:
                    if ur['name'] == name:
                        ur['password'] = user_passwords['password1']
                        user.cover(users_data)
                        return '<h1> 密码更改成功<h2>'

        return render_template('settings.html', action_url=url)
    else:
        return flask.redirect(flask.url_for('/login'))
        # 必须是当前用户才可以修改密码,如果不是就要重新登陆


@app.route('/retrieve_password', methods=['POST', 'GET'])
def retrieve_password():
    if request.method == 'POST':
        user_email = request.form.to_dict()
        print 'user_email: ', user_email
        users = user.load()
        for ur in users:
            if ur['email'] == user_email['email']:
                # 发送用户和密码 送给 该邮箱
                print ur['user_name'], ur['password']
                # return "<h1> 你好, 已经将密码发到 " + user_email['email'] + "</h1>"
                # UnicodeDecodeError: 'gbk' codec can't decode bytes in position 33-34: illegal multibyte sequence
                return "<h1> OK~ ,已经将密码发到你注册的邮箱</h1>"
        return "<h1> 咦？ 这个邮箱还没有注册耶~ ... <br>  come on ，baby  ❤ ~ </h1>"
    return render_template('retrieve_password.html')


@app.route('/problems', methods=['POST', 'GET'])
def problems():
    # redirect to login page if no cookie
    username = request.cookies.get('username')
    if username is None:
        # FIXME, 注意这个url_for的参数是这个文件中出现的函数名比如 def index 这个index
        return flask.redirect(flask.url_for('login'))

    problems_data = problem.load()
    problems_totality = len(problems_data)

    if request.method == 'POST':
        problem_data = request.form.to_dict()
        problem_id = problems_totality + 1
        problem_data['id'] = problem_id

        print "problem_data : ", problem_data

        for pro in problems_data:
            if pro['title'] == problem_data['title']:
                return "<h1> 这个问题题目已经存在，请重新提问。</h1>"
                # 应出现提示框 提醒才对
        if len(problem_data['title']) <= 2:
            return "<h1>the title should more than 2 bytes </h1>"
        else:
            problem_url = "/problems/" + str(problem_id)
            problem_data['url'] = problem_url
            problem.save(problem_data)

    problems_data = problem.load()
    # 重新加载一次，这样才能立刻显示出新添加的题目
    return render_template('problems_list.html', problems=problems_data)


@app.route('/problems/<problem_id>', methods=['POST', 'GET'])
def problem_subpage(problem_id):
    # def create_problem_page(problem_id):
    # FIXME， 这个函数名字取得太烂了，应该叫problem
    # 另外id不对的时候应该abort(404)
    # 树： 然而如果叫problem 就会和 problem.py 命名冲突
    problems_data = problem.load()
    if int(problem_id) > len(problems_data):
        print len(problems_data)
        return '<h1> 没有这道题 <h1>', 404

    problem_data = problems_data[int(problem_id) - 1]
    # 如果不 problem_id -1，每次post 后，显示的是下一题的页面（感觉可以有妙用
    ''' 如果id 并不是自动生成排序，就要这样子判断存取了
    for pro in problems_data:
        if pro['id'] == problem_id:
            problem_data = pro
            # break
    '''
    if request.method == 'POST':
        solution_data = request.form.to_dict()
        solution_data["problem_id"] = problem_id
        problem.save_solution_db_file(problem_id, solution_data)
    solutions_data = problem.load_solution_db_file(problem_id)
    return render_template('problem_id.html', id=problem_id, problem=problem_data, solutions=solutions_data)
    # FIXME, model 的内容不应该放到C 里面来搞
    # 这里根本没必要知道这个数据库存在哪里


'''
    solutions_data = None
    problem_id_solution_file = 'problem_' + str(pro_id) + '_solution.db.txt'
    # 存取这个问题答案的数据文件名
    if request.method == 'POST':
        problem_solution = request.form.to_dict()
        problem_solution["problem_id"] = pro_id    # 自动生成 problem_id 条目 放在 字典里
        problem.save(problem_solution,problem_id_solution_file) #后来改了，不能用了
    '''
# return render_template('problem_id.html', id=problem_id, problem=problem_data, solutions=solutions_data)

'''
@app.errolhandler(404)
def page_not_found():
    return "<h1>page not found</h1>",404
'''

if __name__ == '__main__':
    app.debug = True
    app.run()
