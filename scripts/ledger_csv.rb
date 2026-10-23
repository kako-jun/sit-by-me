# frozen_string_literal: true

# docs/ledger/*.csv の最小 CSV 読み書き（Ruby 3.4 は csv gem が標準添付でないため自前。RFC4180 の引用符・改行に対応）。
module LedgerCsv
  ROOT = ENV['LEDGER_ROOT'] || File.expand_path('..', __dir__)
  LEDGER = File.join(ROOT, 'docs', 'ledger')

  module_function

  def parse(text)
    rows = []
    row = []
    field = +''
    quoted = false
    i = 0
    while i < text.length
      c = text[i]
      if quoted
        if c == '"'
          if text[i + 1] == '"'
            field << '"'
            i += 1
          else
            quoted = false
          end
        else
          field << c
        end
      elsif c == '"'
        quoted = true
      elsif c == ','
        row << field
        field = +''
      elsif c == "\n"
        row << field
        rows << row
        row = []
        field = +''
      elsif c != "\r"
        field << c
      end
      i += 1
    end
    unless field.empty? && row.empty?
      row << field
      rows << row
    end
    rows
  end

  def read(table)
    path = File.join(LEDGER, "#{table}.csv")
    return [] unless File.file?(path)

    rows = parse(File.read(path, encoding: 'UTF-8'))
    header = rows.shift or return []
    rows.map { |r| header.each_with_index.to_h { |h, i| [h, r[i] || ''] } }
  end

  def header(table)
    path = File.join(LEDGER, "#{table}.csv")
    return [] unless File.file?(path)

    parse(File.read(path, encoding: 'UTF-8')).first || []
  end

  def tables
    Dir.glob(File.join(LEDGER, '*.csv')).map { |p| File.basename(p, '.csv') }.sort
  end

  def load_all
    tables.to_h { |t| [t, read(t)] }
  end
end
