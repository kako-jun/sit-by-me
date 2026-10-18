#!/usr/bin/env ruby
# frozen_string_literal: true

# Read connections from the canonical Markdown table; layout is schematic, not GPS.
require 'cgi'
ROOT = File.expand_path('..', __dir__)
source = File.read(File.join(ROOT, 'docs/map-topology.md'))
table = source.split('#### MAP相互接続台帳 v2', 2).last.split('#### 寺町の地形不変条件', 2).first
edges = table.lines.map do |line|
  match = line.match(/^\| ((?:F\d{2}|E\d{2}|N\d+))\.([^ |]+) \| ((?:F\d{2}|E\d{2}|N\d+))\.([^ |]+) \| (edge|door) \|/)
  [match[1], match[3], match[5]] if match
end.compact
specs = File.read(File.join(ROOT, 'docs/map-specifications.md')).lines.map do |line|
  cells = line.split('|').map(&:strip)
  [cells[1], cells[3]] if cells[1]&.match?(/^(?:F\d{2}|E22)$/)
end.compact.to_h
panels = [
  ['兼六園：北↑・13辺・独立閉路4本', 20, 95, 890, 670,
   {'F41'=>[120,550], 'F42'=>[340,510], 'F43'=>[130,330], 'F44'=>[360,320], 'F45'=>[470,160], 'F46'=>[710,235], 'F47'=>[690,410], 'F48'=>[700,550], 'F49'=>[490,550], 'F50'=>[140,100]},
   ['8地区は任意訪問。実在園路をまとめた接続概念図（縮尺・道幅ではない）', '霞ヶ池（上段）→翠滝→瓢池（下段）／長谷池は別水面／池内は歩かない']],
  ['金沢城：北↑・12辺・独立閉路3本', 930, 95, 890, 670,
   {'F51'=>[780,220], 'F52'=>[590,220], 'F53'=>[350,110], 'F54'=>[490,340], 'F55'=>[290,270], 'F56'=>[100,425], 'F57'=>[330,465], 'F58'=>[700,435], 'F59'=>[510,560], 'F60'=>[720,570]},
   ['三の丸の西＝二の丸／二の丸の南の高所＝本丸／玉泉院丸は低地', '攻略目標：F53・F56・F58（任意順）→本丸→架空天守。戦闘・解錠TBD']],
  ['海外：左右の多層双塔（高さの概念図・方位図ではない）', 20, 785, 1130, 690,
   {'F30'=>[530,545], 'F31'=>[240,430], 'F32'=>[240,285], 'F33'=>[240,140], 'F34'=>[830,430], 'F35'=>[830,285], 'F36'=>[830,140], 'F37'=>[530,85], 'F38'=>[530,260]},
   ['左M015／右M016：個性TBD。内部は九龍城的なカオス・雑多・無駄道・多数の袋小路', '階内平面は未設計。M003救出・4人合流後の制限時間・S005脱出戦との関係TBD']],
  ['卯辰山：上・斜め上へ曲がる一本道', 1170, 785, 650, 690,
   {'N8'=>[140,550], 'E22'=>[360,445], 'F04'=>[160,340], 'F05'=>[370,235], 'F06'=>[180,130]},
   ['分岐・宝箱脇道・近道なし。F06北→F07へ', 'サニーランド：二階建て入口・地下水族館・屋外動物園', '下り廊下は約2MAP。詳細接続は口述待ち']]
]
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1840" height="1500" viewBox="0 0 1840 1500" role="img" aria-labelledby="title desc">',
 '<title id="title">改訂ダンジョン接続図</title><desc id="desc">兼六園と金沢城は北上、海外は階層、卯辰山は移動順。線は正本v2の承認された接続のみ。池や堀の正確な形と通行幅は示さない。</desc>',
 '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;fill:#20364a}.edge{stroke:#3f6556;stroke-width:4;fill:none}.door{stroke:#a45f30;stroke-width:4;stroke-dasharray:9 6;fill:none}.node{fill:#fff;stroke:#3f6556;stroke-width:3}.id{font-size:19px;font-weight:700;text-anchor:middle}.label{font-size:14px;text-anchor:middle}.note{font-size:15px;fill:#526574}</style>',
 '<rect width="1840" height="1500" fill="#edf3f1"/><text x="30" y="40" font-size="27" font-weight="700">移動構造の改訂：兼六園・金沢城・海外双塔・卯辰山</text>',
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
    if pi == 0 && [a,b].sort == %w[F44 F45]
      d="M#{ax} #{ay} Q390 180 #{bx} #{by}"
    elsif pi == 0 && [a,b].sort == %w[F45 F46]
      d="M#{ax} #{ay} Q650 120 #{bx} #{by}"
    elsif pi == 0 && [a,b].sort == %w[F43 F44]
      d="M#{ax} #{ay} Q240 275 #{bx} #{by}"
    else
      d="M#{ax} #{ay} L#{bx} #{by}"
    end
    svg << %(<path class="#{kind}" d="#{d}" data-from="#{a}" data-to="#{b}"/>)
  end
  nodes.each do |id, (nx, ny)|
    labels = {'F30'=>'共通基壇', 'F31'=>'左・下層', 'F32'=>'左・中層', 'F33'=>'左・上層／M015', 'F34'=>'右・下層', 'F35'=>'右・中層', 'F36'=>'右・上層／M016', 'F37'=>'共通上層（救出候補）', 'F38'=>'脱出終点（S005候補）', 'F41'=>'真弓坂側入口', 'F42'=>'時雨亭・長谷池', 'F43'=>'瓢池・翠滝下段', 'F44'=>'栄螺山・霞ヶ池西', 'F45'=>'北岸・ことじ灯籠', 'F46'=>'東岸・唐崎松', 'F47'=>'曲水・根上松', 'F48'=>'山崎山・花見橋側', 'F49'=>'梅林・南周回', 'F50'=>'桂坂口・石川橋', 'F51'=>'石川門', 'F52'=>'三の丸', 'F53'=>'菱櫓・五十間長屋', 'F54'=>'橋爪門・続櫓', 'F55'=>'二の丸', 'F56'=>'玉泉院丸（低地）', 'F57'=>'極楽橋・本丸附段', 'F58'=>'鶴の丸・東の丸', 'F59'=>'本丸（高所）', 'F60'=>'架空天守・上層', 'N8'=>'浅野川橋・登り口', 'E22'=>'山腹の蛇行路', 'F04'=>'尾根の折返し', 'F05'=>'石垣沿いの蛇行坂', 'F06'=>'山頂・S002戦'}
    label=labels.fetch(id,specs.fetch(id,id))
    svg << %(<circle class="node" data-map="#{id}" cx="#{nx}" cy="#{ny}" r="27"/><text class="id" x="#{nx}" y="#{ny+7}">#{id}</text><text class="label" x="#{nx}" y="#{ny+48}">#{CGI.escapeHTML(label)}</text>)
  end
  notes.each_with_index { |note, i| svg << %(<text x="20" y="#{h-13-(notes.length-1-i)*22}" class="note">#{CGI.escapeHTML(note)}</text>) }
  svg << '</g>'
end
bridge = edges.find { |a,b,_| [a,b].sort == %w[F50 F51] }
if bridge
  svg << %(<path class="#{bridge[2]}" d="M160 168 L25 168 L25 87 L1710 87 L1710 288" data-from="#{bridge[0]}" data-to="#{bridge[1]}"/><rect x="770" y="76" width="360" height="23" fill="#edf3f1"/><text x="950" y="93" class="label">F50石川橋・M013戦 → 北へF51石川門</text>)
end
svg << '</svg>'
File.write(File.join(ROOT, 'docs/topology/late-dungeons.svg'), svg.join("\n")+"\n")
puts 'Rendered docs/topology/late-dungeons.svg from canonical v2 graph'
