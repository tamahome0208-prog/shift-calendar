# v10.5 Firestore Rules 追加手順

v10.5 で新規追加された `shifts` collection の read/write 許可を、
Firebase Console から手動で反映してください。

## 手順

1. https://console.firebase.google.com/ にログイン
2. 該当プロジェクトを開く → 「Firestore Database」 → 「ルール」タブ
3. 既存の rules ブロック(events / anniversaries)の下に以下を追加:

```
match /shifts/{ym} {
  allow read, write: if request.auth != null;
}
```

4. 「公開」ボタンで反映

## 検証

- 未認証状態でアプリを開く → shifts 読取・書込がエラーになれば正常
- 認証済み(anonymous auth)状態で PDF アップロード → 保存成功で反映
