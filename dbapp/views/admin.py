from flask import Blueprint, render_template, request, abort, session, jsonify, redirect, url_for
from flask_login import login_required
from flask_principal import Permission, RoleNeed
from dbapp import db
from dbapp.models.tables import NEWS, TAGS
from dbapp.form import PostNewsForm, TagForm
from flask import flash

admin_bp = Blueprint('admin_bp', __name__, template_folder='templates')

admin_permission = Permission(RoleNeed('Admin'))

@admin_bp.route('/')
@login_required
@admin_permission.require(403)
def index():
    return render_template('user-pages/index.html')

@admin_bp.route('/edit_tag/<id>', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def edit_tag(id):
    data = TAGS.query.filter(TAGS.id==id).one_or_none()
    form = TagForm()
    if not data:
        abort(404)
    if request.method == 'GET':
        return render_template('admin-pages/edit_tag.html', title='タグの編集', data=data, form=form, tag_id=data.id)
    if request.method == 'POST':
        try:
            data.tag = form.title.data
            data.tips = form.tips.data

            db.session.flush()
            db.session.commit()
        
        except Exception as e:
            flash(e)
            db.session.rollback()

        return redirect(url_for('admin_bp.edit_tag', id=id))

    return render_template('admin-pages/edit_tag.html', title='タグの編集(エラー)', data=data, form=form, tag_id=data.id)


@admin_bp.route('/result')
@login_required
@admin_permission.require(403)
def upload_result():
    id = request.args.get("id")
    try:
        result = session["results"][id]
    except KeyError:
        abort(400)

    return render_template('admin-pages/result.html', title="結果", result=result)

@admin_bp.route('/postnews/', methods=['GET'])
@login_required
@admin_permission.require(403)
def postnews():
    form = PostNewsForm()
    return render_template('admin-pages/postnews.html', title="お知らせ作成", form=form)

@admin_bp.route('/postnews', methods=['POST'])
@login_required
@admin_permission.require(403)
def postnews_receive():
    add_news = NEWS(
        name = request.form.get('title'),
        content = request.form.get('content'),
        raw_markdown = request.form.get('raw_markdown')
    )

    db.session.add(add_news)
    db.session.commit()

    return redirect(url_for('user_bp.news', id=add_news.id))

