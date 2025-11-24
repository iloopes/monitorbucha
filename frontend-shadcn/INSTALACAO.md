# 🚀 Guia de Instalação - Frontend com shadcn/ui

## Pré-requisitos

- **Node.js** 18.17 ou superior
- **npm** 9+ ou **yarn** 3+
- Backend rodando em `http://localhost:8000`

## Instalação Rápida

### 1️⃣ Instale as dependências

```bash
npm install
```

### 2️⃣ Configure variáveis de ambiente

```bash
# Crie o arquivo .env.local
cp .env.local.example .env.local

# Edite e configure a URL da API (se necessário)
# NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 3️⃣ Inicie o servidor de desenvolvimento

```bash
npm run dev
```

Acesse: **http://localhost:3000**

## 📋 Estrutura de Pasta (Novo Frontend)

```
frontend-shadcn/
├── app/                    # Arquivos da aplicação (App Router)
├── components/             # Componentes React reutilizáveis
├── lib/                    # Utilitários e cliente API
├── public/                 # Arquivos estáticos
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── README.md
```

## 🎯 Primeiros Passos

1. **Dashboard** - Visualize o status geral do sistema
2. **Banco de Dados** - Configure sua conexão com SQL Server
3. **Gerar Dados** - Crie dados sintéticos para testes
4. **Otimizar** - Execute análise NSGA-II
5. **Calendário** - Veja manutenções programadas
6. **Visualizar** - Consulte dados de sensores e Pareto

## 📚 Páginas Disponíveis

- `/` - Dashboard
- `/database` - Configuração do banco
- `/generate` - Geração de dados
- `/optimize` - Otimização
- `/calendar` - Calendário de manutenção
- `/data` - Visualização de dados
- `/settings` - Configurações do sistema

## 🔧 Comandos Disponíveis

```bash
# Desenvolvimento
npm run dev

# Build
npm run build

# Produção
npm start

# Linting
npm run lint
```

## ✨ Componentes shadcn/ui Inclusos

- Button
- Card
- Input
- Label
- Alert
- Badge
- Checkbox
- Select

## 🌍 Variáveis de Ambiente

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NODE_ENV=development
```

## 🛠️ Troubleshooting

### Erro: "Failed to fetch API"
- Verifique se o backend está rodando em `http://localhost:8000`
- Confira a variável `NEXT_PUBLIC_API_URL` em `.env.local`

### Erro: "CORS"
- Certifique-se que o backend permite requisições de `http://localhost:3000`

### Porta 3000 já está em uso
```bash
npm run dev -- -p 3001
```

## 📖 Documentação Adicional

- [README.md](./README.md) - Documentação completa
- [Next.js Docs](https://nextjs.org/docs)
- [shadcn/ui Docs](https://ui.shadcn.com)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

## 🎨 Customização

### Alterar Cores

Edite `app/globals.css` e procure por variáveis CSS:

```css
:root {
  --primary: 262.1 80% 50.2%;
  --secondary: 217.2 91.2% 59.8%;
  /* ... */
}
```

### Adicionar Novo Componente UI

Já inclusos: Button, Card, Input, Label, Alert, Badge, Checkbox, Select

Para adicionar mais, copie de [shadcn/ui](https://ui.shadcn.com/docs/components)

## 🚀 Deploy

### Vercel (Recomendado)

```bash
npm install -g vercel
vercel
```

### Docker

```bash
docker build -t bucha-frontend .
docker run -p 3000:3000 bucha-frontend
```

## 💡 Dicas

- Use `'use client'` no topo de componentes interativos
- Importar componentes de `@/components/ui/` e `@/lib/`
- Utilize TypeScript para type safety
- shadcn/ui já inclui acessibilidade (a11y)

## 📞 Suporte

Verifique a documentação principal em `../README.md`

---

**Versão**: 2.0.0
**Última atualização**: 2025
