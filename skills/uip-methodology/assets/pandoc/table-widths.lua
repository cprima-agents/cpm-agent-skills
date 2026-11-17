-- Pandoc filter for the generated documents: every table gets the full page width, and the columns get a width
-- that follows the amount of text in them (a number column stays narrow, a description column gets room).
-- Without it, pandoc writes the width "auto" for a table whose markdown rows are short, and Word makes the table
-- only as wide as its content; all columns are equally wide.
-- Use: pandoc document.md --lua-filter cell-breaks.lua --lua-filter table-widths.lua -o document.docx

local MIN_WEIGHT = 6   -- a column is never narrower than the weight of six characters
local MAX_WEIGHT = 48  -- a very long text does not take all the room

local function text_length(blocks)
  return #pandoc.utils.stringify(blocks)
end

local function rows_of(tbl)
  local rows = {}
  for _, r in ipairs(tbl.head.rows) do rows[#rows + 1] = r end
  for _, body in ipairs(tbl.bodies) do
    for _, r in ipairs(body.body) do rows[#rows + 1] = r end
  end
  return rows
end

function Table(tbl)
  local n = #tbl.colspecs
  if n == 0 then return nil end
  local longest, total, count = {}, {}, {}
  for i = 1, n do longest[i], total[i], count[i] = 0, 0, 0 end
  for _, row in ipairs(rows_of(tbl)) do
    for i, cell in ipairs(row.cells) do
      if i <= n then
        local len = text_length(cell.contents)
        if len > longest[i] then longest[i] = len end
        total[i] = total[i] + len
        count[i] = count[i] + 1
      end
    end
  end
  local weights, sum = {}, 0
  for i = 1, n do
    local average = count[i] > 0 and total[i] / count[i] or 0
    local w = 0.5 * longest[i] + 0.5 * average
    w = math.max(MIN_WEIGHT, math.min(MAX_WEIGHT, w))
    weights[i] = w
    sum = sum + w
  end
  for i = 1, n do
    tbl.colspecs[i] = { tbl.colspecs[i][1], weights[i] / sum }
  end
  return tbl
end
