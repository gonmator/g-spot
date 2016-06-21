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
    def get_tag(attr_name):
        attr_value = request.args.get(attr_name)
        if attr_value:
            return int(attr_value)
        return None

    def get_tag_list(attr_name):
        attr_values = request.args.get(attr_name)
        if attr_values:
            return set(map(lambda s: int(s), attr_values.split(',')))
        return set()

    def update_tag_list(fw_tags, bw_tags, en_fw_tag, dis_fw_tag):
        if en_fw_tag is not None:
            if en_fw_tag not in fw_tags:
                fw_tags.add(en_fw_tag)
            if en_fw_tag in bw_tags:
                bw_tags.remove(en_fw_tag)
        if dis_fw_tag is not None:
            if dis_fw_tag in fw_tags:
                fw_tags.remove(dis_fw_tag)
        assert dis_fw_tag not in bw_tags

    mode = request.args.get('mode', 'big')
    ppp = int(request.args.get('ppp', 16))
    page = int(request.args.get('page', 1))

    inc_tags = get_tag_list('inc_tags')
    exc_tags = get_tag_list('exc_tags')
    en_inc_tag = get_tag('en_inc_tag')
    dis_inc_tag = get_tag('dis_inc_tag')
    en_exc_tag = get_tag('en_exc_tag')
    dis_exc_tag = get_tag('dis_exc_tag')

    update_tag_list(inc_tags, exc_tags, en_inc_tag, dis_inc_tag)
    update_tag_list(exc_tags, inc_tags, en_exc_tag, dis_exc_tag)

    print en_exc_tag, dis_exc_tag, en_exc_tag, dis_exc_tag
    if en_inc_tag is not None or dis_inc_tag is not None or en_exc_tag is not None or dis_exc_tag is not None:
        return redirect(url_for('show', inc_tags=','.join(inc_tags), exc_tags=','.join(exc_tags)))

    all_tags_tree = get_tags_tree()

    tags_to_include = {}
    for tag in inc_tags:
        tags_to_include[tag] = get_sub_tags(all_tags_tree, tag)
    tags_to_exclude = {}
    for tag in exc_tags:
        tags_to_exclude[tag] = get_sub_tags(all_tags_tree, tag)

    photos = Photos.query
    for tag in inc_tags:
        photos = photos.filter(Photos.tags.any(Tags.name.in_([tag] + tags_to_include[tag])))
    photos = photos.order_by(Photos.time)
    for tag in exc_tags:
        photos = photos.filter(~Photos.tags.any(Tags.name == tag))
    print photos

    photos_page = photos.paginate(page, ppp)
    items = items_to_show(photos_page)

    return render_template('show_big.html', title='G-Spot', photos_page=photos_page, items=items,
                           all_tags_tree=all_tags_tree, inc_tags=list(inc_tags), exc_tags=list(exc_tags))


def find_tree(tags_tree, tag, ix=0):
    for tag_info in tags_tree:
        if tag_info['id'] == tag:
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
            sub_tags.append(sub_tag_info['id'])
            sub_sub_tags = get_sub_tags(sub_tag_info['children'], sub_tag_info['id'])
            sub_tags += sub_sub_tags
    return sub_tags


def items_to_show(photos_page):
    def qn(s):
        return unquote(s.encode('utf-8'))

    def norm_uri(s):
        u = urlsplit(s)
        result = SplitResult(qn(u.scheme), qn(u.netloc), qn(u.path), qn(u.query), '')
        return result

    prefix = norm_uri(app.config['FSPOT_PHOTOS_LOCATION_PREFIX'])
    to_show = []
    for item in photos_page.items:
        photo = {}
        base_uri = norm_uri(item.base_uri)
        path = base_uri.path
        if prefix.scheme == base_uri.scheme and prefix.netloc == base_uri.netloc and path.find(prefix.path) == 0:
            s = join(path[len(prefix.path):], item.filename)
            if s[0] == '/':
                photo['path'] = 'static' + join(path[len(prefix.path):], item.filename)
            else:
                photo['path'] = 'static/' + join(path[len(prefix.path):], item.filename)
            photo['tags'] = []
            for tag in item.tags:
                photo['tags'].append(tag.name)
            to_show.append(photo)
        else:
            print base_uri
    return to_show


def get_tags_tree(index=0):
    tags = [{'id': tag.id, 'name': tag.name, 'category_id': tag.category_id}
            for tag in Tags.query.filter_by(category_id=index).all()]
    for tag in tags:
        tag['children'] = get_tags_tree(tag['id'])
    return tags

