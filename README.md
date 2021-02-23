## 人狼ログクローラー

### クローラー
以下のサイトからログを収集しています．
- [るる鯖のセッションログ](https://ruru-jinro.net/searchresult.jsp)
- [人狼知能 自然言語処理部門 対戦ログ](https://kanolab.net/aiwolf/2020/main/single/)


### アノテーションツール
発言に意図を付与したコーパスは少ないため，
発言に含まれる意図をアノテートするためのツールを用意しています．

意図は人狼知能 プロトコル部門で使用されている(CO, VOTE, DIVINED, ESTIMATE, CONFIRM, REQUEST, CHAT)が付与できるようになっています．


### 分類器
発言の意図を推定する簡単な分類器を用意しました．

```
python classifier.py --cv
```
で交差検定しながら訓練します．

```
python classifier.py --test
```
で自分で入力した文の意図を推定できます．

### Note
- [x] CONFIRM反応しづらいしいらんかな
- [x] ユーザー名とか入ってるのを正規化
- [x] 「占い師」を「人狼」，「村人」に置き換えたりしてAugmentation
- [ ] (MeCab -> SentencePiece)
- [ ] 回答が必要か否かのラベル付与 -> アンカーが会ったら必要で十分，何を返すべきかをパターンで分類
- [ ] 雑談応答
- [ ] REQUESTの場合の対応
- [ ] ログ全部分類してみてエラー解析


- 初期  Accuracy:0.74
- ユーザー名初期化  Accuracy:0.7606
- Data Augmentation Accuracy:0.7620

