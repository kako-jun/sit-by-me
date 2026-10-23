# frozen_string_literal: true

# Markdown の表を『見出し行の列名』で読む。列の位置（セル番号）に依存しない。
# 旧 md（map-contract-checklist.md・map-specifications.md・map-topology.md）を読む scripts 用。
# 列を足す・並べ替えても、見出しの名前が同じなら読める。名前が無ければ nil（呼び出し側が検査で落とす）。
module MdTable
  Table = Struct.new(:header, :rows)

  module_function

  # '| a | b |' -> ['a', 'b']（前後の | を除く。行末の改行は無視）
  def split(line)
    s = line.strip
    s = s.sub(/\A\|/, '').sub(/\|\z/, '')
    s.split('|', -1).map(&:strip)
  end

  def separator?(cells)
    !cells.empty? && cells.all? { |c| c.match?(/\A:?-{2,}:?\z/) }
  end

  # text 中の全ての表（見出し行＋区切り行＋データ行）。行は {列名 => セル}（足りない列は nil）。
  def tables(text)
    out = []
    block = []
    flush = lambda do
      if block.length >= 2 && separator?(split(block[1]))
        header = split(block[0])
        rows = block[2..].map do |l|
          cells = split(l)
          h = header.each_with_index.to_h { |name, i| [name, cells[i]] }
          h[:cells] = cells
          h
        end
        out << Table.new(header, rows)
      end
      block = []
    end
    text.each_line do |line|
      if line.start_with?('|')
        block << line
      else
        flush.call
      end
    end
    flush.call
    out
  end

  # 先頭列の名前が first で、names の列を全て持つ表の、全てのデータ行（複数の表にまたがってよい）
  def rows(text, first, *names)
    tables(text).select { |t| t.header.first == first && names.all? { |n| t.header.include?(n) } }.flat_map(&:rows)
  end

  # 節（text）全体を1つの論理表として読む: 先頭列が first で names を全て持つ最初の見出し行を探し、以降の『|』で始まる行を
  # その見出しの列名で読む（途中に地の文・空行が挟まって物理的に表が分かれていても続きの行として読む。区切り行と見出しの再掲は読み飛ばす）。
  def section_rows(text, first, *names)
    header = nil
    out = []
    text.each_line do |line|
      next unless line.start_with?('|')

      cells = split(line)
      if header.nil?
        header = cells if cells.first == first && names.all? { |n| cells.include?(n) }
        next
      end
      next if separator?(cells) || cells == header

      h = header.each_with_index.to_h { |name, i| [name, cells[i]] }
      h[:cells] = cells
      out << h
    end
    out
  end

  # 名前の候補のうち最初に存在する列の値
  def pick(row, *names)
    names.each { |n| return row[n] if row.key?(n) && !row[n].nil? }
    nil
  end
end
