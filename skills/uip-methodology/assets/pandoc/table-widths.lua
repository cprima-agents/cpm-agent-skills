-- Pandoc filter for the generated documents: every table gets the full page width, and the columns get a width
-- that follows the amount of text in them (a number column stays narrow, a description column gets room).
-- Without it, pandoc writes the width "auto" for a table whose markdown rows are short, and Word makes the table
-- only as wide as its content; all columns are equally wide.
-- Use: pandoc document.md --lua-filter cell-breaks.lua --lua-filter table-widths.lua -o document.docx

local MIN_WEIGHT = 10  -- a column is never narrower than the weight of ten characters (a bold word like "Version" fits)
local LONG_WORD = 8     -- a word of this length or more sets the width of its column
local MAX_WEIGHT = 48  -- a very long text does not take all the room
local WORD_FACTOR = 1.9     -- a column is as wide as its longest word, with room for the cell margin
local MAX_WORD_WEIGHT = 60   -- but not wider than this, however long the word

local function length_of(text)
  return utf8.len(text) or #text
end

local function text_length(blocks)
  return length_of(pandoc.utils.stringify(blocks))
end

-- the length of the longest word in the cell: a column is wide enough to keep it in one piece
local function longest_word(blocks)
  local longest = 0
  for word in pandoc.utils.stringify(blocks):gmatch("%S+") do
    longest = math.max(longest, length_of(word))
  end
  return longest
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
  local longest, total, count, word = {}, {}, {}, {}
  for i = 1, n do longest[i], total[i], count[i], word[i] = 0, 0, 0, 0 end
  for _, row in ipairs(rows_of(tbl)) do
    for i, cell in ipairs(row.cells) do
      if i <= n then
        local len = text_length(cell.contents)
        word[i] = math.max(word[i], longest_word(cell.contents))
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
    if word[i] >= LONG_WORD then  -- never break a long word; a short word fits in the minimum width
      w = math.max(w, math.min(WORD_FACTOR * word[i], MAX_WORD_WEIGHT))
    end
    weights[i] = w
    sum = sum + w
  end
  for i = 1, n do
    tbl.colspecs[i] = { tbl.colspecs[i][1], weights[i] / sum }
  end
  return tbl
end
