# frozen_string_literal: true
require 'json'
module MapGraph
  class Graph
    attr_reader :root, :areas, :edges
    def initialize(root)
      @root=root
      @areas=JSON.parse(File.read(File.join(root,'docs/topology/areas.json'))).fetch('areas')
      text=File.read(File.join(root,'docs/map-topology.md')).split('#### MAP相互接続台帳 v2',2).fetch(1).split('#### 寺町の地形不変条件',2).first
      @edges=text.lines.select { |l| l.start_with?('|') }.map do |line|
        c=line.split('|').map(&:strip)
        next if c[1]=='From' || c[1].match?(/\A-+\z/)
        raise "invalid topology row #{line}" unless c.length==6 && %w[edge door event oneway].include?(c[3])
        a,ap=c[1].split('.',2);b,bp=c[2].split('.',2)
        raise 'missing endpoint' unless ap && bp
        {'from'=>a,'from_port'=>ap,'to'=>b,'to_port'=>bp,'kind'=>c[3],'note'=>c[4],'id'=>"#{c[1]}>#{c[2]}:#{c[3]}"}
      end.compact
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
