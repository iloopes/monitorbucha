# Frontend - Sistema de Manutenção Preditiva

Frontend moderno e responsivo para o Sistema de Manutenção Preditiva, construído com **Next.js 14**, **React 18**, **TypeScript** e **shadcn/ui** como design system.

## 🎨 Recursos

- **Design System Moderno**: Utiliza componentes shadcn/ui para uma interface consistente e profissional
- **Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- **Type-Safe**: Desenvolvimento com TypeScript para maior segurança
- **Componentes Reutilizáveis**: Biblioteca de componentes UI bem estruturada
- **Dark Mode Pronto**: Suporte para tema claro e escuro
- **Integração com API**: Cliente HTTP pré-configurado com Axios

## 📋 Funcionalidades

### Páginas Implementadas

1. **Dashboard** - Visão geral do sistema com estatísticas rápidas
2. **Banco de Dados** - Configuração de conexão com SQL Server
3. **Gerar Dados** - Criação de dados sintéticos para testes
4. **Otimizar** - Execução de algoritmos NSGA-II para otimização
5. **Calendário** - Visualização do calendário de manutenção programada
6. **Visualizar Dados** - Consulta de dados de sensores, ordens e Pareto
7. **Configurações** - Informações do sistema

## 🚀 Instalação

### Pré-requisitos

- Node.js 18.17+
- npm ou yarn

### Passos de Instalação

```bash
# 1. Entre no diretório do frontend
cd frontend-shadcn

# 2. Instale as dependências
npm install

# 3. Configure as variáveis de ambiente
cp .env.local.example .env.local

# 4. Edite .env.local e configure a URL da API
# NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## 🏃 Como Executar

### Desenvolvimento

```bash
npm run dev
```

O aplicativo estará disponível em `http://localhost:3000`

### Build para Produção

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## 📁 Estrutura do Projeto

```
frontend-shadcn/
├── app/
│   ├── globals.css              # Estilos globais e CSS customizado
│   ├── layout.tsx               # Layout raiz da aplicação
│   ├── (dashboard)/
│   │   ├── layout.tsx           # Layout do dashboard com sidebar
│   │   ├── page.tsx             # Página inicial
│   │   ├── database/
│   │   │   └── page.tsx         # Configuração do banco de dados
│   │   ├── generate/
│   │   │   └── page.tsx         # Geração de dados sintéticos
│   │   ├── optimize/
│   │   │   └── page.tsx         # Otimização NSGA-II
│   │   ├── calendar/
│   │   │   └── page.tsx         # Calendário de manutenção
│   │   ├── data/
│   │   │   └── page.tsx         # Visualização de dados
│   │   └── settings/
│   │       └── page.tsx         # Configurações
│
├── components/
│   ├── header.tsx               # Componente do header
│   ├── sidebar.tsx              # Componente da sidebar
│   └── ui/                      # Componentes shadcn/ui
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── badge.tsx
│       ├── alert.tsx
│       ├── checkbox.tsx
│       └── select.tsx
│
├── lib/
│   ├── api.ts                   # Cliente HTTP e funções da API
│   └── utils.ts                 # Utilitários (cn para tailwind)
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
├── next.config.js
└── .env.local.example           # Exemplo de variáveis de ambiente
```

## 🔧 Configuração da API

Certifique-se de que o backend está rodando em `http://localhost:8000` (ou configure a URL correta em `.env.local`)

### Variáveis de Ambiente

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NODE_ENV=development
```

## 📦 Dependências Principais

- **next**: Framework React com suporte a SSR
- **react**: Biblioteca UI
- **typescript**: Superset de JavaScript com tipagem
- **tailwindcss**: Framework CSS utilitário
- **shadcn/ui**: Coleção de componentes acessíveis
- **axios**: Cliente HTTP
- **react-hook-form**: Gerenciamento de formulários
- **zod**: Validação de schema
- **lucide-react**: Ícones
- **recharts**: Visualização de dados
- **class-variance-authority**: Utilitário para variantes de CSS

## 🎯 Fluxo de Uso

1. **Iniciar** - Acesse o dashboard para ver status geral
2. **Configurar DB** - Configure conexão com SQL Server
3. **Gerar Dados** - Crie dados sintéticos para testes
4. **Otimizar** - Execute análise NSGA-II
5. **Visualizar** - Consulte calendário e dados gerados

## 🛠️ Desenvolvimento

### Adicionar Novo Componente UI

```bash
# Componentes já disponíveis podem ser importados de @/components/ui/
```

### Criar Novas Páginas

1. Crie um diretório em `app/(dashboard)/`
2. Adicione arquivo `page.tsx`
3. Use `'use client'` no topo para componentes interativos
4. Importe componentes conforme necessário

### Chamadas à API

```typescript
import { api, loadEquipmentList } from '@/lib/api'

// Usar função pré-definida
const equipment = await loadEquipmentList()

// Ou fazer chamada customizada
const response = await api.get('/endpoint')
```

## 📱 Responsividade

O projeto usa Tailwind CSS com grid responsivo:

```tsx
<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
  {/* Conteúdo */}
</div>
```

Breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

## 🔒 Segurança

- Validação de formulários com Zod
- TypeScript para type-safety
- HTTPS recomendado em produção
- Não armazene secrets no cliente

## 🚀 Deployment

### Vercel (Recomendado)

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

```bash
docker build -t bucha-monitor-frontend .
docker run -p 3000:3000 bucha-monitor-frontend
```

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique a documentação em `docs/`
- Consulte o README raiz do projeto
- Abra uma issue no repositório

## 📄 Licença

MIT - veja LICENSE para detalhes

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor, faça um fork e abra um pull request.

---

**Versão**: 2.0.0
**Última atualização**: 2025
