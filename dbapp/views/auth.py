from flask import Blueprint, flash, render_template, request, url_for, redirect, abort, session
from flask_login import login_required, login_user, logout_user, current_user
from flask_principal import Principal, identity_loaded, UserNeed, RoleNeed, identity_changed, Identity, current_app, AnonymousIdentity
from werkzeug.security import check_password_hash
from werkzeug.urls import url_parse
from dbapp import app, db, config_watcher
from dbapp.models.tables import USERS, ROLES, FILEACCESS, FILEPREVIEW
from dbapp.form import LoginForm
from collections import namedtuple

auth = Blueprint('auth_bp', __name__, template_folder='templates')

principals = Principal(app)

config = config_watcher.get_config()

ad_config = config["ADServer"]

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))


from ldap3 import Server, Connection, ALL, NTLM
import re

server = Server('ldap://{}'.format(ad_config["address"]), get_info=ALL)

def ADAuth(username, password):
    conn = Connection(server, user='{}\\{}'.format(".".join(ad_config["domains"]), username), password=password, authentication=NTLM)

    if conn.bind():
        conn.search(",".join(["dc="+x for x in ad_config["domains"]]), '(sAMAccountName={})'.format(username), attributes=['memberOf', 'displayName'])
        result = conn.entries[0]
        security_groups = [re.search('CN=(.+?),', x).group(1) for x in result.memberOf if 'CN=' in x]
        full_name = result.displayName
        return {"groups": security_groups, "fullname": str(full_name).replace('displayName: ', '')}
    else:
        return None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('auth-pages/login.html', title="ログイン", form=form)

    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.is_authenticated:
                if 'Admin' in current_user.roles:
                    url = 'admin_bp.index'
                else:
                    url = 'logined_bp.mypage'
                return redirect(url_for(url))

            form_name = request.form.get('name')
            form_passwd = request.form.get('password')
            form_ad = request.form.get('ad_disable')
            user = USERS.query.filter(USERS.name==form_name).one_or_none()

            if form_ad == "False" and ad_config["use"]:
                ADUser = ADAuth(form_name, form_passwd)
            else:
                ADUser = None

            if not user is None or ADUser is not None:
                if user is None:
                    if ad_config['groups']['Admin'] in ADUser['groups']:
                        role = 'Admin'
                    elif ad_config['groups']['Student'] in ADUser['groups']:
                        role = 'Student'
                    else:
                        abort(500)
                    role = ROLES.query.filter(ROLES.name==role).one()

                    user = USERS(
                        name=form_name,
                        display_name=ADUser['fullname'],
                        password="unnecessary"
                    )
                    user.roles.append(role)
                    db.session.add(user)
                    db.session.commit()

                if check_password_hash(user.password, form_passwd) or ADUser:
                    login_user(user, remember=True)
                    identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
                    next_page = request.args.get('next')
                    if not next_page or url_parse(next_page).netloc != '':
                        if user.has_role('Admin'):
                            next_page = url_for('admin_bp.index')
                        else:
                            next_page = url_for('logined_bp.mypage')

                    if 'accessed_files' in session:
                        for file_id in session['accessed_files']:
                            access_history = FILEACCESS(
                                user_id=current_user.id,
                                file_id=file_id
                            )
                            db.session.add(access_history)
                            db.session.commit()

                    if 'previewed_files' in session:
                        for file_id in session['previewed_files']:
                            preview_history = FILEPREVIEW(
                                user_id=current_user.id,
                                file_id=file_id
                            )
                            db.session.add(preview_history)
                            db.session.commit()

                    return redirect(next_page)

    flash('アカウントが存在しないかパスワードが間違っています')
    return render_template('auth-pages/login.html', title="ログイン", form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    identity_changed.send(app, identity=AnonymousIdentity())
    return redirect(url_for('user_bp.index'))