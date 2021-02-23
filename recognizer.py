from detector import QuestionDetector
from classifier import Classifier
import re
import MeCab

class Morph:
    def __init__(self, word, feature):
        self.word = word
        cols = feature.split(',')
        self.pos = cols[0]
        self.pos2 = cols[1]
    
    def __repr__(self):
        return self.word

class Recognizer:
    def __init__(self, agent_id):
        self.clf = Classifier(
            model_path='./models/model.augmented.pkl',
            vectorizer_path='./models/vectorizer.augmented.pkl',
            label_dict_path='./models/label_dict.augmented.pkl'
        )
        self.q_detector = QuestionDetector(agent_id)
        self.tokenizer = MeCab.Tagger()

    def recognize(self, sentence):
        sentences = self.split_sentence(sentence)
        analyzed_sentences = [self.normalize(s) for s in sentences]
        sentences = [''.join([w.word for w in s]) for s in analyzed_sentences]
        intents = self.clf.predict(sentences)
        is_q = any(self.q_detector.detect(s) for s in sentences)
        results = [self.get_detail(s, i) for s, i in zip(analyzed_sentences, intents)]
        return results

    def get_detail(self, sentence, intent):
        if intent == 'DIVINE':
            agent_id = self.get_agent_id(''.join([w.word for w in sentence]))
            result = self.get_white_black(sentence)
            result = 'HUMAN' if result is None else result
            return ('DIVINE', agent_id, result)

        elif intent == 'VOTE':
            agent_id = self.get_agent_id(''.join([w.word for w in sentence]))
            return ('VOTE', agent_id)

        elif intent == 'ESTIMATE':
            agent_id = self.get_agent_id(''.join([w.word for w in sentence]))
            role = self.get_white_black(sentence)
            role = self.get_role(sentence) if role is None else role
            return ('ESTIMATE', agent_id, role)

        elif intent == 'CO':
            role = self.get_role(sentence)
            return ('CO', role)

        elif intent == 'REQUEST':
            return ('REQUEST')

        else:
            return ('CHAT')

    def get_agent_id(self, sentence):
        m = re.search(r'Agent\[(\d+)\]', sentence)
        if m:
            return m.group(1)
        else:
            return False
    
    def get_role(self, sentence):
        if any(w.word == '人狼' for w in sentence):
            return '狼'
        elif any(w.word == '狂人' for w in sentence):
            return '狂'
        elif any(w.word == '占い師' for w in sentence):
            return '占'
        else:
            return '村'

    def get_white_black(self, sentence):
        if any(w.word == '人狼' for w in sentence):
            return 'WEREWOLF'
        elif any(w.word == '村人' for w in sentence):
            return 'HUMAN'
        else:
            return None
        
    def normalize(self, sentence):
        sentence = self.norm_token(sentence)
        words = self.tokenize(sentence)
        words = [self.norm_role(w) for w in words]
        return words
    
    def tokenize(self, sentence):
        result = []
        for line in self.tokenizer.parse(sentence).strip().split('\n'):
            if line == 'EOS': break
            word, feature = line.split('\t')
            result.append(Morph(word, feature))
        return result
    
    def norm_role(self, s):
        if s.pos == '名詞':
            if re.match(r'人狼|狼|黒', s.word):
                s.word = '人狼'
            elif re.match(r'狂人|狂', s.word):
                s.word = '狂人'
            elif re.match(r'占い師|占い|占', s.word):
                s.word = '占い師'
            elif re.match(r'村人|人間|白', s.word):
                s.word = '村人'
        return s
    
    def norm_token(self, sentence):
        sentence = re.sub(r'[\.．。]', '。', sentence)
        sentence = re.sub(r'[\,，、]', '、', sentence)
        sentence = re.sub(r'\?|？', '？', sentence)
        sentence = re.sub(r'\!|！', '！', sentence)
        return sentence
            
    def split_sentence(self, sentence):
        sentence = self.norm_token(sentence)
        sentence = re.sub(r'？', '？[SEP]', sentence)
        sentence = re.sub(r'！', '！[SEP]', sentence)
        sentence = re.sub(r'。', '。[SEP]', sentence)
        sentence = re.sub(r'\[SEP\]$', '', sentence)
        sentences = sentence.split('[SEP]')
        return sentences

if __name__ == '__main__':
    s = 'Agent[02]に投票しようかな'
    r = Recognizer(1)
    a = r.recognize(s)
    print(a)