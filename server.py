import os
from uuid import uuid4
import json

from flask import Flask, render_template, request, redirect, url_for, abort, make_response

NOT_FOUND_ERROR = 404

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        user_id = get_user_id(request.cookies)
        post_name = get_post_name()
        save_post(request.form, user_id, post_name)
        resp = make_response(redirect(url_for('post', post_name=post_name)))
        resp.set_cookie('user_id', str(user_id))
        return resp
    return render_template('form.html', mode='new')


@app.route('/<post_name>', methods=['GET', 'POST'])
def post(post_name):
    if request.method == 'POST':
        save_post(request.form, get_user_id(request.cookies), post_name)
        return redirect(url_for('post',post_name=post_name))
    post_data = get_post(post_name)
    if post_data:
        if request.cookies.get('user_id') == post_data['user_id']:
            return render_template('form.html', mode='edit', **post_data['post'])
        return render_template('form.html', mode='read', **post_data['post'])
    return abort(NOT_FOUND_ERROR)


def get_post_name():
    posts_dir = os.path.join(os.getcwd(), 'posts')
    return str(len(os.listdir(posts_dir)) + 1)


def save_post(data_dict, user_id, post_name):
    header, signature, body = [data_dict[x] for x in 'header signature body'.split()]
    post_data = {
        'user_id': str(user_id),
        'post': {
            'header': header,
            'signature': signature,
            'body': body
        }

    }
    post_path = os.path.join(os.getcwd(), 'posts', '{}.json'.format(post_name))
    with open(post_path, 'w', encoding='utf-8') as json_file:
        json.dump(post_data, json_file)


def get_post(post_name):
    post_path = os.path.join(os.getcwd(), 'posts', '{}.json'.format(post_name))
    if os.path.exists(post_path):
        with open(post_path, 'r', encoding='utf-8') as json_data:
            return json.load(json_data)
    return None


def get_user_id(cookies):
    user_id = cookies.get('user_id')
    if user_id:
        return user_id
    return uuid4()


if __name__ == "__main__":
    app.run()
