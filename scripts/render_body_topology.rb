#!/usr/bin/env ruby
# frozen_string_literal: true
# Body-only Phase A visual. Full-area atlas generation is a separate phase.
require 'cgi'
require_relative 'map_graph'
root=File.expand_path('..',__dir__)
graph=MapGraph::Graph.new(root)
area=graph.areas.find { |a| a['id']=='body' }
edges=graph.incident(area).map { |e| e.values_at('from','from_port','to','to_port','kind') }
labels=LedgerYaml.read('図配置').to_h { |r| [r['MAP_ID'],r['図ラベル']] }
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="1950" viewBox="0 0 1180 1950" role="img" aria-labelledby="title desc">','<title id="title">体内17MAP：上半身と下半身・手各2枚・足各3枚</title><desc id="desc">幼稚園児の想像する架空人体。園庭から一方向のイベント移動。頭は上、手は左右斜め上、足は左右斜め下の一本道。左右は身体の本人から見る（仰向けの本人を正面から見る構図）：画面左が本人の右手・右足、画面右が本人の左手・左足。</desc>','<defs><marker id="event-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#a44362"/></marker></defs>','<style>text{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;fill:#503c39}.door{stroke:#98725c;stroke-width:5;fill:none}.event{stroke:#a44362;stroke-width:4;fill:none;stroke-dasharray:10 7}.node{fill:#fff8ef;stroke:#9b735f;stroke-width:3}.label{font-size:19px;text-anchor:middle}.id{font-size:15px;font-weight:bold;text-anchor:middle}.note{font-size:18px}</style>','<rect width="1180" height="1950" fill="#f8e9dd"/><text x="30" y="40" font-size="29" font-weight="bold">架空の体内：胴体2MAP・手は各2MAP・足は各3MAP</text>','<text x="30" y="78" class="note">現実離れした幼稚園児の想像。肌色寄りの抽象概念。解剖図・写実的な臓器ではない。</text>']
positions=area['layout'].transform_values { |x,y| [x+100,y+160] }
positions['TRM-03']=[1030,140]
svg << '<rect x="940" y="105" width="210" height="64" rx="8" fill="#fff8ef" stroke="#a44362" data-reference="TRM-03"/><text x="1045" y="143" class="label">TRM-03 境内（幼稚園前の園庭）</text>'
edges.each_with_index do |(a,ap,b,bp,kind),i|
  ax,ay=positions.fetch(a);bx,by=positions.fetch(b);id="#{a}.#{ap}>#{b}.#{bp}:#{kind}"
  arrow=kind=='event' ? ' marker-end="url(#event-arrow)"':''
  svg << %(<path class="#{kind}" data-kind="#{kind}" data-edge-id="#{CGI.escapeHTML(id)}" data-from="#{a}" data-to="#{b}" data-from-port="#{ap}" data-to-port="#{bp}" d="M#{ax} #{ay} L#{bx} #{by}"#{arrow}/>)
end
area['maps'].each do |id|
 x,y=positions[id]
 label_y=id=='BDY-01' ? y-48:y+58
 svg<<%(<circle class="node" data-map="#{id}" cx="#{x}" cy="#{y}" r="34"/><text class="id" x="#{x}" y="#{y+5}">#{id}</text><text class="label" x="#{x}" y="#{label_y}">#{labels[id]}</text>)
end
svg<<'<text x="30" y="1455" class="note">抽象通路の接続（door-passageは物理的な扉ではない）</text>'
edges.each_with_index do |(a,ap,b,bp,kind),i|
 connector=kind=='event' ? '→':'↔'
 svg<<%(<text x="30" y="#{1490+i*24}" font-size="15">#{CGI.escapeHTML("#{a}.#{ap} #{connector} #{b}.#{bp}")}</text>)
end
svg<<'<text x="30" y="1920" class="note">胃・心臓の既存イベントを保持。脳内迷路・幅・maskと物語発火の実装は未確定。</text></svg>'
File.write(File.join(root,'docs/topology/body.svg'),svg.join("\n")+"\n")
puts 'Rendered docs/topology/body.svg (body-only Phase A)'
