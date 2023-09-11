from dbapp import db
from dbapp.models.tables import FILES, STUDIES

import markdown, bleach

allowed_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'p', 'span', 'a', 'br', 'strong', 'em', 's', 'strike', 'del', 'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'th', 'tr', 'td', 'img', 'image', 'audio', 'video', 'input', 'pre', 'code', 'blockquote', 'figure', 'figcaption', 'abbr', 'details', 'summary', 'cite', 'sub', 'sup', 'time', 'address']
allowed_attributes = {
    '*': ['id'],
    'a': ['href', 'title'],
    'input': ['type', 'value', 'checked', 'disabled'],
    'code': ['class'],
    'div': ['class'],
    'span': ['class'],
    'img': ['src', 'alt'],
    'audio': ['src', 'controls'],
    'video': ['src', 'controls'],
}

bleach_config = {
    'tags': allowed_tags,
    'attributes': allowed_attributes,
}

def convertMarkdown(text):
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite', 'attr_list', 'footnotes', 'toc'])
    return bleach.clean(md.convert(text), **bleach_config)

# SEARCH ENGIN
from sqlalchemy import or_, and_

def SearchEngine(
        search_terms=None,
        ascending=True,
        update_at_range=None,
        create_at_range=None,
        field=0,
        sort_column="update_at"
    ):
    # STUDIESとFILESのJOINを作成します。
    query = db.session.query(STUDIES).outerjoin(FILES)

    # 検索対象のカラムを定義します。
    study_columns = [STUDIES.name, STUDIES.summary]
    file_columns = [FILES.summary, FILES.content]

    # 検索条件を準備します。
    search_filters = []

    if search_terms:
        # スペースで区切られた複数の単語でOR検索を実行します。
        search_words = search_terms.split()
        search_conditions = []
        for word in search_words:
            word_conditions = []
            for column in study_columns + file_columns:
                word_conditions.append(column.ilike(f"%{word}%"))
            search_conditions.append(or_(*word_conditions))
        search_filters.append(and_(*search_conditions))

    if update_at_range:
        # STUDIESのupdate_atの範囲指定
        start_date, end_date = update_at_range

        search_filters.append(STUDIES.update_at.between(start_date, end_date))

    if create_at_range:
        # STUDIESのcreate_atの範囲指定
        start_date, end_date = create_at_range
        search_filters.append(STUDIES.create_at.between(start_date, end_date))

    if field != 0:
        # STUDIESのfieldの値
        search_filters.append(STUDIES.field == field)

    # 絞り込み条件を適用します。
    if search_filters:
        query = query.filter(and_(*search_filters))

    # 並び替え条件を設定します。
    if sort_column == 'update_at':
        query = query.order_by(STUDIES.update_at.asc() if ascending else STUDIES.update_at.desc())
    elif sort_column == 'get_total_access_count':
        query = query.order_by(STUDIES.get_total_access_count().asc() if ascending else STUDIES.get_total_access_count().desc())
    elif sort_column == 'get_total_preview_count':
        query = query.order_by(STUDIES.get_total_preview_count().asc() if ascending else STUDIES.get_total_preview_count().desc())
    else:
        query = query.order_by(STUDIES.create_at.asc() if ascending else STUDIES.create_at.desc())

    # 結果を返します。FILESオブジェクトも取得します。
    studies = query.all()

    # 空の場合はタイトルを変えて返します。
    if not search_terms:
        return [studies, "研究一覧"]

    # FILESオブジェクトを取得します。
    for study in studies:
        study.files = db.session.query(FILES).filter(FILES.study_id==study.id, or_(*[or_(FILES.summary.contains(f"%{term}%"), FILES.content.contains(f"%{term}%")) for term in search_words])).all()

    return [studies, '"' + search_terms + '"の検索結果']

import wikipedia
from nltk.corpus import wordnet

wikipedia.set_lang("ja")

def wikipedia_summary(word):
    page = None
    summary = "ユーザーによって追加されたタグ"
    try:
        page = wikipedia.page(word)
        summary = page.summary
        summary += "\nWikipediaより引用 - " + page.url
    except wikipedia.exceptions.DisambiguationError as e:
        wordlist = e.options
        similaritys = []
        for words in wordlist:
            try:
                similaritys.append(wordnet.synsets(word, lang="jpn")[0].path_similarity(wordnet.synsets(words, lang="jpn")[0]))
            except IndexError:
                similaritys.append(0)
    
        dic = dict(zip(wordlist, similaritys))
        dic = sorted(dic.items(), key=lambda x:x[1], reverse=True)
        nums = list(dict((x, y) for x, y in dic).values())

        if nums[0] >= 0.5:
            dic = list(dict((x, y) for x, y in dic).keys())
            word = dic[0]
            summary = str(wikipedia_summary(word))
        else:
            similarity = 0

    except Exception:
        similarity = 0

    try:
        similarity = wordnet.synsets(word, lang="jpn")[0].path_similarity(wordnet.synsets(page.title, lang="jpn")[0])
    except Exception:
        similarity = 0

    if page is not None:
        if not word in page.title and not page.title in word:
            summary = "ユーザーによって追加されたタグ"

    return summary

import hashlib

def sha256_hash(path):
    with open(path, "rb") as f:
        hasher = hashlib.new("sha256")
        for chunk in iter(lambda: f.read(2048 * hasher.block_size), b''):
            hasher.update(chunk)

    return hasher.hexdigest()

import re

def clean_html(html):
    # タグを削除する正規表現パターン
    tag_pattern = re.compile(r'<.*?>')

    # タグを削除
    text = re.sub(tag_pattern, '', html)

    # 別の要素同士のテキストに空白を挿入
    text_with_whitespace = re.sub(r'(\w)([^\w\s])', r'\1 \2', text)
    text_with_whitespace = re.sub(r'([^\w\s])(\w)', r'\1 \2', text_with_whitespace)

    return text_with_whitespace