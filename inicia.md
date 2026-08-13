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
Restore and fully colorize this entire scanned 1994 school composite.

Two requirements are equally important:

1. COMPLETE COLORIZATION
Colorize every portrait on the page, including every person's skin, lips, eyes, hair, and clothing, as well as each portrait background. No person or portrait may remain black-and-white, grayscale, monochrome, or sepia. Use natural skin tones and restrained, realistic, historically plausible colors. When the original color is unknown, choose a plausible color consistently; color uncertainty is not a reason to leave an area uncolored. Keep the paper, printed grid, and text neutral unless a faint natural paper tone is appropriate.

2. CONTENT AND IDENTITY PRESERVATION
Use the input as the sole source for shapes and content. Preserve each person's identity, facial geometry, expression, gaze, hairstyle, clothing, pose, and proportions. For every hairstyle, preserve the exact outer silhouette, hairline, parting, length, volume, smoothness, and direction in which the hair is combed. Color the existing hair without restyling it. Do not add individual strands, spikes, extra volume, curls, bangs, or a punk/spiky appearance that is not clearly visible in the input. Xerox grain and edge noise around the head are not hair. Preserve every garment's exact type, neckline, collar, sleeves, cut, pattern, and visible markings. Printed words, letters, numbers, symbols, emblems, and graphics on clothing are part of the original photograph and must remain in the same position, size, shape, spelling, and contrast; do not erase, cover, simplify, translate, correct, redesign, or replace them. Preserve legible garment text exactly. If a marking is illegible, preserve its original visual shapes without trying to turn it into new readable text. Preserve the sheet layout, crop, portrait positions, borders, numbers, labels, handwriting, and typography. Do not beautify or redesign faces. If a facial detail is unclear, keep its shape soft rather than inventing a sharper feature.

Remove or reduce scratches, dust, stains, fading, uneven exposure, xerographic noise, excessive grain, and scanning artifacts. Improve contrast and clarity moderately.

Do not add or reinterpret any object, accessory, garment detail, or modern element. Reproduce the area from each person's nose through mouth and chin using only the facial anatomy and tones supported by the source. Keep the nose, mouth, chin, cheeks, and jaw visually unobstructed wherever they are visible in the input. Pale patches, white circles, shadows, stains, lines, and missing xerographic information across a face are flat print or paper damage, never a three-dimensional or wearable item. Reduce such damage conservatively; where facial information is missing, use a soft continuation of nearby facial tone without adding seams, folds, straps, hard edges, or a recognizable object. Do not rewrite illegible text or modernize the scene.

Return exactly one restored image with the same composition. Before returning it, verify that every portrait is colorized, that visible noses, mouths, and chins remain unobstructed, and that no new object appears on any person.

```

### Outros cuidados

Sempre pergunte em caso de dúvida
