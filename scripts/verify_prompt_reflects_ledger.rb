#!/usr/bin/env ruby
# frozen_string_literal: true

# 台帳（docs/ledger/*.yaml）の内容が、生成される imagegen 編集プロンプトに漏れなく反映されているかを検査する。
#   ruby scripts/verify_prompt_reflects_ledger.rb                 # 全MAPのプロンプトを導出して検査。違反があれば exit 1
#   ruby scripts/verify_prompt_reflects_ledger.rb --from-json F   # 導出済みの JSON（oblique_prompt_probe.py の出力）を使う
#   ruby scripts/verify_prompt_reflects_ledger.rb --maps TRM-05,TRM-05-fire   # 対象MAPを絞る
#   LEDGER_ROOT=/path/to/root ...                                 # root 差し替え（テスト用）
#
# プロンプトは tools/oblique_prompt_probe.py が oblique_build と同じ導出で作る（画像生成 API は呼ばない）。
# 必須キーが揃わないMAPは oblique_build のゲートで止まるので『ゲートで停止』として対象外に表示する。
#
# 検査（生成可能なMAPごと）:
#   (i)   そのMAPに該当する有効な決定のうち プロンプト出力=必須 のものは、[決定ID] と決定の要点が逐語で DECISIONS 節に現れ、
#         必須語が（注記を除いた本文に）現れ、禁止語は決定・FORBIDDEN 節・否定表現・決定参照つき行以外に現れない
#   (ii)  採用要素（継承要素）: [採用要素ID]・要素・確認語がプロンプトに現れる。素材IDが有る有効な行は、元MAPの採用画像が
#         REFERENCE IMAGES に（素材表と同じパスで）現れる
#   (iii) 特徴(自由記述)は MAP・建物・部位・窓列・要素・窓・端・採用要素・決定のどれも FEATURES 節（決定は DECISIONS 節）にそのまま現れる
#   (iv)  建物窓列に紐づく窓（渡り廊下棟の連窓など）が、その窓を持つ全MAP（屋内・外観）の WINDOWS 節に個数・位置つきで一致して現れる
#   (v)   回帰アンカー: 過去に漏れた事例（畳・化石の石・-fire の勝手口・火事版の上半分・渡り廊下の窓列）を台帳側の件数に依らず
#         固定の期待で検査する（台帳から記述を消されても検出するため、ここに期待をハードコードする）
#   (vi)  時期差分MAP（-kids・-fire など。台帳 時期差分 に行があるもの）は、基準MAPを依存MAPに持ち、REFERENCE IMAGES に基準MAPの行
#         （確定画像のパス、未採用なら『未確定』）と台帳 プロンプト文面.PR.reference.base-era の使い方の文が現れる（#193）。
#         TRM-05-kids・TRM-05-fire は台帳側の依存を消されても検出するよう、基準MAPをここにもハードコードする
require 'json'
require 'open3'
require 'shellwords'
require_relative 'ledger_yaml'

class PromptReflection
  VARIANT_RE = /-(kids|fire|burnt|wc)\z/.freeze
  # 否定・指示の文脈（禁止語がそのまま書いてあっても『描かない』と言っているだけの節）。
  # 否定は禁止語と**同じ節**（。、，,；; 区切り）にあるものだけが免除になる。行単位で除外すると、同じ行の別の文にある禁止語
  # （『い草色の畳敷き（寝室）。ピンクは残さない、壁は描かない。』の畳）が否定のせいで見逃される。
  NEGATION_RE = /描かない|使わない|置かない|入れない|足さない|でなく|ではなく|にせず|禁止|不可|（決定 /.freeze
  CLAUSE_SPLIT = /[。、，,；;]/.freeze
  PROBE = '.claude/skills/sit-field-background/tools/oblique_prompt_probe.py'

  # 過去に漏れた事例。maps の全MAPで: decisions の [決定ID] と要点が現れ、words が現れ、
  # leak（正規表現）は決定・否定表現の行以外に現れない。door_wall は『勝手口』を含む行に別の壁方角を書かない。
  ANCHORS = [
    { id: 'tatami', maps: %w[TRM-02 TRM-03 TRM-04 TRM-05 TRM-05-kids TRM-05-fire], decisions: %w[TRM.no-tatami], leak: /(?<!石)畳/,
      what: '畳の語（畳を描かない決定が出て、畳が本文に漏れない）' },
    { id: 'fossil-stone', maps: %w[TRM-05 TRM-05-kids TRM-05-fire], decisions: %w[TRM-05.fossil TRM-05.stone-pos], words: %w[茶色と黒 右上隅],
      leak: /アンモナイト/, what: '化石の石（決定表から展開される）' },
    { id: 'fossil-state', maps: %w[TRM-05-fire], decisions: %w[TRM-05.fossil-state], words: %w[割れかけ], what: '火事版の化石の状態' },
    { id: 'door-back-fire', maps: %w[TRM-05-fire], decisions: %w[TRM-05.door-back TRM-05.door-back-fire], words: %w[北壁 燃えカス],
      door_wall: '北壁', what: '-fire の勝手口は北壁（西壁などにならない）' },
    { id: 'fire-upper-half', maps: %w[TRM-05-fire], decisions: %w[TRM-05-fire.upper-half TRM-05.fire], words: %w[上半分だけ 上半分], what: '火事版は上半分だけが燃える指示' },
    { id: 'corridor-windows', maps: %w[TRM-03 TRM-04], decisions: %w[TRM.building-shared], words: %w[連窓],
      corridor: { 'BLD-TRM-corridor-w.south-wins' => 3, 'BLD-TRM-corridor-e.south-wins' => 3 }, what: '渡り廊下棟の窓列（屋内・外観で一致）' }
  ].freeze

  attr_reader :errors, :skipped, :checked

  def initialize(records, root: LedgerYaml::ROOT, only: nil)
    @root = root
    @t = LedgerYaml.load_all
    @records = records.select { |r| only.nil? || only.include?(r['map_id']) }
    @errors = []
    @skipped = []
    @checked = []
  end

  def err(map_id, msg) = @errors << "#{map_id}: #{msg}"
  def base_of(id) = id.sub(VARIANT_RE, '')
  def era_of(id) = id == base_of(id) ? '' : id[(base_of(id).size + 1)..]
  def split(s) = s.to_s.split(';').map(&:strip).reject(&:empty?)

  def expand(spec)
    split(spec).flat_map do |tok|
      m = tok.match(/\ATRM-(\d\d)\.\.TRM-(\d\d)\z/)
      m ? (m[1].to_i..m[2].to_i).map { |n| format('TRM-%02d', n) } : [tok]
    end
  end

  def targets?(map_id, spec)
    toks = expand(spec)
    toks.include?(map_id) || toks.include?(base_of(map_id))
  end

  def run
    @records.each do |rec|
      id = rec['map_id']
      unless rec['gated'].to_a.empty?
        @skipped << [id, rec['gated']]
        next
      end
      @checked << id
      @prompt = rec['prompt']
      @lines = @prompt.lines.map(&:chomp)
      check_decisions(id)
      check_inherits(id)
      check_free_text(id)
      check_window_rows(id)
      check_base_reference(id)
    end
    check_anchors
    self
  end

  # ---- プロンプトの節
  # 見出し行（大文字英字で始まり（か:で終わる）から次の空行まで
  def section(prefix)
    i = @lines.index { |l| l.start_with?(prefix) }
    return [] unless i

    @lines[(i + 1)..].take_while { |l| !l.strip.empty? }
  end

  def sections_prefixed(prefix)
    @lines.each_index.select { |i| @lines[i].start_with?(prefix) }.map { |i| @lines[(i + 1)..].take_while { |l| !l.strip.empty? } }
  end

  def decision_lines = section('DECISIONS（')

  # 注記（必須語/禁止語）を除いた決定行の本文
  def strip_annot(line) = line.sub(/（(?:必須語: [^）]*)?(?: \/ )?(?:禁止語: [^）]*)?）\z/, '')

  def forbidden_section = section('FORBIDDEN（')

  # 禁止語の漏れ検査から除外する行: DECISIONS 節・FORBIDDEN 節・否定/決定参照つき行
  # 『石畳』のように禁止語を部分に含む別の語は漏れとして数えない（COMPOUND_OK）。採用要素の節は台帳の引用なので
  # 一般の禁止語検査からは外す（扉の『下半分』など別の意味の同語がある）。回帰アンカーの leak は採用要素も見る。
  COMPOUND_OK = { '畳' => %w[石畳] }.freeze

  def leak_lines(with_inherited: false)
    excluded = decision_lines + forbidden_section
    excluded += section('INHERITED ELEMENTS（') unless with_inherited
    @lines.reject { |l| excluded.include?(l) }
  end

  # 行の中で、述語に一致する節（否定を含む節は除く）。無ければ nil。
  # negation: false（回帰アンカー）は否定表現でも免除しない。免除するのは次の2つだけ（部分文字列では免除しない）:
  #   (a) 有効な決定の『決定の要点』を同じ区切り（CLAUSE_SPLIT）で分けた節のどれかと**完全一致**する節（決定の逐語の引用）
  #   (b) 行末に『（決定 X）』の注記があり、X が全て台帳の決定IDである展開文の節（要素の見た目などが決定参照で展開された文）
  def leaking_clause(line, negation: true)
    return nil if !negation && annotated_expansion?(line)

    clauses = line.split(CLAUSE_SPLIT)
    clauses.each_with_index.find do |c, i|
      next false unless yield(c)

      negation ? !(c.match?(NEGATION_RE) || enumerated_under_negation?(c, clauses[i + 1])) : !decision_clauses.include?(c.strip)
    end&.first
  end

  # 『畳、襖は描かない』のように、述語のない短い名詞だけの節の直後の節が否定なら、同じ否定の列挙とみなす（既知の制約: README）。
  # 述語を持つ節（は・を・が・に・で・も を含む、または9字以上）は列挙とみなさない（『畳、ござを敷く。』の畳は漏れ）
  BARE_NOUN_RE = /\A[^はをがにでも]{1,8}\z/.freeze

  def enumerated_under_negation?(clause, following)
    !following.nil? && following.match?(NEGATION_RE) && clause.strip.match?(BARE_NOUN_RE)
  end

  def annotated_expansion?(line)
    m = line.match(/（決定 ([^）]+)）\s*\z/)
    return false unless m

    ids = m[1].split(/[,、\s]+/).reject(&:empty?)
    !ids.empty? && ids.all? { |i| @t['決定'].any? { |d| d['決定ID'] == i && d['状態'] == '有効' } }
  end

  def decision_clauses
    @decision_clauses ||= @t['決定'].select { |d| d['状態'] == '有効' }.flat_map { |d| d['決定の要点'].split(CLAUSE_SPLIT).map(&:strip) }.reject(&:empty?)
  end

  def mentions?(line, word)
    COMPOUND_OK.fetch(word, []).reduce(line) { |acc, c| acc.gsub(c, '') }.include?(word)
  end

  # ---- (i)
  def active_decisions(map_id)
    @t['決定'].select { |d| d['状態'] == '有効' && d['プロンプト出力'] == '必須' && targets?(map_id, d['対象MAP']) }
  end

  def check_decisions(map_id)
    dl = decision_lines
    leak = leak_lines
    active_decisions(map_id).each do |d|
      did = d['決定ID']
      line = dl.find { |l| l.start_with?("- [#{did}] ") }
      unless line
        err(map_id, "決定 #{did} がプロンプトの DECISIONS 節に現れない（プロンプト出力=必須・有効・対象MAP）")
        next
      end
      err(map_id, "決定 #{did} の要点が DECISIONS 節に逐語で現れない（台帳『決定の要点』と違う）") unless strip_annot(line).include?(d['決定の要点'])
      split(d['必須語']).each do |w|
        err(map_id, "決定 #{did} の必須語『#{w}』がプロンプト本文に現れない") unless dl.map { |l| strip_annot(l) }.concat(@lines - dl).any? { |l| l.include?(w) }
      end
      split(d['禁止語']).each do |w|
        hit = leak.map { |l| leaking_clause(l) { |c| mentions?(c, w) } }.compact.first
        err(map_id, "決定 #{did} の禁止語『#{w}』がプロンプトに現れる: 「#{hit.strip[0, 80]}」") if hit
      end
    end
  end

  # ---- (ii)
  def check_inherits(map_id)
    inh = section('INHERITED ELEMENTS（')
    refs = section('REFERENCE IMAGES（')
    @t['採用要素'].select { |a| %w[有効 記録].include?(a['状態'].split('（').first) && targets?(map_id, a['継承先MAP']) }.each do |a|
      aid = a['採用要素ID']
      line = inh.find { |l| l.start_with?("- [#{aid}] ") }
      unless line
        err(map_id, "採用要素 #{aid} がプロンプトの INHERITED ELEMENTS 節に現れない")
        next
      end
      [['要素', a['要素']], ['内容', a['内容']], ['確認語', a['確認語']]].each do |label, w|
        err(map_id, "採用要素 #{aid} の#{label}『#{w[0, 30]}』がプロンプトに現れない") if !w.empty? && !line.include?(w)
      end
      next if a['素材ID'].empty? # 採用画像の確定前（記録）はプロンプトだけ

      mat = @t['素材'].find { |m| m['素材ID'] == a['素材ID'] }
      path = mat && mat['パス']
      if mat.nil? || path.to_s.empty?
        err(map_id, "採用要素 #{aid}: 素材 #{a['素材ID']} が素材表に無い、またはパスが空（参考画像にできない）")
      elsif refs.none? { |l| l.start_with?("- #{a['元MAP']}: #{path}") }
        err(map_id, "採用要素 #{aid}: 元MAP #{a['元MAP']} の採用画像 #{path} が REFERENCE IMAGES に現れない（plan の depends_on か素材表を確認）")
      end
    end
  end

  # ---- (vi)
  REQUIRED_BASE = { 'TRM-05-kids' => 'TRM-05', 'TRM-05-fire' => 'TRM-05' }.freeze

  def check_base_reference(map_id)
    era = era_of(map_id)
    return if era.empty?

    base = base_of(map_id)
    in_ledger = @t['時期差分'].any? { |r| r['MAP_ID'] == base && r['時期'] == era }
    return unless in_ledger || REQUIRED_BASE.key?(map_id)

    deps = @t['時期差分'].select { |r| r['MAP_ID'] == base && r['時期'] == era && r['項目'] == '依存' }.flat_map { |r| split(r['値']) }
    err(map_id, "時期差分MAPの依存に基準MAP #{base} が無い（台帳 時期差分.依存。基準の確定画像を参照に含める #193）") unless deps.include?(base)
    refs = section('REFERENCE IMAGES（')
    err(map_id, "基準MAP #{base} が REFERENCE IMAGES に現れない（時期差分MAPは基準の確定画像、未採用なら『未確定』で blocked を示す）") unless refs.any? { |l| l.start_with?("- #{base}: ") }
    tpl = @t['プロンプト文面'].find { |r| r['文面ID'] == 'PR.reference.base-era' }
    if tpl.nil?
      err(map_id, '台帳 プロンプト文面.PR.reference.base-era が無い')
    elsif refs.none? { |l| l == tpl['文面'].gsub('{base}', base).gsub('{era}', era) }
      err(map_id, "基準参照の使い方の文（プロンプト文面.PR.reference.base-era）が REFERENCE IMAGES 節に現れない")
    end
  end

  # ---- (iii)
  def free_texts(map_id)
    base = base_of(map_id)
    era = era_of(map_id)
    m = @t['MAP'].find { |r| r['MAP_ID'] == base }
    bids = m ? split(m['建物ID']) - %w[該当なし なし] : []
    out = []
    out << ['MAP', m['MAP_ID'], m['特徴(自由記述)']] if m
    @t['エリア'].select { |a| m && a['エリアID'] == m['エリアID'] }.each { |a| out << ['エリア', a['エリアID'], a['特徴(自由記述)']] }
    @t['建物'].select { |b| bids.include?(b['建物ID']) }.each { |b| out << ['建物', b['建物ID'], b['特徴(自由記述)']] }
    @t['建物部位'].select { |p| bids.include?(p['建物ID']) }.each { |p| out << ['建物部位', p['部位ID'], p['特徴(自由記述)']] }
    @t['建物窓列'].select { |w| bids.include?(w['建物ID']) }.each { |w| out << ['建物窓列', w['窓列ID'], w['特徴(自由記述)']] }
    @t['建物関係'].select { |r| bids.include?(r['建物A']) || bids.include?(r['建物B']) }.each { |r| out << ['建物関係', r['通番'], r['特徴(自由記述)']] }
    @t['建物時期差分'].select { |r| bids.include?(r['建物ID']) && r['時期'] == era }.each { |r| out << ['建物時期差分', "#{r['建物ID']}/#{r['時期']}/#{r['部位ID']}", r['特徴(自由記述)']] }
    { '要素' => '要素ID', '窓' => '窓ID', '端' => '端ID' }.each do |tbl, key|
      @t[tbl].select { |r| r['MAP_ID'] == base && ['', era].include?(r['適用時期']) }.each { |r| out << [tbl, r[key], r['特徴(自由記述)']] }
    end
    @t['接続'].select { |r| r['端A'].split('.').first == base || r['端B'].split('.').first == base }.each { |r| out << ['接続', "#{r['端A']}⇄#{r['端B']}", r['特徴(自由記述)']] }
    @t['素材'].select { |r| base_of(r['所有者ID']) == base && r['状態'] == '採用' }.each { |r| out << ['素材', r['素材ID'], r['特徴(自由記述)']] }
    @t['採用要素'].select { |a| %w[有効 記録].include?(a['状態'].split('（').first) && targets?(map_id, a['継承先MAP']) }.each { |a| out << ['採用要素', a['採用要素ID'], a['特徴(自由記述)']] }
    out.reject { |_, _, t| t.to_s.empty? }
  end

  def check_free_text(map_id)
    feat = section('FEATURES（').join("\n")
    free_texts(map_id).each do |tbl, id, text|
      err(map_id, "#{tbl} #{id} の特徴(自由記述)が FEATURES 節にそのまま現れない: 「#{text[0, 40]}」") unless feat.include?(text)
    end
    dl = decision_lines.join("\n")
    active_decisions(map_id).each do |d|
      t = d['特徴(自由記述)']
      err(map_id, "決定 #{d['決定ID']} の特徴(自由記述)がプロンプトに現れない: 「#{t[0, 40]}」") if !t.empty? && !@prompt.include?(t) && !dl.include?(t)
    end
  end

  # ---- (iv)
  def window_rows(map_id)
    base = base_of(map_id)
    era = era_of(map_id)
    @t['窓'].select { |w| w['MAP_ID'] == base && ['', era].include?(w['適用時期']) && !w['建物窓列ID'].empty? }.group_by { |w| [w['壁'], w['建物窓列ID']] }
  end

  def expected_positions(row)
    n = row['個数'].to_i
    return [] if n.zero? || row['先頭比'].empty? || row['間隔比'].empty?

    (0...n).map { |i| row['先頭比'].to_f + (i * row['間隔比'].to_f) }
  end

  # WINDOWS 節の『壁 ID（…）: N枚の…。left to right: #1 at 0.17, …』から [N, [位置]] を取る
  def parse_window_line(wall)
    line = section('WINDOWS（').find { |l| l.start_with?("- 壁 #{wall}（") || l.start_with?("- 壁 #{wall}:") }
    return nil unless line

    n = line[/: (\d+)枚の/, 1]
    pos = line.scan(/#\d+ at ([0-9.]+)/).flatten.map(&:to_f)
    [n&.to_i, pos, line]
  end

  def check_window_rows(map_id)
    window_rows(map_id).each do |(wall, rid), wins|
      row = @t['建物窓列'].find { |r| r['窓列ID'] == rid }
      unless row
        err(map_id, "窓 #{wins.first['窓ID']} が参照する建物窓列 #{rid} が台帳に無い")
        next
      end
      parsed = parse_window_line(wall)
      unless parsed
        err(map_id, "建物窓列 #{rid}（壁 #{wall}）の窓が WINDOWS 節に現れない")
        next
      end
      n, pos, = parsed
      err(map_id, "建物窓列 #{rid}（壁 #{wall}）: 個数 #{row['個数']} のはずが WINDOWS 節では #{n.inspect} 枚") if n != row['個数'].to_i
      err(map_id, "建物窓列 #{rid}: 台帳の窓（窓表）が #{wins.size} 個で個数 #{row['個数']} と違う") if wins.size != row['個数'].to_i
      exp = expected_positions(row)
      next if exp.empty?

      if pos.size != exp.size || pos.zip(exp).any? { |a, b| (a - b).abs > 0.015 }
        err(map_id, "建物窓列 #{rid}（壁 #{wall}）: WINDOWS 節の位置 #{pos} が台帳（先頭比・間隔比）の #{exp.map { |x| x.round(2) }} と一致しない")
      end
    end
  end

  # ---- (v)
  def check_anchors
    by_id = @records.to_h { |r| [r['map_id'], r] }
    all_ids = @t['決定'].map { |d| d['決定ID'] }
    ANCHORS.each do |a|
      a[:maps].each do |mid|
        rec = by_id[mid]
        next if rec.nil? # --maps で絞った場合など

        if rec['gated'].to_a.any?
          err(mid, "回帰アンカー #{a[:id]}（#{a[:what]}）: このMAPがゲートで止まっていて検査できない")
          next
        end
        @prompt = rec['prompt']
        @lines = @prompt.lines.map(&:chomp)
        dl = decision_lines
        a[:decisions].each do |did|
          err(mid, "回帰アンカー #{a[:id]}（#{a[:what]}）: 決定 #{did} が台帳に無い") unless all_ids.include?(did)
          d = @t['決定'].find { |x| x['決定ID'] == did }
          err(mid, "回帰アンカー #{a[:id]}: 決定 #{did} が有効・プロンプト出力=必須・対象MAP になっていない") if d && !(d['状態'] == '有効' && d['プロンプト出力'] == '必須' && targets?(mid, d['対象MAP']))
          err(mid, "回帰アンカー #{a[:id]}（#{a[:what]}）: [#{did}] がプロンプトの DECISIONS 節に現れない") unless dl.any? { |l| l.start_with?("- [#{did}] ") }
        end
        a.fetch(:words, []).each do |w|
          err(mid, "回帰アンカー #{a[:id]}（#{a[:what]}）: 語『#{w}』がプロンプトに現れない") unless @prompt.include?(w)
        end
        if a[:leak]
          # 回帰アンカーの leak は否定表現でも免除しない（決定・FORBIDDEN 節の外に出たら漏れ）
          hit = leak_lines(with_inherited: true).map { |l| leaking_clause(l, negation: false) { |c| c.match?(a[:leak]) } }.compact.first
          err(mid, "回帰アンカー #{a[:id]}（#{a[:what]}）: 漏れてはいけない語 #{a[:leak].source} が現れる: 「#{hit.strip[0, 80]}」") if hit
        end
        check_door_wall(mid, a) if a[:door_wall]
        check_corridor(mid, a) if a[:corridor]
      end
    end
  end

  # 『勝手口』『door-back』を含む行に、期待の壁（北壁）以外の壁方角が書かれていない。期待の壁を書いた行が1つは有る
  def check_door_wall(mid, a)
    # 文（。区切り）単位で見る: 同じ行の別の文（石の北東の隅など）の壁方角は勝手口の位置ではない
    lines = @lines.flat_map { |l| l.split('。') }.select { |l| l.include?('勝手口') || l.include?('door-back') }
    bad = lines.find { |l| l.scan(/[東西南北]壁/).any? { |w| w != a[:door_wall] } }
    err(mid, "回帰アンカー #{a[:id]}（#{a[:what]}）: 勝手口の行に #{a[:door_wall]} 以外の壁方角がある: 「#{bad.strip[0, 100]}」") if bad
    err(mid, "回帰アンカー #{a[:id]}（#{a[:what]}）: 勝手口を #{a[:door_wall]} と書いた行が無い") unless lines.any? { |l| l.include?(a[:door_wall]) }
  end

  # 渡り廊下棟の窓列行（建物窓列ID => 個数）に紐づく窓が、このMAPのプロンプトに個数どおり現れる
  def check_corridor(mid, a)
    a[:corridor].each do |rid, n|
      row = @t['建物窓列'].find { |r| r['窓列ID'] == rid }
      err(mid, "回帰アンカー #{a[:id]}（#{a[:what]}）: 建物窓列 #{rid} が台帳に無い") && next unless row
      err(mid, "回帰アンカー #{a[:id]}: 建物窓列 #{rid} の個数が #{row['個数']}（期待 #{n}）") if row['個数'].to_i != n
      linked = window_rows(mid).select { |(_, r), _| r == rid }
      err(mid, "回帰アンカー #{a[:id]}（#{a[:what]}）: このMAPに建物窓列 #{rid} へ紐づく窓が無い（屋内と外観で窓列が一致しない）") && next if linked.empty?

      linked.each do |(wall, _), wins|
        parsed = parse_window_line(wall)
        err(mid, "回帰アンカー #{a[:id]}: 壁 #{wall} の窓が WINDOWS 節に現れない") && next unless parsed
        err(mid, "回帰アンカー #{a[:id]}: 壁 #{wall} の窓が #{parsed[0].inspect} 枚（期待 #{n}）") if parsed[0] != n || wins.size != n
      end
    end
  end

  # 屋内と外観で同じ建物窓列が同じ位置で現れる（二つのMAPのプロンプトを突き合わせる）
  def check_cross_map
    by_row = Hash.new { |h, k| h[k] = [] }
    @records.each do |rec|
      next if rec['gated'].to_a.any? || rec['prompt'].to_s.empty?

      @prompt = rec['prompt']
      @lines = @prompt.lines.map(&:chomp)
      window_rows(rec['map_id']).each do |(wall, rid), _|
        row = @t['建物窓列'].find { |r| r['窓列ID'] == rid }
        next if row.nil? || expected_positions(row).empty? # 先頭比・間隔比が未定義の窓列は屋内外の位置を台帳が決めていない

        p_ = parse_window_line(wall)
        by_row[rid] << [rec['map_id'], p_[1]] if p_
      end
    end
    by_row.each do |rid, list|
      base = list.first[1]
      list.each do |mid, pos|
        next if pos.size == base.size && pos.zip(base).all? { |x, y| (x - y).abs <= 0.015 }

        err(mid, "建物窓列 #{rid}: 位置 #{pos} が #{list.first[0]} の #{base} と一致しない（屋内と外観で窓列が違う）")
      end
    end
  end
end

def load_records(argv, root)
  if (i = argv.index('--from-json'))
    return JSON.parse(File.read(argv[i + 1], encoding: 'UTF-8'))
  end

  probe = File.join(root, PromptReflection::PROBE)
  cmd = ENV['LEDGER_PROBE_CMD'] ||
        "uv run --project #{root.shellescape} --with numpy --with opencv-python-headless --with pillow python3 #{probe.shellescape}"
  out, st = Open3.capture2e({ 'LEDGER_ROOT' => root }, cmd)
  abort("プロンプトの導出に失敗: #{out.lines.last(5).join}") unless st.success?
  JSON.parse(out[out.index('[')..])
end

if $PROGRAM_NAME == __FILE__
  root = LedgerYaml::ROOT
  only = (i = ARGV.index('--maps')) ? ARGV[i + 1].split(',') : nil
  v = PromptReflection.new(load_records(ARGV, root), root: root, only: only).run
  v.check_cross_map
  v.skipped.each { |id, miss| puts "ゲートで停止（対象外）: #{id}（必須キー欠落・未決 #{miss.size} 件: #{miss.first.to_s[0, 60]} …）" }
  puts "検査したMAP（#{v.checked.size}）: #{v.checked.join(', ')}"
  if v.errors.empty?
    puts "PASS: プロンプトは台帳を漏れなく反映（検査MAP #{v.checked.size}・ゲート停止 #{v.skipped.size}・回帰アンカー #{PromptReflection::ANCHORS.size}）"
  else
    warn "FAIL: #{v.errors.size} 件の漏れ"
    v.errors.each { |e| warn "  - #{e}" }
    exit 1
  end
end
