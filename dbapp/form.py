import datetime
from dbapp import db
from dbapp.models.tables import STUDIES, USERS, TAGS
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SelectField, TextAreaField, HiddenField, PasswordField, SubmitField, ValidationError, MultipleFileField
from wtforms.validators import InputRequired

class StudyForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    before_title = HiddenField('Before_Title')
    summary = HiddenField('Content', validators=[InputRequired()])
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
    name = StringField('Name')
    password = PasswordField('Password')
    ad_disable = HiddenField('AD-Disable')

class LegacyForm():
    filelist= HiddenField('Filelist', validators=[InputRequired()])
    type = SelectField('Type',choices=[(1, 'ポスター発表'), (2, 'プレゼンテーション'), (3, '報告書'), (4, '要旨')])
    field = SelectField('Field', choices=[(1, '1分野'), (2, '2分野'), (3, '3分野'), (4, '部活動')])

class PostNewsForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = HiddenField('Content', validators=[InputRequired()])
    raw_markdown = TextAreaField('Raw Markdown', validators=[InputRequired()])
