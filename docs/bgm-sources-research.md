# ドヴォルザーク 交響曲第9番「新世界より」フリー録音 調査

調査日: 2026-10-16 / 調査のみ（ダウンロードはしていない）。
目的: 商用ゲームの BGM に使える可能性がある「フリーな録音」の洗い出し。

### ランクの定義（bgm-sources.csv の「ランク」列。他の文書もこれに従う）

| ランク | 意味 |
|---|---|
| A | 発行年から100年が既に経過している（計算上）、かつ CC0・CC BY 等の明確な宣言がある（現在は stokowski1925 のみ） |
| B | クレジット等の条件付きで利用可 |
| C | 根拠が弱い・宣言のみ・米国で保護期間内の可能性。入力専用の参考（stokowski1927 は米国で 2028-01-01 まで保護期間内のため C） |
| X | NC 系で商用不可の可能性 |

（下の 〇/△/× の判定は本書内の一覧用で、ランクとは別。最終判断は人間が行う。）

## 0. 先に結論

### 米国での録音の保護期間（計算式。本書の年はすべてこれによる）

- 出典: 米国著作権局 https://copyright.gov/music-modernization/pre1972-soundrecordings/ 。1923〜1946年に最初に発行された録音は「一般の95年 + 5年 = 発行年から100年」。保護は発行年の100年後の年末まで、翌年1月1日にパブリックドメインに入る。
- 計算結果（いずれも**計算上**で、**弁護士確認は未了**）: 1925年 → 2026-01-01 から PD ／ 1927年 → 2028-01-01 に PD（2027年末まで保護）／ 1934年 → 2035-01-01 ／ 1937年 → 2038-01-01 ／ 1941年 → 2042-01-01 ／ 1923年より前（1919〜21年のアコースティック録音）は既に PD（ただし実際の録音年・発行年は未確認）。
- 発行年は録音年と一致するとは限らない（未確認）。

- 曲（1893年）は著作権切れ。問題は**録音側の権利**（実演家・レコード製作者の権利）。
- 「配布サイトのライセンス表記」と「録音そのものの法的状態」は別。アップロード者が CC0 や PD を宣言しても、本人が権利者でなければ効力は保証されない。
- **全4楽章がそろい、権利面の根拠が相対的に堅い**のは 1925年録音（表のB）。1927年録音は米国で 2028-01-01 まで保護期間内なので、次点の扱い。
  1. **Stokowski / Philadelphia Orchestra 1927年録音（Internet Archive `DvorakSymphonyNo.9`、CC0 表記）**。1927年録音は計算上、米国で 2027年末まで保護期間内（2028-01-01 に PD）。CC0 はアップロード者の宣言のみ（ランクC）。音質は 1927 年の電気録音（モノラル、ノイズあり）。
  2. **Stokowski / Philadelphia 1925年録音（Internet Archive `DvorakSymphony9InEMinorfromTheNewWorld`、CC BY 3.0 表記）**。計算上、米国で 2026-01-01 から PD（ランクA）。アップロード者の CC BY 表記もあるため、クレジットは慣行として付ける。
- 現代録音で全楽章そろうものは、**DuPage Symphony Orchestra 2012（IMSLP、CC BY-SA 3.0）**。クレジットと継承条件（SA）の扱いが論点。
- **Musopen 本体は WebFetch / curl とも HTTP 403 で一次情報を確認できなかった**。Wikimedia Commons 経由の Musopen 由来音源（4楽章）は演奏者が不明のため「要注意」。
- 1950〜60年代の録音（Szell/Cleveland、Bernstein/NYP 等）は、IMSLP 上で「Public Domain (Non-PD US)」表記。これは**米国では PD ではない**という意味。使えない。

「使える」判定の凡例:
- 〇 = 表記が明確で、録音年からも問題が小さい（それでも最終確認は人間）
- △ = 条件付き／根拠が弱い（要注意）
- × = ゲーム商用には使わない

## 1. 一覧表（全4楽章がそろうものを中心に）

| # | 演奏者/団体 | 録音年 | 楽章 | 長さ | ライセンス表記（原文） | クレジット要否 | 形式 | 判定 |
|---|---|---|---|---|---|---|---|---|
| A | Leopold Stokowski / Philadelphia Orchestra（Victor M-1。Stokowski の解説トーク付き） | 1927年10月5・8日 | 全4楽章 + 解説トーク（トークは別トラック） | 約38:19（4楽章合計。解説は別に約3:54） | `licenseurl: http://creativecommons.org/publicdomain/zero/1.0/`（CC0） | 不要（CC0）。ただし移し替え担当 Bob Varney への敬意として記載推奨 | MP3 / Ogg Vorbis | △（米国で 2028-01-01 まで保護の計算。ランクC） |
| B | Leopold Stokowski / Philadelphia Orchestra（最初の電気録音と説明あり。第2楽章でオーボエ独奏 Marcel Tabuteau） | 1925年5月14・15日、10月6・7日、12月8日 | 全4楽章 | 約40:29 | `licenseurl: http://creativecommons.org/licenses/by/3.0/`（CC BY 3.0） | **要**（表示義務あり。クレジットは「uploader varneyelmi (Internet Archive)」に限定。移し替え者が Bob Varney かは推定で未確認） | MP3 / Ogg Vorbis | 〇（計算上、米国で 2026-01-01 から PD。ランクA） |
| C | DuPage Symphony Orchestra / Barbara Schubert（指揮） | 2012-02-12 | 全4楽章 | 約41:32（11:58 + 11:09 + 7:12 + 11:13） | IMSLP 上の表記: "Creative Commons Attribution-ShareAlike 3.0" | **要**（BY）。SA（継承）条件あり | MP3 | △（SA の扱い。後述） |
| D | Columbia University Orchestra / Jeffrey Milarsky（指揮、ファイルコメントより） | 2002（Fall 2002 Concert） | 全4楽章 | 約41:01 | `licenseurl: http://creativecommons.org/licenses/publicdomain/` | 表記上は不要 | MP3 / Ogg Vorbis | △（後述。要注意） |
| E | Jose Iturbi / Rochester Philharmonic Orchestra（Victor DM-899） | 1941 | 全4楽章 | 約37:15 | `licenseurl: http://creativecommons.org/publicdomain/zero/1.0/` | 不要（表記上） | MP3 / Ogg Vorbis | △（要注意。米国では録音自体がまだ保護期間内の可能性） |
| F | Czech Philharmonic / George Szell（Victor DM-469。Bob Varney 版） | 1937 | 全4楽章 | 約38:05 | `licenseurl: http://creativecommons.org/licenses/publicdomain/` | 表記上は不要 | MP3 のみ（ZIP あり） | △（要注意。計算上、米国では 2038-01-01 まで保護の可能性） |
| G | Musopen 由来（演奏者不明） | 不明（Commons 登録 2008-01） | 全4楽章（別ファイル4つ） | 約41:48（10:05 + 11:34 + 8:26 + 11:43） | 「This work has been released into the public domain by its author, Musopen.」 | 表記上は不要。ただし Commons 記述に「credit を」の文言あり（後述） | Ogg Vorbis | △（演奏者・録音年が確認できない。要注意） |
| H | Royal Albert Hall Orchestra / Landon Ronald（HMV D1252-53 他） | 1927 | **一部のみ**（レコード面4枚ぶん。完全な楽章ではない） | 各約3:27〜3:51 | Creative Commons Public Domain Mark 1.0 | 不要（表記上） | FLAC（約120〜140MB／枚） | △（欠けが多い。BGM 用の断片としてなら） |
| I | Royal Albert Hall Orchestra / Landon Ronald（HMV D536 他） | 1919・1921 | 4楽章（わずかに省略ありと説明） | 約30:48 | **IA 側のライセンス欄は空**（`licenseurl` なし） | 不明 | FLAC / MP3 | △（録音年的には問題が小さいが、明示ライセンスなし。アコースティック録音で音質は低い） |

## 2. 個別の詳細（一次情報を確認できたもの）

### A. Stokowski / Philadelphia 1927（CC0）

- ページ: https://archive.org/details/DvorakSymphonyNo.9
- 説明（原文の要旨）: Leopold Stokowski が Philadelphia Orchestra を指揮。Academy of Music, Philadelphia で 1927年10月5・8日録音。Stokowski による主題解説（ピアノは Artur Rodzinski）を含む。Victor 6565–6569 / set M-1。"Transfer and restoration by Bob Varney."
- ライセンス: `http://creativecommons.org/publicdomain/zero/1.0/`
- 直接ダウンロードURL（形式 / 長さ）:
  - https://archive.org/download/DvorakSymphonyNo.9/01_dvorakSym9Mvmt1.ogg （Ogg / 513.5秒）、`.mp3` も同名で存在（513.6秒）
  - https://archive.org/download/DvorakSymphonyNo.9/02_dvorakSym9Mvmt2.ogg （712.8秒）
  - https://archive.org/download/DvorakSymphonyNo.9/03_dvorakSym9Mvmt3.ogg （433.7秒）
  - https://archive.org/download/DvorakSymphonyNo.9/04_dvorakSym9Mvmt4.ogg （638.5秒）
  - 解説トーク: `05_dvorakSym9StokowskiTalk.ogg`（234.1秒。BGM には不要）
- 確認できなかった点:
  - 1927年録音の米国での保護は、計算上 2027年末まで（発行年から100年。冒頭の計算式参照）。弁護士確認は未了。
  - 78rpm の移し替え（Bob Varney）に別途権利が生じるかは不明。本人が CC0 を宣言しているので実害は小さいと思われるが、法的な保証ではない。
  - 英語以外の国での扱い（EU は発行後70年で切れているはず）も未確認。

### B. Stokowski / Philadelphia 1925（CC BY 3.0）

- ページ: https://archive.org/details/DvorakSymphony9InEMinorfromTheNewWorld
- 説明（原文）: "Leopold Stokowski conducting the Philadelphia Orchestra." 録音日は 1925年5月14・15日、10月6・7日、12月8日。第2楽章のオーボエ独奏は Marcel Tabuteau、この交響曲の最初の電気録音。アップロード者 varneyelmi（IA ユーザー名）。
- ライセンス: `http://creativecommons.org/licenses/by/3.0/`
- 直接ダウンロードURL:
  - https://archive.org/download/DvorakSymphony9InEMinorfromTheNewWorld/01__adagioAllegroMolto.ogg （521.95秒）
  - https://archive.org/download/DvorakSymphony9InEMinorfromTheNewWorld/02__Largo.ogg （787.26秒）
  - https://archive.org/download/DvorakSymphony9InEMinorfromTheNewWorld/03__scherzoMoltoVivace-pocoSostenuto.ogg （457.05秒）
  - https://archive.org/download/DvorakSymphony9InEMinorfromTheNewWorld/04__allegroConFuoco.ogg （662.79秒）
  - 各 `.mp3` も同名で存在。
- 確認できなかった点: 移し替え者名がメタデータに明記されているかは未確認（説明欄に Bob Varney の名前なし。アップロード者の IA ユーザー名のみ）。Bob Varney が移し替え者かは推定にとどまる。クレジットは「uploader varneyelmi (Internet Archive)」に限定し、CC BY のクレジット対象としてこれでよいかは判断が必要。

### C. DuPage Symphony Orchestra / Barbara Schubert（CC BY-SA 3.0、IMSLP）

- ページ: https://imslp.org/wiki/Symphony_No.9,_Op.95_(Dvořák,_Antonín)
- 原文: 「Cypressdome (uploaded 2013/8/10), Performed 12 February 2012 by DuPage Symphony Orchestra, Barbara Schubert (conductor)」「Creative Commons Attribution-ShareAlike 3.0」
- ファイル（MP3）:
  - I: PMLP08710-dso20120212-002-dvorak-symphony-no9-mvtI.mp3（14.59MB / 11:58）→ https://imslp.org/wiki/Special:ImagefromIndex/291836
  - II: ...-003-...mvtII.mp3（13.87MB / 11:09）→ .../291837
  - III: ...-004-...mvtIII.mp3（8.88MB / 7:12）→ .../291838
  - IV: ...-005-...mvtIV.mp3（13.65MB / 11:13）→ .../291839
- 注意: IMSLP の `Special:ImagefromIndex/...` は JavaScript による遷移ページ（同意画面を挟む）で、直リンクのダウンロードURLとしては確認できなかった。ダウンロードには IMSLP の免責同意画面を通す必要がある。
- SA（継承）の影響: 録音をそのまま、または加工して BGM にする場合、ゲーム全体ではなく「録音（の改変物）」に同じ CC BY-SA を継承する必要がある、というのが一般的解釈。ゲーム全体のコードやアセットに感染するかは解釈が割れるので、使うなら法務判断が必要。
- 確認できなかった点: 演奏団体自身が CC を許諾した証拠（IMSLP の投稿者 Cypressdome は団体の関係者かもしれないが不明）。

### D. Columbia University Orchestra 2002（IA、publicdomain 表記）【要注意】

- ページ: https://archive.org/details/Dvorak_Symphony_9
- ライセンス: `http://creativecommons.org/licenses/publicdomain/`（旧 "Public Domain Dedication" 系の表記）
- アップロード者: angelchen1111（IA ユーザー名。2007-01-02 最終更新）。説明欄なし。ファイルコメントに指揮者として Jeffrey Milarsky の記載あり。
- 直接ダウンロードURL:
  - https://archive.org/download/Dvorak_Symphony_9/01.Adagio-Allegro_Molto.ogg （590.0秒）
  - https://archive.org/download/Dvorak_Symphony_9/02.Largo.ogg （685.0秒）
  - https://archive.org/download/Dvorak_Symphony_9/03.Scherzo-Molto_vivace.ogg （484.5秒）
  - https://archive.org/download/Dvorak_Symphony_9/04.Allegro_con_fuoco.ogg （702.3秒）
  - `.mp3`（128kbps）も同名で存在。
- **要注意の理由**: 2002年の学生オーケストラの演奏会録音。PD になる年代ではなく、PD 表記はアップロード者の宣言のみ。演奏者全員・大学側の許諾が取れているかは確認できない。権利が曖昧なため、商用製品には使わないのが安全。

### E. Iturbi / Rochester Philharmonic 1941（IA、CC0 表記）【要注意】

- ページ: https://archive.org/details/SymphonyNo.9fromTheNewWorld
- 説明: "Jose Iturbi conducts the Rochester Philharmonic Orchestra. The transfer is from the original Victor 78 set DM-899 by Bob Varney." 録音は 1941 年。公開 2012-10-27。
- ライセンス: `http://creativecommons.org/publicdomain/zero/1.0/`
- 直接ダウンロードURL: https://archive.org/download/SymphonyNo.9fromTheNewWorld/01_adagio_allegroMolto.ogg （511.3秒）、`02_Largo.ogg`（685.1秒）、`03_scherzo_moltoVivace.ogg`（420.5秒）、`04_allegroCoFuoco.ogg`（619.0秒）。
- **要注意の理由**: 移し替え担当の Bob Varney が CC0 を宣言しているが、Victor/RCA 側の録音権や実演家の権利を持つ者ではない。1941年の録音は、計算上（発行年から100年）は米国でまだ 2041年末まで保護される可能性がある（2042-01-01 に PD。弁護士確認は未了）。他国（日本・EU）では切れている可能性が高いが、ゲームを世界配信するなら米国が最大の市場。

### F. Szell / Czech Philharmonic 1937（IA、publicdomain 表記）【要注意】

- ページ: https://archive.org/details/DvorakSymphonyNo.9fromTheNewWorld
- 説明: 1937 年プラハ録音、Victor DM 469 から Bob Varney が復元。2018年8月に音質向上のため再録音（移し替え）。
- ライセンス: `http://creativecommons.org/licenses/publicdomain/`
- 直接ダウンロードURL: https://archive.org/download/DvorakSymphonyNo.9fromTheNewWorld/01_Adagio-AlegroMolto.mp3 （506.1秒）、`02_Largo.mp3`（685.9秒）、`03_Scherzo-MoltoVivace.mp3`（466.0秒）、`04_AllegroConFuoco.mp3`（626.2秒）。Ogg なし。
- **要注意の理由**: Eと同様。移し替え者の宣言だけで、1937録音の米国での権利は残っている可能性が高い。
- 別アップロード（F. Reeder 版）は `DvorakSymphonyNo.9InEMinorOp.95-1937` で、こちらは **CC BY-NC-SA 3.0** → **ゲーム商用不可の可能性。使わない**。

### G. Musopen 由来（Wikimedia Commons）【要注意】

4楽章分のファイルが Commons にある（すべて Musopen 起源、2008年1月に Raul654 氏らがアップロード）。

| 楽章 | Commons ファイル | 長さ | 直接URL |
|---|---|---|---|
| I | Antonin_Dvorak_-_symphony_no._9_in_e_minor_'from_the_new_world',_op._95_-_i._adagio_-_allegro_molto.ogg | 10:05 | https://upload.wikimedia.org/wikipedia/commons/5/5c/Antonin_Dvorak_-_symphony_no._9_in_e_minor_%27from_the_new_world%27%2C_op._95_-_i._adagio_-_allegro_molto.ogg |
| II | ...-_ii._largo.ogg | 11:34 | https://upload.wikimedia.org/wikipedia/commons/c/c3/Antonin_Dvorak_-_symphony_no._9_in_e_minor_%27from_the_new_world%27%2C_op._95_-_ii._largo.ogg |
| III | ...-_iii._molto_vivace.ogg | 8:26 | https://upload.wikimedia.org/wikipedia/commons/b/bd/Antonin_Dvorak_-_symphony_no._9_in_e_minor_%27from_the_new_world%27%2C_op._95_-_iii._molto_vivace.ogg |
| IV | ...-_iv._allegro_con_fuoco.ogg | 11:43 | https://upload.wikimedia.org/wikipedia/commons/1/17/Antonin_Dvorak_-_symphony_no._9_in_e_minor_%27from_the_new_world%27%2C_op._95_-_iv._allegro_con_fuoco.ogg |

- ライセンス表記（原文）: 「This work has been released into the public domain by its author, Musopen. This applies worldwide.」「grants anyone the right to use this work for any purpose」。I 楽章のページには "allows anyone to use it for any purpose, provided that the copyright holder is properly attributed." の文言もあり。III 楽章のページには CC BY-SA 4.0 のバナーも併記されている（表記が揺れている）。
- 演奏者欄: 「(see Musopen for author information)」のみ。**誰の演奏か、いつの録音かは Commons 上では不明**。
- Musopen 本体（https://musopen.org/music/2693-... と /4942-...）は **403 で取得できず**、演奏者を確認できなかった。Web 検索結果によれば Musopen は「アップロードする者は PD であることを表明保証する」規約とのことだが、これは Musopen 側の自己申告にすぎない。
- クレジット: 表記上は不要だが、Commons の説明に「credit を」の文言があるため、「Musopen」を併記しておくのが安全。
- **判定を △ にした理由**: 演奏者・録音年・権利の根拠が一次情報で確認できないため。「使える」とは書けない。Musopen 本体の記載が確認できるまでは保留。

### H. Landon Ronald 1927（Commons、PD Mark）

Commons にあるのは、レコード面ごとの断片 4 つのみ。完全な 4 楽章ではない。

| ファイル（楽章・レコード面） | 長さ | 直接URL |
|---|---|---|
| 2nd Movement, Largo, 3rd record（HMV D1252-5-0518） | 3:47 | https://upload.wikimedia.org/wikipedia/commons/6/6a/PDP-CH_-_Royal_Albert_Hall_Orchestra_-_Landon_Ronald_-_Symphony_No._9%2C_in_E_minor%2C_op._95_-_2nd_Movement%2C_Largo%2C_3rd_record_-_Anton%C3%ADn_Dvo%C5%99%C3%A1k_-_Hmv-d1252-5-0518.flac |
| 3rd Movement, Scherzo, 1st record（D1252-5-0519） | 3:27 | https://upload.wikimedia.org/wikipedia/commons/4/4f/PDP-CH_-_Royal_Albert_Hall_Orchestra_-_Landon_Ronald_-_Symphony_No._9%2C_in_E_minor%2C_op._95_-_3rd_Movement%2C_Scherzo%2C_Molto_Vivace%2C_1st_record_-_Anton%C3%ADn_Dvo%C5%99%C3%A1k_-_Hmv-d1252-5-0519.flac |
| 3rd Movement, Scherzo, 2nd record（D1253-5-0520） | 3:51 | https://upload.wikimedia.org/wikipedia/commons/1/18/PDP-CH_-_Royal_Albert_Hall_Orchestra_-_Landon_Ronald_-_Symphony_No._9%2C_in_E_minor%2C_op._95_-_3rd_Movement%2C_Scherzo%2C_Molto_vivace%2C_2nd_record_-_Anton%C3%ADn_Dvo%C5%99%C3%A1k_-_Hmv-d1253-5-0520.flac |
| 4th Movement, Allegro con fuoco, 1st record（D1253-5-0521） | 3:32 | https://upload.wikimedia.org/wikipedia/commons/b/bd/PDP-CH_-_Royal_Albert_Hall_Orchestra_-_Landon_Ronald_-_Symphony_No._9%2C_in_E_minor%2C_Op._95_-_4th_Movement%2C_Allegro_con_fuoco%2C_1st_record_-_Anton%C3%ADn_Dvo%C5%99%C3%A1k_-_Hmv-d1253-5-0521.flac |

- bgm-sources.csv のランクは C（断片で PD Mark の宣言のみ。1927年録音は計算上、米国で 2028-01-01 まで保護期間内）。
- 録音年: 1927（"1st recording date: 1 January 1927" と表示）。出典は Public Domain Project（Musical Heritage）。
- ライセンス表記（原文）: 「This file has been identified as being free of known restrictions under copyright law, including all related and neighboring rights.」（Creative Commons Public Domain Mark 1.0）。
- 形式: FLAC。サイズが 1 ファイル 120〜140MB と大きい（3〜4 分で）。ほぼ非圧縮に近いのでゲームに入れるなら変換が必要。
- 注意: 第2楽章ファイルのページの "Content" 欄は "2nd Movement: Largo (3rd Record)" だが、ファイル名の 0519（3rd Movement, 1st record）のページでも同じ記述が出る。メタデータの不整合がある。
- 確認できなかった点: Commons 側に "1978年1月1日時点で米国 PD" の記述がある旨を検索結果で見たが、一次ページでは原文を確認できなかった。

### I. Landon Ronald 1919–21（IA、ライセンス欄なし）

- ページ: https://archive.org/details/d-613-dvorak-new-world-iv
- 説明: Royal Albert Hall Orchestra / Landon Ronald、1919 年と 1921 年に HMV Hayes スタジオで録音、1921–22 に分売。「初の全曲に近い録音（やや省略）」。
- ライセンス欄: **なし**。権利表記も空。
- 直接URL例: https://archive.org/download/d-613-dvorak-new-world-iv/D536%20Dvorak%20New%20World%20(i).flac など（i〜iv、各 FLAC / MP3。7:42〜8:08）。
- 録音年（1919–21）は 1923年より前なので、計算上は米国で既に PD の年代（ただし実際の録音年・発行年は未確認）。IA 上の明示ライセンスがないので「使える」とは書かない。音質は音響録音で低い。

## 3. 抜粋・部分・編曲のみのもの

| 内容 | 演奏者 | 年 | 長さ | ライセンス表記 | 備考 |
|---|---|---|---|---|---|
| 第1楽章の抜粋 | hr-Sinfonieorchester（Frankfurt Radio Symphony）/ Andrés Orozco-Estrada | 2018-05-25 | 2:33 | "This file is licensed under the Creative Commons Attribution-Share Alike 4.0 International license." | https://upload.wikimedia.org/wikipedia/commons/5/5b/Anton%C3%ADn_Dvo%C5%99%C3%A1k_Symphony_no._9_1st_movement_excerpt.mp3 。BY-SA。抜粋のみ |
| 第2楽章（打ち込み） | Reinhold Behringer（Virtual Philharmonic Orchestra、Garritan Personal Orchestra 4 によるサンプル音源） | 2010 | 9:37 | GFDL / CC BY-SA 4.0 他 | https://upload.wikimedia.org/wikipedia/commons/7/72/Dvorak_S9M2_100501.ogg 。人間の演奏ではない |
| 全曲（MuseScore 4 + MuseSounds 打ち込み） | Omega13a（Commons） | 2026-09 | 35:58 | "This file is licensed under the Creative Commons Attribution 4.0 International license." | https://upload.wikimedia.org/wikipedia/commons/2/2b/Symphony_No.9%2C_Op.95_%E2%80%93_Anton%C3%ADn_Dvo%C5%99%C3%A1k.oga 。CC BY で商用可の可能性が高いが、音源（MuseSounds）のライセンス上、レンダリング音声の再配布が許されるかは未確認 |
| 全曲（シンセ/MIDI） | Brandon Amaro（IMSLP） | 2024 | 35:54 | "Creative Commons Attribution-ShareAlike 4.0" | MP3、IMSLP #922879 |
| 「Goin' Home」（Largo 主題のバンド編曲） | United States Air Force Band | 2004 | 3:07 | 米軍職員の公務成果として米国で PD（Commons 原文要旨） | https://upload.wikimedia.org/wikipedia/commons/7/74/%22Goin%27_Home%22%2C_performed_by_the_United_States_Air_Force_Band.oga 。編曲は 1994 年の Jari Villanueva。編曲者の権利が別にある可能性。出典が YouTube |
| 第4楽章の約3分抜粋 | LoxLok | 2007 | 3:00 | `licenses/publicdomain/` | https://archive.org/details/Dvorak-newWorldAllegroComFuoco 。演奏者不明 → 使わない |

## 4. 使えない / 使わない（理由つき）

| 録音 | 理由 |
|---|---|
| Bernstein / NYP 1962（IMSLP #708958–61）、Szell / Cleveland 1953（IMSLP #725663–66）、Silvestri / Orchestre national de France 1959（#430470）、Ackermann / Tonhalle-Orchester Zürich 1955（#533060） | IMSLP の表記は "Public Domain" – "Non-PD US"。**米国では PD ではない**ことを示す。1950〜60年代の商業録音なので、日本・米国の商用配布には使わない |
| Szell / Czech Philharmonic 1937（F. Reeder 版）`DvorakSymphonyNo.9InEMinorOp.95-1937` | `licenseurl: http://creativecommons.org/licenses/by-nc-sa/3.0/` → **NC のため、ゲーム商用不可の可能性** |
| Stokowski / Philadelphia 1934（F. Reeder 版）`DVORAKSymphonyNo.9NewWorld-Stokowski-NEWTRANSFER` | 同上 CC BY-NC-SA 3.0 → **商用不可の可能性** |
| Szell / Cleveland 1952（F. Reeder 版）`DvorakSymphonyNo.9newWorld-Szell-cleveland` | 同上 CC BY-NC-SA 3.0 → **商用不可の可能性** |
| Stokowski / Philadelphia 1934（別アップロード）`Dvorak_symphony9-1934` | ライセンス欄なし。1934 年録音は米国でまだ保護期間内の可能性 |
| the carport orchestra「largo」`largo_128`、「new world」`new-world_202312` | CC BY-NC-SA 3.0 / 4.0 → **商用不可の可能性**。しかも演奏の実体が不明 |
| Sound-stretched Classics「Largo (Dvořák)」 | CC BY-NC-SA 3.0 → **商用不可の可能性**。引き伸ばし加工 |
| IA 上の LP 取り込み（Kubelik、Bernstein、Szell、Karajan、Ormandy、Toscanini、Reiner 等） | ライセンス欄なし。1950年代以降の商業録音で、PD の根拠なし |
| Musopen Kickstarter 2012 の DVD / FLAC コレクション | 収録リストに Dvořák 交響曲第9番は**含まれない**（弦楽四重奏「アメリカ」等のみ）。`musopen-dvd` の説明で確認 |

## 5. 確認できなかったこと（総括）

- **Musopen 本体（musopen.org）は全ページ 403**。演奏者、録音年、個別ライセンスの一次情報なし。ブラウザで人間が見る必要あり。
- **IMSLP のファイルページ**は JS 遷移と同意画面があり、直リンクのダウンロードURLは確認できなかった。IMSLP ページ側の件数表示は「15 recordings」だが、取得できたテキストには 7 件しか出ていない（残りは未確認）。
- 米国での録音の著作権保護期間（1925→2026-01-01 から PD、1927→2028-01-01、1934→2035-01-01、1937→2038-01-01、1941→2042-01-01。計算式は冒頭参照）は、計算上の値で、法的に確定した一次情報ではない（弁護士確認は未了）。商用リリース前に法務確認が望ましい。
- 調べきれていないサイト: Free Music Archive、Jamendo、Europeana、Library of Congress National Jukebox（Dvořák 9 全曲の検索はしていない）、YouTube/Bandcamp 等。IA の検索は ElasticSearch エラーが出たため、上記の一覧が網羅とは言い切れない（309 件ヒットのうち 200 件のみ確認）。
- 「CC0 / PD 表記」を付けた人（Bob Varney 等）が録音の権利者であるかどうかは、どのアイテムでも確認できなかった。

## 6. 推奨順（現時点の判断。最終決定は人間が行う）

（注記）録音の記号は「表のB」のように「表の」を付け、ランクは「ランクA」のように「ランク」を付けて書く。両者は別物。

1. **表のB: Stokowski 1925（CC BY 3.0、ランクA）** — 第一候補。全4楽章、OGG あり、計算上、米国で 2026-01-01 から PD（弁護士確認は未了）。クレジットは慣行として付ける。
2. **表のA: Stokowski 1927（CC0、ランクC）** — 音質・聴き比べ用。米国では 2028-01-01 まで保護期間内（計算上）で、CC0 はアップロード者の宣言のみ。公開・商用には使わない。
3. **表のC: DuPage SO 2012（CC BY-SA 3.0、ランクB）** — 現代の録音が必要な場合のみ。SA の扱いを判断してから。
4. 表の G（Musopen 由来）は、Musopen 本体で演奏者・権利を確認できたら格上げを検討。
5. 表の D・E・F は使わない（権利の根拠が薄い）。
