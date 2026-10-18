# 寺町 E01 v3 / E09 v6 生画像・独立 red-team レビュー

- 日付: 2026-10-17
- レビュアー: `/root/e01_e09_visual_redteam`（本候補の画像・prompt・mask・先行レビューの作者ではない独立レビュー担当）
- 対象: `E01 kindergarten` と `E09 old-slope-foot` の**生画像のみ**。候補・mask・台帳状態は変更していない。
- 判定範囲: 「walk mask を作り始められる画像か」。採用／`ready` 判定ではない。

## 検査した正本と入力

- `docs/content-registry.md`
- `docs/map-asset-registry.md`（E01/E09 の legacy 行、104行共通契約）
- `docs/map-specifications.md`（寺町 E01/E09 行）
- `docs/map-topology.md`（§3.0 MAP相互接続台帳 v2、寺町の地形不変条件、屋外・屋内遷移不変条件）
- `docs/map-reference-research.md`（R006、R011、R024、R025）
- `docs/art-direction.md`、`docs/assets-policy.md`
- `.claude/skills/sit-diorama/SKILL.md` と `.claude/skills/sit-artifact-redteam/SKILL.md`
- `docs/teramachi-rebuild-candidates.md`
- 原画像（いずれも `sips` で **1920×1080 PNG** と確認）:
  - `sample/field/rebuild/E01-teramachi-kindergarten-rebuild-v3-candidate.png`
  - `sample/field/rebuild/E09-teramachi-old-slope-foot-rebuild-v6-candidate.png`

作者から渡されたprompt来歴も確認した。E01 は右端の幅広い外部路のみ、北通用門は画面内、left/top/bottom閉鎖、人物・文字・鳥居・地蔵・卒塔婆禁止。E09 はleftからtopへ実画素でつながる立位専用石段、right/bottom閉鎖、スロープなし、人物・文字禁止である。

## 先に固定した接続契約

| ID | 正本の必須接続 | 禁止／通行条件 |
|---|---|---|
| E01 | `E01.right → E02.left`、`E01.door-north → E11.door-kindergarten` | 外周のleft/top/bottomは道路を出さない。北通用門は園庭主路と分離した扉遷移であり、外周exitではない。 |
| E09 | `E08.right → E09.left`、`E09.top → E13.bottom` | right/bottom閉鎖。犀川側段丘の立位期だけの石段であり、車椅子用スロープにしない。 |

相手側の反対辺は、E02.left、E11.door-kindergarten、E08.right、E13.bottom と台帳 v2 で往復確認した。E01/E09 の各辺指定は北上固定の寺町地形とも矛盾しない。E09 はE07の車椅子生活スロープを代替しない。

## E01 v3 の生画像検査

| 検査 | 実画素の証拠 | 結果 |
|---|---|---|
| `right → E02.left` | 画面中段の黒い幅広い路面が右端まで連続し、右端で終わる。横向きで、E02.left へ出る契約と整合する。 | pass |
| 北通用門 | 上部左寄りの雪を載せた小門へ、園庭側の短い黒い通路が達する。門はtop edgeへ抜けず、中央の園庭主路（右端への道路）から分離している。 | pass（door link の後続mask化は未実施） |
| 禁止辺 | left/top/bottom の外周は雪、塀、建物、土台で閉じる。外部MAPに抜ける道路・歩道はない。 | pass |
| 景色・固有性 | 私立幼稚園、遊具、砂場、雪の園庭、背後の寺院建築／長塀が区別できる。単なる道路ではない。冬の雪と融雪後の露出地面があり、廃墟化していない。 | pass |
| 人物・文字・宗教物の禁止 | 人物・読める文字・鳥居・地蔵・卒塔婆は確認されない。右上の石灯籠は寺院庭園の設備であり、人物像ではない。 | pass |
| 手作りジオラマ | 木枠土台、机面、綿状の雪、紙／模型の屋根・塀、遊具の縮尺が明瞭。ほぼ真上からの浅い俯瞰で、空・遠景・消失点がない。 | pass |
| mask gate | この候補専用のtraversal/foreground/linksは存在しない。生画像レビューであり、作成前として期待どおり。現時点で通行幅、門のlink ID、前景被さりは未証明。 | mask authoring で必須 |

**E01 の判定: pass（生画像契約）／mask authoring 可。**

mask作者は、right edgeを `E02.left` として記録し、北門を `door-north` の内部door linkとして別記録すること。園庭と道路を無差別に白へ塗らず、建物・塀・積雪の縁・遊具をblackにし、通用門と園庭主路が同一外周リンクにならないことを確認する。

## E09 v6 の生画像検査

| 検査 | 実画素の証拠 | 結果 |
|---|---|---|
| `left → E08.right` | 左端中央から幅のある石段下／石畳が実画素で入る。v5で欠けていた「左端から入れる基部」は今回は土台端まで到達している。 | pass |
| `top → E13.bottom` | 石段は中央で折れながら上方へ続き、画面上端中央付近に実画素で到達する。 | pass |
| left→top の主路連続 | 左端の石段下から、広い下段、踊り場、中央の上り石段を介してtop edgeへ連続して読める。木・石垣・雪が主路を切断していない。 | pass |
| 禁止辺 | right は石垣・雪・樹木・塀、bottom は土台・雪・石垣で閉じる。外へ抜ける道路、スロープ、橋は見当たらない。 | pass |
| 立位期限定／スロープ非混同 | 全主路が急な段差を持つ石段である。蛇行する緩勾配の車椅子路はなく、E07の生活スロープを代替しない。 | pass（通行クラスはmaskで定義） |
| 景色・模型性 | 段丘の石垣・寺塀・雪の古い石段という固有性がある。段ボール土台、机面、綿雪、粗い石・紙の塀、縮尺物が見え、手作り模型であることが直接読める。 | pass |
| 人物・文字 | 人物および読める文字は確認されない。石灯籠は地蔵・卒塔婆ではない。 | pass |
| mask gate | このv6候補専用のtraversal/foreground/linksは未作成。画像だけでは立位期onlyのorangeと事故後black、両edgeの範囲を証明できない。 | mask authoring で必須 |

**E09 の判定: pass（生画像契約）／mask authoring 可。**

mask作者は、left/topの石段だけを `assist`（立位期のみ）として連続させ、事故後は当該入口から石段までblackにすること。right/bottomにはlinkを置かず、石垣・塀・急段差・雪・土台をblackとして、スロープを描き足さないこと。

## 横断的な未解決事項（採用 blocker、ただし生画像からmaskへ進むこと自体は妨げない）

1. `docs/teramachi-rebuild-candidates.md` はE01を旧名の初回候補、E09をv3かつ`blocked-regenerate`としており、今回のv3/v6 raw output path、prompt本文／Ref、review link、adoption stateをまだ記録していない。**修正先:** 同候補台帳のE01/E09行。mask作者は新しいmaskをこの未記録候補へ曖昧に紐付けてはならない。
2. E01はE11、E09はE08/E13との実行時links・三値traversalの往復照合が未実施。**修正先:** 各候補専用の `sit-field-mask` 出力と、mask完成後の新しい独立red-teamレビュー。
3. E01の屋外／屋内遷移はE11/F01/E12/F02と一体で検査する必要がある。**修正先:** `map-topology.md` の屋外・屋内遷移不変条件に対応するmask links照合。画像単体のpassを採用・`ready`根拠にしてはならない。

## 最終 disposition

両候補は、前版のE09 blockerだったleft-edge入口を含め、今回の生画像上の接続・禁止辺・模型性・人物／文字禁止を満たす。したがって **E01 v3 と E09 v6 は、ともに `pass`（生画像のみ）で `sit-field-mask` のauthoringへ進行可** とする。

これは採用可・runtime可・`ready`ではない。上記の台帳来歴更新、traversal/foreground/links、相手MAPとの往復照合、完成maskを入力とする別の独立red-teamを通過するまで、候補は採用してはならない。
