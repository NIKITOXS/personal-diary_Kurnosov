from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
FILE_NAME = 'entries.json'

def load_entries():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_entries(entries):
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

entries = load_entries()

@app.route('/')
def index():
    return render_template('index.html', entries=entries)

@app.route('/entry/<int:entry_id>')
def detail(entry_id):
    for entry in entries:
        if entry.get('id') == entry_id:
            return render_template('detail.html', entry=entry)
    return "Запись не найдена", 404

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        new_id = max([e.get('id', 0) for e in entries], default=0) + 1
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_entry = {"id": new_id, "title": title, "content": content, "date": current_date}
        entries.append(new_entry)
        save_entries(entries)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit(entry_id):
    for entry in entries:
        if entry.get('id') == entry_id:
            if request.method == 'POST':
                entry['title'] = request.form.get('title')
                entry['content'] = request.form.get('content')
                save_entries(entries)
                return redirect(url_for('index'))
            return render_template('edit.html', entry=entry)
    return "Запись не найдена", 404

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    global entries
    entries = [e for e in entries if e.get('id') != entry_id]
    save_entries(entries)
    return redirect(url_for('index'))

@app.route('/search')
def search():
    q = request.args.get('q', '').lower()
    filtered = [e for e in entries if q in e.get('title', '').lower()]
    return render_template('index.html', entries=filtered)

@app.route('/filter/week')
def filter_week():
    week_ago = datetime.now() - timedelta(days=7)
    filtered = []
    for e in entries:
        try:
            entry_date = datetime.strptime(e.get('date'), "%Y-%m-%d %H:%M")
            if entry_date >= week_ago:
                filtered.append(e)
        except ValueError:
            pass
    return render_template('index.html', entries=filtered)

if __name__ == '__main__':
    app.run(debug=True)