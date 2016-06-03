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
    tags = set(request.args.get('tags', '').split(','))
    if '' in tags:
        tags.remove('')

    aliases = []
    photos = Photos.query
    for tag in tags:
        aliases.append(db.aliased(Tags))
        photos = photos.join(aliases[-1], Photos.tags)
        print aliases[-1]
    print photos
    for i, tag in enumerate(tags):
        photos = photos.filter(aliases[i].name == tag)

    photos_page = photos.paginate(page, ppp)
    items = items_to_show(photos_page)

    return render_template('show_big.html', title='G-Spot', photos_page=photos_page, items=items, tags=list(tags))


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
