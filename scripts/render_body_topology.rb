#!/usr/bin/env ruby
# frozen_string_literal: true
# Body-only Phase A visual. Full-area atlas generation is a separate phase.
require 'json'
require 'cgi'
root=File.expand_path('..',__dir__)
area=JSON.parse(File.read(File.join(root,'docs/topology/areas.json')))['areas'].find { |a| a['id']=='body' }
table=File.read(File.join(root,'docs/map-topology.md')).split('#### MAP相互接続台帳 v2',2).last.split('#### 寺町の地形不変条件',2).first
edges=table.lines.map do |line|
  m=line.match(/^\| ([A-Z]{3}-\d{2})\.([^ |]+) \| ([A-Z]{3}-\d{2})\.([^ |]+) \| (edge|door|event|oneway) \|/)
  [m[1],m[2],m[3],m[4],m[5]] if m && (area['maps'].include?(m[1]) || area['maps'].include?(m[3]))
end.compact
labels={'BDY-01'=>'口・イベント入口','BDY-02'=>'上半身','BDY-03'=>'下半身','BDY-04'=>'脳・迷路通路','BDY-05'=>'左手1','BDY-06'=>'左手2・末端','BDY-07'=>'右手1','BDY-08'=>'右手2・末端','BDY-09'=>'左足1','BDY-10'=>'左足2','BDY-11'=>'左足3・末端','BDY-12'=>'右足1','BDY-13'=>'右足2','BDY-14'=>'右足3・末端','BDY-15'=>'胃・分岐室','BDY-16'=>'心臓・分岐室','BDY-17'=>'肺・分岐室'}
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="1950" viewBox="0 0 1180 1950" role="img" aria-labelledby="title desc">','<title id="title">体内17MAP：上半身と下半身・手各2枚・足各3枚</title><desc id="desc">幼稚園児の想像する架空人体。園庭から一方向のイベント移動。頭は上、手は左右斜め上、足は左右斜め下の一本道。左右は身体の本人から見る（仰向けの本人を正面から見る構図）：画面左が本人の右手・右足、画面右が本人の左手・左足。</desc>','<defs><marker id="event-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#a44362"/></marker></defs>','<style>text{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;fill:#503c39}.door{stroke:#98725c;stroke-width:5;fill:none}.event{stroke:#a44362;stroke-width:4;fill:none;stroke-dasharray:10 7}.node{fill:#fff8ef;stroke:#9b735f;stroke-width:3}.label{font-size:19px;text-anchor:middle}.id{font-size:15px;font-weight:bold;text-anchor:middle}.note{font-size:18px}</style>','<rect width="1180" height="1950" fill="#f8e9dd"/><text x="30" y="40" font-size="29" font-weight="bold">架空の体内：胴体2MAP・手は各2MAP・足は各3MAP</text>','<text x="30" y="78" class="note">現実離れした幼稚園児の想像。肌色寄りの抽象概念。解剖図・写実的な臓器ではない。</text>']
positions=area['layout'].transform_values { |x,y| [x+100,y+160] }
positions['TRM-01']=[1030,140]
svg << '<rect x="940" y="105" width="210" height="64" rx="8" fill="#fff8ef" stroke="#a44362" data-reference="TRM-01"/><text x="1045" y="143" class="label">TRM-01 幼稚園の園庭</text>'
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
