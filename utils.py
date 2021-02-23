import glob
import json
import re
import random


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

def augment():
    data = [line.strip().split('\t') for line in open('./data/werewolf_recognize_corpus.tsv').readlines()]
    of = open('./data/werewolf_recognize_corpus.augmented.tsv', 'w')
    for text, label in data:
        of.write(f'{text}\t{label}\n')
        if label == 'DIVINED':
            for repl_text in augment_by_bw(text):
                of.write(f'{repl_text}\t{label}\n')

            for repl_text in augment_by_agent(text):
                of.write(f'{repl_text}\t{label}\n')

        elif label == 'CO':
            for repl_text in augment_by_vw(text):
                of.write(f'{repl_text}\t{label}\n') 

        elif label == 'ESTIMATE':
            for repl_text in augment_by_bw(text):
                of.write(f'{repl_text}\t{label}\n')

            for repl_text in augment_by_agent(text):
                of.write(f'{repl_text}\t{label}\n')

        elif label == 'VOTE' or label == 'REQUEST':
            for repl_text in augment_by_agent(text):
                of.write(f'{repl_text}\t{label}\n')    

def augment_by_bw(text):
    white_terms = ['白', '人間', '○']
    black_terms = ['黒', '人狼', '狼', '●']
    data = []
    for w_term in white_terms:
        regex = '.*{}.*'.format(w_term)
        if re.match(regex, text):
            b_term = random.choice(black_terms)
            repl_text = re.sub(w_term, b_term, text)
            data.append(repl_text)
            break

    for b_term in black_terms:
        regex = '.*{}.*'.format(b_term)
        if re.match(regex, text):
            w_term = random.choice(white_terms)
            repl_text = re.sub(b_term, w_term, text)
            data.append(repl_text)
            break

    return data

def augment_by_vw(text):
    villager_side_terms = ['村人', '占い師', '人間']
    werewolf_side_terms = ['狂人', '人狼', '狂', '狼']
    data = []
    for vs_term in villager_side_terms:
        regex = '.*{}.*'.format(vs_term)
        if re.match(regex, text):
            ws_term = random.choice(werewolf_side_terms)
            repl_text = re.sub(vs_term, ws_term, text)
            data.append(repl_text)
            break

    for ws_term in werewolf_side_terms:
        regex = '.*{}.*'.format(ws_term)
        if re.match(regex, text):
            vs_term = random.choice(villager_side_terms)
            repl_text = re.sub(ws_term, vs_term, text)
            data.append(repl_text)
            break

    return data

def augment_by_agent(text):
    agent_num = 5
    agent_terms = [f'Agent[0{i+1}]' for i in range(agent_num)]
    data = []
    for i in range(1, agent_num+1):
        regex = re.compile('.*Agent\[0{}\].*'.format(i))
        if regex.match(text):
            other_agent = random.choice(['Agent[0{}]'.format(j) for j in range(1, agent_num+1) if not i == j])
            repl_text = re.sub('Agent\[0{}\]'.format(i), other_agent, text)
            data.append(repl_text)
            break
    return data


if __name__ == '__main__':
    augment()
