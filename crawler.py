import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import urllib.request


class RuRuLogCrawler:
    def __init__(self):
        self.not_found_pattern = re.compile(r'^404(.*?)')
        self.role_pattern = re.compile(r'\<span class\=\"oc([0-9]*?)\"\>(.*?)\<\/span\>')
        self.en_text_pattern =  re.compile(r'[a-zA-Z0-9\!\?\.\,]')
        self.html_tag_pattern = re.compile(r'\<(.*?)\/?\>')

    def get_target_urls(self):
        base_url = 'https://ruru-jinro.net/log'
        base_name = '/log{}.html'
        with open('data/enable_urls.txt', 'w') as f:
            for i in tqdm(range(4334, 492595)):
                for j in range(1, 6):
                    idx = str(j) if j > 1 else ''
                    url = base_url + idx + base_name.format(i)
                    if self.validate_url(url):
                        f.write(url + '\n')
                        break

    def validate_url(self, url):
        url = requests.get(url)
        if url.status_code == 404:
            return False
        soup = BeautifulSoup(url.content, "html.parser")
        title = soup.find('title')
        try:
            if self.not_found_pattern.match(title.string):
                return False
        except:
            return False
        return True

    def get_roles(self, url):
        url = requests.get(url)
        if url.status_code == 404:
            return 0, ['hoge']
        soup = BeautifulSoup(url.content, "html.parser")
        n_member = len(soup.select('td.name'))
        roles = soup.select('.val')
        spans = [span for role in roles for span in role.find_all('span')]
        roles = []
        for span in spans:
            m = self.role_pattern.search(str(span))
            if m is not None:
                role = m.group(2)
                roles.append(role)
        return n_member, roles

    def filtering(self):
        urls = [line.strip() for line in open("./data/enable_urls.txt").readlines()]
        f = open('./data/target_urls.txt', 'a')
        log_f = open('./checkpoint', 'w')
        for i, url in enumerate(urls, 1):
            print(f'\r****** {i}/{len(urls)} ******', end="")
            n_member, roles = self.get_roles(url)
            if n_member < 2: continue
            if all(role in {"村　人", "占い師", "人　狼", "狂　人"} for role in roles):
                f.write(url+'\n')
            log_f.write(f'{str(i)},')

    def get_namelist(self, soup):
        rows = soup.select('div.d1221 tr')
        is_upper_row = True
        namelist = {}
        for row in rows:
            if is_upper_row:
                names = [name.text for name in row.select('td.name span')]
                is_upper_row = False
            else:
                roles = []
                for span in row.select('td.val span'):
                    m = self.role_pattern.search(str(span))
                    if m is not None:
                        role = m.group(2)
                        roles.append(role)

                for name, role in zip(names, roles):
                    if name == '第一犠牲者': continue
                    namelist[name] = role
                is_upper_row = True
        return namelist

    def get_logs(self, soup, namelist):
        logs = []
        rows = soup.select('div.d12151 table tr')
        for row in rows:
            name = row.select('td.cn span.name')
            if len(name) < 1: continue
            name = name[0].text
            if not name in namelist.keys(): continue

            log = row.select('td.cc')
            if len(log) < 1: continue
            log = self.preprocess(log[0].text)
            if log is None: continue
            logs.append({ 'name': name, 'text': log })

        return logs

    def preprocess(self, text):
        if self.en_text_pattern.match(text): return None
        
        text = self.html_tag_pattern.sub('', text)
        if text == '': return None
        return text

    def crawl(self):
        urls = [line.strip() for line in open('./data/target_urls.txt').readlines()]
        for i, url in enumerate(urls, 1):
            print(f'\r****** {i} / {len(urls)} ******', end='')
            res = requests.get(url)
            if res.status_code == 404: continue
            soup = BeautifulSoup(res.content, "html.parser")
            namelist = self.get_namelist(soup)
            logs = self.get_logs(soup, namelist)
            crawled_logs = {
                'namelist': namelist,
                'logs': logs,
                'url': url
            }
            json.dump(crawled_logs, open(f'./data/raw/werewolf_log{i}.json', 'w'), ensure_ascii=False, indent=4, separators=(',', ': '))
        print()
    
    def start(self):
        self.get_target_urls()
        self.filtering()
        self.crawl()

class KanoLabCrawler:
    def __init__(self):
        pass

    def get_target_urls(self):
        base_url = 'https://kanolab.net/aiwolf/2020/main/single/'
        agents = [
            'CanisLupus',
            'Kanolab',
            'Udon'
        ]
        with open('./data/kanolab/target_urls.txt', 'w') as of:
            for agent in agents:
                tgt_url = base_url + f'{agent}50games_log'
                res = requests.get(tgt_url)
                soup = BeautifulSoup(res.content, "html.parser")
                links = soup.select('table a')
                [of.write(f'{tgt_url}/{l.text}\n') for l in links if re.match(r'.*?\.log', l.text)]

    def crawl(self):
        urls = [line.strip() for line in open('./data/kanolab/target_urls.txt').readlines()]
        for idx, url in enumerate(urls, 1):
            with urllib.request.urlopen(url) as u:
                data = u.read().decode('utf-8').split('\n')
            data = [line.split(',') for line in data if not line == '']
            namelist = {}
            logs = []
            for line in data:
                if line[0] == '0' and line[1] == 'status':
                    namelist[f'Agent[{line[2]}]'] = line[3]
                elif line[1] == 'talk' and not line[-1] == 'Skip' and not line[-1] == 'Over':
                    logs.append({
                        'name': f'Agent[{line[4]}]',
                        'text': line[-1]
                    })
                else:
                    pass
            crawled_logs = {
                'namelist': namelist,
                'logs': logs,
                'url': url
            }
            json.dump(crawled_logs, open(f'./data/kanolab/raw/werewolf_log{idx}.json', 'w'), ensure_ascii=False, indent=4, separators=(',', ': '))
    
    def start(self):
        self.get_target_urls()
        self.crawl()


if __name__ == "__main__":
    # RuRuLogCrawler().start()
    KanoLabCrawler().start()