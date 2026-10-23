#!/usr/bin/env ruby
# frozen_string_literal: true

# 台帳 + sit-diorama の規約からフィールド生成プロンプトを組む。
# 生成そのものは行わない。ready かつ TBD 空欄でない限り、プロンプトを
# 出力しないため、未決事項を画像生成でごまかせない。
#
# legacy・非正本（docs/content-registry.md）。md の表は見出し行の列名で読む（md_table.rb。列の位置に依存しない）。
# 台帳（docs/ledger/MAP.yaml）に行がある MAP（寺町）は md を読まず、台帳の状態・未決で停止する（プロンプトは
# oblique_build.py が台帳ゲートつきで作る）。

ROOT = File.expand_path('..', __dir__)
require_relative 'md_table'
require_relative 'ledger_yaml'

def read_doc(name)
  File.read(File.join(ROOT, 'docs', name), encoding: 'UTF-8')
end

# 先頭列（ID／MAP）がこの MAP の行。複数の表にまたがって探す
def table_row(document, first, id, *names)
  MdTable.rows(document, first, *names).find { |r| r[first].to_s.split.first == id }
end

SPEC_ROUTE_COLUMNS = %w[不変条件／接続 方位・主路・通行条件 接続].freeze
SPEC_FIXED_COLUMNS = %w[暫定固定 不変条件／TBD].freeze

id = ARGV.fetch(0, '').upcase
abort 'usage: ruby scripts/build_map_prompt.rb MAP_ID' unless id.match?(/\A[A-Z]{3}-\d{2}\z/)

ledger_row = LedgerYaml.read('MAP').find { |r| r['MAP_ID'] == id && r['状態'] != '廃止' }
if ledger_row
  open_items = LedgerYaml.read('未決').select { |u| u['状態'] == '未決' && (u['対象ID'] == id || u['対象ID'].start_with?("#{id}.")) }
  abort <<~MESSAGE
    #{id}: prompt generation is blocked here. This MAP is managed by the ledger (docs/ledger/MAP.yaml), not by the legacy md tables.
    ledger status: #{ledger_row['状態']} / adoption: #{ledger_row['採用状態']}
    unresolved (docs/ledger/未決.yaml): #{open_items.empty? ? 'none' : open_items.map { |u| "#{u['未決ID']} #{u['キー']}" }.join(', ')}
    Build the prompt with oblique_build.py (ledger-gated): see .claude/skills/sit-field-background/tools/README.md
  MESSAGE
end

checklist = read_doc('map-contract-checklist.md')
specifications = read_doc('map-specifications.md')
topology = read_doc('map-topology.md')
contract = table_row(checklist, 'ID', id, '状態', 'Ref', 'mask / 出力', '具体的TBD')
specification = table_row(specifications, 'MAP', id, '時期', '一言特徴')
abort "#{id}: contract row is missing" unless contract
abort "#{id}: specification row is missing" unless specification

status, refs, mask, tbd = contract['状態'], contract['Ref'], contract['mask / 出力'], contract['具体的TBD']
unless status == 'ready' && tbd.to_s.empty?
  abort <<~MESSAGE
    #{id}: prompt generation is blocked.
    status: #{status}
    refs: #{refs}
    mask/output: #{mask}
    unresolved TBD: #{tbd}
  MESSAGE
end

era, feature = specification['時期'], specification['一言特徴']
route = MdTable.pick(specification, *SPEC_ROUTE_COLUMNS)
fixed = MdTable.pick(specification, *SPEC_FIXED_COLUMNS)

section_start = topology.index('#### MAP相互接続台帳 v2')
section_end = topology.index('#### 寺町の地形不変条件', section_start)
edges = MdTable.section_rows(topology[section_start...section_end], 'From', 'To', '種別', '主路・状態').select { |r| r['From'].to_s.start_with?("#{id}.") }
connections = edges.map { |r| [r['From'], r['To'], r['種別']].join(' / ') }
abort "#{id}: ready but has no topology entry" if connections.empty?

puts <<~PROMPT
  FIELD BACKGROUND CONTRACT — #{id}
  Subject / unique landmark: #{feature}
  Era and story phase: #{era}
  Required route: #{route}
  Fixed constraints: #{fixed}
  Canonical exits: #{connections.join('; ')}
  References: #{refs}

  Contemporary K Prefecture, Japan, winter; handmade tabletop diorama, almost top-down 80–85 degree view, shallow depth, cardboard base and surrounding room visible. Use cotton snow, cardboard/paper-clay buildings, black paper or sandpaper roads, cellophane/resin water, rough cut edges, glue traces and restrained everyday snow-country grime only. No people, no text, no logos, no sky or distant perspective. Draw every canonical exit as a broad unobstructed route to the correct image edge; all other edges are closed. Keep treasure branches internal and separate from the required route. Do not place water, fences, walls, deep snow, stairs, rubble, or foreground objects across the required wheelchair route. For mountains or significant slopes, use a gentle serpentine or hairpin route rather than a straight climb.
  PROMPT
