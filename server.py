import os
from uuid import uuid4

from flask import Flask, render_template, request, redirect, url_for, abort, make_response

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        user_id = get_user_id(request.cookies)
        save_post(request.form, str(user_id))
        resp = make_response(redirect(url_for('post', signature=request.form['signature'],
                                              post_name=request.form['header'], user_id=user_id)))
        resp.set_cookie('user_id', str(user_id))
        return resp
    return render_template('form.html', body='Ваша история', button='Опубликовать')


@app.route('/<user_id>/<signature>/<post_name>', methods=['GET', 'POST'])
def post(user_id, signature, post_name):
    if request.method == 'POST':
        save_post(request.form, user_id, old_post=(signature, post_name))
        return redirect(url_for('post', signature=request.form['signature'],
                                post_name=request.form['header'], user_id=user_id))
    body = get_post_body(signature, post_name, user_id)
    if body:
        if request.cookies.get('user_id') == user_id:
            return render_template('form.html', signature=signature, header=post_name, body=body, button='Изменить')
        return render_template('form.html', signature=signature, header=post_name, body=body, disabled='readonly')
    return abort(404)


def save_post(data_dict, user_id, old_post=None):
    if old_post:
        delete_old_post(old_post, user_id)
    header, signature, body = [data_dict[x] for x in 'header signature body'.split()]
    post_dir = os.path.join(os.getcwd(), 'posts', user_id, signature)
    check_dir(post_dir)
    post_path = os.path.join(post_dir, header)
    with open('{}.txt'.format(post_path), 'w', encoding='utf-8') as post:
        post.write(body)


def check_dir(post_dir):
    if not os.path.exists(post_dir):
        os.makedirs(post_dir)


def delete_old_post(post_data, user_id):
    post_dir, post_name = post_data
    user_dir_path = os.path.join(os.getcwd(), 'posts', user_id)
    post_dir_path = os.path.join(user_dir_path, post_dir)
    post_path = os.path.join(post_dir_path, '{}.txt'.format(post_name))
    os.remove(post_path)
    if not os.listdir(post_dir_path):
        os.rmdir(post_dir_path)
    if not os.listdir(user_dir_path):
        os.rmdir(user_dir_path)


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
