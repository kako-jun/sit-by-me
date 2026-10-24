#!/usr/bin/env ruby
# frozen_string_literal: true

# docs/INDEX.md から（markdown リンクの連鎖で）到達できないファイル（孤立）と壊れたリンクをエラーにする。
#   ruby scripts/verify_index_reachable.rb              # エラーがあれば exit 1
#   LEDGER_ROOT=/path/to/root ruby scripts/verify_index_reachable.rb   # root を差し替え（テスト用）
#
# 規則の正本は台帳の docs/ledger/ファイル配置.yaml:
#   - リポ内の全ファイルが、ちょうど1つの配置規則（パターン）に一致すること（一致なし・複数一致はエラー）
#   - 到達=リンク の規則に一致するファイルは INDEX から辿れること（孤立=エラー）
#   - 到達=許可 の規則は許可リスト。許可リスト理由が必須で、入口（ファイルまたはディレクトリ）が INDEX から辿れること
#   - 辿ったページ（到達=リンクの md）の相対リンクが実在すること（壊れたリンク=エラー）
require 'open3'
require_relative 'ledger_yaml'

class IndexReachability
  INDEX = 'docs/INDEX.md'
  IGNORED = %w[.git __pycache__ .DS_Store .venv node_modules .pytest_cache].freeze
  MAP_ID = '(?:TRM|KRB|STN|NTR|NTB|UTS|SNL|SCH|NTA|UCH|BDY|APT|OVS|GRD|CST)-\d{2}'
  REACH = %w[リンク 許可].freeze

  attr_reader :errors, :warnings

  def initialize(root = LedgerYaml::ROOT)
    @root = File.expand_path(root)
    @errors = []
    @warnings = []
  end

  def err(msg) = @errors << msg
  def warn!(msg) = @warnings << msg

  def run
    rules = load_rules
    return self if rules.nil?

    files = list_files
    governing = classify(rules, files)
    reached_files, reached_dirs = walk(governing)
    check_orphans(governing, reached_files)
    check_allowlist(rules, governing, reached_files, reached_dirs)
    self
  end

  def load_rules
    unless File.file?(File.join(@root, INDEX))
      err("#{INDEX} が無い（到達性の起点）")
      return nil
    end
    rows = LedgerYaml.read('ファイル配置')
    if rows.empty?
      err('docs/ledger/ファイル配置.yaml が無い、または空')
      return nil
    end
    ids = rows.map { |r| r['配置ID'] }
    ids.group_by(&:itself).each { |id, v| err("ファイル配置: 配置ID '#{id}' が重複") if v.size > 1 }
    rows.each do |r|
      id = r['配置ID']
      begin
        r['_re'] = Regexp.new("\\A(?:#{r['パターン'].gsub('{MAP_ID}', MAP_ID)})\\z")
      rescue RegexpError => e
        err("ファイル配置 #{id}: パターンが不正（#{e.message}）")
      end
      err("ファイル配置 #{id}: 到達 '#{r['到達']}' は #{REACH.join('/')} のどちらでもない") unless REACH.include?(r['到達'])
      err("ファイル配置 #{id}: 到達=許可 には許可リスト理由が要る") if r['到達'] == '許可' && r['許可リスト理由'].strip.empty?
      err("ファイル配置 #{id}: 到達=リンク に許可リスト理由・入口は書かない（許可にする）") if r['到達'] == 'リンク' && !(r['許可リスト理由'].strip.empty? && r['入口'].strip.empty?)
    end
    rows.select { |r| r['_re'] }
  end

  # リポ内のファイル（repo root からの相対パス、/ 区切り）。git リポならトラッキング対象＋未追跡（.gitignore 除く）、でなければ全走査。
  def list_files
    paths =
      if File.exist?(File.join(@root, '.git'))
        out, st = Open3.capture2('git', '-C', @root, '-c', 'core.quotepath=off', 'ls-files', '-z', '--cached', '--others', '--exclude-standard')
        st.success? ? out.force_encoding('UTF-8').split("\0") : walk_fs
      else
        walk_fs
      end
    paths.reject { |p| p.split('/').any? { |seg| IGNORED.include?(seg) } }.select { |p| File.file?(File.join(@root, p)) }.uniq.sort
  end

  def walk_fs
    Dir.glob('**/*', File::FNM_DOTMATCH, base: @root).reject { |p| File.directory?(File.join(@root, p)) }
  end

  # 各ファイル → 一致した規則（ちょうど1つ）
  def classify(rules, files)
    gov = {}
    files.each do |f|
      hit = rules.select { |r| r['_re'].match?(f) }
      if hit.empty?
        err("配置規則に無いファイル: #{f}（ファイル配置.yaml に規則を足す）")
      elsif hit.size > 1
        err("複数の配置規則に一致: #{f}（#{hit.map { |r| r['配置ID'] }.join(', ')}）")
      else
        gov[f] = hit.first
      end
    end
    gov
  end

  # INDEX から到達ページ（到達=リンクの md）のリンクを辿る。戻り値: [到達したファイル集合, 到達したディレクトリ集合]
  def walk(governing)
    reached_files = { INDEX => true }
    reached_dirs = {}
    queue = [INDEX]
    until queue.empty?
      page = queue.shift
      links(page).each do |raw|
        target = resolve(page, raw)
        if target.nil?
          err("壊れたリンク（root の外）: #{page} → #{raw}")
          next
        end
        full = File.join(@root, target)
        if File.directory?(full)
          reached_dirs[target.sub(%r{/\z}, '')] = true
        elsif File.file?(full)
          next if reached_files[target]

          reached_files[target] = true
          queue << target if target.end_with?('.md') && governing[target] && governing[target]['到達'] == 'リンク'
        else
          err("壊れたリンク: #{page} → #{raw}")
        end
      end
    end
    [reached_files, reached_dirs]
  end

  def check_orphans(governing, reached_files)
    governing.each do |f, r|
      next unless r['到達'] == 'リンク'

      err("孤立ファイル（INDEX から辿れない）: #{f}（規則 #{r['配置ID']}。リンクを張る、または許可リストにする）") unless reached_files[f]
    end
  end

  def check_allowlist(rules, governing, reached_files, reached_dirs)
    rules.select { |r| r['到達'] == '許可' }.each do |r|
      id = r['配置ID']
      warn!("許可リスト #{id}: 一致するファイルが無い（不要になった規則か）") unless governing.values.any? { |g| g.equal?(r) }
      r['入口'].split(';').map(&:strip).reject(&:empty?).each do |e|
        e = e.sub(%r{/\z}, '')
        full = File.join(@root, e)
        if File.directory?(full)
          err("許可リスト #{id}: 入口ディレクトリ #{e} が INDEX から辿れない") unless reached_dirs[e]
        elsif File.file?(full)
          err("許可リスト #{id}: 入口 #{e} が INDEX から辿れない") unless reached_files[e]
        else
          err("許可リスト #{id}: 入口 #{e} が実在しない")
        end
      end
    end
  end

  # md 中のリンク先（コードブロック・インラインコード内は除く）
  def links(page)
    text = File.read(File.join(@root, page), encoding: 'UTF-8')
    keep = []
    fenced = false
    text.each_line do |ln|
      if ln.lstrip.start_with?('```', '~~~')
        fenced = !fenced
        next
      end
      keep << ln.gsub(/`[^`\n]*`/, '') unless fenced
    end
    body = keep.join
    found = body.scan(/!?\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)/).flatten
    found += body.scan(/^\s*\[[^\]]+\]:\s*<?(\S+?)>?\s*$/).flatten
    found.reject { |t| t.empty? || t.start_with?('#') || t =~ /\A[a-z][a-z0-9+.\-]*:/i }
  end

  # ページからの相対リンクを root からの相対パスにする。root の外なら nil
  def resolve(page, raw)
    t = raw.split('#', 2).first.split('?', 2).first
    t = t.b.gsub(/%\h\h/n) { |m| m[1, 2].hex.chr }.force_encoding('UTF-8')
    return page if t.empty?

    base = t.start_with?('/') ? File.join(@root, t) : File.expand_path(t, File.dirname(File.join(@root, page)))
    prefix = @root + '/'
    return nil unless base == @root || base.start_with?(prefix)

    base == @root ? '' : base[prefix.size..]
  end
end

if $PROGRAM_NAME == __FILE__
  v = IndexReachability.new.run
  v.warnings.each { |w| warn "WARN: #{w}" }
  if v.errors.empty?
    puts 'PASS: INDEX から全ファイルが到達でき、孤立・壊れたリンク・配置規則漏れはない'
  else
    v.errors.each { |e| warn "FAIL: #{e}" }
    warn "FAIL: #{v.errors.size} errors"
    exit 1
  end
end
