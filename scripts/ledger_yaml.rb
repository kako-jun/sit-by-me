# frozen_string_literal: true

require 'yaml'

# docs/ledger/<表名>.yaml の読み込み。マスターは日本語キーの YAML（表ごと1ファイル、中身は行のリスト）。
# 全スカラーを文字列として扱う（読み込み時に to_s で正規化。no/yes/null/001/1e3 が型変換されても文字列へ戻す）。
# 書き出しは Python 側（ledger_io.py）だけが行う。
module LedgerYaml
  ROOT = ENV['LEDGER_ROOT'] || File.expand_path('..', __dir__)
  LEDGER = File.join(ROOT, 'docs', 'ledger')

  module_function

  def str(value)
    value.nil? ? '' : value.to_s
  end

  def path(table)
    File.join(LEDGER, "#{table}.yaml")
  end

  # 行は Hash（欠けた列は '' を返す既定値つき）。
  def read(table)
    p = path(table)
    return [] unless File.file?(p)

    text = File.read(p, encoding: 'UTF-8')
    check_syntax(table, text)
    data = YAML.safe_load(text, aliases: false)
    return [] if data.nil?
    raise "#{table}.yaml: 最上位は行のリストでなければならない" unless data.is_a?(Array)

    data.each_with_index.map do |r, i|
      raise "#{table}.yaml: #{i + 1}行目が辞書でない" unless r.is_a?(Hash)

      row = Hash.new('')
      r.each { |k, v| row[str(k)] = str(v) }
      row
    end
  end

  # YAML の構文木で検査する（Python 側 ledger_io._check_syntax と同じ規則）: 全スカラー（キーも値も）は引用符つきか block scalar、
  # 同じ行（辞書）に同じキーを2回書かない。未引用だと 2026-10-21 が Date になる・no が false になる・重複キーが黙って後勝ちになる。
  def check_syntax(table, text)
    doc = Psych.parse(text)
    return if doc.nil?

    seq = doc.root
    raise "#{table}.yaml: 最上位は行のリストでなければならない" unless seq.is_a?(Psych::Nodes::Sequence)

    seq.children.each_with_index do |item, i|
      raise "#{table}.yaml: #{i + 1}行目が辞書でない" unless item.is_a?(Psych::Nodes::Mapping)

      seen = {}
      item.children.each_slice(2) do |k, v|
        [k, v].each do |n|
          raise "#{table}.yaml: #{n.start_line + 1}行目: スカラー以外（入れ子）は使えない" unless n.is_a?(Psych::Nodes::Scalar)
          raise "#{table}.yaml: #{n.start_line + 1}行目: 引用符のないスカラー『#{n.value}』（全スカラーは \"…\" か |- ブロックで書く）" if n.plain
        end
        raise "#{table}.yaml: #{k.start_line + 1}行目: キー『#{k.value}』が同じ行（#{seen[k.value]}行目に既出）で重複している" if seen.key?(k.value)

        seen[k.value] = k.start_line + 1
      end
    end
  end

  # 表に現れるキー（先頭から出現順の和集合）。
  def header(table)
    read(table).flat_map(&:keys).uniq
  end

  def tables
    Dir.glob(File.join(LEDGER, '*.yaml')).map { |p| File.basename(p, '.yaml') }.sort
  end

  def load_all
    tables.to_h { |t| [t, read(t)] }
  end
end
