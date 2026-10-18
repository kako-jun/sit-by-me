#!/usr/bin/env ruby
# frozen_string_literal: true
require 'cgi'
root=File.expand_path('..',__dir__)
text=File.read(File.join(root,'docs/map-topology.md')).split('#### MAP相互接続台帳 v2',2).last.split('#### 寺町の地形不変条件',2).first
nodes={'F07'=>[140,290,'入口1F・受付'], 'F08'=>[360,290,'下り廊下・前半'], 'F09'=>[590,290,'下り廊下・後半'], 'E24'=>[820,290,'地下水族館'], 'E23'=>[1080,420,'小さな屋外・シャチホコ'], 'F10'=>[1080,680,'狭い昭和の屋外動物園'], 'F63'=>[820,680,'創作の屋外階段'], 'F62'=>[590,680,'和室の宿泊棟'], 'F61'=>[140,680,'入口2F・全方向の窓'], 'E25'=>[360,440,'途中右のゲームセンター'], 'F64'=>[1320,245,'ラッコ館・任意宝箱'], 'F65'=>[1320,580,'海底洞窟・任意宝箱']}
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1540" height="880" viewBox="0 0 1540 880" role="img" aria-labelledby="title desc">','<title id="title">サニーランド双方向円環</title><desc id="desc">入口1階から廊下と地下水族館、屋外空間、動物園、創作の階段、宿泊棟、入口2階へ巡る。任意施設は入口出口別。方位や正確な勾配の図ではない。</desc>','<style>text{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;fill:#233a47}.door{fill:none;stroke:#a45f30;stroke-width:4;stroke-dasharray:9 6}.node{fill:white;stroke:#467260;stroke-width:3}.label{font-size:17px;text-anchor:middle}.note{font-size:18px}.id{font-size:22px;font-weight:bold;text-anchor:middle}</style>','<rect width="1540" height="880" fill="#edf3f1"/><text x="35" y="45" font-size="30" font-weight="bold">サニーランド：最初から両方向に進める円環・12MAP</text>','<text x="35" y="85" class="note">概念図：紙面の上下＝階高や南北ではない。下り廊下は約2MAP、周囲は雪の森。ゲームセンターの右は下降時の進行基準。</text>','<text x="35" y="122" class="note">入口棟は八角形。水族館出口付近＝ピラルク巨大水槽／壁際＝サメ・クジラの陰茎標本。</text>']
seen=Hash.new(0)
text.lines.each do |line|
 m=line.match(/^\| ((?:F\d{2}|E\d{2}))\.([^ |]+) \| ((?:F\d{2}|E\d{2}))\.([^ |]+) \| (edge|door) \|/)
 next unless m && nodes.key?(m[1]) && nodes.key?(m[3])
 a,b=m[1],m[3];ax,ay=nodes[a];bx,by=nodes[b];pair=[a,b].sort;index=seen[pair];seen[pair]+=1
 d=if pair==%w[E23 F64] || pair==%w[E23 F65]
   midx=(ax+bx)/2;midy=(ay+by)/2+(index==0 ? -70:70);"M#{ax} #{ay} Q#{midx} #{midy} #{bx} #{by}"
 else;"M#{ax} #{ay} L#{bx} #{by}";end
 svg<<%(<path class="#{m[5]}" d="#{d}" data-from="#{a}" data-to="#{b}" data-from-port="#{m[2]}" data-to-port="#{m[4]}"/>)
end
nodes.each{|id,(x,y,label)|svg<<%(<circle class="node" data-map="#{id}" cx="#{x}" cy="#{y}" r="31"/><text class="id" x="#{x}" y="#{y+8}">#{id}</text><text class="label" x="#{x}" y="#{y+60}">#{CGI.escapeHTML(label)}</text>)}
svg+=['<text x="35" y="790" class="note">入口1F→水族館側と入口2F→宿泊棟側の2経路。動物園→屋外階段→宿泊棟端はユーザー創作。</text>','<text x="35" y="825" class="note">ラッコ館・洞窟は入口と出口別、主円環には不要。同じ屋外空間の別扉へ戻すのはゲーム配置の採用。</text>','<text x="35" y="858" class="note">洞窟＝低予算昭和の海底探検の作り物（ダイオウイカ・難破船・ニンゲン）。画像・mask未生成、階内経路／幅TBD。</text>','</svg>']
File.write(File.join(root,'docs/topology/sunnyland.svg'),svg.join("\n")+"\n")
puts 'Rendered docs/topology/sunnyland.svg from canonical v2 graph'
