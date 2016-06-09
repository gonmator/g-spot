from flask import redirect, render_template, request, url_for
from os.path import join
from urllib import quote, unquote
from urlparse import urlsplit, SplitResult
from app import app
from .models import Photos, Tags, db


@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('show'))


@app.route('/show')
def show():
    mode = request.args.get('mode', 'big')
    ppp = int(request.args.get('ppp', 16))
    page = int(request.args.get('page', 1))

    inc_tags = set(request.args.get('inc_tags', '').split(','))
    en_inc_tag = request.args.get('en_inc_tag', '')
    dis_inc_tag = request.args.get('dis_inc_tag', '')

    if '' in inc_tags:
        inc_tags.remove('')

    if en_inc_tag:
        if en_inc_tag not in inc_tags:
            inc_tags.add(en_inc_tag)
    if dis_inc_tag:
        if dis_inc_tag in inc_tags:
            inc_tags.remove(dis_inc_tag)
    if en_inc_tag or dis_inc_tag:
        return redirect(url_for('show', inc_tags=','.join(inc_tags)))

    all_tags_tree = get_tags_tree()

    tags_to_include = list(inc_tags)
    for tag in inc_tags:
        tags_to_include += get_sub_tags(all_tags_tree, tag)

    aliases = []
    photos = Photos.query
    for tag in enumerate(tags_to_include):
        aliases.append(db.aliased(Tags))
        photos = photos.join(aliases[-1], Photos.tags)
    for i, tag in enumerate(tags_to_include):
        photos = photos.filter(aliases[i].name == tag)

    photos_page = photos.paginate(page, ppp)
    items = items_to_show(photos_page)

    # all_tags = tags_to_show(Tags.query.all())

    return render_template('show_big.html', title='G-Spot', photos_page=photos_page, items=items,
                           all_tags_tree=all_tags_tree, inc_tags=list(inc_tags))


def find_tree(tags_tree, tag, ix=0):
    for tag_info in tags_tree:
        if tag_info['name'] == tag:
            return tag_info
        else:
            tree = find_tree(tag_info['children'], tag, ix+1)
            if tree:
                return tree
    return {}


def get_sub_tags(tags_tree, tag):
    sub_tags = []
    tag_info = find_tree(tags_tree, tag)
    if tag_info:
        for sub_tag_info in tag_info['children']:
            sub_tags.append(sub_tag_info['name'])
            sub_sub_tags = get_sub_tags(sub_tag_info['children'], sub_tag_info['name'])
            sub_tags += sub_sub_tags
    return sub_tags



def items_to_show(photos_page):
    def qn(s):
        return unquote(s.encode('utf-8'))

    def norm_uri(s):
        u = urlsplit(s)
        return SplitResult(qn(u.scheme), qn(u.netloc), qn(u.path), qn(u.query), '')

    prefix = norm_uri(app.config['FSPOT_PHOTOS_LOCATION_PREFIX'])
    to_show = []
    for item in photos_page.items:
        base_uri = norm_uri(item.base_uri)
        path = base_uri.path
        if prefix.scheme == base_uri.scheme and prefix.netloc == base_uri.netloc and path.find(prefix.path) == 0:
            s = join(path[len(prefix.path):], item.filename)
            if s[0] == '/':
                to_show.append('static' + join(path[len(prefix.path):], item.filename))
            else:
                to_show.append('static/' + join(path[len(prefix.path):], item.filename))
        else:
            print base_uri
    return to_show


def get_tags_tree(index=0):
    tags = [{'id': tag.id, 'name': tag.name, 'category_id': tag.category_id}
            for tag in Tags.query.filter_by(category_id=index).all()]
    for tag in tags:
        tag['children'] = get_tags_tree(tag['id'])
    return tags

