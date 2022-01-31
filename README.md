# Name
IR支援ツール(仮)
# Overview
音ゲーのIRを開催する人向けの、スコア集計補助ツールです。
IR、曲、提出は編集、削除が可能。結果発表の際の補助として、スコアのcsv書き出しにも対応。
# Install
```
git clone https://github.com/ekaraage/ranking_flask.git
```
この後はHerokuにdeployや、自前のサーバーで稼働するなど。
# Caution
Herokuにdeployして運用するとき、これまでのIRのデータが失われるので、更新の前には必ず
```
heroku git:clone -a <app_name>
```
などしてデータベースを保存したのち、復元してください。今はdb以下に.gitignoreを入れていますが、削除してgithubに全てアップロードしておくと良いかもしれません。
# Terms of service
このサービスを使用して起こった損害については、その一切の責任を負いません。
# Author
ekaraage(twitter:[@ekaraage](https://twitter.com/ekaraage/))