#!/usr/bin/env ruby
# frozen_string_literal: true
require 'rexml/document'
require_relative 'map_graph'
module MapAtlasVerification
  def self.assert(condition,message)
    raise message unless condition
  end
  def self.document(root,relative)
    path=File.join(root,'docs/topology',relative)
    assert(File.file?(path),"missing diagram #{relative}")
    REXML::Document.new(File.read(path))
  end
  def self.elements(doc,attribute)
    REXML::XPath.match(doc,"//*[@#{attribute}]")
  end
  def self.check(root,file,nodes,edges,areas,references=nil)
    doc=document(root,file)
    owned=elements(doc,'data-map').map { |n|n.attributes['data-map'] }
    assert(owned.sort==nodes.sort,"#{file}: missing/extra owned MAP")
    labels=REXML::XPath.match(doc,'//text').select { |n| n.attributes['class'].to_s.split.include?('id') }.map { |n|n.text.to_s.strip }
    nodes.each { |id|assert(labels.include?(id),"#{file}: visible ID label missing #{id}") }
    area_ids=elements(doc,'data-area').map { |n|n.attributes['data-area'] }
    assert(area_ids.sort==areas.sort,"#{file}: missing/extra area")
    paths=elements(doc,'data-edge-id')
    assert(paths.map { |n|n.attributes['data-edge-id'] }.sort==edges.map { |e|e['id'] }.sort,"#{file}: missing/extra canonical connection")
    expected=edges.map { |e|[e['id'],e] }.to_h
    text_contents=REXML::XPath.match(doc,'//text').map { |t|t.text.to_s }
    paths.each do |path|
      e=expected.fetch(path.attributes['data-edge-id'])
      assert(path.name=='path',"#{file}: connection must be visible path")
      %w[from to from_port to_port kind].each do |key|
        attr='data-'+key.tr('_','-')
        assert(path.attributes[attr]==e[key],"#{file}: corrupt #{attr}")
      end
      assert(path.attributes['class']==e['kind'],"#{file}: wrong visible line kind")
      assert(!path.attributes['d'].to_s.empty?,"#{file}: missing line geometry")
      if %w[event oneway].include?(e['kind'])
        marker=path.attributes['marker-end'].to_s[/\Aurl\(#([A-Za-z0-9_-]+)\)\z/,1]
        assert(marker && REXML::XPath.first(doc,"//marker[@id='#{marker}']"),"#{file}: directed event/travel needs end arrow")
        assert(!path.attributes['marker-start'],"#{file}: reversed or bidirectional arrow")
      else
        assert(!path.attributes['marker-end'] && !path.attributes['marker-start'],"#{file}: ordinary passage must be bidirectional")
      end
      connector=%w[event oneway].include?(e['kind']) ? '→':'↔'
      caption="#{e['from']}.#{e['from_port']} #{connector} #{e['to']}.#{e['to_port']}"
      assert(text_contents.any? { |text| text.include?(caption) },"#{file}: missing visible endpoint caption")
    end
    if references
      refs=elements(doc,'data-reference-map').map { |n|n.attributes['data-reference-map'] }
      assert(refs.sort==references.sort,"#{file}: missing/extra remote MAP reference")
    end
    doc
  end
  def self.verify!(root)
    g=MapGraph::Graph.new(root)
    all=g.areas.flat_map { |a|a['maps'] }
    ids=g.areas.map { |a|a['id'] }
    expected_total=JSON.parse(File.read(File.join(root,'docs/topology/map-ids.json'))).fetch('expected_count')
    assert(all.length==expected_total && all.uniq.length==expected_total,"atlas membership must contain all #{expected_total} MAPs exactly once")
    assert(ids.length==15 && ids.uniq.length==15,'atlas must cover all 15 areas')
    check(root,'atlas.svg',all,g.edges,ids)
    check(root,'overview.svg',[],g.cross,ids)
    actual_files=Dir.glob(File.join(root,'docs/topology/areas/*.svg')).map { |p|File.basename(p,'.svg') }.sort
    assert(actual_files==ids.sort,'missing/extra per-area SVG file')
    g.areas.each do |area|
      incident=g.incident(area)
      remote=incident.flat_map { |e|[e['from'],e['to']] }.reject { |id|area['maps'].include?(id) }.uniq
      check(root,'areas/'+area['id']+'.svg',area['maps'],incident,[area['id']],remote)
    end
    true
  end
end
if $PROGRAM_NAME==__FILE__
  begin
    MapAtlasVerification.verify!(ENV['LEDGER_ROOT'] || File.expand_path('..',__dir__))
    g=MapGraph::Graph.new(ENV['LEDGER_ROOT'] || File.expand_path('..',__dir__))
    puts "PASS: full atlas #{g.areas.sum { |a| a['maps'].length }} MAPs / #{g.edges.length} connections, 15 areas, overview cross-area ports and directed events"
  rescue StandardError => e
    warn "FAIL: atlas: #{e.message}"
    exit 1
  end
end
