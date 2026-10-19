# コンテンツ台帳の目次

ゲーム内の要素は、思いつきや個別プロンプトで増やさない。全要素をIDで管理し、ここを入口に「種別台帳 → 個別詳細」へたどる。

## 共通の運用

1. 新規要素は、生成・実装・文章化より先に対応する台帳へ1行追加する。
2. その行には少なくとも、ID、状態、登場時期／場所、目的、相互参照、**TBD**を持たせる。TBD は「未決」ではなく、決めるべき具体的な問いを書く。
3. 対象画像が実際に描く項目に未解決TBDがあれば、その対象の生成を `blocked` とする。生成前は原文・接続・建築・材料・参照・寸法の入力契約を独立審査し、通過後にその対象を1枚生成できる。画像やmaskが未作成であることだけは入力契約の未決を意味しない。`ready` は画像・mask・links・独立審査・実機確認まで通過した最終採用状態であり、生成前条件と混同しない。共通外観参照は外観の順序・包含関係を審査し、描かないruntimeの座標・幅はその参照の生成条件にしない。旧legacyの置換は明示された計画だけで行う。
4. プロンプトは、共通方針・台帳の対象行・対応スキルから機械的に組む。台帳にない物語・場所・接続・属性・見た目をプロンプトで創作しない。
5. 1つの詳細を変えたら、参照する行の状態を `needs-review` に戻し、TBDを再評価して矛盾を確認する。

## 種別台帳

| 種別 | ID接頭辞 | 正本 | 相互参照先 | 現在の整備状態 |
|---|---|---|---|---|
| エリア | A | [map-topology.md](map-topology.md) | MAP、ストーリー、敵 | 地区・接続は記録済み。各MAP契約は移行中 |
| フィールド／屋内マップ | MAP | [map-asset-registry.md](map-asset-registry.md)、[map-specifications.md](map-specifications.md)、[map-contract-checklist.md](map-contract-checklist.md) | A、敵、イベント、[参考画像調査](map-reference-research.md) | 130MAPに契約行あり。最終採用readyは未達。生成可否は対象画像が描く項目のTBDと独立入力契約審査で判定し、共通外観参照は別スコープで扱う |
| 登場人物 | C | [art-direction.md](art-direction.md)、[assets-policy.md](assets-policy.md) | 能力、時期、イベント | マスター／年齢段階は記録済み。横断ID表が必要 |
| 敵 | M | [monsters.md](monsters.md)、[dungeon-enemies.md](dungeon-enemies.md) | MAP、魔法、ボス | ID・配置・画像台帳あり |
| 召喚獣 | S | [monsters.md](monsters.md)、[story.md](story.md) | 時期、属性、MAP | ID・属性・取得順あり |
| 魔法／ラーニング | L | [learning-schedule.md](learning-schedule.md) | M、S、能力、成長 | 取得計画あり。個別発動仕様は要統合 |
| 刀／アビリティ | B | [blades.md](blades.md)、[ability-candidates.md](ability-candidates.md) | C、ジョブ、戦利品 | 候補・型はあり。採用状態のID表が必要 |
| ジョブ | J | [ability-candidates.md](ability-candidates.md)、[systems.md](systems.md) | C、B、戦闘 | 候補段階。個別IDと解放条件は未決 |
| アイテム／戦利品 | I | [systems.md](systems.md) | M、B、ショップ | 概念決定済み、個別台帳は未作成 |
| ボス／ギミック | G | [boss-gimmicks.md](boss-gimmicks.md) | M、S、MAP、イベント | G001〜の台帳あり |
| イベント／場面 | E | [scenario-registry.md](scenario-registry.md) | ERA、A、MAP、C、M/S、L/B/I、G | ERA・初期E目次を作成。各イベントはTBD解消までblocked |

## プロンプト組み立て規約

画像を作るときは、次の順で根拠を束ねる。

1. この目次から対象の種別・IDを確定する。
2. 対象台帳の1行から、時期・場所・目的・接続／向き・必須／禁止・相互参照を取得する。
3. [assets-policy.md](assets-policy.md) と [art-direction.md](art-direction.md) から全体の画風・時代・禁止事項を取得する。
4. 対象別スキル（フィールド背景は `sit-field-background`、敵スプライトは `sit-enemy-sprite`、召喚獣スプライトは `sit-summon-sprite`、人物スプライトは `sit-character-sprite`、戦闘背景は `sit-battle-background`、歩行マスクは `sit-field-mask`）から、材料・構図・出力・検査項目を取得する。
5. 以上に無い要素は追加しない。TBDまたは欠けた項目があれば台帳を `blocked` にして、先に決定を記録する。

`ruby scripts/build_map_prompt.rb MAP_ID` は **legacy・非正本** であり、現状の出力を生成許可や完全promptとして使わない。原文の採否ゲート、対象へ入るincoming接続、実ツールの寸法指定・寸法保証条件（目標1920×1080、返せない場合は16:9の1672×941、それ以外は不合格）が欠落するためである。修正・検証されるまでは原文行、双方向接続、未解決TBD、参照画像、寸法条件を手動で束ね、`sit-field-background` の前後検査と独立レビューを通す。寺町の現行束は [20261018-teramachi-preflight.md](production/20261018-teramachi-preflight.md)。同スクリプトが成功しても `blocked` は解除されない。

生成後は、対象IDの行に出力パス・採否・歩行マスクまたは切り抜き・参照したIDを追記する。
