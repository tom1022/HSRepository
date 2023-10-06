import datetime
from dbapp import db
from dbapp.models.tables import STUDIES, FILES, USERS, TAGS, NEWS
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SelectField, TextAreaField, HiddenField, PasswordField, BooleanField, ValidationError, MultipleFileField
from wtforms.validators import InputRequired

class StudyForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    before_title = HiddenField('Before_Title')
    raw_markdown = TextAreaField('Raw Markdown', validators=[InputRequired()])
    field = SelectField('Field', choices=[(1, '1分野'), (2, '2分野'), (3, '3分野')])
    tags = HiddenField('Tag', id='tags')

    def validate(self, extra_validators=None):
        initial_validation = super(StudyForm, self).validate(extra_validators)
        if not initial_validation:
            return False

        check = STUDIES.query.filter(STUDIES.name == self.title.data).first()

        if check is not None:
            if self.before_title.data == self.title.data:
                return True

            self.title.errors.append('このタイトルは使用できません')
            return False

        return True

class AddAuthorForm(FlaskForm):
    add_author_id = StringField('ID', validators=[InputRequired()])

    def validate_id(self, id):
        check = USERS.query.filter(USERS.id == id.data).first()
        if check is None:
            raise ValidationError('ユーザーが存在しません')

class DelAuthorForm(FlaskForm):
    del_author_id = HiddenField('ID', id='id', validators=[InputRequired()])

    def validate_id(self, id):
        check = USERS.query.filter(USERS.id == id.data).first()
        if check is None:
            raise ValidationError('ユーザーが存在しません')

class UploadForm(FlaskForm):
    file = FileField('Upload', validators=[InputRequired()])
    pubyear = SelectField('Published_Year', choices=[(year, str(year) + '年度') for year in reversed(range(2001, int(datetime.datetime.now().strftime('%Y')) + 1))])
    type = SelectField('Type',choices=[(1, 'ポスター発表'), (2, 'プレゼンテーション'), (3, '報告書'), (4, '要旨'), (5, '動画'), (6, '画像')])
    summary = TextAreaField('Summary', validators=[InputRequired()] )

class FileEditForm(FlaskForm):
    pubyear = SelectField('Published_Year', choices=[(year, str(year) + '年度') for year in reversed(range(2001, int(datetime.datetime.now().strftime('%Y')) + 1))])
    type = SelectField('Type',choices=[(1, 'ポスター発表'), (2, 'プレゼンテーション'), (3, '報告書'), (4, '要旨')])
    summary = TextAreaField('Summary', validators=[InputRequired()])

class DeleteForm(FlaskForm):
    id = StringField('ID', id='id', validators=[InputRequired()])
    type = SelectField('Type', choices=[('STUDY', '研究'), ('FILE', 'ファイル'), ('NEWS', 'お知らせ'), ('TAG', 'タグ')])
    reason = TextAreaField('Reason')
    delete = BooleanField('Delete', default=False, false_values=(False, 'false', 0, '0'))

    def validate(self, extra_validators=None):
        initial_validation = super(DeleteForm, self).validate(extra_validators)
        if not initial_validation:
            return False

        if self.type.data == "STUDY":
            check = STUDIES.query.filter(STUDIES.id == self.id.data).first()

            if check is None:
                self.id.errors.append('研究が存在しないようです')
                return False

            if self.reason.data == "":
                self.reason.errors.append('削除理由を入力してください')
                return False

            return True

        elif self.type.data == "FILE":
            check = FILES.query.filter(FILES.id == self.id.data).first()

            if check is None:
                self.id.errors.append('ファイルが存在しないようです')
                return False

            if self.reason.data == "":
                self.reason.errors.append('削除理由を入力してください')
                return False

            return True
        
        elif self.type.data == "NEWS":
            check = NEWS.query.filter(NEWS.id == self.id.data).first()

            if check is None:
                self.id.errors.append('ニュースが存在しないようです')

            return True

        elif self.type.data == "TAG":
            check = TAGS.query.filter(TAGS.id == self.id.data).first()

            if check is None:
                self.id.errors.append('タグが存在しないようです')

            return True

        return False

class TagForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    before_title = HiddenField('Before_Title')
    tips = TextAreaField('Tips', validators=[InputRequired()])

    def validate(self, extra_validators=None):
        initial_validation = super(StudyForm, self).validate(extra_validators)
        if not initial_validation:
            return False

        check = STUDIES.query.filter(STUDIES.name == self.title.data).first()

        if check is not None:
            if self.before_title.data == self.title.data:
                return True

            self.title.errors.append('このタイトルは使用できません')
            return False

        return True

class LoginForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    ad_disable = HiddenField('AD-Disable')

class LegacyForm():
    filelist= HiddenField('Filelist', validators=[InputRequired()])
    type = SelectField('Type',choices=[(1, 'ポスター発表'), (2, 'プレゼンテーション'), (3, '報告書'), (4, '要旨')])
    field = SelectField('Field', choices=[(1, '1分野'), (2, '2分野'), (3, '3分野'), (4, '部活動')])

class PostNewsForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = HiddenField('Content', validators=[InputRequired()])
    raw_markdown = TextAreaField('Raw Markdown', validators=[InputRequired()])

class AddRoleForm(FlaskForm):
    add_user_id = StringField('User_ID', validators=[InputRequired()])

    def valdate_user_id(self, user_id):
        check = USERS.query.filter(USERS.id == user_id.data).first()
        if check is None:
            raise ValidationError('ユーザーが存在しません')
        
class DelRoleForm(FlaskForm):
    del_user_id = HiddenField('ID', id='id', validators=[InputRequired()])

    def validate_id(self, id):
        check = USERS.query.filter(USERS.id == id.data).first()
        if check is None:
            raise ValidationError('ユーザーが存在しません')