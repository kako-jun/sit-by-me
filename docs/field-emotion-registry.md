# フィールド感情吹き出し素材台帳

フィールドの人物立ち絵から少しずらして表示し、感情を表す吹き出し。ダメージ・回復数字と似た印象の、ゲームらしい角張った絵にする（kako-jun 指示 2026-10-27）。制作・実機確認は [#170](https://github.com/kako-jun/sit-by-me/issues/170)、数字は [#169](https://github.com/kako-jun/sit-by-me/issues/169)。

| 素材 | 用途 | 状態 | パス・寸法 |
|---|---|---|---|
| ！ | 感情を表す吹き出し | 採用（kako-jun 2026-10-28）。赤い「！」 | `assets/images/effects/field-emotion/field-emotion-exclaim.png`（256x256 透過PNG） |
| ？ | 感情を表す吹き出し | 採用（kako-jun 2026-10-28）。青い「？」 | `assets/images/effects/field-emotion/field-emotion-question.png`（256x256 透過PNG） |
| ... | 感情を表す吹き出し | 採用（kako-jun 2026-10-28）。灰色の3点 | `assets/images/effects/field-emotion/field-emotion-dots.png`（256x256 透過PNG） |

3枚とも、画像生成（gpt-image-2）の試作（1254x1254）から、アルファ16以上の範囲で切り抜き、長辺240pxへ最近傍法で縮小して、256x256の透明キャンバスの中央に置いた。白地・黒枠・灰色の影・下向きの尾付きの角張ったピクセル風。素材台帳は `docs/ledger/素材.yaml`（A-1051〜A-1053）。

採用経緯・プロンプトは [#170 のコメント](https://github.com/kako-jun/sit-by-me/issues/170#issuecomment-6470555996) に記録。上記以外の種類・色・サイズ・表示位置・タイミング、実機での見やすさの確認は未決。表示ルールは #170、フィールド共通UI #139 と整合させる。

配置（`effects/field-emotion/`）は暫定。フィールド共通UI #139 との境界が未合意なので、#139 と整合させる時に再検討する。見やすさや最終サイズの判断は、実機でフィールドに出す段階に残す。
