-- Os arquivos .md apontam para README.md (útil no GitHub); no site, a página do curso é index.html
function Link(el)
  el.target = el.target:gsub("README%.md$", "index.html")
  return el
end

-- O "# Título" no início de cada .md vira o título da página (aba do navegador e cabeçalho).
-- Nos index.qmd dos cursos, que já têm título, o "# Título" repetido do README é removido.
function Pandoc(doc)
  local i = 1
  while doc.blocks[i] and doc.blocks[i].t == "RawBlock" do i = i + 1 end
  local first = doc.blocks[i]
  if not (first and first.t == "Header" and first.level == 1) then return doc end
  if not doc.meta.title then
    doc.meta.title = pandoc.MetaInlines(first.content)
    doc.meta.pagetitle = pandoc.utils.stringify(first)
    doc.blocks:remove(i)
  elseif pandoc.utils.stringify(first) == pandoc.utils.stringify(doc.meta.title) then
    doc.blocks:remove(i)
  end
  return doc
end
