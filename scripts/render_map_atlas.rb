#!/usr/bin/env ruby
# frozen_string_literal: true
require 'cgi'
require 'fileutils'
require_relative 'map_graph'
module MapAtlas
  ROOT=File.expand_path('..',__dir__)
  STYLE='text{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;fill:#263f4e}.node{fill:#fff;stroke:#527b69;stroke-width:3}.ref{fill:#fff7eb;stroke:#ad8456;stroke-width:2}.edge{fill:none;stroke:#527b69;stroke-width:3}.door{fill:none;stroke:#a16b42;stroke-width:3;stroke-dasharray:8 5}.event{fill:none;stroke:#ac4871;stroke-width:4;stroke-dasharray:6 5}.oneway{fill:none;stroke:#5262a8;stroke-width:4}.id{font-size:21px;font-weight:bold;text-anchor:middle}.label{font-size:16px;text-anchor:middle;paint-order:stroke;stroke:#fbfdfb;stroke-width:5;stroke-linejoin:round}.note{font-size:16px}.small{font-size:14px}.heading{font-size:25px;font-weight:bold}'
  def self.esc(s); CGI.escapeHTML(s.to_s);end
  def self.header(w,h,title)
    %(<svg xmlns="http://www.w3.org/2000/svg" width="#{w}" height="#{h}" viewBox="0 0 #{w} #{h}" role="img"><title>#{esc(title)}</title><defs><marker id="directed-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#8b4c83"/></marker></defs><style>#{STYLE}</style><rect width="#{w}" height="#{h}" fill="#edf3f1"/>)
  end
  def self.attrs(e,canonical=true)
    key=canonical ? 'data-edge-id':'data-reference-edge-id'
    %(#{key}="#{esc(e['id'])}" data-kind="#{e['kind']}" data-from="#{e['from']}" data-to="#{e['to']}" data-from-port="#{e['from_port']}" data-to-port="#{e['to_port']}")
  end
  def self.arrow(e); %w[event oneway].include?(e['kind']) ? ' marker-end="url(#directed-arrow)"':'';end
  def self.port_label(e)
    "#{e['from']}.#{e['from_port']} #{%w[event oneway].include?(e['kind']) ? '→':'↔'} #{e['to']}.#{e['to_port']}"
  end
  def self.node_label(id,spec)
    text=spec.fetch(id,id)
    text.scan(/.{1,12}/m).first(3)
  end
  def self.area_content(g,area,spec,canonical_cross:true)
    coords=area.fetch('layout');xs=coords.values.map(&:first);ys=coords.values.map(&:last)
    minx=xs.min;miny=ys.min;w=[xs.max-minx+(area['id']=='overseas' ? 520:280),1100].max
    positions=coords.transform_values { |x,y| [x-minx+140,y-miny+160] }
    diagram_bottom=ys.max-miny+285
    incident=g.incident(area);h=diagram_bottom+incident.length*42+130
    north=%w[garden castle].include?(area['id']) ? '北↑・接続概念図（縮尺ではない）' : area['id']=='body' ? '架空人体の空間配置・地理的方位ではない' : area['id']=='overseas' ? '階層と移動の概念図・地理的方位ではない' : '接続模式図・地理的方位／縮尺を表さない'
    out=[%(<g data-area="#{area['id']}"><rect x="8" y="8" width="#{w-16}" height="#{h-16}" rx="12" fill="#fbfdfb" stroke="#8aa79a"/><text x="25" y="45" class="heading">#{esc(area['name'])}・#{area['maps'].length}MAP</text><text x="25" y="78" class="note">#{esc(north)}</text>)]
    out<<%(<text x="25" y="108" class="note">デパートのエレベーターはMAPを持たない。各階の扉に入ると階選択ウィンドウが開き、選んだ階の扉前に着く（F83/F85/E15/F86/E16間の破線は階選択の代表経路）</text>) if area['id']=='city'
    counts=Hash.new(0)
    g.internal(area).each do |e|
      ax,ay=positions.fetch(e['from']);bx,by=positions.fetch(e['to']);pair=[e['from'],e['to']].sort;ix=counts[pair];counts[pair]+=1
      # Separate the otter/cave entrance and exit, preserving their endpoint identities.
      d=if %w[F64 F65].any? { |id| pair.include?(id) };"M#{ax} #{ay} Q#{(ax+bx)/2} #{(ay+by)/2+(ix==0 ? -65:65)} #{bx} #{by}";elsif pair==%w[E16 F83];"M#{ax} #{ay} Q#{(ax+bx)/2} #{(ay+by)/2-150} #{bx} #{by}"  # 1階↔5階の直結は同一行のE15を避けて上へ弧を描く
      else;"M#{ax} #{ay} L#{bx} #{by}";end
      out<<%(<path class="#{e['kind']}" #{attrs(e)} d="#{d}"#{arrow(e)}/>)
    end
    area['maps'].each do |id|
      x,y=positions.fetch(id)
      out<<%(<circle class="node" data-map="#{id}" cx="#{x}" cy="#{y}" r="30"/><text class="id" x="#{x}" y="#{y+7}">#{id}</text>)
      if area['id']=='overseas' && id=='F37'
        out<<%(<text x="#{x}" y="#{y-48}" class="label">空中通路・シャー共闘</text>)
      elsif area['id']=='overseas' && %w[F27 F28 F29].include?(id)
        node_label(id,spec).each_with_index { |line,i| out<<%(<text x="#{x}" y="#{y+53+i*21}" class="label">#{esc(line)}</text>) }
      elsif area['id']=='overseas'
        node_label(id,spec).each_with_index { |line,i| out<<%(<text x="#{x+65}" y="#{y-8+i*21}" class="label" style="text-anchor:start">#{esc(line)}</text>) }
      else
        label_y=id=='F19' ? y-42:y+53
        label_x=id=='F82' ? x-75:x
        node_label(id,spec).each_with_index { |line,i| out<<%(<text x="#{label_x}" y="#{label_y+i*21}" class="label">#{esc(line)}</text>) }
      end
    end
    out<<%(<text x="25" y="#{diagram_bottom}" class="note">全接続口（各行は上のMAP IDを参照。外部は隣接エリア名と到着口を明記）</text>)
    referenced=[]
    incident.each_with_index do |e,i|
      y=diagram_bottom+35+i*42;external=g.owner(e['from'])!=g.owner(e['to'])
      if external
        peer=area['maps'].include?(e['from']) ? e['to']:e['from']
        unless referenced.include?(peer)
          out<<%(<circle class="ref" data-reference-map="#{peer}" data-reference="#{peer}" cx="40" cy="#{y-5}" r="13"/>)
          referenced<<peer
        end
        out<<%(<text x="65" y="#{y}" class="small">#{esc(port_label(e))}  [外部: #{esc(g.owner(peer))}]</text>)
        out<<%(<path class="#{e['kind']}" #{attrs(e,canonical_cross)} d="M#{w-160} #{y-7} L#{w-45} #{y-7}"#{arrow(e)}/>)
      else
        out<<%(<text x="25" y="#{y}" class="small">#{esc(port_label(e))}</text>)
      end
    end
    out<<'</g>'
    [out.join("\n"),w,h]
  end
  def self.run
    g=MapGraph::Graph.new(ROOT)
    spec=File.read(File.join(ROOT,'docs/map-specifications.md')).lines.each_with_object({}) do |line,h|
      c=line.split('|').map(&:strip);h[c[1].split.first]=c[3] if c[1]&.match?(/\A(?:E\d{2}|F\d{2}|N\d+)(?:\s|\z)/)
    end
    folder=File.join(ROOT,'docs/topology/areas');FileUtils.mkdir_p(folder)
    panels=g.areas.map do |area|
      content,w,h=area_content(g,area,spec)
      File.write(File.join(folder,area['id']+'.svg'),header(w,h,area['name'])+content+'</svg>')
      content,w,h=area_content(g,area,spec,canonical_cross:false)
      [area,content,w,h]
    end
    col_width=panels.map { |p| p[2] }.max+30
    row_heights=panels.each_slice(3).map { |row| row.map { |p|p[3] }.max+30 }
    atlas_h=150+row_heights.sum+g.cross.length*55+100
    atlas=[header(col_width*3,atlas_h,'全130MAP・全接続アトラス'),'<text x="30" y="45" class="heading">全130MAP接続アトラス：所有MAPは各1回、外部口と全接続を併記</text>','<text x="30" y="85" class="note">各枠は独立した模式図。庭園・城は北上、ほかは注記に従う。詳細はareas/各エリア.svgを等倍表示。</text>']
    y=120
    panels.each_slice(3).with_index do |row,ri|
      row.each_with_index { |p,ci|atlas<<%(<g transform="translate(#{ci*col_width} #{y})">#{p[1]}</g>) }
      y+=row_heights[ri]
    end
    atlas<<%(<text x="30" y="#{y+35}" class="heading">エリア間の全接続（#{g.cross.length}件）：一方向は矢印、双方向は↔</text>)
    g.cross.each_with_index do |e,i|
      ey=y+85+i*55
      atlas<<%(<text x="30" y="#{ey}" class="note">#{esc(g.owner(e['from']))} / #{esc(port_label(e))} / #{esc(g.owner(e['to']))}</text><path class="#{e['kind']}" #{attrs(e)} d="M1400 #{ey-8} L1600 #{ey-8}"#{arrow(e)}/>)
    end
    atlas<<'</svg>';File.write(File.join(ROOT,'docs/topology/atlas.svg'),atlas.join("\n"))
    overview(g)
    puts "Rendered overview, atlas and #{g.areas.length} area diagrams: #{g.areas.sum { |a| a['maps'].length }} maps, #{g.edges.length} connections"
  end
  def self.overview(g)
    # Real-region positions follow the established geography. Fiction/event layers are separate.
    pos={'teramachi'=>[390,1070],'school'=>[650,1160],'city'=>[650,740],'station'=>[430,430],'mountain'=>[1150,450],'sunnyland'=>[1480,310],'uchinada'=>[260,150],'noto_train'=>[1400,120],'noto_before'=>[1730,150],'noto_after'=>[1730,650],'garden'=>[1190,980],'castle'=>[1190,760],'body'=>[1710,1300],'airport'=>[410,1600],'overseas'=>[1110,1600]}
    list_y=1800;h=list_y+g.cross.length*58+100
    out=[header(2050,h,'全エリア間の位置関係と接続'),'<text x="30" y="45" class="heading">全15エリアの位置関係と全接続</text>','<text x="30" y="83" class="note">北↑（実在地域の相対配置）。距離・縮尺は模式化。下段の空港境界・海外・体内は地理配置から分離。</text>','<rect x="80" y="100" width="1910" height="1110" rx="15" fill="#f9fcfa" stroke="#a4b9ae"/><rect x="80" y="1230" width="1910" height="490" rx="15" fill="#fff8f0" stroke="#b9a38e"/><text x="100" y="1260" class="note">非地理のイベント層／所在・方角を固定しない空港境界と海外</text>']
    g.cross.each do |e|
      ax,ay=pos.fetch(g.owner(e['from']));bx,by=pos.fetch(g.owner(e['to']))
      d=e['kind']=='event' ? 'M390 1070 L930 1070 L1560 1170 L1710 1300':"M#{ax} #{ay} L#{bx} #{by}"
      out<<%(<path class="#{e['kind']}" #{attrs(e,false)} d="#{d}"#{arrow(e)}/>)
    end
    out<<'<text x="850" y="1047" class="label">E01園庭 → F19口（物語イベント）</text>'
    g.areas.each do |a|
      x,y=pos.fetch(a['id'])
      out<<%(<g data-area="#{a['id']}"><rect x="#{x-145}" y="#{y-44}" width="290" height="88" rx="10" fill="#fff" stroke="#527b69" stroke-width="3"/><text x="#{x}" y="#{y-8}" class="label">#{esc(a['name'])}</text><text x="#{x}" y="#{y+21}" class="label">#{a['maps'].length} MAP（#{a['id']}）</text></g>)
    end
    out<<'<text x="100" y="1305" class="note">能登被災前／後は時期差分（徒歩接続ではない）。未登録の接続を補って描かない。</text><text x="100" y="1340" class="note">K空港はワープ到達・起点を固定しない。体内は園庭のイベントから、海外へは一方向の旅客機。</text>'
    out<<%(<text x="30" y="1765" class="heading">エリアをまたぐ全#{g.cross.length}接続の出入口（線の交差は乗換・接続を意味しない）</text>)
    g.cross.each_with_index do |e,i|
      y=list_y+i*58
      out<<%(<text x="30" y="#{y}" class="note">#{esc(g.owner(e['from']))} / #{esc(port_label(e))} / #{esc(g.owner(e['to']))}</text><path class="#{e['kind']}" #{attrs(e)} d="M1550 #{y-7} L1790 #{y-7}"#{arrow(e)}/>)
    end
    out<<'</svg>';File.write(File.join(ROOT,'docs/topology/overview.svg'),out.join("\n"))
  end
end
MapAtlas.run if $PROGRAM_NAME==__FILE__
