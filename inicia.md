Projeto de melhoria de foto tipo "carômetro" do site etfsp

## Objetivo

Melhorar a qualidade de fotos antigas que na verdade são imagens digitalizadas de diversas cópias xerográficas de pequenas fotos de todos os alunos de cada sala de aula. Ou seja, são fotos de fotos

## Onde estão a fotos a serem melhoradas

No diretório fotos/melhorar

## Ferramentas que serão utilizadas

Modelo Nano Banana (ou sub tipo adequado) que será utilizado via fornecimento de api key

## Como deve ser feito

Pode ser criado script em Python

As fotos melhoradas devem ser criada em um subditerório tipo "melhorada". Os arquivos melhorados devem preservar os nomes originais.

## Cuidados

Cuidados que devem ser tomados / requisitos diversos

### Custo

O modelo deve ser utilizado com parcimônia pois tem custo.

Utilize o modo "batch", que é duas vezes mais barato.

Fazer o teste inicial com poucas imagens e sempre solicitar confirmação. Depois, permitir processamento gradual em lotes de tamanho escolhido pelo usuário.

Para testes do script, por exemplo, uma imagem é suficiente

Somente executar para todas as fotos mediante confirmação

### Com as melhorias

Garantir que as fotos sejam apenas melhoradas, com colorização e redução de ruído.

Segue sugestão de prompt:

```
Colorize this entire black-and-white school composite and apply light photographic restoration.

The source image is authoritative. Keep all visible content and geometry unchanged: the same people, faces, expressions, hair, clothing, markings, text, layout, borders, and background. Do not add, remove, replace, redesign, complete, or reinterpret anything. Do not reconstruct missing or unclear details; leave them soft or damaged as in the source.

The only permitted changes are realistic, historically plausible color, gentle noise and stain reduction, and modest correction of exposure and contrast. Apply color throughout every portrait, but change color only—not shapes, edges, textures, or objects. Preserve all readable text exactly and leave unreadable marks unreadable.

Return one image with exactly the same composition and content as the source.

```

### Outros cuidados

Sempre pergunte em caso de dúvida
