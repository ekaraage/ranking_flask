ファイル構成
	resources/db/ir_db.json
	resources/db/(ir_id)/songs.json
	resources/db/(ir_id)/submits.json

db.jsonの構造
	1. IRのID
	1. IRのタイトル
	1. 開始日
	1. 終了日
	1. 編集/削除パス(4桁？)
	1. salt

songs.jsonの構造
	1. IRのID
	1. 曲のID
	1. 機種(コース名)
	1. 曲名
	1. 編集/削除パス(4桁？)
	1. salt
を各曲ごとに

submits.jsonの構造
	1. 提出のID
	1. 提出者の名前
	1. 曲のID
	1. スコア
	1. 画像へのURL
	1. コメント
	1. 編集/削除パス(4桁？)
	1. salt
を各提出ごとに