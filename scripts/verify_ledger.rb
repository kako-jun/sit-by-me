#!/usr/bin/env ruby
# frozen_string_literal: true

# docs/ledger/*.yaml（日本語マスター）の整合性検証。外部キー・一意性・必須キー・語彙・別名・決定の整合・生成物の鮮度・自由記述の矛盾警告。
#   ruby scripts/verify_ledger.rb            # エラーがあれば exit 1（警告は表示だけ）
require 'json'
require 'digest'
require 'shellwords'
require 'open3'
require_relative 'ledger_yaml'
require_relative 'ledger_required_keys'

class LedgerVerifier
  attr_reader :errors, :warnings

  def initialize(root = LedgerYaml::ROOT)
    @root = root
    @errors = []
    @warnings = []
    @t = LedgerYaml.load_all
  end

  def err(msg) = @errors << msg
  def warn!(msg) = @warnings << msg

  def map_ids
    @map_ids ||= begin
      ids = JSON.parse(File.read(File.join(@root, 'docs/topology/map-ids.json'), encoding: 'UTF-8'))
      ids.fetch('areas').flat_map { |code, n| (1..n).map { |i| format('%s-%02d', code, i) } }
    end
  end

  def base_map(id) = id.sub(/-(kids|fire|burnt|wc)\z/, '')

  def run
    check_presence
    check_columns
    check_required_definition_columns
    check_free_text_tables
    check_unique
    check_fks
    check_required
    check_aliases
    check_decisions
    check_buildings
    check_windows
    check_layout
    check_generated
    check_index_fresh
    check_views_fresh
    check_free_text
    check_code_texts
    self
  end

  # 描画定数・プロンプト文面: 空値なし、変数列と本文の {名前} が一致、コード（oblique_*.py）が参照するIDが全て在り、どの行もコードから参照されている（死んだ行を残さない）
  CODE_REF = /["']((?:PR|MK|TP)\.[A-Za-z0-9._-]*|(?:view|width|door|window|slab|occlusion|topology)\.[A-Za-z0-9._-]*)["']/.freeze

  def check_code_texts
    texts = @t['プロンプト文面']
    consts = @t['描画定数']
    texts.each do |r|
      id = r['文面ID']
      err("プロンプト文面 #{id}: 文面が空") if r['文面'].to_s.strip.empty?
      vars = r['文面'].to_s.scan(/\{([A-Za-z0-9_]+)\}/).flatten.uniq.sort
      err("プロンプト文面 #{id}: 変数列 '#{r['変数']}' が本文の変数 #{vars.join(',')} と違う") unless r['変数'].to_s.split(',').sort == vars
      err("プロンプト文面 #{id}: 使用箇所が空") if r['使用箇所'].to_s.strip.empty?
    end
    consts.each do |r|
      err("描画定数 #{r['定数ID']}: 値が空") if r['値'].to_s.strip.empty?
      err("描画定数 #{r['定数ID']}: コード内の名前が空") if r['コード内の名前'].to_s.strip.empty?
    end
    tools = File.join(@root, '.claude/skills/sit-field-background/tools')
    refs = Dir.glob(File.join(tools, 'oblique_*.py')).flat_map { |f| File.read(f, encoding: 'UTF-8').scan(CODE_REF).flatten }.uniq
    all_ids = texts.map { |r| r['文面ID'] } + consts.map { |r| r['定数ID'] }
    refs.each do |ref|
      # 末尾が '.' のものは動的に連結する接頭辞（"PR.door.wname." + k）
      ok = ref.end_with?('.') ? all_ids.any? { |i| i.start_with?(ref) } : all_ids.include?(ref)
      err("コードが参照する台帳ID '#{ref}' が 描画定数/プロンプト文面 に無い") unless ok
    end
    all_ids.each do |i|
      used = refs.any? { |ref| ref.end_with?('.') ? i.start_with?(ref) : ref == i }
      err("台帳ID #{i} がどのコード（oblique_*.py）からも参照されていない（死んだ行。消すか、コードを台帳参照にする）") unless used
    end
  end

  def check_presence
    %w[エリア MAP 建物 建物部位 建物窓列 建物関係 建物時期差分 端 接続 接続図設定 要素 窓 時期差分 既定値 エリア固定 装飾プール 語彙 決定 採用要素 素材 生成物 必須キー 未決 キー別名 ファイル配置 Issue点検 描画定数 プロンプト文面].each do |n|
      err("表 #{n}.yaml が無い") unless File.file?(File.join(@root, 'docs/ledger', "#{n}.yaml"))
    end
  end

  # 各行のキーが表定義（ledger_io.py の SCHEMA）に含まれること。綴り間違い（『決定参考』）や未定義列は、読み手が黙って空欄扱いにして
  # 検査をすり抜けるので、ここで止める。表定義は Python の SCHEMA を JSON で出して読む（定義を二重に持たない）。
  def schema
    @schema ||= begin
      tool = File.expand_path('../.claude/skills/sit-field-background/tools/ledger_io.py', __dir__)
      project = File.expand_path('..', __dir__)
      out, err_, st = Open3.capture3('uv', 'run', '--project', project, 'python3', tool, 'schema')
      raise "表定義(ledger_io.py schema)を読めない: #{err_.lines.first(3).join(' / ')}" unless st.success?

      JSON.parse(out)
    end
  end

  def check_columns
    LedgerYaml.tables.each do |tb|
      cols = schema[tb]
      if cols.nil?
        err("表 #{tb}.yaml は表定義（ledger_io.py の SCHEMA）に無い")
        next
      end
      @t[tb].each_with_index do |row, i|
        extra = row.keys - cols
        err("表 #{tb}.yaml の#{i + 1}行目（#{row[cols.first]}）に表定義に無い列 #{extra.inspect}（綴り間違い？ 正しい列: #{cols.join(' / ')}）") unless extra.empty?
      end
    end
  end

  # 特徴(自由記述)の欄がある表は、全て導出（ledger_query.free_texts／決定は DECISIONS 節）と検査（verify_prompt_reflects_ledger.rb の (iii)）の
  # 対象でなければならない。新しい表に欄を足したのに導出・検査を足し忘れると、自由記述がプロンプトに黙って出なくなる。
  FREE_TEXT_COVERED = %w[エリア MAP 建物 建物部位 建物窓列 建物関係 建物時期差分 端 接続 要素 窓 素材 採用要素 決定].freeze

  def check_free_text_tables
    with_free = schema.select { |_, cols| cols.include?('特徴(自由記述)') }.keys
    (with_free - FREE_TEXT_COVERED).each do |tb|
      err("表 #{tb} に特徴(自由記述)の欄があるが、プロンプトへの導出（ledger_query.free_texts）と反映検査（verify_prompt_reflects_ledger.rb）の対象になっていない（FREE_TEXT_COVERED に足す前に両方を実装する）")
    end
    (FREE_TEXT_COVERED - with_free).each { |tb| err("FREE_TEXT_COVERED の表 #{tb} に特徴(自由記述)の欄が無い（定義が変わった。導出・検査を見直す）") }
  end

  # 必須キー表のキー・条件の列名が、対象テーブルの表定義に在る（綴り間違いの条件は『=』だと常に偽になり、検査が黙って外れる）
  def check_required_definition_columns
    @t['必須キー'].each do |rk|
      cols = schema[rk['対象テーブル']]
      next if cols.nil? # 対象テーブル不明は LedgerRequiredKeys.check_definition がエラーにする

      err("必須キー #{rk['対象テーブル']}.#{rk['キー']}: キーが表定義に無い") unless rk['キー'].start_with?('@') || cols.include?(rk['キー'])
      rk['条件'].to_s.split('&').each do |c|
        m = c.strip.match(/\A(.+?)(!=|=)(.*)\z/) or next
        err("必須キー #{rk['対象テーブル']}.#{rk['キー']}: 条件『#{c.strip}』の列『#{m[1]}』が表定義に無い") unless cols.include?(m[1])
      end
    end
  end

  UNIQUE = {
    'エリア' => ['エリアID'], 'MAP' => ['MAP_ID'], '建物' => ['建物ID'], '建物部位' => ['部位ID'], '建物窓列' => ['窓列ID'],
    '端' => %w[端ID 適用時期], '窓' => %w[窓ID 適用時期], '要素' => %w[MAP_ID 適用時期 要素ID], '決定' => ['決定ID'], '採用要素' => ['採用要素ID'],
    '素材' => ['素材ID'], '生成物' => ['生成物ID'], '語彙' => ['語彙ID'], '未決' => ['未決ID'], '既定値' => ['既定ID'], 'ファイル配置' => ['配置ID'], 'Issue点検' => ['コメントURL'], '描画定数' => ['定数ID'], 'プロンプト文面' => ['文面ID']
  }.freeze

  def check_unique
    UNIQUE.each do |tb, cols|
      dup = @t[tb].group_by { |r| cols.map { |c| r[c] } }.select { |_, v| v.size > 1 }.keys
      err("#{tb}: 主キー重複 #{dup.map { |k| k.join('/') }.join(', ')}") unless dup.empty?
    end
    pairs = @t['接続'].map { |r| [r['端A'], r['端B']].sort }
    dup = pairs.group_by(&:itself).select { |_, v| v.size > 1 }.keys
    err("接続: 同じ端の組が重複 #{dup.map { |k| k.join('⇄') }.join(', ')}") unless dup.empty?
    ends = @t['接続'].flat_map { |r| [r['端A'], r['端B']] }
    ends.group_by(&:itself).each do |e, v|
      next unless v.size > 1 && e.match?(/\.door/)

      err("接続: 扉の端 #{e} が複数の接続に使われている")
    end
  end

  def ids(table, col) = @t[table].map { |r| r[col] }

  def fk(table, col, target_table, target_col, allow: [], list: false, optional: true)
    set = ids(target_table, target_col)
    @t[table].each do |r|
      v = r[col].to_s
      next if v.empty? && optional

      (list ? v.split(';') : [v]).each do |tok|
        next if allow.include?(tok) || set.include?(tok)

        err("外部キー #{table}.#{col}='#{tok}' が #{target_table}.#{target_col} に無い（#{r.values.first}）")
      end
    end
  end

  def check_fks
    fk('MAP', 'エリアID', 'エリア', 'エリアID', optional: false)
    fk('MAP', '建物ID', '建物', '建物ID', list: true, allow: %w[該当なし])
    @t['MAP'].each do |m|
      m['依存MAP'].to_s.split(';').each do |d|
        next if %w[なし 該当なし 未決(要確認)].include?(d)

        err("外部キー MAP.依存MAP='#{d}' が MAP に無い（#{m['MAP_ID']}）") unless ids('MAP', 'MAP_ID').include?(d)
        err("依存MAPの自己参照 #{m['MAP_ID']}") if d == m['MAP_ID']
      end
    end
    check_dep_cycle
    fk('建物', 'エリアID', 'エリア', 'エリアID')
    fk('建物部位', '建物ID', '建物', '建物ID', optional: false)
    fk('建物窓列', '建物ID', '建物', '建物ID', optional: false)
    fk('建物窓列', '部位ID', '建物部位', '部位ID')
    fk('建物関係', '建物A', '建物', '建物ID')
    fk('建物関係', '建物B', '建物', '建物ID')
    fk('建物関係', '接続端ID', '端', '端ID')
    fk('建物時期差分', '建物ID', '建物', '建物ID', optional: false)
    fk('建物時期差分', '部位ID', '建物部位', '部位ID')
    fk('端', 'MAP_ID', 'MAP', 'MAP_ID', optional: false)
    fk('端', '建物部位ID', '建物部位', '部位ID')
    fk('窓', 'MAP_ID', 'MAP', 'MAP_ID', optional: false)
    fk('窓', '建物窓列ID', '建物窓列', '窓列ID')
    fk('要素', 'MAP_ID', 'MAP', 'MAP_ID', optional: false)
    fk('要素', '建物部位ID', '建物部位', '部位ID')
    fk('既定値', 'MAP_ID', 'MAP', 'MAP_ID', optional: false)
    fk('時期差分', 'MAP_ID', 'MAP', 'MAP_ID', optional: false)
    @t['接続'].each do |r|
      %w[端A 端B].each do |c|
        err("接続.#{c}='#{r[c]}' の MAP が MAP ID 登録に無い") unless map_ids.include?(r[c].split('.').first)
      end
    end
    @t['端'].each do |e|
      next if e['相手端'].to_s.empty?

      ok = @t['接続'].any? { |c| [c['端A'], c['端B']].sort == [e['端ID'], e['相手端']].sort }
      err("端 #{e['端ID']} の相手端 #{e['相手端']} が接続表に無い（接続は接続表が正）") unless ok
    end
    check_decision_fks
    check_issue_audit
    @t['採用要素'].each do |a|
      err("外部キー 採用要素.素材ID='#{a['素材ID']}' が素材に無い") unless a['素材ID'].to_s.empty? || ids('素材', '素材ID').include?(a['素材ID'])
      err("採用要素 #{a['採用要素ID']} の元MAP #{a['元MAP']} が MAP に無い") unless ids('MAP', 'MAP_ID').include?(base_map(a['元MAP']))
      a['継承先MAP'].split(';').each { |m| err("採用要素 #{a['採用要素ID']} の継承先MAP #{m} が MAP に無い") unless ids('MAP', 'MAP_ID').include?(base_map(m)) }
    end
    @t['素材'].each do |s|
      owner = s['所有者ID']
      ok = ids('MAP', 'MAP_ID').include?(base_map(owner))
      err("素材 #{s['素材ID']} の所有者 #{owner} が MAP に無い") unless ok
    end
    # 決定参照（全表）: 存在し、訂正済み・撤回済みの決定を参照していない
    dec = @t['決定'].to_h { |d| [d['決定ID'], d] }
    @t.each do |tb, rows|
      next unless rows.first&.key?('決定参照')

      rows.each do |r|
        r['決定参照'].to_s.split(';').each do |ref|
          if !dec.key?(ref)
            err("決定参照 #{tb}(#{r.values.first})='#{ref}' が決定表に無い")
          elsif dec[ref]['状態'] != '有効'
            err("決定参照 #{tb}(#{r.values.first})='#{ref}' は #{dec[ref]['状態']}（置換先 #{dec[ref]['置換先']}）の決定を参照している")
          end
        end
      end
    end
    @t['未決'].each do |u|
      err("未決 #{u['未決ID']} の解決決定ID #{u['解決決定ID']} が決定表に無い") unless u['解決決定ID'].to_s.empty? || dec.key?(u['解決決定ID'])
    end
  end

  def check_dep_cycle
    deps = @t['MAP'].to_h { |m| [m['MAP_ID'], m['依存MAP'].to_s.split(';').reject { |d| %w[なし 該当なし 未決(要確認)].include?(d) }] }
    state = {}
    visit = lambda do |n, path|
      return if state[n] == :done
      return err("依存MAPの循環 #{(path + [n]).join('→')}") if state[n] == :open

      state[n] = :open
      (deps[n] || []).each { |d| visit.call(d, path + [n]) }
      state[n] = :done
    end
    deps.each_key { |n| visit.call(n, []) }
  end

  def check_decision_fks
    tabs = { 'エリア' => ['エリア', 'エリアID'], 'MAP' => ['MAP', 'MAP_ID'], '建物' => ['建物', '建物ID'], '端' => ['端', '端ID'], '要素' => ['要素', '要素ID'], '窓' => ['窓', '窓ID'], '接続' => ['接続', '端A'] }
    @t['決定'].each do |d|
      tt = tabs[d['対象種別']]
      if tt.nil?
        err("決定 #{d['決定ID']}: 対象種別 '#{d['対象種別']}' が不正")
      else
        set = ids(*tt)
        set += ids('接続', '端B') if d['対象種別'] == '接続'
        err("決定 #{d['決定ID']}: 対象ID '#{d['対象ID']}' が #{d['対象種別']} 表に無い") unless set.include?(d['対象ID'])
      end
      d['対象MAP'].to_s.split(';').each do |m|
        err("決定 #{d['決定ID']}: 対象MAP '#{m}' が MAP に無い") unless ids('MAP', 'MAP_ID').include?(base_map(m))
      end
      if d['状態'] == '訂正済み'
        err("決定 #{d['決定ID']}: 訂正済みなのに置換先が無い") if d['置換先'].to_s.empty?
        err("決定 #{d['決定ID']}: 置換先 #{d['置換先']} が決定表に無い") unless d['置換先'].to_s.empty? || ids('決定', '決定ID').include?(d['置換先'])
      end
    end
  end

  # Issue点検.yaml: 分類は語彙『Issue点検分類』、決定IDは決定表に在る、反映済みには決定IDが要る、URL と Issue番号が合う
  def check_issue_audit
    classes = @t['語彙'].select { |v| v['グループ'] == 'Issue点検分類' }.map { |v| v['値'] }
    fk('Issue点検', '決定ID', '決定', '決定ID', list: true)
    @t['Issue点検'].each do |r|
      id = r['コメントURL']
      err("Issue点検 #{id}: 分類 '#{r['分類']}' が語彙（Issue点検分類）に無い") unless classes.include?(r['分類'])
      err("Issue点検 #{id}: 分類が『決定表に反映済み』なのに決定IDが空") if r['分類'] == '決定表に反映済み' && r['決定ID'].empty?
      err("Issue点検 #{id}: Issue番号 '#{r['Issue番号']}' が URL の Issue と違う") unless id.match?(%r{/(issues|pull)/#{Regexp.escape(r['Issue番号'])}(\#|\z)})
      err("Issue点検 #{id}: 候補の要約が空") if r['候補の要約'].empty?
    end
    pending = @t['Issue点検'].count { |r| r['分類'] == '未反映(要取込み)' }
    warn!("Issue点検: 未反映(要取込み)が #{pending} 件（決定表へ取り込むか分類を確定する）") if pending.positive?
  end

  def check_required
    errors, undecided = LedgerRequiredKeys.check_rows(@t)
    errors.each { |e| err(e) }
    @undecided = undecided
  end

  def check_aliases
    aliases = @t['キー別名'].map { |r| [r['別名'], r['正規名']] }.to_h
    @t['必須キー'].each { |r| err("必須キー表のキー '#{r['キー']}' は別名（正規名: #{aliases[r['キー']]}）") if aliases.key?(r['キー']) }
    LedgerYaml.tables.each do |tb|
      LedgerYaml.header(tb).each { |h| warn!("別名の列名 #{tb}.#{h}（正規名 #{aliases[h]} に直す）") if aliases.key?(h) }
    end
    (@t['エリア固定'] + @t['装飾プール']).each do |r|
      k = r['項目'].to_s.split(/[.\[]/).last
      warn!("項目 '#{r['項目']}' の末尾が別名 #{k}（正規名 #{aliases[k]}）") if aliases.key?(k)
    end
  end

  def check_decisions
    @t['決定'].each do |d|
      id = d['決定ID']
      d['必須語'].to_s.split(';').each { |w| err("決定 #{id}: 必須語『#{w}』が決定の要点に無い") unless d['決定の要点'].include?(w) }
      d['禁止語'].to_s.split(';').each { |w| err("決定 #{id}: 禁止語『#{w}』が決定の要点に無い") unless d['決定の要点'].include?(w) }
      err("決定 #{id}: 日付が YYYY-MM-DD でない") unless d['日付'].match?(/\A\d{4}-\d\d-\d\d\z/)
      if d['出典'].start_with?('Issue') && !d['出典URL'].match?(%r{\Ahttps://github\.com/[^/]+/[^/]+/issues/\d+#issuecomment-\d+\z})
        err("決定 #{id}: 出典URL が Issue コメントのURLでない")
      end
      err("決定 #{id}: 出典の Issue 番号と出典URLが食い違う") if d['出典'] =~ /#(\d+)/ && !d['出典URL'].to_s.empty? && !d['出典URL'].include?("/issues/#{$1}#")
    end
  end

  def check_buildings
    parts = @t['建物部位']
    @t['建物窓列'].each do |w|
      part = parts.find { |p| p['部位ID'] == w['部位ID'] }
      next unless part

      err("建物窓列 #{w['窓列ID']}: 部位 #{part['部位ID']} が開放なのに窓列がある（開放と窓列は両立しない）") if part['状態'] == '開放' && w['個数'].to_i.positive?
      err("建物窓列 #{w['窓列ID']}: 部位が窓なしなのに個数が #{w['個数']}") if part['状態'] == 'なし' && w['個数'].to_i.positive?
    end
    # 屋内と外観の食い違い防止: 建物窓列のある建物は、窓表の行数が個数と一致する（MAP・時期ごと）
    @t['窓'].select { |w| !w['建物窓列ID'].to_s.empty? }.group_by { |w| [w['建物窓列ID'], w['MAP_ID'], w['適用時期'], w['壁']] }.each do |(wid, mid, era, wall), rows|
      n = @t['建物窓列'].find { |x| x['窓列ID'] == wid }&.fetch('個数', nil)
      err("窓 #{mid}#{era.empty? ? '' : "-#{era}"} の壁 #{wall}: 建物窓列 #{wid} の個数 #{n} と窓表の行数 #{rows.size} が違う") if n && n.to_i != rows.size
    end
  end

  def check_windows
    @t['窓'].each do |w|
      next if w['種別'] == '窓なし'

      err("窓 #{w['窓ID']}: 壁側/状態が空") if w['壁側'].empty? || w['状態'].empty?
    end
  end

  MAP_ID_RE = '(?:TRM|KRB|STN|NTR|NTB|UTS|SNL|SCH|NTA|UCH|BDY|APT|OVS|GRD|CST)-\\d{2}'

  def layout_regexps
    @layout_regexps ||= @t['ファイル配置'].map do |r|
      Regexp.new("\\A(?:#{r['パターン'].gsub('{MAP_ID}', MAP_ID_RE)})\\z")
    rescue RegexpError
      nil
    end
  end

  # ファイル配置表: 列の値・外部キー（所有表→表名、入口→実在パス）・生成物のパスがどれかの規則に一致すること
  def check_layout
    rows = @t['ファイル配置']
    table_names = LedgerYaml.tables
    rows.each_with_index do |r, i|
      id = r['配置ID']
      err("ファイル配置 #{id}: パターンが空・正規表現として不正") if r['パターン'].to_s.empty? || layout_regexps[i].nil?
      err("ファイル配置 #{id}: 種別・用途が空") if r['種別'].to_s.empty? || r['用途'].to_s.empty?
      err("ファイル配置 #{id}: 到達 '#{r['到達']}' は リンク/許可 のどちらでもない") unless %w[リンク 許可].include?(r['到達'])
      if r['到達'] == '許可'
        err("ファイル配置 #{id}: 到達=許可 には許可リスト理由が要る") if r['許可リスト理由'].to_s.strip.empty?
      elsif !r['許可リスト理由'].to_s.strip.empty? || !r['入口'].to_s.strip.empty?
        err("ファイル配置 #{id}: 到達=リンク に許可リスト理由・入口がある")
      end
      split_semi(r['所有表']).each do |tb|
        err("外部キー ファイル配置.所有表='#{tb}' が表に無い（#{id}）") unless table_names.include?(tb)
      end
      split_semi(r['入口']).each do |e|
        err("外部キー ファイル配置.入口='#{e}' が実在しない（#{id}）") unless File.exist?(File.join(@root, e))
      end
    end
    @t['生成物'].each do |g|
      next if layout_regexps.compact.any? { |re| re.match?(g['パス']) }

      err("生成物 #{g['生成物ID']}: パス #{g['パス']} がどの配置規則（ファイル配置）にも一致しない")
    end
  end

  def split_semi(s) = s.to_s.split(';').map(&:strip).reject(&:empty?)

  # docs/INDEX.md の生成ビューが台帳から再生成した内容と一致するか（古ければエラー）
  def check_index_fresh
    tool = File.expand_path('../.claude/skills/sit-field-background/tools/ledger_index.py', __dir__)
    project = File.expand_path('..', __dir__)
    out = `LEDGER_ROOT=#{@root.shellescape} uv run --project #{project.shellescape} python3 #{tool.shellescape} check 2>&1`
    err("docs/INDEX.md の生成ビューが古い、または検査できない: #{out.strip.lines.first(2).join(' / ')}") unless $?.success?
  end

  # docs/ledger-views/*.md（人が読むビュー）は台帳からの生成物。手編集・台帳変更後の再生成漏れ・手書きファイルの混入をエラーにする
  def check_views_fresh
    tool = File.expand_path('../.claude/skills/sit-field-background/tools/ledger_views.py', __dir__)
    project = File.expand_path('..', __dir__)
    out = `LEDGER_ROOT=#{@root.shellescape} uv run --project #{project.shellescape} python3 #{tool.shellescape} check 2>&1`
    err("docs/ledger-views/ の生成ビューが古い、または検査できない: #{out.strip.lines.first(2).join(' / ')}") unless $?.success?
  end

  def check_generated
    @t['生成物'].each do |g|
      path = File.join(@root, g['パス'])
      unless File.file?(path)
        err("生成物 #{g['生成物ID']}: パス #{g['パス']} が無い（リンク切れ）")
        next
      end
      next unless g['パス'].end_with?('.json') && !g['入力ハッシュ'].to_s.empty?

      prov = (JSON.parse(File.read(path, encoding: 'UTF-8'))['_provenance'] || {})
      err("生成物 #{g['生成物ID']}: JSON の _provenance.input_sha が生成物表と違う（手編集か古い）") if prov['input_sha'] != g['入力ハッシュ']
    end
    return if ENV['LEDGER_SKIP_REGEN']

    tool = File.join(@root, '.claude/skills/sit-field-background/tools/ledger_build.py')
    return unless File.file?(tool)

    out = `uv run python3 #{tool} check 2>&1`
    err("派生JSONが台帳から再生成した内容と一致しない: #{out.strip.lines.first(3).join(' / ')}") unless $?.success?
  end

  # 自由記述（特徴）: 禁止語との衝突・必須キー値との食い違い・構造化できる内容（寸法・個数・材質）を警告
  def check_free_text
    free = '特徴(自由記述)'
    forb = @t['決定'].select { |d| d['状態'] == '有効' }.flat_map { |d| d['禁止語'].to_s.split(';') } + @t['語彙'].select { |v| v['グループ'] == '禁止語' }.map { |v| v['値'] }
    @t.each do |tb, rows|
      next unless rows.first&.key?(free)

      rows.each do |r|
        text = r[free].to_s
        next if text.empty?

        who = "#{tb} #{r.values.first}"
        forb.uniq.each do |w|
          next unless text.include?(w)

          warn!("自由記述 #{who}: 禁止語『#{w}』が出る（否定形でなければ衝突）") unless text.match?(/描かない|ない|禁止|不可|しない/)
        end
        warn!("自由記述 #{who}: 寸法らしい数値（#{$&}）→ 必須キー・要素表へ移す候補") if text =~ /\d+\s*(px|cm|mm|単位|ピクセル)/
        warn!("自由記述 #{who}: 個数らしい数値（#{$&}）→ 必須キーへ移す候補") if text =~ /\d+\s*(個|本|枚|つ|か所)/
        if tb == 'MAP' && r['床材'].to_s != '' && text =~ /畳/ && !r['床材'].include?('畳')
          warn!("自由記述 #{who}: 床材キー（#{r['床材']}）と食い違う可能性（畳）")
        end
      end
    end
  end
end

if $PROGRAM_NAME == __FILE__
  v = LedgerVerifier.new.run
  v.warnings.each { |w| warn "WARN: #{w}" }
  if v.errors.empty?
    puts "PASS: ledger tables=#{LedgerYaml.tables.size}, decisions=#{v.instance_variable_get(:@t)['決定'].size}, maps=#{v.instance_variable_get(:@t)['MAP'].size}, warnings=#{v.warnings.size}"
  else
    v.errors.each { |e| warn "FAIL: #{e}" }
    warn "FAIL: #{v.errors.size} errors"
    exit 1
  end
end
