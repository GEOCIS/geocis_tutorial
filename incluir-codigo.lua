-- ```{.python include="dados.py"}``` vira um bloco com o conteúdo do arquivo
-- (caminho relativo à página), para mostrar o código-fonte sem copiá-lo.
function CodeBlock(el)
  local arquivo = el.attributes.include
  if not arquivo then return nil end
  local pasta = pandoc.path.directory(quarto.doc.input_file)
  local h = io.open(pandoc.path.join({pasta, arquivo}), "r")
  if not h then error("incluir-codigo.lua: arquivo não encontrado: " .. arquivo) end
  el.text = h:read("a"):gsub("%s+$", "")
  h:close()
  el.attributes.include = nil
  return el
end
