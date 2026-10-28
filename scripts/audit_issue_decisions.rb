#!/usr/bin/env ruby
# frozen_string_literal: true

# sit-by-me の Issue（本文・コメント）から『kako-jun の決定』と読める候補を列挙し、決定表（docs/ledger/決定.yaml）と突合して
# docs/ledger/Issue点検.yaml（分類つき）の過不足を検査・更新する。誤検出より漏れ検出を優先する（迷ったら『未反映(要取込み)』）。
#
#   ruby scripts/audit_issue_decisions.rb                       # gh で全 Issue/コメントを取得 → 候補を分類 → Issue点検.yaml と突合（未点検があれば exit 1）
#   ruby scripts/audit_issue_decisions.rb --from-json F         # 事前取得した JSON を使う（オフライン・テスト用）
#   ruby scripts/audit_issue_decisions.rb --fetch F             # gh の取得結果を F に保存して終わる（--from-json 用）
#   ruby scripts/audit_issue_decisions.rb --write               # Issue点検.yaml を更新（【手動】と書いた行の分類は保つ）
#   ruby scripts/audit_issue_decisions.rb --list 未反映(要取込み)  # 分類ごとの一覧
#   ruby scripts/audit_issue_decisions.rb --check-quotes [--from-json F]  # 決定.逐語の各引用が 出典URL（; 区切り複数）のコメント本文に実在するか検査（違反があれば exit 1）
#   ruby scripts/audit_issue_decisions.rb --check-sources [--from-json F] # 全実Issueの出典・ハッシュ・命題リンクを検査
#   ruby scripts/audit_issue_decisions.rb --check-sources --require-reviewed # 全命題の意味判定完了も要求（未判定があれば exit 1）
#   LEDGER_ROOT=/path/to/root ...                               # root 差し替え（テスト用）
#
# 候補のヒューリスティック（README: tools/README.md にも同文）:
#   投稿者での絞り込みはしない（Claude が kako-jun のアカウントで投稿するため全コメントが『本人投稿』）。次のいずれかを候補にする:
#   見出し  行頭 # の見出しに 決定|確定|承認|合意|指示|発言|指摘|判定|回答|方針|訂正 を含む
#   逐語    本文に『逐語』の語がある
#   引用    kako-jun|本人|ユーザー|発言|原文|指示|回答|承認 を含む行に 「…」『…』の引用がある
#   言及    kako-jun の直後（12字以内）に 指示|決定|承認|OK|まかせ|よい|判断 がある
# 分類（上から順に最初に当たったもの。決まらなければ 未反映(要取込み)）:
#   対象外            プルリクエスト（本文・会話）
#   決定表に反映済み   コメントURLが 決定.出典URL にある、または 逐語に抽出した引用（10字以上）が全て 決定.逐語/決定の要点 に含まれる
#   決定でない         先頭の見出しが 結果|これからやること|実施記録|進捗|完了|再開|棚卸し 等の作業記録で、逐語の引用が1つも無い
#   未反映(要取込み)   上のどれでもない（逐語ありの発言だけが決定表へ取り込む根拠になる。備考に逐語あり/なしを書く）
require 'json'
require 'digest'
require 'open3'
require 'set'
require 'shellwords'
require_relative 'ledger_yaml'

class IssueAudit
  REPO = 'kako-jun/sit-by-me'
  CLASSES = ['決定表に反映済み', '未反映(要取込み)', '決定でない', '対象外'].freeze
  HEAD_RE = /\A#{'#'}{1,4}\s*.*(決定|確定|承認|合意|指示|発言|指摘|判定|回答|方針|訂正)/.freeze
  ATTR_RE = /kako-jun|本人|ユーザー|発言|原文|指示|回答|承認/.freeze
  MENTION_RE = /kako-jun.{0,12}(指示|決定|承認|OK|まかせ|よい|判断)/.freeze
  QUOTE_RE = /[「『](.{4,400}?)[」』]/.freeze
  WORKLOG_RE = /\A(?:#{'#'}{1,4}\s*)?(?:\d{4}-\d{2}-\d{2}\s*)?(結果|これからやること|これから行う|実施記録|実施結果|進捗|完了|反映完了|再開|棚卸し|レビュー|実装)/.freeze
  MANUAL = '【手動】'

  attr_reader :rows

  def initialize(data, tables = LedgerYaml.load_all)
    @issues = data['issues'].to_h { |i| [i['number'], i] }
    @comments = data['comments']
    @t = tables
    index_ledger
    @rows = candidates.map { |c| classify(c) }.compact.sort_by { |r| [r['Issue番号'].to_i, r['_at']] }
  end

  def norm(s) = s.to_s.gsub(/\s+/, '')

  # 出典URL → コメントID（文字列）／Issue 本文（"issue-N"）／どちらでもなければ nil
  def self.source_id(url)
    m = url.match(%r{/issues/(\d+)(?:#issuecomment-(\d+))?\z})
    m ? (m[2] || "issue-#{m[1]}") : nil
  end

  # 逐語欄から「…」『…』の引用を取り出す（最外側の括弧は 「」『』 のどちらでも引用。入れ子の括弧は外側の引用の一部。括弧書きの注記など引用の外は無視）。
  # 比較用に空白・markdown の強調（**）・バッククォートを除き、入れ子の括弧は「」にそろえる。長さでは除外しない（短い引用の扱いは check_quotes）
  def self.verbatim_quotes(text)
    out = []
    depth = 0
    buf = +''
    text.each_char do |ch|
      if depth.zero?
        if ['「', '『'].include?(ch)
          depth = 1
          buf = +''
        end
        next
      end
      if ['「', '『'].include?(ch)
        depth += 1
        buf << '「'
      elsif ['」', '』'].include?(ch)
        depth -= 1
        if depth.zero?
          out << buf
        else
          buf << '」'
        end
      else
        buf << ch
      end
    end
    out.map { |q| squash(q) }.reject(&:empty?)
  end

  def self.squash(s) = s.to_s.gsub(/\s+/, '').delete('*`').tr('『』', '「」')

  SHORT_QUOTE = 4 # これ未満の引用は、部分一致だと別の文に紛れるので「」ごと完全一致で照合する
  NO_QUOTE_MARK = '（逐語の引用なし' # 逐語欄にこの語を明記した決定だけが『引用0件』の例外（Issue記録の決定文など、kako-jun の発言そのものが無い場合）

  attr_reader :quote_stats

  # 決定表の各決定について、逐語の各引用が出典URL群のどれかのコメント（または Issue 本文）の本文に実在することを検査する。
  # 出典が Issue の決定は、照合できる引用を最低1件必須（例外は逐語欄に NO_QUOTE_MARK と明記した決定のみ。件数は quote_stats に別掲）。
  # 保証するのは『出典コメントに転記された文との一致』まで。元の発言そのものとの一致は保証しない。
  # 戻り値: エラー文のリスト（空なら合格）。候補（引用が実在する別コメント）も添える。
  def check_quotes
    bodies = {}
    @issues.each_value { |i| bodies["issue-#{i['number']}"] = [self.class.squash(i['body']), i['html_url']] }
    @comments.each { |c| bodies[c['id'].to_s] = [self.class.squash(c['body']), c['html_url']] }
    errors = []
    @quote_stats = { decisions: @t['決定'].size, checked: 0, quotes: 0, exceptions: [] }
    @t['決定'].each do |d|
      id = d['決定ID']
      qs = self.class.verbatim_quotes(d['逐語'])
      marked = d['逐語'].include?(NO_QUOTE_MARK)
      urls = d['出典URL'].split(';').map(&:strip).reject(&:empty?)
      # docs/decisions.md の帰属記録から取り込んだ決定は Issue のコメントを持たない。逐語なしの例外として数える
      if d['出典'].to_s.start_with?('docs/decisions.md') && marked
        @quote_stats[:exceptions] << id
        next
      end
      if urls.empty?
        errors << "決定 #{id}: 出典URLが無い"
        next
      end
      srcs = urls.map { |u| [u, self.class.source_id(u)] }
      srcs.select { |_, sid| sid.nil? }.each { |u, _| errors << "決定 #{id}: 出典URL『#{u}』が Issue のコメント（または本文）のURLでない" }
      srcs.select { |_, sid| sid && !bodies.key?(sid) }.each { |u, _| errors << "決定 #{id}: 出典URL『#{u}』のコメントを取得結果に見つけられない" }
      if qs.empty?
        if marked
          @quote_stats[:exceptions] << id
        else
          errors << "決定 #{id}: 逐語に照合できる引用（「…」『…』）が無い（引用のない決定は逐語欄に『#{NO_QUOTE_MARK}: 理由）』と明記する）"
        end
        next
      end
      @quote_stats[:checked] += 1
      @quote_stats[:quotes] += qs.size
      have = srcs.map { |_, sid| bodies[sid] }.compact
      qs.each do |q|
        needle = q.size < SHORT_QUOTE ? "「#{q}」" : q
        next if have.any? { |b, _| b.include?(needle) }

        cands = bodies.values.select { |b, _| b.include?(needle) }.map(&:last).first(3)
        errors << "決定 #{id}: 逐語の引用「#{q[0, 30]}」が出典URL群のどのコメントにも実在しない" + (cands.empty? ? '（どのコメントにも無い）' : "（実在するコメント: #{cands.join(' ')}）")
      end
    end
    errors
  end

  # ---- 台帳側の参照
  def index_ledger
    @by_url = Hash.new { |h, k| h[k] = [] }
    @t['決定'].each do |d|
      d['出典URL'].split(';').map(&:strip).reject(&:empty?).each { |u| @by_url[self.class.source_id(u)] << d['決定ID'] }
    end
    @ledger_text = @t['決定'].map { |d| [norm(d['逐語']), d['決定ID']] } + @t['決定'].map { |d| [norm(d['決定の要点']), d['決定ID']] }
  end

  # ---- 候補の抽出
  def reasons(text)
    r = []
    r << '見出し' if text.each_line.any? { |l| l.match?(HEAD_RE) }
    r << '逐語' if text.include?('逐語')
    r << '引用' if text.each_line.any? { |l| l.match?(ATTR_RE) && l.match?(QUOTE_RE) }
    r << '言及' if text.match?(MENTION_RE)
    r
  end

  def candidates
    out = []
    @issues.each_value do |i|
      rs = reasons(i['body'].to_s)
      out << { number: i['number'], url: i['html_url'], id: "issue-#{i['number']}", text: i['body'].to_s, at: i['created_at'], reasons: rs, kind: '本文', pr: i['pull_request'] } unless rs.empty?
    end
    @comments.each do |c|
      n = c['issue_url'][/(\d+)\z/, 1].to_i
      rs = reasons(c['body'].to_s)
      next if rs.empty?

      out << { number: n, url: c['html_url'], id: c['id'].to_s, text: c['body'].to_s, at: c['created_at'], reasons: rs, kind: 'コメント', pr: @issues.dig(n, 'pull_request') }
    end
    out
  end

  # 逐語として扱う引用（逐語の語があれば本文全体、無ければ帰属表現のある行の引用）。10字以上のものだけを突合に使う
  def quotes(text)
    lines = text.include?('逐語') ? text.lines : text.lines.select { |l| l.match?(ATTR_RE) }
    lines.flat_map { |l| l.scan(QUOTE_RE).flatten }.map { |q| norm(q) }.select { |q| q.size >= 10 }.uniq
  end

  def classify(c)
    text = c[:text]
    qs = quotes(text)
    first = text.lines.map(&:strip).find { |l| !l.empty? }.to_s
    head = text.lines.find { |l| l.match?(HEAD_RE) }.to_s.strip
    summary = (head.empty? ? first : head).sub(/\A#+\s*/, '')[0, 70]
    quote = text.scan(QUOTE_RE).flatten.first
    summary += "／「#{quote[0, 50]}」" if quote
    ids = []
    cls = nil
    note = "検出: #{c[:reasons].join('・')}（#{c[:kind]}）"
    if c[:pr]
      cls = '対象外'
      note += '。プルリクエストの会話'
    elsif (hit = @by_url[c[:id]]) && !hit.empty?
      cls = '決定表に反映済み'
      ids = hit
      note += '。決定.出典URL に一致'
    elsif !qs.empty? && qs.all? { |q| @ledger_text.any? { |t, _| t.include?(q) } }
      cls = '決定表に反映済み'
      ids = qs.flat_map { |q| @ledger_text.select { |t, _| t.include?(q) }.map(&:last) }.uniq
      note += "。逐語#{qs.size}件が決定表に含まれる"
    elsif qs.empty? && first.match?(WORKLOG_RE) && !c[:reasons].include?('逐語') && !c[:reasons].include?('引用')
      cls = '決定でない'
      note += '。作業記録（逐語の引用なし）'
    else
      cls = '未反映(要取込み)'
      matched = qs.count { |q| @ledger_text.any? { |t, _| t.include?(q) } }
      note += qs.empty? ? '。逐語の引用なし（取込みの根拠にできない。要確認）' : "。逐語あり#{qs.size}件（うち決定表に含まれる #{matched}件）"
    end
    { 'Issue番号' => c[:number].to_s, 'コメントURL' => c[:url], '候補の要約' => summary.gsub(/\s+/, ' '), '分類' => cls,
      '決定ID' => ids.join(';'), '備考' => note, '_at' => c[:at].to_s }
  end

  def counts = rows.group_by { |r| r['分類'] }.transform_values(&:size)
end

def fetch_all
  fetch = lambda do |path|
    out, st = Open3.capture2e('gh', 'api', '--paginate', '--slurp', path)
    abort("gh api #{path} に失敗: #{out.lines.last(3).join}") unless st.success?
    JSON.parse(out).flatten
  end
  { 'issues' => fetch.call("repos/#{IssueAudit::REPO}/issues?state=all&per_page=100"),
    'comments' => fetch.call("repos/#{IssueAudit::REPO}/issues/comments?per_page=100") }
end

def write_table(rows, root)
  existing = LedgerYaml.read('Issue点検')
  manual = existing.select { |r| r['備考'].include?(IssueAudit::MANUAL) }.to_h { |r| [r['コメントURL'], r] }
  merged = rows.map { |r| manual[r['コメントURL']] || r.reject { |k, _| k.start_with?('_') } }
  tool = File.join(root, '.claude/skills/sit-field-background/tools/ledger_write_rows.py')
  out, st = Open3.capture2e({ 'LEDGER_ROOT' => root }, 'uv', 'run', '--project', root, 'python3', tool, 'Issue点検', stdin_data: JSON.generate(merged))
  abort("Issue点検.yaml の書き込みに失敗: #{out}") unless st.success?
  merged.size
end

# Issue点検の候補ヒューリスティックとは独立した、全実Issueの出典網羅検査。
# PASS は出典の保存と構造的なリンクだけを意味し、各節の意味判定の完了を意味しない。
def check_source_coverage(data, require_reviewed: false)
  issues = data['issues'].to_h { |issue| [issue['number'].to_s, issue] }
  originals = data['issues'].reject { |issue| issue['pull_request'] }.map do |issue|
    [issue['html_url'], issue['body'].to_s]
  end
  originals += data['comments'].filter_map do |comment|
    number = comment['issue_url'].split('/').last
    next if issues[number].nil? || issues[number]['pull_request']

    [comment['html_url'], comment['body'].to_s]
  end
  expected = originals.to_h
  sources = LedgerYaml.read('Issue出典')
  claims = LedgerYaml.read('Issue命題')
  decisions = LedgerYaml.read('決定').to_h { |d| [d['決定ID'], d] }
  source_by_url = sources.to_h { |s| [s['URL'], s] }
  source_by_id = sources.to_h { |s| [s['出典ID'], s] }
  errors = []
  errors << "Issue出典.URL に重複あり" unless source_by_url.size == sources.size
  errors << "Issue出典.出典ID に重複あり" unless source_by_id.size == sources.size
  (expected.keys - source_by_url.keys).each { |url| errors << "Issue出典に無い: #{url}" }
  (source_by_url.keys - expected.keys).each { |url| errors << "取得結果に無いIssue出典: #{url}" }
  expected.each do |url, body|
    row = source_by_url[url]
    next unless row

    errors << "Issue出典の原文SHA256が変化: #{url}" unless row['本文SHA256'] == Digest::SHA256.hexdigest(body)
    errors << "Issue出典の安全化SHA256が不一致: #{url}" unless row['安全化SHA256'] == Digest::SHA256.hexdigest(row['本文'])
  end
  claims_by_source = claims.group_by { |claim| claim['出典ID'] }
  sources.each do |source|
    errors << "Issue出典に命題行が無い: #{source['出典ID']}" if claims_by_source.fetch(source['出典ID'], []).empty?
  end
  claims.each do |claim|
    source = source_by_id[claim['出典ID']]
    if source.nil?
      errors << "Issue命題 #{claim['命題ID']}: 出典IDが無い"
      next
    end
    excerpt = claim['原文抜粋']
    errors << "Issue命題 #{claim['命題ID']}: 安全化出典に抜粋が無い" unless excerpt.empty? || source['本文'].include?(excerpt)
    next unless claim['分類'] == '決定反映'

    # 決定IDは ';' 区切りで複数指定できる（節に複数の決定が混在する場合）。各IDを個別に検査する
    claim['決定ID'].split(';').map(&:strip).reject(&:empty?).each do |decision_id|
      decision = decisions[decision_id]
      if decision.nil?
        errors << "Issue命題 #{claim['命題ID']}: 決定IDが無い（#{decision_id}）"
      elsif !decision['出典URL'].split(';').map(&:strip).include?(source['URL'])
        errors << "Issue命題 #{claim['命題ID']}: 決定の出典URLと一致しない（#{decision_id}）"
      end
    end
  end
  unresolved = claims.count { |claim| claim['分類'] == '要確認' }
  unreviewed_sources = sources.count { |source| source['点検状態'] != '確認済み' }
  if require_reviewed && (unresolved.positive? || unreviewed_sources.positive?)
    errors << "意味判定が未完了: 出典 #{unreviewed_sources} 件・命題 #{unresolved} 件"
  end
  errors.first(30).each { |error| warn "FAIL: #{error}" }
  puts "Issue出典の構造検査: 実Issue #{expected.size} 件、出典表 #{sources.size} 件、命題表 #{claims.size} 件、出典未点検 #{unreviewed_sources} 件、命題要確認 #{unresolved} 件"
  puts errors.empty? ? 'PASS: 全実Issueの出典保存・ハッシュ・命題リンクは一致（意味判定は別）' : "FAIL: 出典保存・リンク #{errors.size} 件"
  errors.empty?
end

if $PROGRAM_NAME == __FILE__
  root = LedgerYaml::ROOT
  arg = ->(flag) { (i = ARGV.index(flag)) && ARGV[i + 1] }
  if (f = arg.call('--fetch'))
    File.write(f, JSON.generate(fetch_all))
    puts "保存: #{f}"
    exit 0
  end
  data = (f = arg.call('--from-json')) ? JSON.parse(File.read(f, encoding: 'UTF-8')) : fetch_all
  if ARGV.include?('--check-sources')
    exit(check_source_coverage(data, require_reviewed: ARGV.include?('--require-reviewed')) ? 0 : 1)
  end
  audit = IssueAudit.new(data)
  if ARGV.include?('--check-quotes')
    errors = audit.check_quotes
    errors.each { |e| warn "FAIL: #{e}" }
    st = audit.quote_stats
    ex = st[:exceptions]
    puts errors.empty? ? "PASS: 決定#{st[:decisions]}件中、照合#{st[:checked]}件・引用#{st[:quotes]}個・例外#{ex.size}件（逐語の引用なし明記: #{ex.join(' ')}）。出典コメントの転記との一致までを保証する（元の発言との一致は保証しない）" : "FAIL: 逐語の引用が出典に実在しない／照合できない #{errors.size} 件"
    exit(errors.empty? ? 0 : 1)
  end
  puts "Issue #{data['issues'].size} 件・コメント #{data['comments'].size} 件を走査 → 候補 #{audit.rows.size} 件"
  IssueAudit::CLASSES.each { |c| puts format('  %-18s %d', c, audit.counts.fetch(c, 0)) }
  if (cls = arg.call('--list'))
    audit.rows.select { |r| r['分類'] == cls }.each { |r| puts "#{r['Issue番号']}\t#{r['コメントURL']}\t#{r['候補の要約']}\t#{r['備考']}" }
  end
  if ARGV.include?('--write')
    puts "Issue点検.yaml に #{write_table(audit.rows, root)} 行を書いた"
    exit 0
  end
  table = LedgerYaml.read('Issue点検').to_h { |r| [r['コメントURL'], r] }
  missing = audit.rows.reject { |r| table.key?(r['コメントURL']) }
  stale = table.keys - audit.rows.map { |r| r['コメントURL'] }
  diff = audit.rows.select { |r| (t = table[r['コメントURL']]) && t['分類'] != r['分類'] && !t['備考'].include?(IssueAudit::MANUAL) }
  missing.first(20).each { |r| warn "未点検の候補: Issue ##{r['Issue番号']} #{r['コメントURL']}（自動分類: #{r['分類']}）#{r['候補の要約']}" }
  diff.first(20).each { |r| warn "分類が自動判定と違う: #{r['コメントURL']}（表: #{table[r['コメントURL']]['分類']} / 自動: #{r['分類']}）" }
  warn "未点検の候補 #{missing.size} 件・自動判定と違う分類 #{diff.size} 件・表にあるが候補でなくなった行 #{stale.size} 件" unless missing.empty? && diff.empty?
  actual = table.values.group_by { |r| r['分類'] }.transform_values(&:size)
  puts "台帳の分類: #{actual.map { |name, count| "#{name}=#{count}" }.join('、')}"
  puts missing.empty? && diff.empty? ? 'PASS: Issue点検.yaml は候補走査結果と一致（全Issueの意味判定は --check-sources で別途確認）' : 'FAIL: --write で更新するか、【手動】つきで分類を確定する'
  exit(missing.empty? && diff.empty? ? 0 : 1)
end
