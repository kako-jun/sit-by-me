# frozen_string_literal: true
require 'json'
require_relative 'md_table'
module MapGraph
  class Graph
    attr_reader :root, :areas, :edges
    def initialize(root)
      @root=root
      @areas=JSON.parse(File.read(File.join(root,'docs/topology/areas.json'))).fetch('areas')
      text=File.read(File.join(root,'docs/map-topology.md')).split('#### MAP相互接続台帳 v2',2).fetch(1).split('#### 寺町の地形不変条件',2).first
      # 見出し行の列名（From/To/種別/主路・状態）で読む。列の位置に依存しない
      @edges=MdTable.section_rows(text,'From','To','種別','主路・状態').map do |r|
        raise "invalid topology row #{r[:cells].join(' | ')}" unless r[:cells].length==4 && r.values_at('From','To','種別','主路・状態').none?(&:nil?) && %w[edge door event oneway].include?(r['種別'])
        a,ap=r['From'].split('.',2);b,bp=r['To'].split('.',2)
        raise 'missing endpoint' unless ap && bp
        {'from'=>a,'from_port'=>ap,'to'=>b,'to_port'=>bp,'kind'=>r['種別'],'note'=>r['主路・状態'],'id'=>"#{r['From']}>#{r['To']}:#{r['種別']}"}
      end
    end
    def owner(id)
      @areas.find { |a| a['maps'].include?(id) }&.fetch('id')
    end
    def internal(area)
      @edges.select { |e| area['maps'].include?(e['from']) && area['maps'].include?(e['to']) }
    end
    def incident(area)
      @edges.select { |e| area['maps'].include?(e['from']) || area['maps'].include?(e['to']) }
    end
    def cross
      @edges.select { |e| owner(e['from']) != owner(e['to']) }
    end
  end
end
