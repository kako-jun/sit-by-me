#!/usr/bin/env ruby
# frozen_string_literal: true

# 必須キー（docs/ledger/必須キー.yaml）の強制。空欄=未決として検出、語彙外の値=エラー、『未決(要確認)』は未決表への登録が要る。
#   ruby scripts/ledger_required_keys.rb MAP_ID   # そのMAP（とエリア・建物・端）の必須キーが全部埋まっているか。欠落を列挙して exit 1
# verify_map_ledger.rb からはライブラリとして使う。
require_relative 'ledger_yaml'

module LedgerRequiredKeys
  UNDECIDED = '未決(要確認)'
  NOT_APPLICABLE = %w[該当なし なし].freeze
  KEY_TABLE_ID = { 'エリア' => 'エリアID', 'MAP' => 'MAP_ID', '建物' => '建物ID', '端' => '端ID', '決定' => '決定ID', '採用要素' => '採用要素ID', '素材' => '素材ID', '生成物' => '生成物ID' }.freeze

  module_function

  def cond_true?(cond, row)
    return true if cond.to_s.empty?

    cond.split('&').all? do |c|
      if (m = c.strip.match(/\A(.+?)(!=|=)(.*)\z/))
        eq = row[m[1]].to_s == m[3]
        m[2] == '=' ? eq : !eq
      else
        true
      end
    end
  end

  def vocab(tables)
    tables['語彙'].group_by { |r| r['グループ'] }.transform_values { |rs| rs.map { |r| r['値'] } }
  end

  # 戻り値: [errors(blank/語彙外/未登録の未決), undecided([テーブル, ID, キー])]
  def check_rows(tables, only: nil)
    errors = []
    undecided = []
    voc = vocab(tables)
    unresolved = tables['未決'].map { |r| [r['対象テーブル'], r['対象ID'], r['キー']] }
    map_ids = tables['MAP'].map { |r| r['MAP_ID'] }
    pools = tables['装飾プール'].map { |r| r['プールID'] }.uniq
    tables['必須キー'].each do |rk|
      t = rk['対象テーブル']
      idcol = KEY_TABLE_ID[t] or next
      tables[t].each do |row|
        id = row[idcol]
        next if only && !only.call(t, row)
        next unless rk['必須度'] == '必須' || cond_true?(rk['条件'], row)

        key = rk['キー']
        if key.start_with?('@')
          err = pseudo(key, tables, row, t)
          errors << "#{t} #{id}: #{key} #{err}" if err
          next
        end
        v = row[key].to_s
        if v.strip.empty?
          errors << "#{t} #{id}: 必須キー『#{key}』が空欄（未決は『#{UNDECIDED}』と明示して未決表に載せる）"
          next
        end
        if v == UNDECIDED
          undecided << [t, id, key]
          errors << "#{t} #{id}: 『#{key}』が#{UNDECIDED}なのに未決表に行が無い" unless unresolved.include?([t, id, key])
          next
        end
        g = rk['語彙グループ']
        next if g.to_s.empty?

        toks = %w[依存MAP 建物ID].include?(key) ? v.split(';') : [v]
        toks.each do |tok|
          ok = (voc[g] || []).include?(tok)
          ok ||= key == '依存MAP' && map_ids.include?(tok)
          ok ||= key == '装飾プールID' && pools.include?(tok)
          errors << "#{t} #{id}: 『#{key}』の値『#{tok}』が語彙（#{g}）に無い" unless ok
        end
      end
    end
    [errors, undecided]
  end

  def pseudo(key, tables, row, table)
    case key
    when '@接続'
      id = row['MAP_ID']
      hit = tables['接続'].any? { |c| c['端A'].start_with?("#{id}.") || c['端B'].start_with?("#{id}.") }
      hit ? nil : '接続表に行が無い（出入口と相手を書く）'
    when '@窓の整合'
      id = row['MAP_ID']
      wins = tables['窓'].select { |w| w['MAP_ID'] == id && w['適用時期'].to_s.empty? && w['種別'] != '窓なし' }
      case row['窓']
      when '窓あり' then wins.empty? ? '『窓あり』なのに窓表に窓の行が無い' : nil
      when '窓なし' then wins.empty? ? nil : '『窓なし』なのに窓表に窓の行がある'
      end
    when '@時期差分の整合'
      id = row['MAP_ID']
      bs = row['建物ID'].to_s.split(';')
      rows = tables['時期差分'].count { |r| r['MAP_ID'] == id }
      rows += tables['建物時期差分'].count { |r| bs.include?(r['建物ID']) } if row['表現する部位'] == '外側'
      if row['時期差分'].start_with?('あり')
        rows.zero? ? '『あり』なのに時期差分表・建物時期差分表に行が無い' : nil
      elsif row['時期差分'] == 'なし'
        rows.zero? ? nil : '『なし』なのに時期差分の行がある'
      end
    when '@語句'
      row['必須語'].to_s.empty? && row['禁止語'].to_s.empty? ? '必須語か禁止語のどちらかが要る' : nil
    end
  end

  def for_map(tables, map_id)
    m = tables['MAP'].find { |r| r['MAP_ID'] == map_id } or return [["MAP #{map_id} が MAP 表に無い"], []]
    bs = m['建物ID'].to_s.split(';')
    only = lambda do |t, row|
      case t
      when 'エリア' then row['エリアID'] == m['エリアID']
      when 'MAP' then row['MAP_ID'] == map_id
      when '建物' then bs.include?(row['建物ID'])
      when '端' then row['MAP_ID'] == map_id
      else false
      end
    end
    check_rows(tables, only: only)
  end
end

if $PROGRAM_NAME == __FILE__
  id = ARGV.fetch(0, '')
  tables = LedgerYaml.load_all
  errors, undecided = LedgerRequiredKeys.for_map(tables, id)
  lines = errors + undecided.reject { |t, i, k| errors.any? { |e| e.include?("#{t} #{i}: 『#{k}』") } }.map { |t, i, k| "#{t} #{i}: 『#{k}』が未決（生成を起動できない）" }
  puts lines
  exit(lines.empty? ? 0 : 1)
end
