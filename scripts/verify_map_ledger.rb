#!/usr/bin/env ruby
# frozen_string_literal: true

# MAP生成台帳の構造検査。Markdownを正本のまま読み、生成可能性を
# "見た目の印象" ではなく 104 行・参照・接続端の不変条件で検査する。

ROOT = File.expand_path('..', __dir__)

def read(name)
  File.read(File.join(ROOT, 'docs', name), encoding: 'UTF-8')
end

def fail!(message)
  warn "FAIL: #{message}"
  exit 1
end

def ids
  (1..33).map { |n| format('E%02d', n) } +
    [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12].map { |n| "N#{n}" } +
    (1..60).map { |n| format('F%02d', n) }
end

expected = ids
checklist = read('map-contract-checklist.md')
specifications = read('map-specifications.md')
references = read('map-reference-research.md')
topology = read('map-topology.md')
assets = read('map-asset-registry.md')

contract_rows = checklist.lines.map do |line|
  next unless line.match?(/^\| (?:E\d{2}|N\d+|F\d{2}) \|/)

  cells = line.split('|').map(&:strip)
  [cells[1], cells[2], cells[3], cells[4], cells[5]]
end.compact

contract_ids = contract_rows.map(&:first)
fail!("契約行が104件ではない: #{contract_ids.length}") unless contract_ids.length == 104
fail!("契約ID重複: #{contract_ids.tally.select { |_, v| v > 1 }.keys.join(', ')}") unless contract_ids.uniq.length == 104
fail!("契約ID不足: #{(expected - contract_ids).join(', ')}") unless (expected - contract_ids).empty?
fail!("未知の契約ID: #{(contract_ids - expected).join(', ')}") unless (contract_ids - expected).empty?

valid_status = %w[blocked legacy-needs-review ready]
contract_rows.each do |id, status, refs, mask, tbd|
  fail!("#{id}: 不正な状態 #{status}") unless valid_status.include?(status)
  fail!("#{id}: Refがない") if refs.nil? || refs.empty?
  fail!("#{id}: mask/output欄がない") if mask.nil? || mask.empty?
  fail!("#{id}: 具体的TBDがない") if tbd.nil? || tbd.empty?
  fail!("#{id}: TBDありなのにready") if status == 'ready'
  next unless status == 'legacy-needs-review'

  relative_image = mask[/`([^`]+\.png)`/, 1]
  fail!("#{id}: legacy画像パスがない") unless relative_image
  absolute_image = File.join(ROOT, 'sample', 'field', relative_image)
  fail!("#{id}: legacy画像がない #{relative_image}") unless File.file?(absolute_image)
end

reference_ids = references.scan(/^\| (R\d{3}) \|/).flatten.uniq
contract_rows.each do |id, _, refs, _, _|
  refs.split(',').each do |ref|
    fail!("#{id}: 未登録Ref #{ref}") unless reference_ids.include?(ref)
  end
end

spec_rows = specifications.lines.map do |line|
  next unless line.match?(/^\| (?:E\d{2}|N\d+|F\d{2})(?:\s|\|)/)

  cells = line.split('|').map(&:strip)
  [cells[1].split.first, cells]
end.compact
spec_ids = spec_rows.map(&:first).uniq
fail!("個別仕様にないID: #{(expected - spec_ids).join(', ')}") unless (expected - spec_ids).empty?
spec_rows.each do |id, cells|
  fail!("#{id}: 個別仕様の欄不足") unless cells.length >= 6
  fail!("#{id}: 一言特徴がない") if cells[3].nil? || cells[3].empty?
  fail!("#{id}: 接続・通行条件がない") if cells[4].nil? || cells[4].empty?
end

asset_ids = assets.scan(/^\| ((?:E\d{2}|N\d+|F\d{2})) \|/).flatten.uniq
fail!("画像台帳にないID: #{(expected - asset_ids).join(', ')}") unless (expected - asset_ids).empty?

start = topology.index('#### MAP相互接続台帳 v2')
finish = topology.index('#### 寺町の地形不変条件', start)
fail!('v2接続台帳の範囲を取得できない') unless start && finish
topology_rows = topology[start...finish].lines.map do |line|
  next unless line.match?(/^\| (?:E\d{2}|N\d+|F\d{2})\./)

  cells = line.split('|').map(&:strip)
  [cells[1], cells[2], cells[3]]
end.compact
fail!('v2接続台帳が空') if topology_rows.empty?

edge_ends = Hash.new { |h, k| h[k] = [] }
opposite = { 'top' => 'bottom', 'bottom' => 'top', 'left' => 'right', 'right' => 'left' }
topology_rows.each_with_index do |(from, to, kind), index|
  [from, to].each do |endpoint|
    id = endpoint.split('.').first
    fail!("v2 row #{index + 1}: 未知MAP #{id}") unless expected.include?(id)
  end
  next unless kind == 'edge'

  from_side = from.split('.', 2)[1]
  to_side = to.split('.', 2)[1]
  fail!("v2 row #{index + 1}: 反対辺でない #{from} -> #{to}") unless opposite[from_side] == to_side
  [from, to].each { |endpoint| edge_ends[endpoint] << index + 1 }
end
topology_ids = topology_rows.flat_map { |from, to, _| [from.split('.').first, to.split('.').first] }.uniq
fail!("v2接続台帳にないMAP: #{(expected - topology_ids).join(', ')}") unless (expected - topology_ids).empty?
reused = edge_ends.select { |_, rows| rows.length > 1 }
fail!("同一画像辺の二重使用: #{reused.map { |k, v| "#{k}(#{v.join(',')})" }.join(', ')}") unless reused.empty?

puts "PASS: MAP contracts=#{contract_ids.length}, assets=#{asset_ids.length}, specs=#{spec_ids.length}, refs=#{reference_ids.length}, topology MAPs=#{topology_ids.length}, topology rows=#{topology_rows.length}, repeated edge endpoints=0"
