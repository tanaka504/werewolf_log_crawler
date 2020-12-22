import glob
import json


def summary():
    kano_files = glob.glob('./data/kanolab/annotated/*.json')
    ruru_files = glob.glob('./data/ruru_server/annotated/*.json')
    files = kano_files + ruru_files
    with open('./data/werewolf_recognize_corpus.tsv', 'a') as of:
        for idx, filename in enumerate(files, 1):
            print(f'\r***** {idx}/{len(files)} *****', end='')
            data = json.load(open(filename))
            [of.write(f'{log["text"]}\t{log["annotation"]}\n') for log in data['logs'] if not log['annotation'] == 'trash']
        print()

if __name__ == '__main__':
    summary()