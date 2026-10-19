#!/usr/bin/env ruby
# frozen_string_literal: true

# 台帳 + sit-diorama の規約からフィールド生成プロンプトを組む。
# 生成そのものは行わない。ready かつ TBD 空欄でない限り、プロンプトを
# 出力しないため、未決事項を画像生成でごまかせない。

ROOT = File.expand_path('..', __dir__)

def read_doc(name)
  File.read(File.join(ROOT, 'docs', name), encoding: 'UTF-8')
end

def row_for(document, id)
  document.lines.find { |line| line.start_with?("| #{id} ") }
end

id = ARGV.fetch(0, '').upcase
abort 'usage: ruby scripts/build_map_prompt.rb MAP_ID' unless id.match?(/\A[A-Z]{3}-\d{2}\z/)

checklist = read_doc('map-contract-checklist.md')
specifications = read_doc('map-specifications.md')
topology = read_doc('map-topology.md')
contract = row_for(checklist, id)
specification = row_for(specifications, id)
abort "#{id}: contract row is missing" unless contract
abort "#{id}: specification row is missing" unless specification

contract_cells = contract.split('|').map(&:strip)
status, refs, mask, tbd = contract_cells[2], contract_cells[3], contract_cells[4], contract_cells[5]
unless status == 'ready' && tbd.to_s.empty?
  abort <<~MESSAGE
    #{id}: prompt generation is blocked.
    status: #{status}
    refs: #{refs}
    mask/output: #{mask}
    unresolved TBD: #{tbd}
  MESSAGE
end

spec_cells = specification.split('|').map(&:strip)
era, feature, route, fixed = spec_cells[2], spec_cells[3], spec_cells[4], spec_cells[5]

section_start = topology.index('#### MAP相互接続台帳 v2')
section_end = topology.index('#### 寺町の地形不変条件', section_start)
edges = topology[section_start...section_end].lines.grep(/^\| #{id}\./)
connections = edges.map { |line| line.split('|').map(&:strip)[1..3].join(' / ') }
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
