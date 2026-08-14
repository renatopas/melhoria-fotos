# Orientações do projeto

Leia `REQUIREMENTS.md` antes de alterar ou executar o projeto.

## Regras obrigatórias

- Trate todas as fotografias como dados privados e mantenha `fotos/` fora do Git.
- Nunca registre chaves de API, arquivos `.env` ou credenciais.
- Preserve os nomes dos arquivos nas imagens restauradas.
- A restauração deve ser conservadora e incluir colorização; não altere feições, expressões, cabelos, roupas, objetos, proporções ou o contexto histórico.
- Prefira a modalidade batch da API para reduzir custos.
- Para validar o script, processe inicialmente somente uma imagem.
- Peça confirmação antes de qualquer processamento pago. O usuário pode escolher lotes graduais de qualquer quantidade positiva com `--limit`.
- Peça confirmação explícita antes de processar o conjunto completo.
- Não sobrescreva os arquivos originais. Grave em `fotos/melhorada/` uma composição com original à esquerda e restauração à direita, identificada como imagem colorizada por IA.
- Em caso de ambiguidade que possa afetar custo, fidelidade ou arquivos originais, interrompa e pergunte.

## Desenvolvimento

- Use Python para automação, com dependências declaradas e instruções reproduzíveis.
- Separe a preparação e validação local da chamada paga à API sempre que possível.
- Inclua um modo de simulação (`--dry-run`) antes de implementar processamento em lote.
