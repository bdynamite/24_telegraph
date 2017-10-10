import os
from uuid import uuid4

from flask import Flask, render_template, request, redirect, url_for, abort, make_response

NOT_FOUND_ERROR = 404

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        user_id = get_user_id(request.cookies)
        post_name = get_post_name(request.form, str(user_id))
        resp = make_response(redirect(url_for('post', signature=request.form['signature'],
                                              post_name=post_name, user_id=user_id)))
        resp.set_cookie('user_id', str(user_id))
        return resp
    return render_template('form.html', body='Ваша история', button='Опубликовать')


@app.route('/<user_id>/<signature>/<post_name>', methods=['GET', 'POST'])
def post(user_id, signature, post_name):
    if request.method == 'POST':
        post_name = get_post_name(request.form, str(user_id))
        return redirect(url_for('post', signature=request.form['signature'],
                                post_name=post_name, user_id=user_id))
    body = get_post_body(signature, post_name, user_id)
    if body:
        if request.cookies.get('user_id') == user_id:
            return render_template('form.html', signature=signature, header=post_name, body=body, button='Изменить')
        return render_template('form.html', signature=signature, header=post_name, body=body, disabled='readonly')
    return abort(NOT_FOUND_ERROR)


def get_post_name(data_dict, user_id):
    header, signature, body = [data_dict[x] for x in 'header signature body'.split()]
    post_dir = os.path.join(os.getcwd(), 'posts', user_id, signature)
    check_dir(post_dir)
    post_name = header
    if os.path.exists('{}.txt'.format(os.path.join(post_dir, post_name))):
        post_name += str(len(os.listdir(post_dir)) + 1)
    save_post(post_dir, post_name, body)
    return post_name


def save_post(post_dir, post_name, body):
    post_path = os.path.join(post_dir, post_name)
    with open('{}.txt'.format(post_path), 'w', encoding='utf-8') as post:
        post.write(body)


def check_dir(post_dir):
    if not os.path.exists(post_dir):
        os.makedirs(post_dir)


def get_post_body(signature, header, user_id):
    post_path = os.path.join(os.getcwd(), 'posts', user_id, signature, '{}.txt'.format(header))
    if os.path.exists(post_path):
        with open(post_path, 'r', encoding='utf-8') as post:
            return post.read()
    return None


def get_user_id(cookies):
    user_id = cookies.get('user_id')
    if user_id:
        return user_id
    return uuid4()


if __name__ == "__main__":
    app.run()
