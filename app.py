from flask import Flask, render_template, request, redirect, url_for
import json, os, glob
from collections import Counter
app = Flask(__name__)

id2annotation = {
    "0": "CO",
    "1": "VOTE",
    "2": "DIVINED",
    "3": "ESTIMATE",
    "4": "CONFIRM",
    "5": "REQUEST",
    "6": "CHAT",
    "7": "trash"
}

@app.route('/')
def annotation():
    log_id = request.args.get('log_id', default=1, type=int)
    data = get_target(log_id)
    if len(data['logs']) < 1:
        return redirect(f'/?log_id={log_id+1}')
    else:
        return render_template('index.html', data=data, log_id=log_id)

@app.route('/submit', methods=['POST'])
def submit():
    log_id = request.form.get('log_id', default=1, type=int)
    data = get_target(log_id)
    for idx, log in enumerate(data['logs']):
        # annotation = request.args.get(f'annotation{idx}', default='7', type=str)
        annotation = request.form.get(f'annotation{idx}', default='7', type=str)
        log['annotation'] = id2annotation[annotation]
    save_annotation(data, log_id)

    return redirect(f'/?log_id={log_id+1}')

@app.route('/stat')
def stat():
    stat = current_stat()
    return render_template('stat.html', data=stat)


def get_target(log_id):
    data = json.load(open(f'./data/kanolab/raw/werewolf_log{log_id}.json'))
    return data

def save_annotation(data, log_id):
    json.dump(data, 
        open(f'./data/kanolab/annotated/werewolf_log{log_id}.annotated.json', 'w'), 
        ensure_ascii=False, indent=4, separators=(',', ': '))

def current_stat():
    files = glob.glob('./data/kanolab/annotated/*.annotated.json')
    whole_annts = []
    for filename in files:
        jsondata = json.load(open(filename))
        annts = [log['annotation'] for log in jsondata['logs'] if not log['annotation'] == 'trash']
        whole_annts.extend(annts)
    return Counter(whole_annts)

if __name__ == '__main__':
    app.debug = True
    app.run()
