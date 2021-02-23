import re

class QuestionDetector:
    def __init__(self, agent_id):
        self.agent_id = int(agent_id)
        self.anchor_regex = re.compile(r'>>\s?Agent\[(\d+)\]\s')
    
    def has_anchor(self, sentence):
        # 自分にアンカーついてるかどうか
        m = self.anchor_regex.search(sentence)
        if m:
            anchor_target = int(m.group(1))
            return self.agent_id == anchor_target
        return False
        
    def is_wh(self, sentence):
        #who
        if re.match(r'.*(誰|だれ|どなた).*', sentence):
            return 'WHO'
        elif re.match(r'.*(なぜ|何故|なんで|理由|わけ).*',sentence):
            return 'WHY'
        elif re.match(r'.*(どう|どのように).*', sentence):
            return 'HOW'
        elif re.match(r'.*(下さい|ください|くれ)(．|。|.)', sentence):
            return 'REQUEST'
        else:
            return False
    
    def has_question(self, sentence):
        if re.match(r'.*(\?|？).*', sentence):
            return 'QUESTION'
        else:
            return False
    
    def detect(self, sentence):
        if not self.has_anchor(sentence): return False
        sentence = self.anchor_regex.sub('', sentence)
        wh = self.is_wh(sentence)
        if wh: return wh
        q = self.has_question(sentence)
        if q: return q
        return False

if __name__ == '__main__':
    det = QuestionDetector(1)
    det.detect('>>Agent[01] Agent[01]さん、随分と必死ですね。')
