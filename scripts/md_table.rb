# frozen_string_literal: true

# Markdown の表を『見出し行の列名』で読む。列の位置（セル番号）に依存しない。
# 旧 md（map-contract-checklist.md・map-specifications.md・map-topology.md）を読む scripts 用。
# 列を足す・並べ替えても、見出しの名前が同じなら読める。名前が無ければ nil（呼び出し側が検査で落とす）。
#
# 読み方（旧実装の『| で始まる行を全部読む』と同じ緩さを保つ）: 先頭列の名前が first で names を全て持つ見出し行が現れたら、
# 以降の『|』で始まる行をその見出しの列名で読む。途中に地の文・空行が挟まって物理的に表が分かれていても、また表の外に
# 足された行でも、続きの行として読む（行の取りこぼしで検査をすり抜けさせない）。区切り行は読み飛ばす。同じ先頭列の別の
# 見出し行が現れたらそこから切り替える（names を持たない見出しなら、次の見出しまで読まない）。
module MdTable
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

  # 行は {列名 => セル, :cells => 生のセル配列}（足りない列は nil）
  def rows(text, first, *names)
    header = nil
    out = []
    text.each_line do |line|
      next unless line.start_with?('|')

      cells = split(line)
      next if separator?(cells)

      if cells.first == first
        header = names.all? { |n| cells.include?(n) } ? cells : nil
        next
      end
      next if header.nil?

      h = header.each_with_index.to_h { |name, i| [name, cells[i]] }
      h[:cells] = cells
      out << h
    end
    out
  end

  # 節（text）全体を1つの論理表として読む（rows と同じ。節の切り出し側を明示するための別名）
  def section_rows(text, first, *names)
    rows(text, first, *names)
  end

  # 名前の候補のうち最初に存在する列の値
  def pick(row, *names)
    names.each { |n| return row[n] if row.key?(n) && !row[n].nil? }
    nil
  end
end
