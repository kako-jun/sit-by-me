# 体内MAP（BDY-xx）基準状態の採用記録（共通・2026-10-22、#142）

BDY-02 は個別記録 [20261022-bdy02-adoption.md](20261022-bdy02-adoption.md) にある。BDY-02 以外の体内MAP（16枚）は、この文書の採用表に1行ずつ追記する。いずれも mask・links・独立red-team未通過のため **runtimeへは切り替えず**、台帳statusは `blocked` のまま。

## 経緯
- 2段階生成（簡素な背景の段階1 → 装飾の段階2）を試したが、kako-jun 指示（2026-10-22「簡素な背景で一度作ってからやり直すのをやめろよ」）で**廃止**した。手間がかかるため。
- 過去の装飾込み1回生成は幾何が崩れた（BDY-02 neck-v1 は床IoU 0.775、BDY-10 は床IoU 0.303）。ただしどちらも様式参照画像（BDY-10 試験画像=参照3）を渡していた。様式参照なしの構造 prompt は幾何が保たれた（BDY-02 の簡素な生成は床IoU 0.92）。
- そこで仮説「様式参照画像が幾何を崩す主因」を立て、**様式参照なし・参照2枚（clean 割付図＋材料見本）・装飾込み1回生成**を既定にした（手順は `.claude/skills/sit-field-background/SKILL.md` の onepass）。
- BDY-09 での結果: 床IoU 0.715（床が期待の約8割に細る）、チェッカー総合FAIL。幾何は完全には保たれなかったが、kako-jun が目視で「よい」と採用した。仮説は半分だけ支持（BDY-10 の 0.303 よりは大きく改善、BDY-02 の簡素生成 0.92 には届かない）。
- BDY-09 の旧版（旧プールのフェルトの花入り・床IoU 0.715・sha256 `7096c7b5…`）は、新プール（人体関連）への作り直し版を kako-jun が採用したため**取り消し・削除**した（旧送信文は [BDY-09-old-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-09-old-prompt-send.txt) に来歴として残す）。現行の採用は作り直し版（床IoU 0.775）。
- BDY-03 は新プール導入前の版を kako-jun が採用した（2026-10-22、目視『このままでいい』）。元PNG sha256 `39ec5d5ba09e85f93b198935c8870087c3bc11fd215b9fcc8701a88efcea4bfe`（1672×941、WebP変換前に照合）。生成は様式参照なし・参照2枚（clean割付図＋材料見本）・装飾込み1回。現行の新プール版 prompt は未使用のため保存しない。

## 採用表
保存形式は非可逆WebP品質85・実寸（リサイズなし）。PNG原本は残さない。送信文は `20261022-body-maps-adoption-prompts/` に保存する。

| MAP | 保存先 | sha256 | 実寸 | 床IoU | checker結果 | 既知の逸脱 | 送信文 |
|---|---|---|---|---|---|---|---|
| BDY-09（左足通路1・付け根側） | `assets/images/fields/reference/body-left-leg-1-bdy09-adopted.webp`（270,378 bytes。作り直し版） | `3ff693ab1b735e14f53a401e2c9e8e97543d700feb15386c2e35e5b4160a85b2` | 1672×941 | 0.775 | 総合FAIL（赤紙5枚のみ。指定6）。四辺の土台縁PASS、装飾の色域0.00%、通路WARN（S辺+14px・幅-10%、W辺-20px・幅-22%） | 赤紙5枚、毛の房が多く毛の生えた肌にも見える | [BDY-09-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-09-prompt-send.txt)（新プール版。sha256 `8ec37781c9c736a6d60dedb58af645c212b820e46e0298480d1939b033e18a2e`） |
| BDY-03（下半身・胴体下段・4本合流） | `assets/images/fields/reference/body-lower-torso-bdy03-adopted.webp`（226,386 bytes。新プール導入前の版） | `22724fc3a41f13e91a9a0bcaacb0f771d3d2ed9b69863d8e722a96f036f520dc` | 1672×941 | 0.942（旧checker）／0.901（較正後） | 総合FAIL（赤紙5枚。指定6）。東辺上側の通路が期待より約38%細い、四辺の土台縁は旧checkerでFAIL（N/E/W 0px判定。目視では見える）。広間なしPASS、色の逸脱PASS、装飾の色域0.00% | 赤紙5枚、東辺上側の通路が細い（V字くさびが床側へ食い込み）、装飾は新プール導入前の計画（ボタン・ビーズ・半透明の紙片・masking tape・細い毛糸。人体関連の骨・細胞等のモチーフではない。花・雲は含まない） | [BDY-03-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-03-prompt-send.txt)（当時の版。装飾計画は DISC/PAPER/TAPE の旧計画。sha256 `03f8b9418b916996082e97efed5579de5ced29bec1a500563137a2a200b799ec`。verification/body-layout/prompts の現行 BDY-03 送信文＝人体関連の新プール・CELL/PLASTER/PULSE とは別物） |
| BDY-01（口） | `assets/images/fields/reference/body-mouth-bdy01-adopted.webp`（267,372 bytes） | `5331efc4c98cb024aa854e0fd8c235179e0adfbf907ad97511e57c1245409441` | 1672×941 | 0.901 | 総合WARN（S辺の通路が+27px）。赤紙6枚、四辺の土台縁PASS、色域外0.00% | 角の毛の房（初回v1は草花の庭で色契約違反だったため作り直し、v2を採用） | [BDY-01-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-01-prompt-send.txt)（sha256 `cd979dd4045aff980f1a932b13281a66771dd227c644af72595a53a4f7bcdc9b`） |
| BDY-05（左手通路1・付け根側） | `assets/images/fields/reference/body-left-arm-1-bdy05-adopted.webp`（212,068 bytes） | `e735fd28fd1d99b8935db4f0eb392447870b0c39e014e2465f452a5c5404f317` | 1672×941 | 0.839 | 総合FAIL（土台縁の波形が四辺で見えない、N/W辺の通路ずれ、S辺に期待0本のところ実測4本）。赤紙5枚、色域外0.09% | 遠近のある斜め上からの構図、土台縁の欠け、赤紙5枚 | [BDY-05-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-05-prompt-send.txt)（sha256 `f3002ee32d6588ec239a67bd38f572d75253f3cc907cf09488e4fa82cb1be160`） |
| BDY-06（左手通路2・末端） | `assets/images/fields/reference/body-left-arm-2-bdy06-adopted.webp`（322,122 bytes） | `612a4e1a899b896ced85799afa34f5cb5962394816f59b1ac312cc8390ab5272` | 1672×941 | 0.828 | 総合WARN（S辺の通路が+34px）。赤紙6枚、四辺の土台縁PASS、色域外0.00% | 特になし（赤紙6枚） | [BDY-06-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-06-prompt-send.txt)（sha256 `3c997da34372532d19817ba425fef6042c5d9ed45e3ffd8a136622bfc38f038b`） |
| BDY-07（右手通路1・付け根側） | `assets/images/fields/reference/body-right-arm-1-bdy07-adopted.webp`（316,554 bytes） | `41e0c9cd768b4508ec589c1def2d399c1f1d87c8f9f7211796cfb4888f2af7ef` | 1672×941 | 0.000（床色の推定失敗。実画像は帯が期待位置） | 総合FAIL（床IoU・通路・赤紙・床の汚れは、床色を黄土色 (201,148,112) と誤推定したことによる偽FAIL）。S辺の縁取りWARN、色域外0.00% | チェッカーの床色推定の失敗（画像側の問題ではない） | [BDY-07-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-07-prompt-send.txt)（sha256 `e436c6cf176536abd7f1c1ca16fa8389126b3b47c8cf3cfc791b3dc508b63e6a`） |
| BDY-08（右手通路2・末端） | `assets/images/fields/reference/body-right-arm-2-bdy08-adopted.webp`（261,072 bytes） | `d69af93e9150e9357019bea407804252d07e76be017fce08c42e4a9435821cd4` | 1672×941 | 0.904 | 総合FAIL（赤紙5枚、模型外の赤1個 (33,165)）。通路PASS、四辺の土台縁PASS、色域外0.00% | 赤紙5枚、模型外の赤 | [BDY-08-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-08-prompt-send.txt)（sha256 `3a3fe6b6dbf2a637c42708cb9fe6c015498c490842e29f64605177d4f67ff1d5`） |
| BDY-10（左足通路2・中間） | `assets/images/fields/reference/body-left-leg-2-bdy10-adopted.webp`（249,814 bytes） | `caabd723d724d8b1baa1366dfd04514ad2d131a391f4a12b59a838fe065f66be` | 1672×941 | 0.954 | 総合FAIL（N辺の通路が+60px・幅-54%、赤紙5枚）。四辺の土台縁PASS、色域外0.00% | 赤紙5枚 | [BDY-10-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-10-prompt-send.txt)（sha256 `6ae8e49912d294a426ae04d45874f0c6c417ac5cdbbaf4b2b45b7a74f7b8a5a9`） |
| BDY-11（左足通路3・末端） | `assets/images/fields/reference/body-left-leg-3-bdy11-adopted.webp`（340,390 bytes） | `c498110a52afc0d4eb2bdeddd716f9dc879872ffb40e3c832cfafeed77e8f2d9` | 1672×941 | 0.857 | 総合FAIL（W辺の机・縁取り・波形が0px、N/S辺の縁取りずれ、赤紙5枚）。N辺の通路WARN、色域外0.00% | ちぎり絵風の質感、土台縁の欠け（W辺）、赤紙5枚 | [BDY-11-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-11-prompt-send.txt)（sha256 `a0f5bfaef58a16b1cbe625dfda421463c0f94cb2c5a28676a33647acd11d5c1b`） |
| BDY-12（右足通路1・付け根側） | `assets/images/fields/reference/body-right-leg-1-bdy12-adopted.webp`（304,990 bytes） | `adc110d58f80dfc131b38568f5e361eeffed62b2e830cd32debb6f4a9ff43ccf` | 1672×941 | 0.842 | 総合FAIL（S辺の縁取り・波形が0px、N/E/W辺の縁取りずれ、赤紙5枚）。E辺の通路WARN（幅-11%）、色域外0.00% | 土台縁の欠け（S辺）、赤紙5枚 | [BDY-12-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-12-prompt-send.txt)（sha256 `3dbb8cdbf7a6faf3b21a035672800abf740119b2421e0d741fec14ec097d2ef5`） |
| BDY-13（右足通路2・中間） | `assets/images/fields/reference/body-right-leg-2-bdy13-adopted.webp`（349,056 bytes） | `9293c0284a14edc20b29844a1a304c6003c975d4e2d10b39e83113fd97783d85` | 1672×940（16:9、元PNGも1672×940） | 0.879 | 総合FAIL（赤紙5枚、模型外の赤1個 (1607,903)）。通路WARN（床色が机の上に438pxはみ出す）、四辺の土台縁PASS、色域外0.00% | 模型外の赤、赤紙5枚 | [BDY-13-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-13-prompt-send.txt)（sha256 `13d246bc56e89e879cf57f6279f6e2bc2e8a0853598b42b3958b8e2df43c691c`） |
| BDY-14（右足通路3・末端） | `assets/images/fields/reference/body-right-leg-3-bdy14-adopted.webp`（269,066 bytes） | `ef44dfb132af74e73192d5eaefbe4959fd5c0c73abbd4aba40c0e88514ab6911` | 1672×941 | 0.874 | 総合FAIL（S辺の波形が0px、W辺の机・縁取り・波形が0px、赤紙5枚、模型外の赤1個 (12,306)）。通路PASS、色域外0.00% | 土台縁の欠け（W/S辺）、模型外の赤、赤紙5枚 | [BDY-14-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-14-prompt-send.txt)（sha256 `e5be258c8afadd3b4514ce9cc7816e76404fbe55fe637ca4459d684af41e5f81`） |
| BDY-04（頭・脳の迷路通路） | `assets/images/fields/reference/body-brain-maze-bdy04-adopted.webp`（245,358 bytes） | `4f441b8cca1106f665c1670decd51008adf8b80e6f5ae485563eff61ae0f3982` | 1672×941 | 0.829 | 総合WARN（S辺の縁取り12px）。迷路検査は全一致（通路77・床セル78・ループ0・行き止まり11・T字10・壁の連続破れ0・入口は南辺1本） | 迷路の内側の壁面の装飾が少ない | [BDY-04-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-04-prompt-send.txt)（生成時の版＝現行 prompts/ と同一の版。sha256 `4463974f5a1abc5b42eb8a8e025b248bb2cfd9ba6c3311d1d371efe319c91d7f`）
| BDY-15（胃・分岐室） | `assets/images/fields/reference/body-stomach-bdy15-adopted.webp`（220,986 bytes） | `16ce82a76c721a5638399993d2089ec9ee8bd7a23720c59465c1bea238a1c93a` | 1672×941 | 0.862 | 総合FAIL（机・縁の誤判定。机が薄い木目で縁取りと同色のため、N/W の通路は縁取り帯で床が止まる扱いになった）。赤紙6枚 | 鳥の首のようにも見える形、装飾が疎、机の薄い木目でチェッカーが机/縁取り/床を誤判定（画像側の問題ではない） | [BDY-15-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-15-prompt-send.txt)（**生成時の旧版**。独立レビュー指摘の反映前。現行 prompts/BDY-15-prompt-send.txt は修正版で別物。sha256 `1db6be46deb1f00259ed45286e5dd75d4f7e8d590de03ebe428abaadd2a17b0e`）
| BDY-16（心臓・分岐室） | `assets/images/fields/reference/body-heart-bdy16-adopted.webp`（301,770 bytes） | `19b4bc72d609719991036633ebaec98cdcb746da37d9093318344eac593ff2ce` | 1672×941 | 0.866 | 赤紙6枚。床の汚れ判定17.26%（目視では床に欠けなし）。机の薄い木目によるチェッカーの誤判定あり | 部屋の丸みが通路幅に対し小さく骨のような形に見える、模型外（机の上）に毛糸の「8」の字と玉が落ちている | [BDY-16-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-16-prompt-send.txt)（**生成時の旧版**。現行 prompts/ の同名ファイルは修正版で別物。sha256 `b2ac6688d9cd1ad2757056938d07effbd05604e684b481c10ba5ae2a07cf9017`）
| BDY-17（肺・分岐室。案A） | `assets/images/fields/reference/body-lungs-bdy17-adopted.webp`（194,058 bytes） | `dc1c67d1c156565ca19ec006d38de13a484a601064aa5cecbbec80e9702633a4` | 1672×941 | 0.830 | 赤紙6枚。床の汚れ判定56.4%・机へのはみ出し（床色推定が机の薄桃に引かれた誤判定。画像側の問題ではない） | 部屋の丸みが通路幅に対し小さく骨のような形に見える、模型外（机の上）に毛糸の束と玉が落ちている | [BDY-17-prompt-send.txt](20261022-body-maps-adoption-prompts/BDY-17-prompt-send.txt)（**生成時の旧版**。現行 prompts/ の同名ファイルは修正版で別物。sha256 `246ec8a20e6f29a6dd75553d6a004b52479adcee1318d7d73ff53284b682f427`）

BDY-09（作り直し版）の元PNG（sha256 `91430ac92c37aec43e7d90ffe3957c5838ff98cb463acfc8e075b15b881d1555`、1672×941）はWebP変換前に照合した。生成は様式参照なし・参照2枚（clean割付図＋材料見本）・新プール prompt で1回のみ。採用日 2026-10-22、決定者 kako-jun（目視）。

### 体内10枚（BDY-01・05〜08・10〜14）の追記（2026-10-22）

元PNG（変換前に照合）の sha256: BDY-01 `2fa017f5a6633229723082c9918c66ad6f2d61588fdccbd99665c5d2e55f941d`、BDY-05 `a7a3ab0ea0f1d3bc8de70e8d92987d168a17218c46b1f94aeb52d85387079b36`、BDY-06 `c7b60c752a6efd8611ba437f94ae2938155d2291bd0b2e9e9a769318225f5756`、BDY-07 `25c1ba92ed86701c145409310513f481eff821c4eab48a4d4a169080b80701dd`、BDY-08 `a98cf228fbcdbf36e88acdec048cc0cb6a3ccf67133fafbee9b103f20fe984a6`、BDY-10 `dd4e7a44fbf7801b34bb0b443cc502e304e3d9e5e9de70a91d807522ab8f1c5e`、BDY-11 `cbefeaf1b64366bfb49316e7bbe584a1aa2798b6ed42b6ed9148b11e47c69239`、BDY-12 `71b499f799e5aa1ec391fbe86db779c5f019e98d002cbabeedd1eb812a0b9757`、BDY-13 `f8fe56b6ea2902cf4becea1ea3d664e19240420d8db8e6531fb245192d3c1a3f`、BDY-14 `0e2a904e7d0a5ce580fa75cd3c21449aa959b59a2e8e4c1985b663d9c10fd0aa`。生成は各1回のみ（BDY-01 は初回 v1 を草花の庭の色契約違反で却下し作り直した v2、BDY-10〜14 も v2。いずれも採用は kako-jun の目視、一覧を見て10枚とも『よい』）。

逐語の来歴:
- 2段階生成（簡素な背景→装飾）は廃止し、**装飾込み1回生成（様式参照なし・参照2枚）**にした。
- **マンネリ回避**: MAPごとに装飾計画を変えた。計画は [decoration-plan.md](20261022-body-maps-adoption-prompts/decoration-plan.md)（主役モチーフ族・配置パターン・地形の色味・縁取り毛糸・机の木目などをMAPごとに割り付け、隣接MAPの被りを機械検査）。
- **人体関連の新プール**: 花・雲を廃止し、骨・細胞・筋肉の糸・鼓動線・皮膚・ばんそうこう・毛・ばい菌などの人体に関係する抽象的な工作物にした。BDY-01 の初回が草花の庭で色契約違反（装飾の色域外 9.0%）だったための作り直し。
- **チェッカー較正**: 床色を画像から推定、床IoUを `body_floor_overlay.py` と共通化、赤紙は『模型の中の枚数』と『模型の外の赤』に分離、『装飾の色域』を追加（SKILL.md のチェッカー節）。

既知の逸脱（kako-jun が目視で許容して採用）: 赤い紙片が5枚（05・08・10〜14。06・01は6枚）、BDY-05 の遠近のある斜め上からの構図、BDY-01 の角の毛の房、BDY-11 のちぎり絵風の質感、土台縁の欠け（05・11・12・14など）、模型外の赤（08・13・14）、BDY-07 のチェッカー床色推定の失敗（実画像は帯が期待位置）。

BDY-02・09 は新プールで作り直す予定。

### 部屋・迷路の4枚（BDY-04・15・16・17）の追記（2026-10-22）

これで**体内17枚（BDY-01〜17）の基準状態が全て揃った**。採用表は BDY-02（個別記録 [20261022-bdy02-adoption.md](20261022-bdy02-adoption.md)）を除く16行で、BDY-02 と合わせて17枚。

元PNG（変換前に照合）の sha256: BDY-04 `ebf4d9846775b659ba0c90a8ab77aebaca7b740ad3d6881dca7bdefc240c1550`、BDY-15 `1ebe8ce0c971257e3294a8320274e68f35c2f02df0e917ad690fcc4f67513870`、BDY-16 `35d8f3b9ae5aa6c0577095459f2d864f6c0d0acd0df8b9e8b78965ca8d99490a`、BDY-17 `0114bc4b354e3045fbdbb24131debb087d47068609a5011063ba878a68483d13`（いずれも1672×941）。生成は各1回（様式参照なし・参照2枚・装飾込み）。採用は kako-jun の目視『よい』（2026-10-22）。

経緯:
- 部屋・迷路の4MAPは、ビルダー `build_body_prompt.py` を専用の本文（`build_prompt_rooms`）に拡張して対応した。形は kako-jun の決定（脳=迷路、胃=分岐なしJ字の1袋、心臓=2x2の丸い4部屋の環、肺=案A=外周の環・行き止まりなし）とモック承認に基づく。
- 独立レビューは2回（opus）。迷路は生成1回目で成功し、BDY-04 のみに許可していた再生成（最大2回）は使わなかった。
- 胃のモックは kako-jun の指摘で、分岐ありの形から**分岐なしのJ字の1袋**へ作り直した（台帳の行もそれに更新）。
- 送信文の版: BDY-04 は現行 prompts/ と同一。BDY-15・16・17 は**生成時の旧版**（独立レビュー指摘の反映前）を保存した。現行 `verification/body-layout/prompts/BDY-15/16/17-prompt-send.txt` はその後の修正版で、採用画像の生成には使っていない。

既知の逸脱（kako-jun が目視で許容して採用）: 心臓・肺は部屋の丸みが通路幅に対し小さく、骨のような形に見える（承認モックの部屋半径160・通路230pxの結果）。胃は鳥の首のようにも見え、装飾が疎。机の薄い木目でチェッカーが机・縁取り・床を誤判定する（15・16・17。画像側の問題ではない）。模型外（机の上）の落とし物（16=毛糸の「8」の字と玉、17=毛糸の束と玉）。迷路は内側の壁面の装飾が少ない。いずれも mask・links・red-team 未通過で runtime へは切り替えない。
