#!/usr/bin/env ruby
# frozen_string_literal: true

# Executable design contract, deliberately separate from the game's runtime.
require 'json'
module OverseasProgression
  def self.load(path)
    JSON.parse(File.read(path))
  end

  def self.step(contract, state, event)
    matches = contract.fetch('transitions').select do |t|
      t['event'] == event && t['from'] == state['phase'] && t.fetch('requires').all? { |k,v| state[k] == v }
    end
    raise "ambiguous event #{event}" if matches.length > 1
    return nil if matches.empty?
    state.merge(matches.first.fetch('set')).merge('phase'=>matches.first.fetch('to'))
  end

  def self.verify!(c)
    raise 'not a design contract' unless c['kind'] == 'design-contract-not-game-runtime'
    raise 'left magic / right ability required' unless c.dig('bosses','left') == {'id'=>'M015','map'=>'OVS-09','only'=>'magic'} && c.dig('bosses','right') == {'id'=>'M016','map'=>'OVS-14','only'=>'ability'}
    raise 'third dragon encounter prohibited' unless c['family_id'] == 'M003' && c['bridge_battle'] == 'ordinary_enemies_only'
    raise 'deadline must be authorities, not explosion' unless c['deadline'] == 'authorities_arrive_and_arrest_shah'
    raise 'timer/save/reset policy changed' unless c['save_during_timer'] == false && c['third_tower_preentry'] == false && c['s005_timer_continues'] == true && c['failure'] == 'restore_last_pre_timer_save_and_chests'
    raise 'five floor paths changed' unless c['tower_paths'] == {'left'=>%w[OVS-05 OVS-06 OVS-07 OVS-08 OVS-09],'right'=>%w[OVS-10 OVS-11 OVS-12 OVS-13 OVS-14],'escape'=>%w[OVS-16 OVS-17 OVS-18 OVS-19 OVS-20]}
    raise 'each of 15 floors must be comparable full-floor area' unless c['floor_area_class'] == c['tower_paths'].values.flatten.map { |id| [id,'comparable_full_floor'] }.to_h
    initial = c.fetch('initial')
    raise 'invalid initial state' unless initial == {'phase'=>'exploring','left_defeated'=>false,'right_defeated'=>false,'timer_running'=>false,'third_unlocked'=>false,'third_entered'=>false,'floor'=>5,'s005_defeated'=>false,'exited'=>false,'four_party'=>false,'timer_starts'=>0,'timer_id'=>'escape'}
    allowed_events = %w[defeat_left defeat_right reveal_and_cooperate finish_cooperation enter_third collect_chest descend_5_to_4 descend_4_to_3 descend_3_to_2 descend_2_to_1 reach_exit defeat_s005 actual_exit timeout]
    raise 'unknown event' unless c.fetch('transitions').all? { |t| allowed_events.include?(t['event']) && t.keys.sort == %w[event from requires set to] && t['requires'].is_a?(Hash) && t['set'].is_a?(Hash) && (t['requires'].keys+t['set'].keys-initial.keys).empty? }
    states = [initial]; seen = {}; reachable_events = []
    until states.empty?
      state = states.shift
      key = JSON.generate(state.sort.to_h)
      next if seen[key]
      seen[key] = true
      phase=state['phase']
      raise 'invalid phase' unless %w[exploring bridge cooperation escaping exit_battle escaped failed].include?(phase)
      raise 'early bridge/reunion' if %w[bridge cooperation escaping exit_battle escaped].include?(phase) && !(state['left_defeated'] && state['right_defeated'])
      raise 'timer phase mismatch' unless state['timer_running'] == %w[escaping exit_battle].include?(phase)
      raise 'single escape timer must start exactly once' unless state['timer_id']=='escape' && state['timer_starts']==(%w[escaping exit_battle escaped failed].include?(phase) ? 1:0)
      raise 'third tower unlocked before cooperation ends' unless state['third_unlocked'] == %w[escaping exit_battle escaped failed].include?(phase)
      raise 'third entered early' if state['third_entered'] && !state['third_unlocked']
      raise 'S005 exit must finish timer' if phase=='escaped' && !(state['s005_defeated'] && state['exited'] && state['floor']==1 && state['third_entered'])
      allowed_events.each do |event|
        next_state=step(c,state,event)
        next unless next_state
        legal=case event
        when 'defeat_left','defeat_right'; phase=='exploring' && !state[event.sub('defeat_','')+'_defeated']
        when 'reveal_and_cooperate'; phase=='bridge'
        when 'finish_cooperation'; phase=='cooperation'
        when 'enter_third'; phase=='escaping' && state['third_unlocked']
        when 'collect_chest'; phase=='escaping' && state['third_entered']
        when /\Adescend_(\d)_to_(\d)\z/; phase=='escaping' && state['third_entered'] && state['floor']==$1.to_i && $2.to_i==$1.to_i-1 && next_state['floor']==$2.to_i
        when 'reach_exit'; phase=='escaping' && state['third_entered'] && state['floor']==1
        when 'defeat_s005'; phase=='exit_battle' && !state['s005_defeated'] && next_state['s005_defeated'] && next_state['timer_running']
        when 'actual_exit'; phase=='exit_battle' && state['s005_defeated'] && next_state['exited']
        when 'timeout'; %w[escaping exit_battle].include?(phase)
        else; false
        end
        raise "illegal event #{event} during #{phase}" unless legal
        reachable_events << event
        states << next_state
      end
      raise 'unbounded contract' if seen.length > 200
    end
    raise 'missing reachable event' unless (allowed_events-reachable_events).empty?
    [%w[defeat_left defeat_right],%w[defeat_right defeat_left]].each do |order|
      state=initial
      route=order+%w[reveal_and_cooperate finish_cooperation enter_third collect_chest descend_5_to_4 descend_4_to_3 descend_3_to_2 descend_2_to_1 reach_exit defeat_s005 actual_exit]
      route.each { |event| state=step(c,state,event) or raise "blocked required route #{event}" }
      raise 'escape incomplete' unless state['phase']=='escaped'
    end
    true
  end
end

if $PROGRAM_NAME == __FILE__
  begin
    path=ARGV[0] || File.expand_path('../docs/topology/overseas-progression.json',__dir__)
    OverseasProgression.verify!(OverseasProgression.load(path))
    puts 'PASS: overseas design progression, both boss orders, third-tower gate, continuous timer and S005 exit'
  rescue StandardError => e
    warn "FAIL: overseas progression: #{e.message}"
    exit 1
  end
end
