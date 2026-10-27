# frozen_string_literal: true
require_relative 'ledger_yaml'
module MapGraph
  class Graph
    attr_reader :root, :areas, :edges
    def initialize(root)
      @root=root
      read = ->(name) { LedgerYaml.read(name, root: root) }
      area_rows = read.call('エリア')
      placements = read.call('図配置').group_by { |r| r['エリアID'] }
      @areas = area_rows.map do |area|
        rows = placements.fetch(area['エリアID']).sort_by { |r| Integer(r['順番']) }
        {'id' => area['エリアID'], 'name' => area['名称'],
         'maps' => rows.map { |r| r['MAP_ID'] },
         'layout' => rows.to_h { |r| [r['MAP_ID'], [Integer(r['X']), Integer(r['Y'])]] }}
      end
      @edges = read.call('接続').map do |r|
        raise "invalid topology kind #{r['種別']}" unless %w[edge door event oneway].include?(r['種別'])
        a,ap=r['端A'].split('.',2);b,bp=r['端B'].split('.',2)
        raise 'missing endpoint' unless ap && bp
        {'from'=>a,'from_port'=>ap,'to'=>b,'to_port'=>bp,'kind'=>r['種別'],'note'=>r['主路・状態'],'id'=>"#{r['端A']}>#{r['端B']}:#{r['種別']}"}
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
