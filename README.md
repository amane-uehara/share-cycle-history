# シェアサイクルの利用履歴の取得スクリプト

シェアサイクルの利用履歴をJSON形式で取得するためのPythonスクリプト。

## INSTALL

```sh
$ pip3 install beautifulsoup4
```

## USAGE

2021/09/01 から 2021/09/30 までのデータを取得するコマンド

```sh
$ python3 fetch_history.py 'https://tcc.docomo-cycle.jp/cycle/TYO/cs_web_main.php' member_id password 2021 9
```

結果

```
[
  {
    "bgn": {
      "dt": "20210902182500",
      "symbol": "A1-01",
      "name_jp": "ああああああ",
      "name_en": "Aaaaaaa Bbbb Cccccc",
    },
    "end": {
      "dt": "20210902183000",
      "symbol": "A1-02",
      "name_jp": "ううう",
      "name_en": "Ddddddd",
    },
    "cost": "0"
  },
  ... (略) ...
```

## LICENSE

MIT
