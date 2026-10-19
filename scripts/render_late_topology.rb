#!/usr/bin/env ruby
# frozen_string_literal: true

# Read connections from the canonical Markdown table; layout is schematic, not GPS.
require 'cgi'
ROOT = File.expand_path('..', __dir__)
source = File.read(File.join(ROOT, 'docs/map-topology.md'))
table = source.split('#### MAP相互接続台帳 v2', 2).last.split('#### 寺町の地形不変条件', 2).first
edges = table.lines.map do |line|
  match = line.match(/^\| ([A-Z]{3}-\d{2})\.([^ |]+) \| ([A-Z]{3}-\d{2})\.([^ |]+) \| (edge|door) \|/)
  [match[1], match[3], match[5]] if match
end.compact
specs = File.read(File.join(ROOT, 'docs/map-specifications.md')).lines.map do |line|
  cells = line.split('|').map(&:strip)
  [cells[1], cells[3]] if cells[1]&.match?(/^(?:OVS|GRD|CST)-\d{2}$|^UTS-02$/)
end.compact.to_h
panels = [
  ['兼六園：北↑・13辺・独立閉路4本', 20, 95, 890, 670,
   {'GRD-01'=>[120,550], 'GRD-02'=>[340,510], 'GRD-03'=>[130,330], 'GRD-04'=>[360,320], 'GRD-05'=>[470,160], 'GRD-06'=>[710,235], 'GRD-07'=>[690,410], 'GRD-08'=>[700,550], 'GRD-09'=>[490,550], 'GRD-10'=>[140,100]},
   ['8地区は任意訪問。実在園路をまとめた接続概念図（縮尺・道幅ではない）', '霞ヶ池（上段）→翠滝→瓢池（下段）／長谷池は別水面／池内は歩かない']],
  ['金沢城：北↑・12辺・独立閉路3本', 930, 95, 890, 670,
   {'CST-01'=>[780,220], 'CST-02'=>[590,220], 'CST-03'=>[350,110], 'CST-04'=>[490,340], 'CST-05'=>[290,270], 'CST-06'=>[100,425], 'CST-07'=>[330,465], 'CST-08'=>[700,435], 'CST-09'=>[510,560], 'CST-10'=>[720,570]},
   ['三の丸の西＝二の丸／二の丸の南の高所＝本丸／玉泉院丸は低地', '攻略目標：CST-03・CST-06・CST-08（任意順）→本丸→架空天守。戦闘・解錠TBD']],
  ['海外：左右攻略2塔＋脱出第3塔（すべて5階）', 20, 785, 1130, 690,
   {'OVS-04'=>[350,555], 'OVS-05'=>[140,465], 'OVS-06'=>[140,375], 'OVS-07'=>[140,285], 'OVS-08'=>[140,195], 'OVS-09'=>[140,105], 'OVS-10'=>[520,465], 'OVS-11'=>[520,375], 'OVS-12'=>[520,285], 'OVS-13'=>[520,195], 'OVS-14'=>[520,105], 'OVS-15'=>[340,65], 'OVS-16'=>[900,105], 'OVS-17'=>[900,215], 'OVS-18'=>[900,325], 'OVS-19'=>[900,435], 'OVS-20'=>[900,545]},
   ['左5F＝魔法のみ／右5F＝アビリティのみ。任意順→2体目撃破→空中通路でシャーと雑魚共闘', '共闘終了＝タイマー開始・第3塔初解放。全階同程度の広さで宝箱を選び下降→S005戦（時間継続）→実際の脱出で終了']],
  ['卯辰山：上・斜め上へ曲がる一本道', 1170, 785, 650, 690,
   {'UTS-01'=>[140,550], 'UTS-02'=>[360,445], 'UTS-03'=>[160,340], 'UTS-04'=>[370,235], 'UTS-05'=>[180,130]},
   ['分岐・宝箱脇道・近道なし。UTS-05北→SNL-01へ', 'サニーランドの双方向円環はsunnyland.svg参照', '下り廊下は約2MAP。階段のassist・幅はTBD']]
]
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1840" height="1500" viewBox="0 0 1840 1500" role="img" aria-labelledby="title desc">',
 '<title id="title">改訂ダンジョン接続図</title><desc id="desc">兼六園と金沢城は北上、海外は階層、卯辰山は移動順。線は正本v2の承認された接続のみ。池や堀の正確な形と通行幅は示さない。</desc>',
 '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;fill:#20364a}.edge{stroke:#3f6556;stroke-width:4;fill:none}.door{stroke:#a45f30;stroke-width:4;stroke-dasharray:9 6;fill:none}.node{fill:#fff;stroke:#3f6556;stroke-width:3}.id{font-size:14px;font-weight:700;text-anchor:middle}.label{font-size:14px;text-anchor:middle}.note{font-size:15px;fill:#526574}</style>',
 '<rect width="1840" height="1500" fill="#edf3f1"/><text x="30" y="40" font-size="27" font-weight="700">移動構造の改訂：兼六園・金沢城・海外三塔・卯辰山</text>',
 '<text x="30" y="70" class="note">実線＝屋外端接続／茶破線＝実在建物または階層の遷移。ゲーム設計の概念図。未生成・mask未確定・実装完了ではない。</text>']
panels.each_with_index do |(title, x, y, w, h, nodes, notes), pi|
  scoped = edges.select { |a,b,_| nodes.key?(a) && nodes.key?(b) }
  title = title.sub(/\d+辺・独立閉路\d+本/, "#{scoped.length}辺・独立閉路#{scoped.length-nodes.length+1}本")
  svg << %(<g transform="translate(#{x} #{y})"><rect width="#{w}" height="#{h}" rx="12" fill="#fbfdfb" stroke="#78948a" stroke-width="2"/><text x="20" y="32" font-size="21" font-weight="700">#{CGI.escapeHTML(title)}</text>)
  if pi == 0
    svg << '<ellipse cx="560" cy="275" rx="95" ry="92" fill="#d5eaf1"/><text x="560" y="270" class="label">霞ヶ池・上段</text><ellipse cx="200" cy="405" rx="65" ry="45" fill="#c6e3ee"/><text x="200" y="410" class="label">瓢池・下段</text><ellipse cx="430" cy="445" rx="50" ry="27" fill="#d5eaf1"/><text x="430" y="450" class="label">長谷池</text>'
  end
  edges.each do |a, b, kind|
    next unless nodes.key?(a) && nodes.key?(b)
    ax, ay = nodes[a]; bx, by = nodes[b]
    # Garden's southern connection wraps around the pond rather than crossing it.
    if pi == 0 && [a,b].sort == %w[GRD-04 GRD-05]
      d="M#{ax} #{ay} Q390 180 #{bx} #{by}"
    elsif pi == 0 && [a,b].sort == %w[GRD-05 GRD-06]
      d="M#{ax} #{ay} Q650 120 #{bx} #{by}"
    elsif pi == 0 && [a,b].sort == %w[GRD-03 GRD-04]
      d="M#{ax} #{ay} Q240 275 #{bx} #{by}"
    else
      d="M#{ax} #{ay} L#{bx} #{by}"
    end
    svg << %(<path class="#{kind}" d="#{d}" data-from="#{a}" data-to="#{b}"/>)
  end
  nodes.each do |id, (nx, ny)|
    labels = {'OVS-04'=>'共通基壇', 'OVS-05'=>'左・下層', 'OVS-07'=>'左・中層', 'OVS-09'=>'左・上層／M015', 'OVS-10'=>'右・下層', 'OVS-12'=>'右・中層', 'OVS-14'=>'右・上層／M016', 'OVS-15'=>'共通上層（救出候補）', 'OVS-20'=>'脱出終点（S005候補）', 'GRD-01'=>'真弓坂側入口', 'GRD-02'=>'時雨亭・長谷池', 'GRD-03'=>'瓢池・翠滝下段', 'GRD-04'=>'栄螺山・霞ヶ池西', 'GRD-05'=>'北岸・ことじ灯籠', 'GRD-06'=>'東岸・唐崎松', 'GRD-07'=>'曲水・根上松', 'GRD-08'=>'山崎山・花見橋側', 'GRD-09'=>'梅林・南周回', 'GRD-10'=>'桂坂口・石川橋', 'CST-01'=>'石川門', 'CST-02'=>'三の丸', 'CST-03'=>'菱櫓・五十間長屋', 'CST-04'=>'橋爪門・続櫓', 'CST-05'=>'二の丸', 'CST-06'=>'玉泉院丸（低地）', 'CST-07'=>'極楽橋・本丸附段', 'CST-08'=>'鶴の丸・東の丸', 'CST-09'=>'本丸（高所）', 'CST-10'=>'架空天守・上層', 'UTS-01'=>'浅野川橋・登り口', 'UTS-02'=>'山腹の蛇行路', 'UTS-03'=>'尾根の折返し', 'UTS-04'=>'石垣沿いの蛇行坂', 'UTS-05'=>'山頂・S002戦'}
    tower_labels={'OVS-04'=>'共通基壇', 'OVS-05'=>'左1F', 'OVS-06'=>'左2F', 'OVS-07'=>'左3F', 'OVS-08'=>'左4F', 'OVS-09'=>'左5F・魔法のみ', 'OVS-10'=>'右1F', 'OVS-11'=>'右2F', 'OVS-12'=>'右3F', 'OVS-13'=>'右4F', 'OVS-14'=>'右5F・アビリティのみ', 'OVS-15'=>'空中通路・雑魚共闘', 'OVS-16'=>'第3塔5F', 'OVS-17'=>'第3塔4F', 'OVS-18'=>'第3塔3F', 'OVS-19'=>'第3塔2F', 'OVS-20'=>'第3塔1F・S005'}
    label=tower_labels.fetch(id,labels.fetch(id,specs.fetch(id,id)))
    svg << %(<circle class="node" data-map="#{id}" cx="#{nx}" cy="#{ny}" r="32"/><text class="id" x="#{nx}" y="#{ny+5}">#{id}</text><text class="label" x="#{nx}" y="#{ny+53}">#{CGI.escapeHTML(label)}</text>)
  end
  notes.each_with_index { |note, i| svg << %(<text x="20" y="#{h-13-(notes.length-1-i)*22}" class="note">#{CGI.escapeHTML(note)}</text>) }
  svg << '</g>'
end
bridge = edges.find { |a,b,_| [a,b].sort == %w[CST-01 GRD-10] }
if bridge
  svg << %(<path class="#{bridge[2]}" d="M160 168 L25 168 L25 87 L1710 87 L1710 288" data-from="#{bridge[0]}" data-to="#{bridge[1]}"/><rect x="770" y="76" width="360" height="23" fill="#edf3f1"/><text x="950" y="93" class="label">GRD-10石川橋・M013戦 → 北へCST-01石川門</text>)
end
svg << '</svg>'
File.write(File.join(ROOT, 'docs/topology/late-dungeons.svg'), svg.join("\n")+"\n")
puts 'Rendered docs/topology/late-dungeons.svg from canonical v2 graph'
