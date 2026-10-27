#!/usr/bin/env ruby
# frozen_string_literal: true
require 'cgi'
require_relative 'ledger_yaml'
root = ENV['LEDGER_ROOT'] || File.expand_path('..', __dir__)

maps = LedgerYaml.read('MAP').select { |row| row['エリアID'] == 'sunnyland' }
map_ids = maps.map { |row| row['MAP_ID'] }
expected_ids = %w[SNL-01 SNL-02 SNL-03 SNL-04 SNL-05 SNL-06 SNL-07 SNL-08 SNL-09 SNL-10 SNL-11 SNL-12]
raise "sunnyland MAP ledger mismatch: #{map_ids.inspect}" unless map_ids.sort == expected_ids.sort
specified_ids = LedgerYaml.read('MAP仕様').map { |r| r['MAP_ID'] }
raise 'MAP仕様.yaml lacks one or more sunnyland MAP IDs' unless (expected_ids - specified_ids).empty?

connections = LedgerYaml.read('接続').filter_map do |row|
  a, b, kind = row.values_at('端A', '端B', '種別')
  next unless %w[door edge].include?(kind)
  next unless a.split('.', 2).first.start_with?('SNL-') && b.split('.', 2).first.start_with?('SNL-')

  [a.split('.', 2).first, a.split('.', 2).last, b.split('.', 2).first, b.split('.', 2).last, kind]
end
edges = connections
nodes = {'SNL-01'=>[140,290,'入口1F・受付'], 'SNL-02'=>[360,290,'下り廊下・前半'], 'SNL-04'=>[590,290,'下り廊下・後半'], 'SNL-05'=>[820,290,'地下水族館'], 'SNL-06'=>[1080,420,'小さな屋外・シャチホコ'], 'SNL-09'=>[1080,680,'狭い昭和の屋外動物園'], 'SNL-10'=>[820,680,'創作の屋外階段'], 'SNL-11'=>[590,680,'和室の宿泊棟'], 'SNL-12'=>[140,680,'入口2F・全方向の窓'], 'SNL-03'=>[360,440,'途中右のゲームセンター'], 'SNL-07'=>[1320,245,'ラッコ館・任意宝箱'], 'SNL-08'=>[1320,580,'海底洞窟・任意宝箱']}
raise "sunnyland connection ledger mismatch: #{edges.length}" unless edges.length == 14
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1540" height="880" viewBox="0 0 1540 880" role="img" aria-labelledby="title desc">','<title id="title">サニーランド双方向円環</title><desc id="desc">入口1階から廊下と地下水族館、屋外空間、動物園、創作の階段、宿泊棟、入口2階へ巡る。任意施設は入口出口別。方位や正確な勾配の図ではない。</desc>','<style>text{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;fill:#233a47}.door{fill:none;stroke:#a45f30;stroke-width:4;stroke-dasharray:9 6}.node{fill:white;stroke:#467260;stroke-width:3}.label{font-size:17px;text-anchor:middle}.note{font-size:18px}.id{font-size:15px;font-weight:bold;text-anchor:middle}</style>','<rect width="1540" height="880" fill="#edf3f1"/><text x="35" y="45" font-size="30" font-weight="bold">サニーランド：最初から両方向に進める円環・12MAP</text>','<text x="35" y="85" class="note">概念図：紙面の上下＝階高や南北ではない。下り廊下は約2MAP、周囲は雪の森。ゲームセンターの右は下降時の進行基準。</text>','<text x="35" y="122" class="note">入口棟は八角形。水族館出口付近＝ピラルク巨大水槽／壁際＝サメ・クジラの陰茎標本。</text>']
seen=Hash.new(0)
edges.each do |a,ap,b,bp,kind|
 next unless nodes.key?(a) && nodes.key?(b)
 ax,ay=nodes[a];bx,by=nodes[b];pair=[a,b].sort;index=seen[pair];seen[pair]+=1
 d=if pair==%w[SNL-06 SNL-07] || pair==%w[SNL-06 SNL-08]
   midx=(ax+bx)/2;midy=(ay+by)/2+(index==0 ? -70:70);"M#{ax} #{ay} Q#{midx} #{midy} #{bx} #{by}"
 else;"M#{ax} #{ay} L#{bx} #{by}";end
 svg<<%(<path class="#{kind}" d="#{d}" data-from="#{a}" data-to="#{b}" data-from-port="#{ap}" data-to-port="#{bp}"/>)
end
nodes.each{|id,(x,y,label)|svg<<%(<circle class="node" data-map="#{id}" cx="#{x}" cy="#{y}" r="34"/><text class="id" x="#{x}" y="#{y+5}">#{id}</text><text class="label" x="#{x}" y="#{y+63}">#{CGI.escapeHTML(label)}</text>)}
svg+=['<text x="35" y="790" class="note">入口1F→水族館側と入口2F→宿泊棟側の2経路。動物園→屋外階段→宿泊棟端はユーザー創作。</text>','<text x="35" y="825" class="note">ラッコ館・洞窟は入口と出口別、主円環には不要。同じ屋外空間の別扉へ戻すのはゲーム配置の採用。</text>','<text x="35" y="858" class="note">洞窟＝低予算昭和の海底探検の作り物（ダイオウイカ・難破船・ニンゲン）。画像・mask未生成、階内経路／幅TBD。</text>','</svg>']
File.write(File.join(root,'docs/topology/sunnyland.svg'),svg.join("\n")+"\n")
puts 'Rendered docs/topology/sunnyland.svg from YAML ledger'
