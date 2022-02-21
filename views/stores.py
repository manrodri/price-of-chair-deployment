import json
from flask import Blueprint, render_template, request, redirect, url_for
from models.store_dynamo import Store
from models.user_dynamo.decorators import requires_admin

store_blueprint = Blueprint('stores', __name__)


@store_blueprint.route('/')
def index():
    stores = Store.all()
    return render_template('stores/store_index.html', stores=stores)


@store_blueprint.route('/new', methods=['GET', 'POST'])
@requires_admin
def create_store():
    if request.method == 'POST':
        name = request.form['name']
        url_prefix = request.form['url_prefix']
        tag_name = request.form['tag_name']
        query = json.loads(request.form['query'])

        store =Store(name, url_prefix, tag_name, query)
        Store.save_to_dynamo(store.json())

    # What happens if it's a GET request
    return render_template("stores/new_store.html")



@store_blueprint.route('/edit/<string:store_id>', methods=['GET', 'POST'])
@requires_admin
def edit_store(store_id):
    if request.method == 'POST':
        name = request.form['name']
        url_prefix = request.form['url_prefix']
        tag_name = request.form['tag_name']
        query = json.loads(request.form['query'])

        store = Store.find_by_url(store_id)

        store.name = name
        store.url_prefix = url_prefix
        store.tag_name = tag_name
        store.query = query

        Store.save_to_dynamo(store.json())

        return redirect(url_for('.index'))

    # What happens if it's a GET request
    return render_template("stores/edit_store.html", store=Store.find_by_url(store_id))


@store_blueprint.route('/delete/<string:store_id>')
@requires_admin
def delete_store(store_id):
    # todo error handling
    store = Store.find_by_url(store_id)
    Store.remove_from_dynamo({
        "url_prefix": store.url_prefix
    })
    return redirect(url_for('.index'))

