-- Pandoc filter for the generated documents: a <br> inside a table cell becomes a real line break.
-- Without it, pandoc drops <br> when it writes docx, and the parts of a cell run together.
-- Use: pandoc document.md --lua-filter cell-breaks.lua -o document.docx
function RawInline(el)
  if el.format == "html" and el.text:match("^<br%s*/?>$") then
    return pandoc.LineBreak()
  end
end
