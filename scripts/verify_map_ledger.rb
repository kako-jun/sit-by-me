#!/usr/bin/env ruby
# frozen_string_literal: true

# MAP生成台帳の構造検査。Markdownを正本のまま読み、生成可能性を
# "見た目の印象" ではなく 登録された全行・参照・接続端の不変条件で検査する。

ROOT = File.expand_path('..', __dir__)
require 'rexml/document'
require 'json'
require_relative 'verify_overseas_progression'

def read(name)
  File.read(File.join(ROOT, 'docs', name), encoding: 'UTF-8')
end

def fail!(message)
  warn "FAIL: #{message}"
  exit 1
end

def ids
  register = JSON.parse(read('topology/map-ids.json'))
  result = register.fetch('ranges').flat_map { |prefix, bounds| (bounds[0]..bounds[1]).map { |n| format('%s%02d',prefix,n) } }
  result += register.fetch('explicit').flat_map { |prefix, numbers| numbers.map { |n| prefix+n.to_s } }
  fail!('ID登録件数不一致') unless result.length == register.fetch('expected_count') && result.uniq.length == result.length
  result
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
fail!("契約行が登録件数ではない: #{contract_ids.length}") unless contract_ids.length == expected.length
fail!("契約ID重複: #{contract_ids.group_by(&:itself).select { |_, v| v.length > 1 }.keys.join(', ')}") unless contract_ids.uniq.length == expected.length
fail!("契約ID不足: #{(expected - contract_ids).join(', ')}") unless (expected - contract_ids).empty?
fail!("未知の契約ID: #{(contract_ids - expected).join(', ')}") unless (contract_ids - expected).empty?

valid_status = %w[blocked legacy-needs-review ready recreate-required-1920x1080]
contract_rows.each do |id, status, refs, mask, tbd|
  fail!("#{id}: 不正な状態 #{status}") unless valid_status.include?(status)
  fail!("#{id}: Refがない") if refs.nil? || refs.empty?
  fail!("#{id}: mask/output欄がない") if mask.nil? || mask.empty?
  fail!("#{id}: 具体的TBDがない") if tbd.nil? || tbd.empty?
  fail!("#{id}: TBDありなのにready") if status == 'ready'
  next unless status == 'legacy-needs-review'

  relative_image = mask[/`([^`]+\.png)`/, 1]
  fail!("#{id}: legacy画像パスがない") unless relative_image
  absolute_image = File.join(ROOT, relative_image)
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
  next unless line.start_with?('|')
  cells = line.split('|').map(&:strip)
  next if cells[1] == 'From' || cells[1].match?(/\A-+\z/)
  fail!("v2接続行の欄不足: #{line.strip}") unless cells.length == 6
  [cells[1], cells[2], cells[3], cells[4]]
end.compact
fail!('v2接続台帳が空') if topology_rows.empty?

edge_ends = Hash.new { |h, k| h[k] = [] }
door_ends = Hash.new { |h, k| h[k] = [] }
active = []
pending = []
opposite = { 'top' => 'bottom', 'bottom' => 'top', 'left' => 'right', 'right' => 'left' }
topology_rows.each_with_index do |(from, to, kind, reason), index|
  fail!("v2 row #{index + 1}: 未知・未設定の種別 #{kind.inspect}") unless %w[edge door event oneway pending].include?(kind)
  [from, to].each do |endpoint|
    id = endpoint.split('.').first
    fail!("v2 row #{index + 1}: 未知MAP #{id}") unless expected.include?(id)
  end
  from_side = from.split('.', 2)[1]
  to_side = to.split('.', 2)[1]
  if kind == 'pending'
    fail!("v2 row #{index + 1}: 保留理由がない") if reason.nil? || reason.empty?
    pending << [from, to]
    next
  end
  fail!("v2 row #{index + 1}: 自己接続 #{from} -> #{to}") if from.split('.').first == to.split('.').first
  if kind == 'edge'
    fail!("v2 row #{index + 1}: 不正・反対辺でない #{from} -> #{to}") unless opposite.key?(from_side) && opposite[from_side] == to_side
    [from, to].each { |endpoint| edge_ends[endpoint] << index + 1 }
  elsif kind == 'event'
    fail!('物語イベントの端名が不正') unless [from,to].all? { |p| p.match?(/\.event-[A-Za-z0-9_-]+\z/) }
  else
    [from, to].each do |endpoint|
      fail!("v2 row #{index + 1}: 扉IDがない #{endpoint}") unless endpoint.match?(/\.door(?:-[A-Za-z0-9_-]+)?\z/)
      door_ends[endpoint] << index + 1
    end
  end
  active << [from.split('.').first, to.split('.').first, kind]
end
topology_ids = topology_rows.flat_map { |from, to, _| [from.split('.').first, to.split('.').first] }.uniq
fail!("v2接続台帳にないMAP: #{(expected - topology_ids).join(', ')}") unless (expected - topology_ids).empty?
reused = edge_ends.select { |_, rows| rows.length > 1 }
fail!("同一画像辺の二重使用: #{reused.map { |k, v| "#{k}(#{v.join(',')})" }.join(', ')}") unless reused.empty?
reused_doors = door_ends.select { |_, rows| rows.length > 1 }
fail!("同一扉端の二重使用: #{reused_doors.keys.join(', ')}") unless reused_doors.empty?

fail!('旧サニーランドpendingは廃止') unless pending.empty?
entry=topology_rows.select { |_,_,kind,_| kind=='event' }
fail!('体内イベントは園庭E01から口F19への一方向のみ') unless entry.map { |a,b,k,_| [a,b,k] } == [['E01.event-kiss','F19.event-mouth','event']]
flights=topology_rows.select { |_,_,kind,_| kind=='oneway' }
fail!('一方向の海外渡航が不正') unless flights.map { |a,b,k,_| [a,b,k] } == [['F40.door-gate','F27.door-arrival','oneway']]
membership=JSON.parse(read('topology/areas.json'))
area_ids=membership.fetch('areas').map { |a| a.fetch('id') }
fail!('エリアID重複') unless area_ids.uniq==area_ids
members=membership.fetch('areas').flat_map { |a| a.fetch('maps') }
fail!('エリア所属が全MAP一意網羅でない') unless members.sort==expected.sort
membership.fetch('areas').each do |a|
  fail!("エリア配置のMAP不一致 #{a['id']}") unless a.fetch('layout').keys.sort==a.fetch('maps').sort
  fail!("エリア配置座標が不正 #{a['id']}") unless a['layout'].values.all? { |xy| xy.is_a?(Array) && xy.length==2 && xy.all? { |n| n.is_a?(Numeric) && n.finite? } }
end
body_paths=[%w[F19 F74],%w[F74 F76],%w[F74 F24],%w[F74 F77 F20],%w[F74 F78 F21],%w[F76 F79 F80 F22],%w[F76 F81 F82 F23],%w[F76 F25],%w[F74 F26],%w[F74 F75]]
body=membership['areas'].find { |a| a['id']=='body' }
fail!('体内17MAPの所属不一致') unless body && body['maps'].sort==body_paths.flatten.uniq.sort
body_pairs=body_paths.flat_map { |path| path.each_cons(2).map(&:sort) }.sort
body_active=active.select { |a,b,_| body['maps'].include?(a) && body['maps'].include?(b) }
fail!('体内の上半身/下半身・手2枚・足3枚の一本道接続が不一致') unless body_active.map { |a,b,_| [a,b].sort }.sort==body_pairs && body_active.all? { |_,_,kind| kind=='door' }
body_external=active.select { |a,b,_| body['maps'].include?(a) != body['maps'].include?(b) }
fail!('園庭以外からの体内入口／逆方向出口がある') unless body_external==[['E01','F19','event']]
coords=body['layout']; ux,uy=coords.fetch('F74');lx,ly=coords.fetch('F76')
fail!('胴体は上半身と下半身の縦2MAP') unless ux==lx && uy<ly
fail!('頭は胴体の上') unless coords['F24'][0]==ux && coords['F24'][1]<uy
[%w[F74 F77 F20],%w[F74 F78 F21],%w[F76 F79 F80 F22],%w[F76 F81 F82 F23]].each_with_index do |path,i|
  base_x,base_y=coords.fetch(path.first)
  direction_x=i.even? ? -1:1; direction_y=i<2 ? -1:1
  fail!('手は左右斜め上・足は左右斜め下の連続通路') unless path.drop(1).all? { |id| (coords[id][0]-base_x)*direction_x>0 } && path.each_cons(2).all? { |a,b| (coords[b][1]-coords[a][1])*direction_y>0 }
end
expected_spokes={'upper_torso'=>'F74','lower_torso'=>'F76','head'=>'F24','left_arm'=>%w[F77 F20],'right_arm'=>%w[F78 F21],'left_leg'=>%w[F79 F80 F22],'right_leg'=>%w[F81 F82 F23],'rooms'=>%w[F25 F26 F75]}
fail!('体内方向・枚数契約不一致') unless membership['body_spokes']==expected_spokes
sunny = %w[F07 F08 F09 E24 E23 F10 F63 F62 F61 E25 F64 F65]
sunny_ring = %w[F07 F08 F09 E24 E23 F10 F63 F62 F61 F07]
sunny_ring.each_cons(2) do |a,b|
  fail!("サニーランド円環がない #{a} -> #{b}") unless active.any? { |x,y,_| [x,y].sort == [a,b].sort }
end
%w[F64 F65].each do |id|
  routes=active.select { |a,b,_| [a,b].sort == ['E23',id].sort }
  fail!("任意施設の入口出口がない #{id}") unless routes.length==2
  fail!("任意施設に未承認出口 #{id}") if active.any? { |a,b,_| (a==id || b==id) && ![a,b].include?('E23') }
end
fail!('ゲームセンター分岐がない') unless active.any? { |a,b,_| [a,b].sort == %w[E25 F08] }
sunny_expected=sunny_ring.each_cons(2).map { |a,b| [a,b].sort }+[ %w[E25 F08] ]+%w[F64 F65].flat_map { |id| [['E23',id].sort]*2 }
sunny_actual=active.select { |a,b,_| sunny.include?(a)&&sunny.include?(b) }.map { |a,b,_| [a,b].sort }
fail!('サニーランド接続集合不一致') unless sunny_actual.sort==sunny_expected.sort

def graph_check(name, nodes, active, minimum)
  edges = active.select { |a, b, _| nodes.include?(a) && nodes.include?(b) }
  pairs = edges.map { |a, b, _| [a, b].sort }
  fail!("#{name}: MAP間接続が重複") unless pairs.uniq.length == pairs.length
  visited = []
  queue = [nodes.first]
  until queue.empty?
    node = queue.shift
    next if visited.include?(node)
    visited << node
    edges.each do |a, b, _|
      queue << b if a == node && !visited.include?(b)
      queue << a if b == node && !visited.include?(a)
    end
  end
  fail!("#{name}: 到達不能MAP #{(nodes - visited).join(', ')}") unless visited.sort == nodes.sort
  cycles = edges.length - nodes.length + 1
  fail!("#{name}: 独立閉路#{cycles}は最低#{minimum}未満") if cycles < minimum
  cycles
end

garden = (41..50).map { |n| format('F%02d', n) }
castle = (51..60).map { |n| format('F%02d', n) }
towers = (30..38).map { |n| format('F%02d', n) } + (66..73).map { |n| format('F%02d', n) }
garden_cycles = graph_check('兼六園', garden, active, 4)
castle_cycles = graph_check('金沢城', castle, active, 3)
tower_cycles = graph_check('双塔', towers, active, 1)
third=%w[F70 F71 F72 F73 F38]
third_pairs=third.each_cons(2).map(&:sort)
active.each do |a,b,_|
  if third.include?(a) && third.include?(b)
    fail!('第3塔の階飛ばし接続') unless third_pairs.include?([a,b].sort)
  elsif third.include?(a) != third.include?(b)
    fail!('第3塔の事前進入を許す未承認接続') unless [a,b].sort==%w[F37 F70]
  end
end
[%w[F30 F31 F66 F32 F67 F33 F37], %w[F30 F34 F68 F35 F69 F36 F37], %w[F37 F70 F71 F72 F73 F38]].each do |route|
  route.each_cons(2) do |a, b|
    fail!("双塔: 階層経路がない #{a} -> #{b}") unless active.any? { |x, y, kind| kind == 'door' && [x, y].sort == [a, b].sort }
  end
end
mountain = %w[N8 E22 F04 F05 F06]
mountain_pairs = mountain.each_cons(2).map(&:sort)
actual_mountain = active.select { |a, b, _| mountain.include?(a) && mountain.include?(b) }.map { |a, b, _| [a, b].sort }
fail!('卯辰山: 一本道の接続不一致・近道あり') unless actual_mountain.sort == mountain_pairs.sort
allowed_entrances = [%w[N11 N8].sort, %w[F06 F07].sort]
active.each do |a, b, _|
  next unless mountain.include?(a) != mountain.include?(b)
  fail!("卯辰山: 分岐禁止 #{a} -> #{b}") unless allowed_entrances.include?([a, b].sort)
end

[['late-dungeons.svg',[garden,castle,towers,mountain]], ['sunnyland.svg',[sunny]]].each do |filename,panels|
diagram_path = File.join(ROOT, 'docs/topology', filename)
fail!('接続図がない') unless File.file?(diagram_path)
begin
  diagram = REXML::Document.new(File.read(diagram_path, encoding: 'UTF-8'))
rescue REXML::ParseException => e
  fail!("接続図のXML不正: #{e.message}")
end

expected_nodes = panels.flatten.sort
actual_nodes = REXML::XPath.match(diagram, '//*[@data-map]').map { |node| node.attributes['data-map'] }.sort
fail!('接続図のMAP集合が正本と不一致') unless actual_nodes == expected_nodes
expected_paths = active.select { |a, b, _| expected_nodes.include?(a) && expected_nodes.include?(b) }.map { |a, b, kind| [*[a, b].sort, kind] }.sort
actual_paths = REXML::XPath.match(diagram, '//*[@data-from or @data-to]').map do |path|
  [*[path.attributes['data-from'], path.attributes['data-to']].sort, path.attributes['class']]
end.sort
fail!('接続図の有効辺集合が正本と不一致（欠落・余分・保留の実線化）') unless actual_paths == expected_paths

end
begin
  OverseasProgression.verify!(OverseasProgression.load(File.join(ROOT,'docs/topology/overseas-progression.json')))
rescue StandardError => e
  fail!("海外状態契約: #{e.message}")
end

puts "PASS: MAP contracts=#{contract_ids.length}, assets=#{asset_ids.length}, specs=#{spec_ids.length}, refs=#{reference_ids.length}, topology MAPs=#{topology_ids.length}, topology rows=#{topology_rows.length}, pending=#{pending.length}, cycles garden=#{garden_cycles} castle=#{castle_cycles} towers=#{tower_cycles}, diagram verified"
