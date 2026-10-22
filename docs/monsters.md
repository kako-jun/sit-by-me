# モンスター台帳

どのモンスターが、どこに出て、属性が何か、を管理する正本（2026-10-14 kako-jun 指示で開始）。

**運用ルール**: 新しい敵・召喚獣・中ボス・ラスボスを決めたら、同じ変更でこの表を更新する。**記録に書いていないことは決めない**。属性・弱点・出現場所が決まっていないものは「未定」と書く。決まったら根拠（Issue 番号・日付）を添えて埋める。

出典は、`art-direction.md`（イマジナリー敵の棚）、`systems.md`、`story.md`、`decisions.md`、Issue #1 #12 #17 #18 #20 #25 #26。

## 1. 管理項目の定義

| 項目 | 内容 |
|---|---|
| ID | `M` + 通し番号。欠番は詰めない。召喚獣は `S`。**案（決定ではない）: 魔法「かくぶんれつ」「かくゆうごう」〔ID±1。魔法の1つ・ラーニング。systems.md〕を採るなら、ID の隣り合う敵が「原子番号の隣」として意味を持つので、通し番号の並びを設計する必要がある（kako-jun 2026-10-21）。** |
| 名前 | 記録上の呼び名。名前が決まっていないものは棚の名前（例: 「釘」）を仮に使う。 |
| 分類 | Issue #12 / `art-direction.md` のイマジナリー敵の棚。物語上の敵は「物語の敵」「召喚獣」。 |
| 出る場所 | 章・人生の時代、フィールド、ダンジョン。記録に無ければ「未定」。 |
| 属性 | 火・水・氷・風・土・雷・聖。記録に無ければ「未定」。 |
| 弱点・耐性 | 記録に無ければ「未定」。 |
| 役割 | ラスボス / 中ボス / 雑魚 / 環境敵（背景と連動するギミック）。記録に無ければ「未定」。**呼称の決定（kako-jun 2026-10-15）: ラスボス以外のボスは、すべて「中ボス」と呼ぶ。1つのダンジョンに中ボスが2人いてもよい。** ラスボスは M004・M005（M004→M005 は一続きの最終形）・M006 だけ。**個性方針（決定 kako-jun 2026-10-15）: ボスはどれも個性豊かにする。FF5 の次元城のように、ボスごとに得意な攻撃も属性もバラバラにする（かぶらせない）。理由はボスラッシュが「これまでの集大成」だから。一覧は docs/enemy-allocation.md §5。** |
| 絵の状態 | `assets/images/enemies/` などの実ファイル名 / 未生成 / 仕様のみ。 |
| ドロップ | 倒したときに落とすアイテム。お金は別（decisions.md: お金は敵を倒すと落ちる）。記録に無ければ「未定」。 |
| ぬすむ（通常枠） | ぬすんで得られるアイテムの通常枠。FF 同様、敵ごとに持つ（2026-10-14 kako-jun）。記録に無ければ「未定」。 |
| ぬすむ（レア枠） | ぬすんで得られるアイテムのレア枠。通常枠とは別に持つ（同上）。記録に無ければ「未定」。 |
| 根拠 | Issue 番号、docs のファイル名。 |
| サイズ区分 | 戦闘画面での敵の大きさ。セルの幅×高さで表す（FF 同様。2026-10-14 kako-jun）: 1x1=普通 / 2x1=横2倍 / 1x2=縦2倍 / 2x2=縦横2倍。それ以上も可。敵のサイズは1種類にしない。記録に無ければ「未定（既定は1x1）」。 |

ドロップ・ぬすむ（通常枠）・ぬすむ（レア枠）の3項目は、台帳の表が横に長くなるため、3-6 の別表『戦利品』に ID で対応させて置く。サイズ区分も同様に、3-7 の別表『サイズ区分』に ID で対応させて置く。

## 2. 属性体系の要約（新しく決めない。既存の決定の引用）

- 属性は **火・水・氷・風・土・雷** の6つ。FF5／6時代の直感的な体系を基準にする。FF6の体系にある**聖**は、6属性の外にある隠しの召喚獣（イマジナリー鼓門）だけが建前上持つ（decisions.md、2026-10-14）。
- 各属性の魔法は**一つだけ**（下位・中位・上位の重複を作らない）。各属性の召喚獣は**一体だけ**。ゾンビ／かっぱは属性・魔法・召喚獣のカテゴリに入れない（systems.md、#17、#18）。（基本完成までの一時措置。2026-10-20、decisions.md 287行参照）
- 魔法は敵の技を受けて戦闘終了時にラーニングして得る。魔法名は敵の技名で、確定済み: 火=ひあそび、水=ずぶぬれ、氷=とうしょう、風=ざくざく、土=どろだらけ、雷=かんでん。回復は「いたいのいたいのとんでいけ」（systems.md、#26）。どの敵がどの技を使うか: 土=M101・M102・M108、雷=M151 は決定（2026-10-15）。**それ以外は未決**。
- 武器に属性は置かない。属性は魔法・召喚獣・防具が担う。防具は属性防御のみ。威の色との対応案: 火=赤、水=藍・紺、氷=白、風=緑、土=黄・茶、雷=紫（案。systems.md）。
- 敵は「明らかに怖い物」だけ。属性の穴を埋めるときも、恐怖の根拠がある物だけを採る（雪だるま・ドライヤー・提灯は不採用。art-direction.md）。
- 通常敵・中ボスは、弱点を突く一解にせず、複数の勝ち筋と観察できる予兆を持たせる（systems.md、#15）。
- 竜のモチーフを使う召喚獣・敵は、最後の**雷竜**だけに限定する（systems.md、story.md）。（**決定 2026-10-15 kako-jun**: 龍と竜は別。この制限は「竜」の字の話で、匿龍（龍）は対象外。decisions.md 末尾）
- 二周目のみ明記されている相性: 雷の使い手の子供が水に特攻（decisions.md）。
- **属性の穴（解消。2026-10-15 kako-jun 決定）**: 土（どろだらけ）のラーニング元＝ロードローラー M101・大型ドリル M102・蓋の開いたマンホール M108。雷（かんでん）のラーニング元＝たこ足配線 M151。敵自身の属性と敵が使う技の属性は別（M151 の敵属性は火のまま）。技の効果・ダメージ・他にどの敵が持つかは未決（docs/enemy-allocation.md §2.2・§4。3-3 の末尾にも注記）。

## 3. 台帳

### 3-1. 物語の敵・中ボス・ラスボス

| ID | 名前 | 分類 | 出る場所 | 属性 | 弱点・耐性 | 役割 | 絵の状態 | 根拠 |
|---|---|---|---|---|---|---|---|---|
| M001 | 段ボールのドラゴン | 劇用の手作り物 | 幼稚園編・冒頭のお遊戯会の劇（舞台） | 未定 | 未定 | 冒頭の戦闘相手。**脚本固定の特別戦闘。HP は極めて高い（数値は未決。kako-jun 2026-10-15）。味方は最強クラスの魔法・アビリティを固定付与で撃つ。勝敗は付かず、地震で中断**（decisions.md）。旧記述「劇は無事に終わる」は訂正済み（decisions.md）。中ボスか雑魚かの区分は未定。美術: 幼稚園児が自分で作った段ボールの竜。オレンジ色の段ボールを下地にし、胴・翼・尾を含む全身へ黄色いクレヨンを粗くジグザグに走らせる。塗りは丁寧な面塗りにせず、クレヨンの蝋の粒と塗りはみ出しを見せる。その線が見る人には雷を連想させるが、子供は意図していない。段ボールの角も稲妻状のジグザグにし、翼と自立用の4本足を持つ。色と黄色線の配置がS006に偶然似るが、S006を見て模倣したのではない。**技名: ペトロザヴォーツク、ヘスダーレン（雷竜S006/M005と同じ。kako-jun 2026-10-22。記録上の読み。2つとも使うか／どちらか／別の技も持つかは保留=今は決めない。効果・属性・演出・使用形態・使う数は保留=今は決めない。kako-jun「具体的にはいまはきめない」）**。劇の中ではドラゴンも味方4人（最強級をイマジナリーゆえに使う）も「子供の想像」の最強同士、という読み（案） | `assets/images/enemies/M001.webp`（採用、1337×1177 WebP quality85・alpha保持。kako-jun目視採用 2026-10-21） | #1、story.md、assets-policy.md、#141 |
| M002 | 不良（集団） | 物語の敵 | 少年編前半（小学生）。近所の冒険で絡まれて戦う | 未定 | 未定 | 未定 | 仕様のみ（敵として戦う記述のみ。「人間を敵にしない」原則との整合は未整理） | story.md |
| M003 | 匿龍・トクリュウ組織の龍の共通意匠（非遭遇ID） | 意匠族の管理 | 海外左右塔のM015/M016へ統合（#71） | 未定 | 未定 | 中華系・双頭の龍の組織シンボル。独立した第三ボス・空中通路龍戦を置かない。頭数の具体図TBD | 仕様のみ。既存資料は意匠参考で新ボス採用画像ではない | #71、story.md |
| M004 | 日本海寒帯気団収束体（ラスボス・一周目） | 物語の敵 / 召喚獣 | 壮年編・一周目の最終ダンジョン（兼六園・金沢城、最終夜のイマジナリー天守閣。ラストダンジョンはボスラッシュで、ラスボスはその先） | 雷 | 未定 | ラスボス。雲核を持つ気象現象。雲核を断つと M005 が現れる | S006の同一存在。雲の姿 `assets/images/summons/S006-cloud.webp` を含む四段階の採用画像は S006 行に記録 | #14、#20、story.md、systems.md、#141 |
| M005 | 雷竜 | 物語の敵 | M004 の雲核を断った後の最後のターゲット | 雷（M004 の雷の召喚獣として） | 未定 | ラスボス最終形。雲核の先に現れる雷。顔は雲と雷に浮くドクロ | S006の同一存在。雷竜の姿 `assets/images/summons/S006-full.webp` を含む四段階の採用画像は S006 行に記録 | story.md、systems.md、#141 |
| M006 | 顔の見えない巨人（主人公夫婦の2体同時出現） | 物語の敵 | 二周目の終盤・金沢駅の鼓門前（ホームではない。中ボスなし、ラスボスの M006 のみ。決定 2026-10-15） | 火と水の召喚獣を使い、全属性を駆使する | 雷の使い手の子供が水に特攻。「火に対する弱点を誰が突くか」は未決（#25） | ラスボス（二周目）。夫婦2体が同時出現。各2x2。C001オトン／C002ナムそれぞれ立ち姿・車椅子姿の4形態。子供視点のイマジナリーな恐怖像として、頭を極端に小さく、手のひら・背中を大きくし、顔を影で隠す。露出の多い衣装でオトンは筋肉、ナムは女性性を強調し、ナムは母の象徴として表す（kako-jun 2026-10-22）。阿形・吽形のような対のポーズを取り、オトンは開いた掌を前へ出し、ナムは動きのある官能的な守りの構えを取る。車椅子姿は脚を布で覆い、断端・足先を見せない（kako-jun 2026-10-22）。採用: `assets/images/enemies/M006-otton-standing.webp` / `M006-otton-wheelchair.webp` / `M006-nam-standing.webp` / `M006-nam-wheelchair.webp`（全て1254×1254、WebP品質85・alpha保持、kako-jun目視採用 2026-10-22） | decisions.md、systems.md、#25 |
| M007 | 一周目のビジョン（お金・戦争・地震など） | 物語の敵 | 二周目ラスボス戦で攻撃として使う。一周目での出現場所は未定 | 未定 | 未定 | M006 戦の攻撃群 | 仕様のみ | systems.md |
| M008 | シャチホコ | 物語の敵（イマジナリー） | 少年編前半・卯辰山のサニーランド屋外SNL-06シャチホコ（#14追加口述、docs/enemy-allocation.md §1.3） | 未定 | 未定 | サニーランドの中ボス（想像の刃の第一段階の初使用。kako-jun 2026-10-15。呼称は「中ボス」で確定。地面の予兆(AoE)・強制前後衛交代あり＝boss-gimmicks.md G020、#122）。白いコンクリート像で毛など全体の造形がくるくると丸い印象。実物は高さ5m以上（kako-jun 2026-10-20） | 採用: `assets/images/enemies/M008.webp`（1024×1536、WebP品質85・透過、kako-jun目視採用 2026-10-20） | 主人公の不安のイマジナリーが、サニーランドにあった大きな白いコンクリートのシャチホコ像を怖く見せた姿。SaGa2 のオマージュ。decisions.md、story.md、timeline.md、docs/enemy-allocation.md §1.3・§2.3 |
| M009 | エラー細胞 | 物語の敵（体内） | 体内ダンジョン・胃（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.6） | 未定 | 未定 | イベントバトル。逃走し倒せない（逃したことが将来の不治の病になる） | 採用: `assets/images/enemies/M009.webp`（元画像 `exec-eeab27c6-666d-4be4-852a-bb5bbd05b70e.png`、1254×1254・1x1。kako-jun 2026-10-21 全部採用）。[生成前契約](reviews/artifact-redteam/20261021-M009-contract-prompt.md)・[画像レビュー](reviews/artifact-redteam/20261021-M009-raw-image-eeab27c6.md)（32×31px、中央・透過・pass）。初回の星状発光版は置換 | 1ドットくらいの小さな、FF5 のムーバーのような敵。story.md 302・303行、decisions.md、docs/enemy-allocation.md §1.6 |
| M010 | オミクロン株（体内・胃の盾役の中ボス。名前は kako-jun 2026-10-15 に決定。実在の病原体名は固有名として使い、特定の患者・実在の被害・集団を揶揄しない） | 物語の敵（体内） | 体内ダンジョン・胃（M009 と同じ戦闘）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.6） | 未定 | 未定 | 中ボス（胃でエラー細胞を守る大きな盾役）。体内の「部位ごとの中ボス」の1つ（胃担当）。体内の中ボスは新型コロナの各株名（decisions.md 末尾） | 採用: `assets/images/enemies/M010.webp`（1536×1024、WebP品質85・alpha保持、kako-jun目視採用 2026-10-20） | story.md 303行、docs/enemy-allocation.md §1.6 |
| M011 | 脳の防御反応（**非遭遇ID。脳のエリアの舞台設定・演出。戦う相手は M012 だけ**（kako-jun 2026-10-19、#125）。決定前の記述: 頭＝脳の中ボス。名前未定。内心を知られたくない防御反応としての脳。脳の中の本心を守る像で、具体の姿・技は決めない。株名との関係は要確認） | 物語の敵（体内） | 体内ダンジョン・頭（脳）（kako-jun 決定 2026-10-15、decisions.md 末尾、docs/enemy-allocation.md §1.6） | 未定 | 未定 | 非遭遇（戦闘の相手ではない。中ボスから外す（kako-jun 2026-10-19、#125））。脳のエリアの舞台設定・演出。決定前の記述: 部位ごとの中ボスの1つ（頭担当）。「脳で幼馴染が主人公をどう思っていたかを知る」見せ場の関門 | 未生成（仕様のみ） | decisions.md 84行付近・末尾 |
| M012 | マクロファージ（免疫細胞。体内では主人公が「異物」なので攻撃してくる。株名との関係は要確認。案あり: boss-gimmicks.md G021(#125)） | 物語の敵（体内） | 体内ダンジョン・**頭（脳）のエリア**（kako-jun 2026-10-19、#125）（当初 2026-10-15 は部位未定。decisions.md 末尾、docs/enemy-allocation.md §1.6） | 未定 | 未定 | 中ボス（部位ごとの中ボスの1つ。**担当部位は頭（脳）のエリア**（kako-jun 2026-10-19、#125）。顕微鏡写真のような不定形の細胞から粘る長い突起を伸ばし、白血球らしいイマジナリーなパーツを持つ（kako-jun 2026-10-20） | 採用: `assets/images/enemies/M012.webp`（1297×1212、WebP品質85・alpha保持、kako-jun目視採用 2026-10-20） | decisions.md 末尾、story.md 303行 |
| （手足の中ボス） | 右手・左手・右足・左足の4部位の中ボス（アルファ・ベータ・ガンマ・デルタの4株＝M018〜M021。胃のオミクロン株M010とは別。部位と株の対応は未決。kako-jun 2026-10-20） | 物語の敵（体内） | 体内ダンジョン・右手／左手／右足／左足 | 未定 | 未定 | 中ボス（部位ごとの中ボスの各1）。各株の戦闘枠は2x2。5株は共通の系列とし、色と周囲の形を変えて個性を持たせる。丸・三角・四角などは架空の造形。マクロファージM012や他の病原体とは形を区別する（kako-jun 2026-10-20）。M012は別の脳の中ボス | 未定（仕様のみ） | decisions.md 末尾 |
| M013 | 石川橋の強大な敵（名前未定。FF5 のツインタニアのような強敵のオマージュ。ゲーム内の名前にしない） | 物語の敵（中ボスの扱い） | 壮年編・一周目最終、兼六園から金沢城へ渡る石川橋（ボスラッシュの中の見せ場。kako-jun 2026-10-15） | 未定 | 未定 | 中ボスの扱い（ラスボスは M004/M005/M006 のまま）。カウントダウン（boss-gimmicks.md G022、#129）。姿・技・強さは未決 | 未生成（仕様のみ） | decisions.md 末尾、docs/enemy-allocation.md §1.8 |
| M014 | 金沢城の三闘神のような敵（名前未定。FF6 の三闘神のオマージュ。3体はそれぞれ独立したボス。戦闘では三体が一組になる。構成体は3（WW1・WW2・WW3の戦争の擬人化で、三毒＝貪・瞋・痴。kako-jun 決定 2026-10-19、#123）。ゲーム内の名前にしない） | 物語の敵（中ボスの扱い） | 壮年編・一周目最終、金沢城（ラスボス M004/M005 の前段。kako-jun 2026-10-15） | 未定 | 未定 | 中ボスの扱い。護衛敵 M202〜M205（雑魚）とは別物（決定 2026-10-15）。子ども3人（ハク・ハツ・チュン）との因縁（三毒。割り当ては未決、#123、docs/boss-gimmicks.md P016）。**WW1・WW2・WW3の戦争の擬人化（kako-jun 2026-10-22）**。WW1はガスマスク・複葉戦闘機・毒ガスをまとい低く身構える。WW2は爆撃機・戦車の意匠を持つ女神で片足を上げて舞う。WW3は核ミサイル・無人機・電子戦をまとい空中で身をひねる。三毒との対応は未決。国旗や実在軍の徽章は使わない。戦闘順は M014 → ノストラダムラー（ID 案 M022）→ ラスボス M004/M005 | 採用: WW1 `assets/images/enemies/M014-WW1.webp`（元 `exec-201c7f0a-bcfb-4c26-814d-66f9e1c69b4b.png`、1254×1254）、WW2 `assets/images/enemies/M014-WW2.webp`（元 `exec-dc99dd4c-57e2-440c-bfe2-9c0fe1b201bb.png`、1222×1287、女神・片足を上げた舞う姿）、WW3 `assets/images/enemies/M014-WW3.webp`（元 `exec-57b8e8fc-ba2e-4a55-a4f9-33dd2cb032fa.png`、1254×1254）。kako-jun 採用 2026-10-22 | decisions.md 末尾、docs/enemy-allocation.md §1.8 |
| M022（ID は案・未決。空き番号は M022。M015〜M021 は使用済み） | ノストラダムラー（読みは記録上の読み。kako-jun 原文は「ノストラダムラー」）。モデルはノストラダムス。「人間であり、肖像画自体から上半身だけ飛び出している」（kako-jun 逐語）。**人間の姿のまま。絵の中に二人目を残さず、人物は一人だけ**。**実在の肖像画をモデルにする決定済み例外**。「人間を敵にしない」「実在の人物・氏名を使わない」方針に対する例外は維持する。候補はセザール・ド・ノートルダム作とされる約1614年の肖像を暫定参照。肖像画の中央から上半身が出て、人物は右を向き目線も右。肖像画は古びた金箔と彫刻装飾のある縦長・左右対称のルネサンス額縁。走らず、片手の人差し指を上げて煽り、もう片手を差し出す。技「だいよげん」**効果（kako-jun 決定 2026-10-22 逐語「だいよげんはランダムで地球が滅ぶような現象を起こす。主に隕石の衝突（**取り消し**: kako-jun 2026-10-22「だいよげんの「主に隕石」はいらない」。だいよげんに隕石は含めず隕石以外の現象〔具体は未決〕。隕石は恐怖の大王が毎回使う技のみ。旧文は残す）」）: ランダムで地球が滅ぶような現象を起こす。主に隕石の衝突（**取り消し**: kako-jun 2026-10-22「だいよげんの「主に隕石」はいらない」。だいよげんに隕石は含めず隕石以外の現象〔具体は未決〕。隕石は恐怖の大王が毎回使う技のみ。旧文は残す）**。ダメージ・対象・確率・隕石以外の現象の種類は未決、「ランダム」が毎ターン抽選か複数の現象から 1 つを選ぶかも未確認（要確認）。隕石は架空の天体現象とし、実在の災害・事件を想起させない。「運命が敵なので」（逐語）は story.md の運命の像（M004 日本海寒帯気団収束体）の主題に連なる、という記録上の読み。サイズ2x1を決定。左の縦長肖像画の中央から上半身だけが出る。属性・弱点は未定 | 物語の敵（中ボスの扱い） | 壮年編・一周目最終、金沢城。**M014（三闘神級）の後、天守のラスボス M004/M005 の直前**に戦うボス戦（三闘神の1つではなく別のボス。kako-jun 訂正 2026-10-22）。雑魚 8種に含めない | 未定 | 未定 | 中ボスの扱い。護衛敵 M202〜M209（雑魚）とも M014 とも別物 | 採用: `assets/images/enemies/M022.webp`（元 `exec-b7e6f9a7-8335-475c-a87e-697a7647cab1.png`、1122×1402、縦長の対称金色額縁の中央から出る右向き上半身。kako-jun採用 2026-10-22） | #123、docs/dungeon-enemies.md、docs/boss-gimmicks.md |
| M023（ID は案・未決。M022 とは別の空き番号） | 恐怖の大王（読みは記録上の読み。原文は「恐怖の大王」）。外見は「火星に凶悪な顔がついたような」（逐語。凶悪な顔の具体は未決）。ノストラダムラー（M022 案）とは別の敵。役割は盾役にもする（逐語）。ノストラダムラーと同じ戦闘に 2 体が並ぶ（kako-jun 決定。召喚獣ではない）。ノストラダムラーの前の位置に並ぶ盾役と読む（要確認）。天体の像（人間でない）。**隕石を降らすのは恐怖の大王（kako-jun 決定 2026-10-22「恐怖の大王が隕石を降らすのだ」）**。盾役＋隕石を降らす攻撃役の二面性。隕石は恐怖の大王が毎回使う（決定。だいよげんとは別。読みを訂正）。だいよげんとの重複・毎回の意味・ダメージは要確認。サイズ2x2を決定。属性・弱点は未定 | 物語の敵（中ボスの扱い） | 壮年編・一周目最終、金沢城。ノストラダムラー戦（M014 の後・ラスボス直前） | 未定 | 未定 | 中ボスの扱い（M022 と同じ戦闘に 2 体が並ぶ。決定）。盾役の読み・G014・P012・G020 は候補として参照のみ | 採用: `assets/images/enemies/M023.webp`（元画像 `exec-415a9ca6-2f35-44f3-982e-3fc44a0f8159.png`、1312×1199。火星のような悪相の天体、隕石、右向き。kako-jun 2026-10-22採用） | #123、docs/dungeon-enemies.md、docs/boss-gimmicks.md |
| M015 | 匿龍・左塔ボス（固有名TBD。**案: 『すべてをFFにするもの』という名前の魔術師**、kako-jun 2026-10-21。boss-gimmicks.md G027） | 物語の敵 | 青年後半・左塔5階OVS-09 | 魔法のみ有効 | 未定 | M003共通意匠の戦闘個体。順序自由、右はM016。双頭意匠の具体図TBD。**G027 の案（魔術師・数字を FF にする）と M003 の双頭意匠との関係は未決** | 未生成・設計枠 | #71 |
| M016 | 匿龍・右塔ボス（固有名TBD） | 物語の敵 | 青年後半・右塔5階OVS-14 | アビリティのみ有効 | 未定 | M003共通意匠の戦闘個体。順序自由、左はM015。双頭意匠の具体図TBD | 未生成・設計枠 | #71 |
| M017 | 荒波の触手 | 物語の敵（体内） | 体内ダンジョン・心臓。水の召喚獣S001の合体前 | 水（波そのもの。kako-jun 2026-10-21） | 未定 | 雑魚敵。葛飾北斎の浮世絵の波のように、触手のような先端へ伸びる白い荒波。各個体に足と中央があり、複数体が集まってS001となる | 生成済み・採用: `assets/images/enemies/M017.webp`（kako-jun承認 2026-10-19） | #130 |
| M018 | アルファ株 | 物語の敵（体内） | 右手・左手・右足・左足のいずれか（未割当） | 未定 | 未定 | コロナ変異株の中ボス。M010と同系列、青色で明瞭な三角形の突起 | 採用: `assets/images/enemies/M018.webp`（1536×1024、WebP品質85・alpha保持、作り直しをkako-jun目視採用 2026-10-20）。旧画像の別名保存は不要（kako-jun 2026-10-20） | 2026-10-20 kako-jun |
| M019 | ベータ株 | 物語の敵（体内） | 右手・左手・右足・左足のいずれか（未割当） | 未定 | 未定 | コロナ変異株の中ボス。M010と同系列、紫色で丸みのある四角形の突起 | 採用: `assets/images/enemies/M019.webp`（1536×1024、WebP品質85・alpha保持、作り直しをkako-jun目視採用 2026-10-20） | 2026-10-20 kako-jun |
| M020 | ガンマ株 | 物語の敵（体内） | 右手・左手・右足・左足のいずれか（未割当） | 未定 | 未定 | コロナ変異株の中ボス。M010と同系列、金色で星形の突起 | 採用: `assets/images/enemies/M020.webp`（1536×1024、WebP品質85・alpha保持、kako-jun目視採用 2026-10-20） | 2026-10-20 kako-jun |
| M021 | デルタ株 | 物語の敵（体内） | 右手・左手・右足・左足のいずれか（未割当） | 未定 | 未定 | コロナ変異株の中ボス。M010と同系列、緑色で先が分かれた突起 | 採用: `assets/images/enemies/M021.webp`（1536×1024、WebP品質85・alpha保持、kako-jun目視採用 2026-10-20） | 2026-10-20 kako-jun |
| （ID未割当・要確認） | 4階の鏡（ボス扱い。ID・ギミック・強さは要確認 #87） | 物語の敵 | デパート4階KRB-05（隠し階。映った自分たち自身。技「ものまね」。兼六園には出ない。kako-jun決定 2026-10-19） | 未定 | 未定 | 未定 | 未着手 | #87 |
| （ID未割当・案） | **カッペ**（名前は kako-jun 案。因縁の敵） | 物語の敵（因縁の敵。FF のギルガメッシュやオルトロスのように、何度も立ちはだかる敵という位置づけ） | 未定 | 未定 | 未定 | **技（案。kako-jun 2026-10-21）: 「さんしむらまつり」と「かんなかんな」**。マンガ『マテリアル・パズル』の敵「ジールボーイ」が使う技へのオマージュ（kako-jun の説明。出典の一次情報は未確認）。技名は和語・ひらがな中心の方針に沿っている。**技の効果・属性・威力・どちらが先に出るか・ラーニング可否〔敵の技名はそのまま魔法名になる規則〕は未決**。出現回数・場所・時期・強さ・姿・役割〔中ボスか雑魚の扱いか〕・負けたときの扱いも未決 | 未着手 | kako-jun 2026-10-21（案）。状態「カッペ」と同名: boss-gimmicks.md G028 |

M010の造形（kako-jun採用 2026-10-20）: 胃の盾役を踏まえ、幅広く扁平なウイルスの本体にコロナ状の短い突起を備え、長い触手を持たない。既存M132の緑紫の球体と長い触手のシルエットとは区別する。残り4株は同じ系列と分かる共通性を維持しつつ、色と周囲の形に個性を持たせる。各株の色・形は上記の採用画像を参照。

体内の通常敵の方向（kako-jun 2026-10-20）: コロナ変異株の中ボスとは別に、体内にある身近な「悪いもの」や病原体を題材にする。例は「あくだまこれすてろーる」と「ほんこんえーがた」。後者は既存のstory.mdの「インフルエンザのA香港型」と対応する候補。LDLコレステロールは病原菌ではなく、インフルエンザも誰の体内にも常在するものではないため、体内の敵は現実をそのまま再現したものではなくイマジナリーな表現とする。両者の個別ID・サイズ・出現部位・姿は未決。病名・株名は既存方針どおり専門家確認を受ける。

コロナ変異株以外の体内のイマジナリーは、目を付けたり、漫画のようなバイキンの形にしたりしてよい（kako-jun 2026-10-20）。例: 頭マップだけに虫歯の悪魔のような敵を出す。例の採否・個別ID・サイズ・姿の詳細は未決。

### 3-2. 召喚獣（元は敵素材。右向きマスターを作り、味方として呼ぶときは描画側で左右反転）

魔石の装備・属性付与は systems.md「召喚獣と魔石」と #134 を参照（要確認あり）。

| ID | 名前 | 出る場所（取得・登場） | 属性 | 敵として戦うか | 絵の状態 | 根拠 |
|---|---|---|---|---|---|---|
| S001 | 日本海の召喚獣 | 幼稚園編の能登・日本海（水難事故）。能登の釣り場（被災前・被災後）の負けイベント。体内ダンジョン・心臓では「水の精霊」として現れ、心臓を止めようとする中ボス戦を行う（同一の存在のため新規IDは作らない。kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.5・§1.6、story.md 302行） | 水 | 敵になる（事故）。**心臓の戦い（体内）でのみ合体（G011、#130）。能登の負けイベントでは使わない**。画像は3枚構成: (1) 合体前の別ID M017「荒波の触手」複数体、(2) 合体直後・正体を見せる前の中央核（丸い黒〜濃藍の塊と発光する目だけを見せ、顔は波の内側に隠す。周囲の波の触手は描かず、M017を別敵として表示する。採用: `assets/images/summons/S001-core.webp`、kako-jun承認 2026-10-19）、(3) 正体を表した巨大な黒いアンモナイト型の本体（渦巻き殻と荒波の渦がつながり、波の触手の隙間から黒い顔を少し見せ、目を光らせる。kako-jun採用 2026-10-20）。(2)(3)とも蛸の姿にしない。ただの波にしない。(3)では中央から葛飾北斎の浮世絵の波のような白い波の触手が四方八方へ伸び、周囲には波の花の白い泡が舞う | 画像(1) M017採用済み、画像(2) `assets/images/summons/S001-core.webp`採用済み、画像(3) `assets/images/summons/S001.webp`採用済み（黒いアンモナイト型、1254×1254 WebP・品質85・透過。kako-jun目視採用 2026-10-20） | story.md、systems.md、#130 |
| S002 | 卯辰山の召喚獣 | 少年編前半・卯辰山の山のダンジョンの中ボス（山中。場所は山の続きの絵のどこか、後で）（kako-jun 2026-10-15、decisions.md） | 氷（遭難しそうな冬の森。複数の木々が集まって長老の木のような巨大な年寄りの顔を1つ浮かべる、不気味な姿。瞳はない。雪山も背景にあってよい。kako-jun 2026-10-20。「顔なし」は訂正） | **中ボスとして戦う（取得は戦いを通る）**。のち味方 | 採用: `assets/images/summons/S002.webp`（1536×1024、WebP品質85・alpha保持、kako-jun目視採用 2026-10-20）。旧案は差し替え | systems.md、art-direction.md |
| S003 | 内灘の風の召喚獣（名前は未定） | 少年編後半・内灘（砂浜〜松林道）。**中ボス戦であることは確定（kako-jun 2026-10-15）。戦闘の中身は案（story.md 315行付近）**。砂丘。砲弾の欠片の気配が混ざる殺意の強風。土の要素を入れない。風そのものの鳥形と、砲弾のように尖る風に変身する | 風 | **中ボスとして戦う（取得は勝つこと）**。変身タイプ（G011、#127）。鳥形（嘴状に尖る螺旋の気流＝鳥を暗示する風）と砲弾型（尖った風）の2形態。FF4のバルバリシアのオマージュ（kako-jun 2026-10-20）。取得後は味方 | 2形態採用: 砲弾型 `assets/images/summons/S003.webp`、鳥形 `assets/images/summons/S003-bird.webp`（ともに1548×1016、WebP品質85・alpha保持、kako-jun目視採用 2026-10-20） | art-direction.md、#26、#127 |
| S004 | 火の召喚獣（旧称「川から来た火の召喚獣」） | 中3の火事（寺の台所・庫裏。寺町）。虎（旧ネコ型。2026-10-19 決定、#80。四つん這いで足は車輪のまま。竜に対抗。かわいい版とリアル版の2種。かわいい版はフィールド専用（マスコット・会話・主人公の横）、戦闘に出るのはリアル版のみ。決定 kako-jun 2026-10-19、#80。基本は炎の赤、顔の模様は青い高温の炎）・会話できる・マスコット。**取得は中3の火事の戦いで確定（kako-jun 2026-10-15。先の「青年編前に川から」「体内編で得る」を置き換え。decisions.md）。虎の由来は決定済み（下記）**。虎の由来は、幼馴染と川（手取川）で拾った化石（魔石の出どころの既存決定＝幼馴染の部屋にあった、2人で川でとった化石。割っていない・中身不明、と同じもの）。中身は作中でも不明のままで、おそらくサーベルタイガー、白山火山帯から手取川で流れてきたものの欠片かもしれない（推測。断定しない。「その程度の由来でいい」で作り込まない。決定 kako-jun 2026-10-19、#80。サーベルタイガー(哺乳類)にした理由は、化石と言えば恐竜という風潮へのアンチテーゼ（竜との対比とは別の理由。2026-10-19、#80））。足の車輪・火車の連想は虎でも維持（決定 kako-jun 2026-10-19、#80） | 火 | **中ボスとして戦う（取得）**。バトルのあと平伏→大爆発。取得後は味方。二周目ラスボス戦では主人公が使う | **採用**: `assets/images/summons/S004.webp`（戦闘用リアル版、1536×1024 WebP、品質85、alpha保持。kako-jun目視採用 2026-10-19）。かわいい版はフィールド素材 | systems.md、#26、#80 |
| S005 | 土の召喚獣（名前は未定） | 青年編・海外砂漠の密集垂直都市の脱出の中ボス。九龍城砦をモチーフとする、今までいた街そのものが巨人となる（kako-jun 2026-10-20）。黒と茶色の街、窓には夜の部屋の明かり。明るい砂色は使わない | 土 | 脱出の中ボス。細身の女性を思わせるシルエット、顔の目・口は不要。変身は3段階: (1) 建物が地面に埋もれた巨人の指や頭にも見えるよう不自然に立つ街、(2) 巨人の上半身が現れ、へそから下は地中、(3) 完全に地上に出て歩き始め、前かがみで襲いかかる巨人。足元には砂埃。建物と人体の合成は造形で表す（kako-jun 2026-10-20、G011、#127） | 3形態採用: (1) `assets/images/summons/S005-city.webp`（2172×724）、(2) `assets/images/summons/S005-rising.webp`（1486×1059）、(3) `assets/images/summons/S005-full.webp`（1486×1059）。WebP品質85・alpha保持、kako-jun目視採用 2026-10-20。旧案は不要として削除（kako-jun 2026-10-20） | systems.md、#26 |
| S006 | 雷の召喚獣 | 壮年編一周目最終・金沢城。倒した後の二周目で最強の味方になる | 雷 | 一周目は敵（M004→M005と同一の存在）。四段階変身 | 4形態（第1〜第4形態採用）: (1) `S006-cloud.webp` 夜空に浮かぶ暗いが美しい灰色の積乱雲だけ（採用、1536×1024、WebP quality85・alpha保持）、(2) `S006-awakening.webp`（採用、1536×1024、WebP quality85・alpha保持）雲に深淵のようなあやふやな円形の穴ができ、その内側に宇宙が広がる。灰色の雲と穴を保ちつつ黄色が入り始める。金箔風の抽象雲形を従える、(3) `S006-lightning.webp`（採用、1536×1024、WebP quality85・alpha保持。kako-jun目視採用 2026-10-21）雲の輪郭から多方向へ飛び出す、荒く鋭いジグザグ雷が主役。複数の龍の顔をぼんやり連想させ、宇宙の気配を少し残し、色は黄色からオレンジへ移る。金箔風の抽象雲も残る、(4) `S006-full.webp`（採用、1536×1024、WebP quality85・alpha保持。kako-jun目視採用 2026-10-21）宇宙へ伸びるスプライト現象のような粒・波・塊が、頭部・首・胴体・広がる翼・長い尾をもつオレンジ色の竜の輪郭を作る。硬い実体や骨格はなく、ドクロ顔は暗い抜けと雷光で明確に見え、禍々しい。周囲の黄色い龍状雷は全方向へ放射状に伸びる。金箔風の抽象雲を従え、黄色と灰色の名残を保つ。M001の段ボールドラゴンはこの雷竜を幼稚園児が工作にした姿へ寄せ、必要なら後で描き直す。ラスボス攻撃技名: **ペトロザヴォーツク**、**ヘスダーレン**（名称のみ決定、効果・属性・演出・使用形態は未決）。M001の段ボールドラゴンも同じ技名を使う（kako-jun 2026-10-22、#1） | #141、systems.md、story.md、art-direction.md、[第1形態raw-image review](reviews/artifact-redteam/20261021-S006-stage1-raw-image.md)、[第2形態raw-image review](reviews/artifact-redteam/20261021-S006-stage2-raw-image.md) |
| S007 | イマジナリー鼓門（隠しの召喚獣） | 二周目ラストバトル（金沢駅の鼓門前）だけ。長子が使う。アレクサンダーのようにビーム | 建前上は聖。本当の属性は未定 | 味方 | 採用: assets/images/summons/S007.webp（1537×1023、WebP品質85・alpha保持。左右反転した青白い鼓門、淡い青白いオーラ。ビームは画面効果で描画。kako-jun目視採用 2026-10-22） | decisions.md、art-direction.md |
| S008 | 水の召喚獣（配偶者が化身） | 二周目ラスボス戦で、配偶者が使い、のち水の召喚獣化して子供側につく | 水 | M006 戦の一部 | S001 と同一の存在として採用済みの `assets/images/summons/S001.webp` を共有。S008のファイルは補作しない（同一画像の決定 2026-10-14、S001最終形の採用 2026-10-20 kako-jun。decisions.md） | systems.md |

### 3-3. 日常の恐怖・イマジナリー敵（#12 のカテゴリ表）

属性・弱点・役割・出る場所は、記録にある分だけ埋める。

**「出る場所」の方針（kako-jun 一任による決定 2026-10-15）**: 1つの敵は原則1つのダンジョンだけ。ダンジョン別の割り当て・理由・例外は `docs/dungeon-enemies.md` が正本。兼六園は全敵（雑魚・環境敵）が再登場する例外なので、各行には書かない。城専用雑魚 M202〜M209 は金沢城専用。台帳に単独の場所が明記されていた敵は変えていない。

| ID | 名前 | 分類 | 出る場所 | 属性 | 弱点・耐性 | 役割 | 絵の状態 | 根拠 |
|---|---|---|---|---|---|---|---|---|
| M101 | ロードローラー | 圧倒的な機械・物 | 雪国の道路（フィールド・章は未定）。寺町 wide-road（広い道路）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M101.webp`（1536×1024、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M101-contract-prompt.md)（pass、prompt stageのみ）。raw-image: [初回候補](reviews/artifact-redteam/20261021-M101-raw-image-481e4a05.md)（blocker: alpha bboxが中央80%外、余白不足）、[retry2候補](reviews/artifact-redteam/20261021-M101-raw-image-e63460aa.md)（blocker: 対象が過大、余白不足、左・下端にalpha残り）、[edit候補](reviews/artifact-redteam/20261021-M101-raw-image-87e203cc.md)（blocker: 放射状背景・ボックス外アルファ）。リトライ契約審査: [初版](reviews/artifact-redteam/20261021-M101-retry-contract-prompt.md)（major: 45°基準未定義・スケール下限なし）、[改訂版](reviews/artifact-redteam/20261021-M101-retry2-contract-prompt.md)（pass、prompt stageのみ）。edit契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M101-edit-contract-prompt.md)（pass、prompt stageのみ） | #12。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 `[特技]`。効果・ダメージは未決。属性欄・弱点は変えない） |
| M102 | 大型ドリル | 圧倒的な機械・物 | 海外 密集垂直都市（青年後半）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.7） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M102.webp`（1536×1024、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。契約審査: [初版](reviews/artifact-redteam/20261021-M102-contract-prompt.md)（major: 角度基準未定義・参照画像を除外・細部の根拠不足）、[改訂版](reviews/artifact-redteam/20261021-M102-retry-contract-prompt.md)（pass、prompt stageのみ）。raw-image: [retry候補](reviews/artifact-redteam/20261021-M102-raw-image-ab073035.md)（blocker: 面の向きが未達・未対応の第2トラック・サイズ過大と余白不足・下端alpha残り）、[edit候補](reviews/artifact-redteam/20261021-M102-raw-image-93cc91ed.md)（blocker: 放射状背景・指定ボックス外アルファ）、[背景除去候補](reviews/artifact-redteam/20261021-M102-raw-image-70c629cd.md)（blocker: 背景残存、主体ピクセル変化、既存サイズ問題）、[retry3候補](reviews/artifact-redteam/20261021-M102-raw-image-328625d6.md)（blocker: 左端の1/255 alpha漏れ）。edit契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M102-edit-contract-prompt.md)（pass、prompt stageのみ）。背景除去契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M102-bg-contract-prompt.md)（pass、背景除去のみ。既存の縮尺/ボックス問題は別途未解決）。retry3契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M102-retry3-contract-prompt.md)（pass、prompt stageのみ） | #12。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 `[特技]`。効果・ダメージは未決。属性欄・弱点は変えない） |
| M103 | 使用者のいない銃 | 圧倒的な機械・物 | 海外 密集垂直都市（青年後半）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.7） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M103.webp`（1536×1024、WebP品質85・alpha保持。使用者なし。kako-jun採用 2026-10-21）。raw審査: [採用候補](reviews/artifact-redteam/20261021-M103-adopted-candidate.md) | #12 |
| M104 | 乱暴な自転車 | 交通と騒音 | 寺町 hinomi-bend（弧の道）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M104.webp`（1536×1024、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M104-contract-prompt.md)（pass、prompt stageのみ）。raw-image: [初回候補](reviews/artifact-redteam/20261021-M104-raw-image-ccbf1a25.md)（blocker: 横顔寄り・輪郭の色にじみ、余白不足）、[retry候補](reviews/artifact-redteam/20261021-M104-raw-image-fd5cec7e.md)（blocker: 横顔寄り・サイズ過大、余白不足・端alpha残り）、[final edit候補](reviews/artifact-redteam/20261021-M104-raw-image-e281af63.md)（blocker: 横顔・車輪の非重なり・サイズ過大・放射状背景）。リトライ契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M104-retry-contract-prompt.md)（pass、prompt stageのみ）。edit契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M104-edit-contract-prompt.md)（pass、prompt stageのみ） | #12、art-direction.md |
| M105 | 乱暴な車 | 交通と騒音 | 香林坊 korinbo-crossroads（十字）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M105.webp`（1536×1024、WebP品質85・alpha保持。運転者なし。kako-jun採用 2026-10-21）。契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M105-contract-prompt.md)（初版majorを記録、1536×1024・forward-leaning除去の改訂版はpass、prompt stageのみ）。raw-image: [候補審査](reviews/artifact-redteam/20261021-M105-raw-image-e0efc5d0.md)（blocker: 上端2 pixelの1/255 alpha漏れ） | 同上 |
| M106 | 大音量のバイク | 交通と騒音 | 香林坊 convenience-store（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M106.webp`（1536×1024、WebP品質85・alpha保持。無人。kako-jun採用 2026-10-21）。raw-image: [採用候補審査](reviews/artifact-redteam/20261021-M106-raw-image-7ae91bc9.md)（前輪・上鏡切れ、45°未達疑いを記録。kako-jun判断で採用） | 同上 |
| M107 | 大型立体看板（序盤のボス・香林坊。無骨な骨組み・ボロボロの看板・クレーン。kako-jun決定 2026-10-19、#120。旧称お神輿型は不要と決定。看板の商品は架空のスポーツドリンク「エクメトテロエス」、昭和のレトロなボロボロの看板（kako-jun指定 2026-10-20）） | 都市の巨大物 | 香林坊（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.2） | 未定 | 未定 | 序盤のボス（kako-jun 決定 2026-10-19、#120。docs の旧表記「中ボス」との区分は要確認。boss-gimmicks.md G019） | 採用済み（kako-jun目視採用 2026-10-20）: `assets/images/enemies/M107.webp`（1282×1227、WebP品質85・透過。エクメトテロエスの巨大缶看板・鉄骨・クレーン） | 同上 |
| M108 | 蓋の開いたマンホール | 暗い開口部 | 寺町 well-merge（井戸の合流）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M108.webp`（1254×1254、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw-image: [採用候補審査](reviews/artifact-redteam/20261021-M108-raw-image-c0b8c2f7.md)（赤い縁取り・石材風の縁を記録。kako-jun判断で採用） | 同上。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 `[特技]`。効果・ダメージは未決。属性欄・弱点は変えない） |
| M109 | 夜の森の葉・枝（悪魔に見える） | 錯視 | 夜の森（章は未定）。卯辰山 UTS-01 登り口・山の続き（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M109.webp（mid-3 を採用: 顔なし・非対称の自然な枝葉で、上端の2本の枝が角、左の塊が肩、右の枝が腕に見える。採用: kako-jun 2026-10-14） | #12 |
| M110 | 顔に見える壁の染み | 錯視 | 寺町 narrow-lane（縦の路地）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.1） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M110.webp（採用: kako-jun 2026-10-14） | #12 |
| M111 | 防火シャッター | 展示物・玩具（環境敵） | 香林坊の閉店後の商店街（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.2） | 未定 | 未定 | 環境敵（背景と連動して戦場を狭める画面ギミック） | 仕様のみ（スプライトを持たない） | #12 |
| M112 | マネキン | 展示物・玩具 | 香林坊のショーウィンドウ（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.2） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M112.webp`（1024×1536、WebP品質85・alpha保持。顔なし・無衣装。kako-jun採用 2026-10-21）。採用候補と後続候補の審査記録: [M112候補審査](reviews/artifact-redteam/20261021-M112-candidates.md) | #12 |
| M113 | 人形 | 展示物・玩具 | 子供部屋・古道具店・祭りの飾り（章・フィールドは未定）。香林坊 chaya-lane（茶屋街）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定（並び替わる・手をつなぐ・合体して大きく見える） | 採用: `assets/images/enemies/M113.webp`（570×640。右向き・座り姿の陶器人形・kako-jun採用 2026-10-22） | #12 |
| M114 | 18禁の成人向け週刊誌（目隠しされた表紙） | 恐怖メディア | 未定（棚の高い位置） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M114.webp`（新版 `exec-fa7c7b39-3307-4c5a-ac00-c298fb6c0b24.png`、1024×1536・1x2。kako-jun 2026-10-22 採用、旧画像から差し替え） | #12 |
| M115 | ホラーDVD | 恐怖メディア | サニーランド sunnyland-arcade-indoor（廃ゲームセンター）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.3） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M115.webp`（左右反転版、1254×1254、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [左右反転版](reviews/artifact-redteam/20261021-M115-raw-image-flipped.md)（表紙の風景・人物影を指摘、ユーザー採用） | #12 |
| M116 | 怪奇本 | 恐怖メディア | サニーランド sunnyland-arcade-indoor（補充候補。一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M116.webp`（左右反転版、887×1774、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [左右反転版](reviews/artifact-redteam/20261021-M116-raw-image-flipped.md)（縦横比と端の余白を指摘、ユーザー採用） | #12 |
| M117 | 怪人・黒マントと仮面帽子の紳士的な百面相キャラ | 恐怖メディア | 未定 | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M117.webp`（新候補 `exec-f1d0ccfc-09d0-4747-bb4d-4798fe19208c.png`、1254×1254、1x1。黒マント・仮面・帽子の紳士的な怪人。kako-jun 2026-10-22 採用。従来画像を置換） | #12 |
| M118 | 笑い袋 | 恐怖メディア | サニーランド sunnyland-arcade-indoor（廃ゲームセンター）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.3） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M118.webp`（左右反転版、1254×1254、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [左右反転版](reviews/artifact-redteam/20261021-M118-raw-image-flipped.md)（余白と赤い輪郭を指摘、ユーザー採用） | #12 |
| M119 | 指名手配ポスター（右向きの架空人物） | 恐怖メディア | 未定 | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M119.webp`（新版 `exec-b5d94329-ed7b-4314-afe5-a6fb215194e7.png`、887×1774・1x2。右向きの架空人物顔写真・指名手配見出し・懸賞金欄。kako-jun 2026-10-22 採用、旧画像から差し替え） | #12 |
| M120 | 歩行者専用標識（誘拐に見えるという都市伝説） | 恐怖メディア | 未定 | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M120.webp`（新版 `exec-21a6ad3a-d526-4e50-8131-fcd2948ee6cb.png`、887×1774・1x2。右向きの親子図案。kako-jun 2026-10-22 採用、旧画像から差し替え）。都市伝説の参考: [BEST TiMES](https://www.kk-bestsellers.com/articles/-/8632/) | #12 |
| M121 | 分厚い百科事典・難解な勉強の本 | 知識の恐怖 | 未定 | 未定 | 未定 | 未定（ページがめくれるたびに難問・重みが増す） | 採用: `assets/images/enemies/M121.webp`（1254×1254、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [候補](reviews/artifact-redteam/20261021-M121-raw-image-8d613a1f.md)（上下の余白不足を指摘、ユーザー採用） | #12 |
| M122 | 人体模型 | 医療・理科室 | 体内ダンジョン・頭（脳）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.6） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M122.webp`（1024×1536、WebP品質85・alpha保持、無衣装。kako-jun採用 2026-10-21）。raw review: [候補](reviews/artifact-redteam/20261021-M122-raw-image-9ad57e16.md)（向き・上端余白を指摘、ユーザー採用） | #12 |
| M123 | ホルマリン漬けのびん | 医療・理科室 | 体内ダンジョン・頭（脳）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.6） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M123.webp`（左右反転版、1254×1254、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [左右反転版](reviews/artifact-redteam/20261021-M123-raw-image-flipped.md)（ユーザーの向き指定を反映） | 同上 |
| M124 | 骨格模型 | 医療・理科室 | 体内ダンジョン・心臓（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.6） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M124.webp`（ガラス製、1024×1536、WebP品質85・alpha保持。kako-jun採用・材質指定 2026-10-21）。raw review: [ガラス候補](reviews/artifact-redteam/20261021-M124-raw-image-b31d1eb7.md)（頭の向き・上下余白を指摘、ユーザー採用） | 同上 |
| M125 | 注射器 | 医療・理科室 | 体内ダンジョン・両手・両足（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.6） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M125.webp`（1536×1024、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [候補](reviews/artifact-redteam/20261021-M125-raw-image-91998db4.md)（真横寄り・左右余白不足を指摘、ユーザー採用） | 同上 |
| M126 | 歯科ドリル | 医療・理科室 | 体内ダンジョン・口（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.6） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M126.webp`（1536×1024、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [候補](reviews/artifact-redteam/20261021-M126-raw-image-30e5b12a.md)（横向き寄り・左右余白不足を指摘、ユーザー採用） | 同上 |
| M127 | イカ | 水辺の生物 | 水辺（章は未定）。サニーランド sunnyland-aquarium-indoor（補充候補。大型雑魚。2x2 の穴埋め）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（海の生物。kako-jun 2026-10-21） | 未定 | 大型ボス的（巨体・長い触腕・墨） | 採用: `assets/images/enemies/M127.webp`（1536×1024、WebP品質85・透過、kako-jun目視採用 2026-10-20） | #12 |
| M128 | タコ | 水辺の生物 | 水辺（章は未定）。能登 実家 v2（被災前。水のラーニング元なので被災後の能登の海辺でも出て再戦できる）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（海の生物。kako-jun 2026-10-21） | 未定 | 通常敵（吸い付き・からみつき・多腕のトリッキーな戦い） | 採用: `assets/images/enemies/M128.webp`（1254×1254、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [候補](reviews/artifact-redteam/20261021-M128-raw-image-fd852008.md)（輪郭フリンジを指摘、ユーザー採用） | #12 |
| M129 | ゴンズイ | 水辺の生物 | 水辺（章は未定）。内灘 uchinada-beach（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（魚。kako-jun 2026-10-21） | 未定 | 未定（群れと毒棘） | 採用: `assets/images/enemies/M129.webp`（1536×1024、WebP品質85・alpha保持。5匹の群れ。kako-jun採用 2026-10-21）。契約審査: [2026-10-21 再審](reviews/artifact-redteam/20261021-M129-contract-prompt-recheck.md)（pass、prompt stageのみ。以前の要確認点と解消は審査記録）。retry契約審査: [初版](reviews/artifact-redteam/20261021-M129-retry-contract-prompt.md)（major: 淡水魚とする誤記）、[改訂版](reviews/artifact-redteam/20261021-M129-retry2-contract-prompt.md)（pass、prompt stageのみ）、[retry3](reviews/artifact-redteam/20261021-M129-retry3-contract-prompt.md)（初版majorを記録、横並び改訂版はpass、prompt stageのみ）。[最新候補raw審査](reviews/artifact-redteam/20261021-M129-raw-image-03ec1d11.md)（45°未達・端のalpha残り、ユーザー採用）。raw-image 審査: [初回候補](reviews/artifact-redteam/20261021-M129-raw-image-aea25d47.md)（blocker: 横顔・尾びれの切れ・輪郭の色にじみ）、[retry2候補](reviews/artifact-redteam/20261021-M129-raw-image-4c50e815.md)（blocker: 45°未達、透過・余白不成立、髭切れ）、[採用候補raw review](reviews/artifact-redteam/20261021-M129-raw-image-03ec1d11.md)（ユーザー採用済み。レビュー所見: 45°証拠未達、周縁alpha） | #12 |
| M130 | フグ | 水辺の生物 | 水辺（章は未定）。サニーランド sunnyland-aquarium-indoor（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（魚。kako-jun 2026-10-21） | 未定 | 未定（膨らみと毒） | 採用: `assets/images/enemies/M130.webp`（1372×1147、WebP品質85・透過。kako-jun目視採用 2026-10-21。raw審査は45°未達を指摘したが、kako-jun判断で採用）。契約審査: [再審](reviews/artifact-redteam/20261021-M130-contract-prompt-recheck.md)。raw審査: [審査記録](reviews/artifact-redteam/20261021-M130-raw-image-01a15ccc.md)。初回major履歴: [初回審査](reviews/artifact-redteam/20261021-M130-contract-prompt.md) | #12 |
| M131 | スズメバチ | 生物 | 卯辰山 UTS-01 登り口（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M131.webp`（1536×1024、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M131-contract-prompt.md)（pass、prompt stageのみ）。raw-image: [初回候補](reviews/artifact-redteam/20261021-M131-raw-image-6c34f2f8.md)（blocker: 触角の切れ・輪郭の色にじみ）、[retry候補](reviews/artifact-redteam/20261021-M131-raw-image-64fd3fa8.md)（blocker: 放射状背景・外周alpha）。retry契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M131-retry-contract-prompt.md)（初版majorを記録、寸法追加改訂版はpass、prompt stageのみ） | #12、#17 |
| M132 | 病原体（今どきのウイルスなど。実在の病原体名を使う。体内の敵は種類を増やす＝各種ウイルス・免疫細胞も出てよい。マクロファージは雑魚でなく部位の中ボスの1つ＝M012（体内では主人公が「異物」なので、免疫は主人公を異物と見て攻撃する）。kako-jun 2026-10-15。台帳へは後で起こす） | 毒と尖り | 体内ダンジョン（異性の友達の病院が舞台。中盤のトクリュウ対決より前）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.6） | 未定 | 未定 | 未定 | 生成済み: `assets/images/enemies/M132.webp`（採用: kako-jun 2026-10-14。透過） | #12、story.md、assets-policy.md |
| M133 | 毒キノコ | 毒と尖り | 湿った林・古い木壁・山の遊園地跡。卯辰山 utatsuyama-sunnyland（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定（胞子で視界や判断を乱す） | 採用: `assets/images/enemies/M133.webp`（1536×1024、WebP品質85・alpha保持。胞子つき。kako-jun採用 2026-10-21）。契約審査: [2026-10-21 初回](reviews/artifact-redteam/20261021-M133-contract-prompt.md)（pass、長文prompt）。実生成prompt再審: [短文版](reviews/artifact-redteam/20261021-M133-contract-prompt-actual.md)（pass、透過引数確認済み）。raw-image: [初回候補](reviews/artifact-redteam/20261021-M133-raw-image-6ffdcb7d.md)（blocker: 輪郭の色にじみ、隅のアルファ残り）。再生成契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M133-retry-contract-prompt.md)（pass）。再生成raw-image: [候補審査](reviews/artifact-redteam/20261021-M133-raw-image-b9c2771e.md)（blocker: 色縁、10%余白を満たさず）。retry2契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M133-retry2-contract-prompt.md)（pass、prompt stageのみ）。retry2 raw-image: [候補審査](reviews/artifact-redteam/20261021-M133-raw-image-263b8baf.md)（blocker: 透過不成立、指定ボックス外のアルファ・縦はみ出し）。edit契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M133-edit-contract-prompt.md)（pass、prompt stageのみ）。edit raw-image: [候補審査](reviews/artifact-redteam/20261021-M133-raw-image-370149f0.md)（blocker: 放射状背景、指定ボックス外へのはみ出し）、[背景除去候補](reviews/artifact-redteam/20261021-M133-raw-image-7d3bcdf9.md)（blocker: 背景残存、主体形状・胞子・縮尺変化）。背景除去契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M133-bg-contract-prompt.md)（pass、背景除去のみ。既存の縮尺/ボックス問題は別途未解決） | #12 |
| M134 | 釘 | 毒と尖り（尖ったもの） | 能登 NTB-02 上り坂（被災後）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M134.webp`（1254×1254、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [候補](reviews/artifact-redteam/20261021-M134-raw-image-8e744430.md)（端の低alpha残り、緑橙フリンジを指摘、ユーザー採用） | #12 |
| M135 | 割れたガラス | 毒と尖り（尖ったもの） | 能登 NTB-04 下り坂（被災後）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M135.webp`（1254×1254、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [候補](reviews/artifact-redteam/20261021-M135-raw-image-493a75ad.md)（周縁alpha、シアン白フリンジを指摘、ユーザー採用） | #12 |
| M136 | 金網 | 毒と尖り（尖ったもの） | 卯辰山 utatsuyama-sunnyland（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M136.webp`（1536×1024、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [候補](reviews/artifact-redteam/20261021-M136-raw-image-3f3c86ed.md)（背景alpha残り、周縁余白、追加レールを指摘、ユーザー採用） | #12 |
| M137 | 有刺鉄線 | 毒と尖り（尖ったもの） | 海外 荒れ地A・B（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M137.webp`（1536×1024、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。raw review: [候補](reviews/artifact-redteam/20261021-M137-raw-image-89a2070f.md)（低alphaフリンジを記録、ユーザー採用） | #12 |
| M138 | 氷柱 | 毒と尖り（尖ったもの） | 卯辰山 UTS-01 登り口（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 氷（kako-jun 2026-10-21） | 未定 | 未定 | 採用: `assets/images/enemies/M138.webp`（1024×1536、WebP品質85・alpha保持。kako-jun採用 2026-10-21）。契約審査: [2026-10-21](reviews/artifact-redteam/20261021-M138-contract-prompt.md)（pass、prompt stageのみ）。raw-image: [生成候補審査](reviews/artifact-redteam/20261021-M138-raw-image-2ccaf772.md)（pass、ユーザー採用済み） | #12 |
| M139 | ウニ | 毒と尖り（尖ったもの） | 能登 釣り場（被災前。水のラーニング元なので被災後の能登の海辺でも出て再戦できる）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（海の生物。kako-jun 2026-10-21） | 未定 | 未定 | 採用: `assets/images/enemies/M139.webp`（1254×1254、WebP品質85・透過、kako-jun採用 2026-10-21）。raw review: [候補](reviews/artifact-redteam/20261021-M139-raw-image-94b13979.md)（端の低alpha残り、紫赤フリンジ、向きの証拠不足を記録。ユーザー採用） | #12 |
| M140 | タバコの煙と灰 | におい・空気 | 未定 | 未定 | 未定 | 環境敵として検討（視界・詠唱・行動順に作用）。使用者は敵にしない | 仕様のみ | #12 |
| M141 | 酒の強いアルコール臭と揺れる液面 | におい・空気 | 未定 | 未定 | 未定 | 環境敵として検討（同上）。飲酒者は敵にしない | 仕様のみ | #12 |
| M142 | 落ちてきそうなシャンデリア | 崩壊・落下 | サニーランド屋内（旧円形ホール配置は失効、詳細再配置TBD） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M142.webp`（1024×1536、WebP品質85・透過、kako-jun採用 2026-10-21） | #12 |
| M143 | 割れた窓 | 崩壊・落下 | サニーランド屋内（旧円形ホール配置は失効、詳細再配置TBD） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M143.webp`（1024×1536、WebP品質85・透過、kako-jun採用 2026-10-21）。生成前審査: [prompt contract](reviews/artifact-redteam/20261021-M143-contract-prompt.md)（pass）。raw review: [候補](reviews/artifact-redteam/20261021-M143-raw-image-ce775a16.md)（端の低alpha・右余白16pxを記録、ユーザー採用） | #12 |
| M144 | 破れた障子 | 崩壊・落下 | 香林坊 chaya-lane（茶屋街）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.2） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M144.webp`（1024×1536、WebP品質85・透過、kako-jun採用 2026-10-21）。prompt contract: [生成前審査](reviews/artifact-redteam/20261021-M144-contract-prompt.md)（pass）。raw review: [候補](reviews/artifact-redteam/20261021-M144-raw-image-84e8b034.md)（余白・枠右側の厚み不足・端の低alphaを記録、ユーザー採用） | #12、#14 |
| M145 | 割れた酒瓶（割れたビール瓶） | 崩壊・落下 | 寺町 sento（銭湯）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.1） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M145.webp`（元画像 `exec-6bee855e-e505-42fe-b69a-a9fc25121eeb.png`、1536×1024。旧版を更新、kako-jun 2026-10-21 採用）。prompt contract: [生成前審査](reviews/artifact-redteam/20261021-M145-contract-prompt.md)（pass）。raw review: [候補](reviews/artifact-redteam/20261021-M145-raw-image-6bee855e.md)（横たわる割れた瓶、斜めの口と奥行きを確認。低alphaの細部はアクスタ演出を踏まえ採用） | #12 |
| M146 | プロペラ | 回転する刃（風） | 内灘 uchinada-station・UCH-03 松林道（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.4） | 風 | 未定 | 未定 | 採用: `assets/images/enemies/M146.webp`（元画像 `exec-6e373f21-7ae8-4fad-acc2-b195e258c19b.png`、1254×1254。旧版を更新、kako-jun 2026-10-21 採用）。prompt contract: [生成前審査](reviews/artifact-redteam/20261021-M146-contract-prompt.md)（pass）。raw review: [候補](reviews/artifact-redteam/20261021-M146-raw-image-6e373f21.md)（3枚羽根と斜めのハブ面を確認。余白・色フリンジはアクスタ演出を踏まえ採用） | art-direction.md、#26 |
| M147 | 扇風機・換気扇の羽根 | 回転する刃（風） | 寺町 sento（銭湯）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 風 | 未定 | 未定 | 採用: `assets/images/enemies/M147.webp`（元画像 `exec-7ed4c16c-cd6f-4569-8576-5db0c0335248.png`、1254×1254。旧版を更新、kako-jun 2026-10-21 採用）。prompt contract: [生成前審査](reviews/artifact-redteam/20261021-M147-contract-prompt.md)（pass）。raw review: [候補](reviews/artifact-redteam/20261021-M147-raw-image-7ed4c16c.md)（ガード・ハブ・3枚羽根を確認。端の余白と色フリンジはアクスタ演出を踏まえ採用） | 同上 |
| M148 | 凍った水たまり | 凍った足元（氷） | 寺町 connector・well-merge（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 氷 | 未定 | 未定 | 採用: `assets/images/enemies/M148.webp`（元画像 `exec-e5198b30-d41f-48ca-8cea-ba16992ec7c5.png`、1536×1024。地面の輪と丸い氷面を採用、kako-jun 2026-10-21）。prompt contract: [生成前審査](reviews/artifact-redteam/20261021-M148-contract-prompt.md)（修正後pass）。raw review: [候補](reviews/artifact-redteam/20261021-M148-raw-image-e5198b30.md) | 同上 |
| M149 | 石油ストーブ | 火事の原因（火） | 寺町 sento（銭湯。中3の火事に向けて慣れさせる）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.1） | 火 | 未定 | 未定 | 採用: `assets/images/enemies/M149.webp`（元画像 `exec-ae79d9f6-ce72-4ef3-9763-03d4c56304c7.png`、1254×1254。旧版を更新、kako-jun 2026-10-21 採用）。prompt contract: [生成前審査](reviews/artifact-redteam/20261021-M149-contract-prompt.md)（pass）。raw review: [候補](reviews/artifact-redteam/20261021-M149-raw-image-ae79d9f6.md)（グリル・タンク・取っ手と内部の発熱光を確認。細かな余白と色フリンジはアクスタ演出を踏まえ採用） | 同上 |
| M150 | ライター | 火事の原因（火） | 寺町 sento（銭湯。中3の火事に向けて慣れさせる）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.1） | 火 | 未定 | 未定 | 採用: `assets/images/enemies/M150.webp`（元画像 `exec-2a5c44c4-c92c-4ba7-a625-15fbf008f4bf.png`、1024×1536）。prompt contract: [生成前審査](reviews/artifact-redteam/20261021-M150-contract-prompt.md)（pass）。raw review: [候補](reviews/artifact-redteam/20261021-M150-raw-image-2a5c44c4.md)（炎が右上へ伸びる。余白・低alphaの細部はアクスタ演出を踏まえ採用） | 同上 |
| M151 | 古いたこ足配線 | 火事の原因（火） | 寺町 sento（銭湯。雷のラーニング元を早く取れるよう寺町に置く）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 火 | 未定 | 未定 | 採用: `assets/images/enemies/M151.webp`（元画像 `exec-e2e097f3-8c9c-4001-b99b-194c43da0b80.png`、1536×1024。旧版を更新、kako-jun 2026-10-21 採用）。prompt contract: [生成前審査](reviews/artifact-redteam/20261021-M151-contract-prompt.md)（pass）。raw review: [候補](reviews/artifact-redteam/20261021-M151-raw-image-e2e097f3.md)（焦げた差込口・右へ広がるコード・斜めの見えを確認。端の切れはアクスタ演出を踏まえ採用） | 同上。技: かんでん（雷のラーニング元。2026-10-15 kako-jun 決定。敵の専用 `[特技]`。効果・ダメージは未決。敵自身の属性は火のまま。火事の技と感電の技の両方を持ってよい） |
| M152 | ライフル弾状に空中分解する砲弾の欠片 | 回転する刃（風）に準ずる風のラーニング元 | 内灘 UCH-03 松林道（防砂林・砂丘）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.4） | 風（風のラーニング元「ざくざく」。kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.4） | 未定 | 未定 | 採用: `assets/images/enemies/M152.webp`（新版 `exec-09f20352-d773-49ad-b071-fc2239c5381d.png`、1254×1254・1x1。ライフル弾状の輪郭を保って空中分解する。kako-jun 2026-10-22 採用、旧画像から差し替え） | 砲弾を思わせる輪郭を保って空中分解させ、実在兵器の型式・細部は再現しない（S003の「砲弾の欠片の気配」と対応） |

**属性の穴（解消。kako-jun 2026-10-15 決定。docs/enemy-allocation.md §2.2）**: 土（どろだらけ）＝M101・M102・M108 が技として持つ。雷（かんでん）＝M151 が技として持つ（M151 の敵属性は台帳どおり火。火事の技と感電の技の両方を持ってよい）。属性欄・弱点は決めない。技の効果・ダメージは未決。

### 3-4. 場所が決まっている物語上の敵群（種類・個体は未定）

| ID | 名前 | 分類 | 出る場所 | 属性 | 弱点・耐性 | 役割 | 絵の状態 | 根拠 |
|---|---|---|---|---|---|---|---|---|
| M201 | 異国への誤像（キョンシー的な跳び人形、波紋のある刃、包帯の人形、暗い土の塚、異様な編み飾り、仮面） | 物語の敵（誤像） | 中盤〜青年編・トクリュウ救出地点の密集垂直都市（砂漠） | 未定 | 未定 | 未定 | 採用: `assets/images/enemies/M201.webp`（元画像 `exec-d7a63c76-b157-49c3-9705-83ade5e29da5.png`、1254×1254・2x2。kako-jun 2026-10-21 全部採用）。生成前契約: [審査記録](reviews/artifact-redteam/20261021-M201-contract-prompt.md)（pass）。raw review: [候補](reviews/artifact-redteam/20261021-M201-raw-image-d7a63c76.md)（6モチーフ・透過・全体余白・実写風を確認、微小なフリンジ/alpha specksあり） | art-direction.md、story.md |
| M202 | 城の護衛敵: 白黒の怖い侍 | 物語の敵 | 金沢城（ラストダンジョン。雑魚。護衛敵は金沢城専用）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 雑魚（ラストダンジョンの護衛敵。M014 とは別物） | 採用: `assets/images/enemies/M202.webp`（元画像 `exec-5c2aa26a-fd04-40f6-b78e-846872f39b12.png`、1024×1536・1x2。kako-jun 2026-10-21 全部採用、2026-10-22 左右反転）。[生成前審査](reviews/artifact-redteam/20261021-M202-contract-prompt.md)・[画像レビュー](reviews/artifact-redteam/20261021-M202-raw-image-5c2aa26a.md) | art-direction.md |
| M203 | 城の護衛敵: インフレ（デジタル数字・飛ぶ紙幣・ボロボロの靴） | 物語の敵 | 金沢城（ラストダンジョン。雑魚。護衛敵は金沢城専用）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 雑魚（ラストダンジョンの護衛敵。M014とは別物） | 採用: `assets/images/enemies/M203.webp`（新版 `exec-fa6a1551-236a-4dc1-a485-3efc568a4a62.png`、1774×887・2x1。デジタル数字・飛ぶ紙幣・傷んだ靴。kako-jun 2026-10-22 採用、旧画像から差し替え） | 同上 |
| M204 | 城の護衛敵: 外国での戦争（第一次世界大戦期の複葉機・警戒サイレン） | 物語の敵 | 金沢城（ラストダンジョン。雑魚。護衛敵は金沢城専用）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 雑魚（ラストダンジョンの護衛敵。M014とは別物） | 採用: `assets/images/enemies/M204.webp`（新版 `exec-556ae7b3-fa02-4626-b6ae-9af6cae94a87.png`、1774×887・2x1。雲なし、右向き複葉機3機と赤い警戒サイレン。kako-jun 2026-10-22 採用、旧画像から差し替え） | 同上。国・軍・市民・実在兵器は敵にしない |
| M205 | 城の護衛敵: 核兵器・放射能の恐怖（現代彫刻のニュークリア記号・コンプトン散乱光） | 物語の敵 | 金沢城（ラストダンジョン。雑魚。護衛敵は金沢城専用）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 雑魚（ラストダンジョンの護衛敵。M014とは別物） | 採用: `assets/images/enemies/M205.webp`（新版 `exec-e2811a54-bc0a-495a-9e9f-076bf8620376.png`、1254×1254・2x2。現代彫刻のようなニュークリア記号と散乱光。サイレン・黒い影なし。kako-jun 2026-10-22 採用、旧画像から差し替え） | 同上 |
| M206 | 城の雑魚: 忍者 | 物語の敵 | 金沢城（ラストダンジョン。専用雑魚。kako-jun 2026-10-21、#140） | 未定 | 未定 | 雑魚（M014とは別物） | 採用: `assets/images/enemies/M206.webp`（元画像 `exec-78833a1d-2d55-4c9d-aade-c756406ec920.png`、1024×1536・1x2。kako-jun 2026-10-22 採用）。旧画像 `exec-cf3ba92a-2acf-407f-90e0-8be7a1ab3243.png` から差し替え。くないを突き出す前傾の走り攻撃。[候補レビュー](reviews/artifact-redteam/20261022-M206-M209-weapon-raw-review.md)（姿勢・武器pass。背景のビネット指摘はあるが本人採用）[初回候補](reviews/artifact-redteam/20261022-M206-M209-raw-image-review.md) | #140 |
| M207 | 城の雑魚: 姫 | 物語の敵 | 金沢城（ラストダンジョン。専用雑魚。kako-jun 2026-10-21、#140） | 未定 | 未定 | 雑魚（M014とは別物） | 採用: `assets/images/enemies/M207.webp`（元画像 `exec-b9502417-27dd-43b8-8b87-22f0a8ca1445.png`、887×1774・1x2。kako-jun 2026-10-21 全部採用）。[生成前契約](reviews/artifact-redteam/20261021-M207-final-edit-contract-prompt.md)（角度/canvas pass。極低alphaの端ピクセル指摘あり）・[画像レビュー](reviews/artifact-redteam/20261021-M207-raw-image-b9502417.md)（顔・胴体とも右斜め正面、透過、全身のraw pass） | #140 |
| M208 | 城の雑魚: 怨霊 | 物語の敵 | 金沢城（ラストダンジョン。専用雑魚。kako-jun 2026-10-21、#140） | 未定 | 未定 | 雑魚（M014とは別物）。柳の下に現れる和風幽霊。長い黒髪・白い死装束・霧に消える下半身 | 採用: `assets/images/enemies/M208.webp`（新版 `exec-026169e3-3108-41fc-9a2a-2430de0b8e95.png`、1145×1374・2x2。柳の枝・和風幽霊。kako-jun 2026-10-22 採用、旧画像から差し替え） | #140 |
| M209 | 城の雑魚: くのいち | 物語の敵 | 金沢城（ラストダンジョン。専用雑魚。kako-jun 2026-10-21、#140） | 未定 | 未定 | 雑魚（M014とは別物）。忍者 M206 と異なり、水色の忍装束を着た木製人形が空中から蹴りかかり、手裏剣を構える | 初回候補 `exec-076d1aea-a11f-42a8-92e6-42cd02902231.png` を保管。採用: `assets/images/enemies/M209.webp`（元画像 `exec-844e3d01-5594-46c8-baec-4bd8edfa5d8f.png`、1024×1536・1x2。kako-jun 2026-10-22）。水色の装束で空中蹴りを放ち、手裏剣を構える。[候補レビュー](reviews/artifact-redteam/20261022-M206-M209-weapon-raw-review.md)（姿勢・武器pass。背景のシアンハロー指摘はあるが本人採用）。[初回画像レビュー](reviews/artifact-redteam/20261022-M206-M209-raw-image-review.md) | #140 |
| M210 | レッドペーパー（召集令状） | 戦争系の恐怖 | 未定（出現場所はマップ側の記録を参照） | 未定 | 未定 | 雑魚 | 新規追加（kako-jun 2026-10-22）。召集令状をモチーフにした赤い紙の敵。縦長1x2。採用: `assets/images/enemies/M210.webp`（透過元画像 `exec-09301265-498f-44e9-b21b-83aac9bd4715.png`、1024×1536。右向き、kako-jun 2026-10-22 採用絵に近い赤紙デザイン） | kako-jun 2026-10-22 |
| M211 | ダビデ | ラストダンジョン | 金沢城（ラストダンジョン。具体的な出現MAPはマップ側の記録を正本とする） | 未定 | 未定 | 雑魚（FF4「フェイズ」のオマージュ）。ダビデ像の巨大な石膏製の頭だけ。キャラクター側を向く右向き。瞳孔は描かず、首元は地面に接地させる | 採用: `assets/images/enemies/M211.webp`（元画像 `exec-6d42f216-b0b7-41b8-9eb2-902d5fe3a8be.png`、1254×1254、WebP品質85・alpha保持。kako-jun採用 2026-10-22）。サイズ2x2 | kako-jun 2026-10-22 |

### 3-5. 敵以外の生成済み素材（戦闘背景・フィールド。敵の出現場所の候補を見るための突き合わせ）

絵の状態は、リポジトリ内の実ファイルを開いて確認した（2026-10-14）。敵との対応は記録に無いので、出現場所には使わない。

| ファイル | 内容 | 使われている所 |
|---|---|---|
| `assets/images/battle-backgrounds/BG001.webp` | 雪の寺町風の道（土塀・石垣・用水・赤白スノーポール） | 戦闘背景の素材（敵との対応は未定） |
| `assets/images/battle-backgrounds/BG005.webp` | 舞台の床（雪山・城の書き割り） | M001 との戦闘背景（採用中） |
| `assets/images/fields/` | 寺町のフィールド背景（overview・wide-road・narrow-lane・connector、試作の kindergarten・danchi-court・sento・well-merge など）と歩行マスク | フィールド。敵の配置は未定 |

### 3-6. 戦利品（ドロップ・ぬすむ）

**ぬすむはオトン・ナムの 2 人まで使える（オトン側 1 本・ナム側 1 本の刀のアビリティ。その刀を持っているときだけ使える。主人公・相方の区別なし。同時に 2 人が使えてよい。kako-jun 2026-10-15。関連 Issue #831。decisions.md、docs/ability-candidates.md §5-4）。**

敵ごとの枠の構造だけが決まっている（2026-10-14 kako-jun。decisions.md）。**この表に行が無い敵は、3項目とも全て「未定」**。決まったら ID で行を足し、根拠を添える。

| ID | ドロップ | ぬすむ（通常枠） | ぬすむ（レア枠） | 根拠 |
|---|---|---|---|---|
| （まだ無し） | 未定 | 未定 | 未定 | - |
| M008 | 未定 | 未定 | 未定 | 新規登録のため（2026-10-15） |
| M009 | 未定 | 未定 | 未定 | 同上 |
| M010 | 未定 | 未定 | 未定 | 同上 |
| M011 | 未定 | 未定 | 未定 | 新規登録のため（2026-10-15） |
| M012 | 未定 | 未定 | 未定 | 同上 |
| M152 | 未定 | 未定 | 未定 | 同上 |

### 3-7. サイズ区分

敵のサイズは1種類にしない（decisions.md、2026-10-14 kako-jun）。**通常敵・中ボスは 1x1 / 2x1 / 1x2 / 2x2 のいずれかを、生成前にIDごとに決める。ラスボスのみ 2x6 のような大型枠を使える。** 全戦闘IDの先行指定は次表が正本。エンジン側の対応は name-name#839。

| ID | gridClass | 根拠 |
|---|---|---|
| M001〜M003 | 1x1 | 劇用・非遭遇意匠を含む先行指定 |
| M004〜M005 | **2x6** | 一周目のラスボス（M004からM005へ連続） |
| M006 | **2x2（夫婦の各個体）** | 二周目ラスボスの親2体は同時出現。kako-jun決定 2026-10-22 |
| M007 | 2x2 | M006戦で画面を占めるビジョン群 |
| M008 | **1x2** | 高さ5m以上の白いコンクリートのシャチホコ像。縦長の中ボス（kako-jun 2026-10-20） |
| M009 | 1x1 | 1ドットくらいの小さなイベント敵 |
| M010 | 2x2 | 胃でM009を守る大きな盾役 |
| M018〜M021 | **2x2** | アルファ・ベータ・ガンマ・デルタ。オミクロンを含む5株はすべて2x2（kako-jun 2026-10-20） |
| M011 | 1x1 | 非遭遇IDの演出素材用 |
| M012〜M016 | **2x2** | 体内・脳、石川橋、金沢城、左右塔の中ボス。M014のWW1・WW2・WW3は独立した三体の人型ボスで、個別画像を使う |
| M022 | 2x1 | 左の肖像から上半身だけが現れ、指を上げて煽るノストラダムラー |
| M023 | 2x2 | 凶悪な顔を持つ火星のような天体と、周囲へ降らせる隕石 |
| M017 | **1x1** | S001合体前の荒波の触手の雑魚敵。戦闘画面に約5体を同時に出す |
| M101 | 2x1 | 横幅のあるロードローラー |
| M102〜M103 | 2x1 | 大型ドリル・無人の銃 |
| M104 | 2x1 | 横長の自転車 |
| M105〜M106 | 2x1 | 無人の車・大音量のバイク |
| M107 | **2x2** | 香林坊の大型立体看板ボス |
| M108〜M109 | 1x1 | マンホール・葉枝 |
| M110 | 1x2 | 縦の壁面に現れる壁の染み |
| M111 | 2x2 | 戦場を狭める防火シャッター |
| M112 | 1x2 | 直立するマネキン |
| M113 | 1x1 | 座り姿の陶器人形 |
| M114〜M116 | 1x2 | 棚に立てる本・DVDケース |
| M117〜M118 | 1x1 | 絵本キャラ・笑い袋 |
| M119〜M120 | 1x2 | 立てるポスター・標識 |
| M121〜M124 | 1x2 | 直立する百科事典・模型・びん |
| M125〜M126 | 2x1 | 注射器・歯科ドリル |
| M127〜M128 | 2x2 | 巨体のイカ・多腕のタコ |
| M129 | 2x1 | 5匹のゴンズイの群れを横に並べる |
| M130〜M135 | 1x1 | フグ・スズメバチ・病原体・毒キノコ・釘・割れたガラス |
| M136〜M137 | 2x1 | 横へ伸びる金網・有刺鉄線 |
| M138 | 1x2 | 縦に伸びる氷柱 |
| M139 | 1x1 | ウニ |
| M140 | 2x1 | 横へ広がる煙と灰 |
| M141 | 1x1 | 酒の液面 |
| M142〜M144 | 1x2 | 上から垂れる物・縦の建具 |
| M145 | 2x1 | 横たわる割れた酒瓶 |
| M146〜M147 | 1x1 | 回転する羽根 |
| M148 | 2x1 | 横に広がる凍った水たまり |
| M149 | 1x1 | 石油ストーブ |
| M150 | 1x2 | 立てたライター |
| M151 | 2x1 | 横に広がるたこ足配線 |
| M152 | 1x1 | ライフル弾状の輪郭を保って空中分解する砲弾の欠片 |
| M201 | 2x2 | 複数の誤像を一体として扱う敵 |
| M202 | 1x2 | 白黒の怖い侍 |
| M203 | 2x1 | デジタル数字・飛ぶ紙幣・傷んだ靴のインフレ像 |
| M204 | 2x1 | 雲なし。右向き複葉機の複数機と赤い警戒サイレン |
| M205 | 2x2 | 現代彫刻のようなニュークリア記号とコンプトン散乱光 |
| M206 | 1x2 | 前傾を深くして走り込み、くないを突き出して攻撃する忍者人形（#140。縦長） |
| M207 | 1x2 | 直立する姫のイマジナリー（#140。縦長） |
| M208 | 2x2 | 長い黒髪と白い死装束、柳の枝のように垂れる霊気を持つ和風の怨霊（#140。大型） |
| M209 | 1x2 | 水色の忍装束の人形が空中蹴りを放ち、手裏剣を構えるくのいち（#140。縦長の跳躍姿勢） |
| M210 | 1x2 | 縦長の赤い召集令状（レッドペーパー） |
| M211 | 2x2 | 巨大なダビデ像の石膏製の頭部。瞳孔なし、地面に接地 |
| S001〜S004 | **2x2** | 中ボスとして戦う大型の召喚獣。S004は虎と4輪を収める |
| S005 第1形態 | **4x1（特例）** | 横4マス×縦1マスの街。通常の4種にはない横長の特例（kako-jun 2026-10-20） |
| S005 第2・第3形態 | **2x2** | 上半身が出た形態・全身で歩く形態（kako-jun 2026-10-20） |
| S006 第1・第2形態 | **2x3** | 灰色の積乱雲に深淵状のあやふやな円形開口が現れ、内部に宇宙が広がる形態（#141） |
| S006 第3形態 | **2x4** | 雲から外へ飛び出して多方向へジグザグに荒くとがって走る雷が複数の龍の顔をぼんやり連想させる段階（#141） |
| S006 第4形態 | **2x6** | 粒・波・塊からなる竜状の放電現象とドクロ顔、龍状のいかずち。画面いっぱいの最大形態（#141） |
| S007 | **2x2** | 二周目最終戦専用の味方召喚獣（ラスボスではない） |
| S008 | **2x2** | S001と同一の存在。新規ファイルは作らない |

**割り当て規則**: 既存画像の縦横比は台帳の gridClass を後追いで決める根拠にしない。全IDは上表の値を生成・再生成の契約として使う。通常敵・中ボスは4種、ラスボスは台帳に明記した大型枠を使う。S006は変身段階ごとに2x3・2x4・2x6を使う特例（#141）。

### 3-8. 通常敵画像の進捗（2026-10-21）

対象は M101〜M152 の52 ID。画像ファイルの存在を `assets/images/enemies/` と照合した。**画像ファイルあり49/52 ID（未作成は環境敵のM111・M140・M141のみ）。そのうちM107・M127はボス、M111・M140・M141は環境敵枠のため通常雑魚の作成数から分ける。通常雑魚は47/47体に採用画像あり（M114・M117・M119・M120・M152は採用済み（M114・M117・M119・M120・M152の新版を2026-10-22採用））。**

| 状態 | ID | 次の扱い |
|---|---|---|
| 採用画像あり | M101〜M110（M107はボスとして現状維持）、M112〜M139（M111は環境敵。M127はボスとして現状維持）、M142〜M152 | 通常雑魚47体分の正本画像あり。M145〜M151の最終候補、およびM114・M117・M119・M120・M152はkako-junが採用（2026-10-21） |
| 未作成の通常雑魚 | M002 | 人間を敵にしない原則と「不良に絡まれて戦う」記述が未整理。方針が定まるまで画像・サイズを決めない |
| 追加分（11体採用） | M009、M201〜M210 | M009とM201〜M210を採用済み。M210は召集令状をモチーフにした新規敵。既存採用分のサイズ・詳細は各行の記載を参照 |
| 新規追加（採用済み） | M211 | ラストダンジョンの雑魚。ダビデ像の巨大な石膏製の頭部。2x2。画像採用済み |
| 環境敵（別枠） | M111、M140、M141 | M111は確定済み防火シャッター環境敵。M140・M141は環境敵として検討中。通常雑魚の画像件数に含めず、出現場所や役割をここで補わない |

M101〜M152の通常雑魚は採用47/47体。M009とM201〜M211の計12体も採用済み（M211は2x2）。M002は人間敵の扱いが未整理のため画像・サイズ未決。M107・M127は既存ボス画像を維持する。M111・M140・M141は環境敵として別管理し、既存の配置記録を変更しない。召喚獣S001・S003・S005・S006の変身・合体形態画像は各行に記載し、S006は4形態すべて採用済みで再作成対象外。

**全雑魚の範囲確認（2026-10-22更新）**: M101〜M152の通常雑魚に加え、M009、海外のM201（6種を1 IDとして扱う）と金沢城専用のM202〜M209・M211も制作対象。M210レッドペーパーを追加（出現場所は未割当。マップ側の記録を正本とする）。M209は1x2で採用済み。M206は1x2の走り攻撃・くないの画像へ差し替え、採用済み。M017は抽象的な荒波の触手で、2026-10-19に採用済み、顔や左右向きの解剖学的要素を持たないため再作成対象外。金沢城のサイズ: M206忍者=1x2、M207姫=1x2、M208怨霊=2x2、M209くのいち=1x2、M211ダビデ=2x2。M002は人間敵禁止の方針と少年編の戦闘記述が衝突しているため未着手。出現場所は既存のマップ側記録を正本とし、ここでは重ねて管理しない。

**採用（2026-10-21、kako-jun「全部採用」）**: 採否待ちだった14候補（M009、M114、M117、M119、M120、M152、M201〜M208）を `assets/images/enemies/Mxxx.webp`（quality 85・alpha保持・実寸不変）へ変換して正本化した。元の生成PNGは `~/.codex/generated_images/` に残してある。

**2026-10-22新版画像の進捗**: M114・M117・M119・M120・M152・M203・M204・M205・M208の新版を採用し、各正本画像を更新。M204は雲を除き、右向き複葉機を複数配置。レッドペーパー M210 は縦長1x2で追加し、右向き画像を採用。

**敵画像のキャンバス実測（旧画像の区分・変更履歴は参考値。生成・再生成契約は §3-7 の gridClass が正本）**

| ID | 旧画像の区分・変更履歴（参考） | 現在の画像・寸法・縦横比 |
|---|---|---|
| M101 | 旧1x1 → 現行2x1 | `assets/images/enemies/M101.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M102 | 2x1（横2倍） | `assets/images/enemies/M102.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M103 | 2x1（横2倍） | `assets/images/enemies/M103.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M104 | 旧1x1 → 現行2x1 | `assets/images/enemies/M104.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M105 | 未作成 → 現行2x1 | `assets/images/enemies/M105.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M106 | 2x1（横2倍） | `assets/images/enemies/M106.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M108 | 1x1（普通） | `assets/images/enemies/M108.webp` 1254x1254、縦横比 1.00（採用 2026-10-21） |
| M109 | 1x1（普通） | `assets/images/enemies/M109.webp` 640x468、縦横比 1.37 |
| M110 | 1x2（縦2倍） | `assets/images/enemies/M110.webp` 323x640、縦横比 0.50 |
| M112 | 1x2（縦2倍） | `assets/images/enemies/M112.webp` 1024x1536、縦横比 0.67（採用 2026-10-21） |
| M113 | 1x1（普通） | `assets/images/enemies/M113.webp` 570x640、縦横比 0.89 |
| M115 | 1x2（縦2倍） | `assets/images/enemies/M115.webp` 1254x1254、縦横比 1.00（採用 2026-10-21） |
| M116 | 1x2（縦2倍） | `assets/images/enemies/M116.webp` 887x1774、縦横比 0.50（採用 2026-10-21） |
| M118 | 1x1（普通） | `assets/images/enemies/M118.webp` 1254x1254、縦横比 1.00（採用 2026-10-21） |
| M121 | 1x1（普通） | `assets/images/enemies/M121.webp` 1254x1254、縦横比 1.00（採用 2026-10-21） |
| M122 | 1x2（縦2倍） | `assets/images/enemies/M122.webp` 1024x1536、縦横比 0.67（採用 2026-10-21） |
| M123 | 1x1（普通） | `assets/images/enemies/M123.webp` 1254x1254、縦横比 1.00（採用 2026-10-21） |
| M124 | 1x2（縦2倍） | `assets/images/enemies/M124.webp` 1024x1536、縦横比 0.67（採用 2026-10-21） |
| M125 | 2x1（横2倍） | `assets/images/enemies/M125.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M126 | 2x1（横2倍） | `assets/images/enemies/M126.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M128 | 2x2 | `assets/images/enemies/M128.webp` 1254x1254、縦横比 1.00（採用 2026-10-21） |
| M129 | 旧1x1 → 現行2x1 | `assets/images/enemies/M129.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M130 | 現行1x1 | `assets/images/enemies/M130.webp` 1372x1147、縦横比 1.20（kako-jun採用 2026-10-21） |
| M131 | 1x1（普通） | `assets/images/enemies/M131.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M132 | 1x1（普通） | `assets/images/enemies/M132.webp` 640x462、縦横比 1.39 |
| M133 | 1x1（普通） | `assets/images/enemies/M133.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M134 | 旧1x1 → 現行1x1 | `assets/images/enemies/M134.webp` 1254x1254、縦横比 1.00（採用 2026-10-21） |
| M135 | 旧1x1 → 現行1x1 | `assets/images/enemies/M135.webp` 1254x1254、縦横比 1.00（採用 2026-10-21） |
| M136 | 2x1（横2倍） | `assets/images/enemies/M136.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M137 | 2x1（横2倍） | `assets/images/enemies/M137.webp` 1536x1024、縦横比 1.50（採用 2026-10-21） |
| M138 | 旧1x1 → 現行1x2 | `assets/images/enemies/M138.webp` 1024x1536、縦横比 0.67（採用 2026-10-21） |
| M139 | 1x1（普通） | `assets/images/enemies/M139.webp` 1254x1254、縦横比 1.00（採用 2026-10-21） |
| M142 | 1x2（縦2倍） | `assets/images/enemies/M142.webp` 1024x1536、縦横比 0.67（採用 2026-10-21）。gridClass は §3-7 の先行指定 |
| M143 | 1x2（縦2倍） | `assets/images/enemies/M143.webp` 1024x1536、縦横比 0.67（採用 2026-10-21）。gridClass は §3-7 の先行指定 |
| M144 | 1x2（縦2倍） | `assets/images/enemies/M144.webp` 1024x1536、縦横比 0.67（採用 2026-10-21）。gridClass は §3-7 の先行指定 |
| M145 | 2x1（横2倍） | `assets/images/enemies/M145.webp` 1536x1024、採用 2026-10-21 |
| M146 | 1x1（普通） | `assets/images/enemies/M146.webp` 1254x1254、採用 2026-10-21 |
| M147 | 1x1（普通） | `assets/images/enemies/M147.webp` 1254x1254、採用 2026-10-21 |
| M148 | 2x1（横2倍） | `assets/images/enemies/M148.webp` 1536x1024、採用 2026-10-21 |
| M149 | 1x1（普通） | `assets/images/enemies/M149.webp` 1254x1254、採用 2026-10-21 |
| M150 | 1x2（縦2倍） | `assets/images/enemies/M150.webp` 1024x1536。gridClass は §3-7 の先行指定 |
| M151 | 2x1（横2倍） | `assets/images/enemies/M151.webp` 1536x1024、採用 2026-10-21 |
| M009 | 1x1（普通） | `assets/images/enemies/M009.webp` 1254x1254、採用 2026-10-21 |
| M114 | 18禁の成人向け週刊誌（目隠しされた表紙） | 恐怖メディア | 未定（棚の高い位置） | 未定 | 未定 | 未定 | 現行採用: `assets/images/enemies/M114.webp`（元画像 `exec-e323a5bf-5d5e-4983-9c9d-cbbc1609a330.png`、1024×1536、1x2。kako-jun 2026-10-21 全部採用）。kako-jun 2026-10-22 指示で新版候補を作成中：18禁の成人向け週刊誌と分かる色・表紙構成。採否前は現行画像を保持。[旧候補レビュー](reviews/artifact-redteam/20261021-M114-raw-image-e323a5bf.md) | #12\n| M117 | 1x1（普通） | `assets/images/enemies/M117.webp` 1254x1254、採用 2026-10-21 |
| M119 | 1x2（縦2倍） | `assets/images/enemies/M119.webp` 1024x1536、採用 2026-10-21 |
| M120 | 1x2（縦2倍） | `assets/images/enemies/M120.webp` 887x1774、採用 2026-10-21 |
| M152 | 1x1（普通） | `assets/images/enemies/M152.webp` 1254x1254、採用 2026-10-21 |
| M201 | 2x2 | `assets/images/enemies/M201.webp` 1254x1254、採用 2026-10-21 |
| M202 | 1x2（縦2倍） | `assets/images/enemies/M202.webp` 1024x1536、採用 2026-10-21 |
| M203 | 2x1（横2倍） | `assets/images/enemies/M203.webp` 1536x1024、採用 2026-10-21 |
| M204 | 2x1（横2倍） | `assets/images/enemies/M204.webp` 1774x887、採用 2026-10-21 |
| M205 | 2x2 | `assets/images/enemies/M205.webp` 1254x1254、採用 2026-10-21 |
| M206 | 1x2（縦2倍） | `assets/images/enemies/M206.webp` 1024x1536、採用 2026-10-21 |
| M207 | 1x2（縦2倍） | `assets/images/enemies/M207.webp` 887x1774、採用 2026-10-21 |
| M208 | 2x2 | `assets/images/enemies/M208.webp` 1145x1374、採用 2026-10-22 |

この表の実寸は既存ファイルの記録であり、gridClass の正本は §3-7 である。再生成では §3-7 の先行指定に合わせる。

## 4. 出現場所ごとの逆引き

記録で場所が決まっているものだけを載せる。「場所未定」の敵（M101〜M151 の大半）は末尾にまとめる。

| 章・時代 | 場所 | 出る敵・召喚獣 |
|---|---|---|
| 幼稚園編 | お遊戯会の劇（舞台） | M001 段ボールのドラゴン |
| 幼稚園編 | 能登・日本海（水難事故） | S001 日本海の召喚獣（水） |
| 少年編前半 | 近所（おつかいなど） | M002 不良（集団） |
| 少年編前半 | サニーランド屋外SNL-06シャチホコ | M008 シャチホコ（サニーランドの中ボス） |
| 少年編後半 | 内灘 UCH-03 松林道 | M152 砲弾の欠片（風のラーニング元） |
| 中盤（トクリュウ対決より前） | 体内ダンジョン・部位ごとに中ボス（口は雑魚のみ） | 頭（脳）のエリア=M012 マクロファージ（M011 は非遭遇ID・舞台設定・演出）、胃=M009 エラー細胞（逃走）・M010 盾役の中ボス、心臓=S001 水の精霊、手足4部位の中ボス（未定） |
| 少年編前半 | 卯辰山の山のダンジョン（山中） | S002 卯辰山の召喚獣（氷）の中ボス戦（kako-jun 2026-10-15）。M133 毒キノコは「山の遊園地跡」が候補 |
| 少年編後半 | 内灘 | S003 内灘の風の召喚獣（風） |
| 中学3年 | 寺町（火事。寺の庫裏・台所） | S004 火の召喚獣（火。中ボス。2026-10-15。先の「青年編前・川」を置き換え） |
| 中盤（トクリュウ対決より前） | 体内ダンジョン（異性の友達の病院） | M132 病原体 |
| 中盤〜青年編 | トクリュウ救出地点（海外の砂漠の密集垂直都市） | M015 左塔5階、M016 右塔5階、M201 異国への誤像、S005 第3塔1階出口直前（時間継続）。M003は非遭遇意匠ID |
| 壮年編・一周目最終 | 兼六園・金沢城（イマジナリー天守閣） | M004 日本海寒帯気団収束体、M005 雷竜、S006 雷の召喚獣、M202〜M209 金沢城専用雑魚 |
| 二周目・エキストラ | 能登のシーサイド（エキストラダンジョン。#111） | 作中最強のボス（正体・強さ・報酬は要確認。ID 未割当。内部は地図待ち） |
| 二周目・終盤 | 金沢駅の鼓門前 | M006 巨人（夫婦）、M007 ビジョン、S004・S008 を使う、S007 イマジナリー鼓門（味方） |
| 場所は決まっている（章は未定） | 香林坊 | M107 大型立体看板（序盤のボス。kako-jun決定 2026-10-19、#120）、M111 防火シャッター（閉店後の商店街）、M112 マネキン（ショーウィンドウ） |
| 場所は決まっている（章は未定） | 湿った林・古い木壁・山の遊園地跡 | M133 毒キノコ（候補） |
| 場所は決まっている（章は未定） | 子供部屋・古道具店・祭りの飾り | M113 人形 |
| 場所は決まっている（章は未定） | 雪国の道路 | M101 ロードローラー |
| 場所は決まっている（章は未定） | 夜の森 | M109 葉・枝 |
| 場所は決まっている（章は未定） | 水辺 | M127 イカ、M128 タコ、M129 ゴンズイ、M130 フグ |

**場所が未定のフィールド・ダンジョン**（敵の割り当てが記録に無い）: 寺町・鱗町・思案橋・菊川の背景パック、内灘線(架空)の魔列車区間、粟崎遊園の記憶の砂浜、茶屋街の茶室、被災後の能登、K空港、廃墟探検。

**場所未定の敵**: M101〜M151 のうち上表に出ないもの（M102〜M106、M108、M110、M114〜M126、M131、M134〜M151 など）。スズメバチ・釘・割れたガラス・ウニ・氷柱・割れたビール瓶は絵があるが出る場所は未定。

## 5. 未決の一覧

| 論点 | 状態 | 参照 |
|---|---|---|
| 全ての敵（M101〜M205）の属性・弱点・耐性 | 水辺の生物（M127〜M130・M139）と水の波（M017）は水、氷柱M138は氷として決定。風・氷・火の既存記録も参照。その他の属性・弱点・耐性は引き続き未定 | docs/monsters.md §3-3 |
| 各敵の役割（ラスボス・中ボス・雑魚）。中ボスの記録あり: M107（中ボス）、S002（山のダンジョンの中ボス）、M008（サニーランドの中ボス） | 未決 | #12 |
| どの敵がどの技（ひあそび・ずぶぬれ・とうしょう・ざくざく・どろだらけ・かんでん・いたいのいたいのとんでいけ）を使うか | どろだらけ=M101・M102・M108、かんでん=M151 は決定（2026-10-15）。それ以外の技の持ち主は未決 | #17、#26 |
| 日常の恐怖の敵が出る章・フィールド（香林坊以外のほぼ全て） | 未決 | #11、#14 |
| 不良（M002）の扱い。「人間を敵にしない」原則との整合 | 記録上は未整理 | story.md、art-direction.md |
| 匿龍（M003。「龍」）と最終戦の雷竜（M005。「竜」）の響かせ方（龍と竜は別系列。制限は竜の字の話で匿龍は対象外、は決定済み） | 未決 | story.md |
| 一周目のビジョン（M007）の中身と、出現場所 | 未決 | systems.md |
| 二周目ラスボス戦で、雷の使い手の子供（2人目か3人目か）と、火に対する弱点を誰が突くか | 未決 | #25 |
| イマジナリー鼓門（S007）の本当の属性、取得の仕方、見つけ方 | 未決 | decisions.md |
| 兼六園・金沢城のボスラッシュ（決定 2026-10-15）で再戦する中ボス（召喚獣を含むか）・順序・各戦の強さ | 未決 | decisions.md、docs/enemy-allocation.md §2.3 |
| M013（石川橋）・M014（金沢城の三闘神級）の姿・名前・技（構成体は3＝三毒で決定、#123。子どもとの割り当ても未決）、ラスボス M004/M005 との関係 | 未決（護衛敵 M202〜M205 とは別物で雑魚と決定済み） | decisions.md、docs/enemy-allocation.md §1.8 |
| 水の召喚獣（S001）と、配偶者が使う水の召喚獣（S008）が同一か | **解決済み**: 同一（同じ絵を使う。2026-10-14 kako-jun） | decisions.md |
| 風・土の召喚獣の固有名。氷・火・水・雷も名前が確定しているかは要確認 | 未決 | #18 |
| 生成済みの敵画像の採否（ドリル・銃・病原体・マンホール・壁の染み・人体模型・ホルマリンびん・骨格模型・注射器・歯科ドリル・シャンデリア・割れた窓ほか） | 解決済み（kako-jun 2026-10-14「どの敵もいいね」。生成済みは全て採用。以後に増える画像も同様に扱う） | #12、#29 |
| 釘・割れたガラス・ウニ・氷柱・割れたビール瓶・スズメバチの採否 | 解決済み（全て採用。釘・割れたガラス・ウニ・氷柱・割れたビール瓶は kako-jun 2026-10-14） | #12 |
| 環境敵（防火シャッター、タバコの煙、酒のにおい）を、敵の一覧と同じ枠で数えるか | 未決 | #12 |
| 病原体の名前（地名を冠した通称を使うか）と専門家確認 | 未決 | story.md、#2 |
| 手足の中ボスは4部位（右手・左手・右足・左足）ぶん「株名の中ボス」で未決（部位と株の対応は未決）。マクロファージ M012 と株名の関係（併存か、株名に一本化か）は要確認。M011 は非遭遇ID、M012 の部位は頭（脳）のエリアに決定（kako-jun 2026-10-19、#125）（体内は部位ごとに専用の中ボス。最大7。2026-10-15） | 未決 | decisions.md 末尾、docs/enemy-allocation.md §1.6 |
| 体内の敵の種類（各種ウイルス・マクロファージ等の免疫細胞）の台帳への起こし方。免疫細胞（主人公を異物と見て攻撃する。理由は決定済み） | 後で台帳に起こす（2026-10-15） | story.md 303行、decisions.md |
| 弱点・耐性の記法（一つの弱点でなく複数の勝ち筋を持つため、表の列は「弱点・耐性・予兆・答えの組」にするか） | 未決 | systems.md、#15 |
| どの敵が何を落とす／持つか（ドロップ・ぬすむ通常枠・ぬすむレア枠の中身）、ぬすむの仕組みを誰がどう使うか（アビリティとして） | 未決（枠の構造だけ決定済み） | decisions.md |
| 各敵の gridClass | **解消**。通常敵・中ボスは4種、ラスボスは2x6を含め、§3-7 に全戦闘IDを先行指定済み（2026-10-19） | docs/monsters.md §3-7、#17 |
| 中3の火事の火の召喚獣戦と S004 の時期の食い違い | **解消**（中3の火事の戦いで確定。2026-10-15）。由来も決定（化石。2026-10-19、#80。推測で断定しない） | decisions.md |
| 内灘の風の召喚獣 S003 の戦いの中身 | 中ボス戦は確定（2026-10-15）。中身は案（S003 の行に注記） | story.md 315行付近 |
| 土・雷のラーニング元の敵（属性の穴） | 解消（2026-10-15 決定。土=M101・M102・M108、雷=M151。技の効果・ダメージは未決） | docs/enemy-allocation.md §2.2・§4 |
