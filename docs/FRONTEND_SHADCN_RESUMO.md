# ✨ Frontend com shadcn/ui - Resumo da Implementação

## 📦 O que foi criado

Um **frontend completo e moderno** para o Sistema de Manutenção Preditiva, usando:

- **Next.js 14** - Framework React com suporte a Server-Side Rendering
- **React 18** - Biblioteca UI
- **TypeScript** - Superset de JavaScript com tipagem estática
- **Tailwind CSS** - Framework CSS utilitário
- **shadcn/ui** - Componentes acessíveis e reutilizáveis
- **Axios** - Cliente HTTP para integração com API
- **React Hook Form** - Gerenciamento de formulários
- **Zod** - Validação de schemas

## 🎨 Design System - shadcn/ui

O projeto utiliza **shadcn/ui** como design system completo, oferecendo:

✅ Componentes acessíveis (WCAG 2.1)
✅ Customizáveis via Tailwind CSS
✅ Type-safe com TypeScript
✅ Dark mode suportado
✅ Responsivo por padrão
✅ Baseado em Radix UI

## 📂 Estrutura do Projeto

```
frontend-shadcn/
├── app/                              # App Router (Next.js 14)
│   ├── globals.css                   # Estilos globais
│   ├── layout.tsx                    # Layout raiz
│   └── (dashboard)/                  # Grupo de rotas
│       ├── layout.tsx                # Layout com sidebar
│       ├── page.tsx                  # Dashboard
│       ├── database/page.tsx          # Configuração BD
│       ├── generate/page.tsx          # Geração de dados
│       ├── optimize/page.tsx          # Otimização
│       ├── calendar/page.tsx          # Calendário
│       ├── data/page.tsx              # Visualização
│       └── settings/page.tsx          # Configurações
│
├── components/
│   ├── header.tsx                    # Componente do header
│   ├── sidebar.tsx                   # Menu lateral
│   └── ui/                           # Componentes shadcn/ui
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── alert.tsx
│       ├── badge.tsx
│       ├── checkbox.tsx
│       └── select.tsx
│
├── lib/
│   ├── api.ts                        # Cliente Axios + funções
│   └── utils.ts                      # Utilitários (cn, etc)
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
├── postcss.config.js
├── .eslintrc.json
├── .env.local.example
├── README.md
└── INSTALACAO.md
```

## 🖥️ Páginas Implementadas

### 1. Dashboard (`/`)
- Status geral do sistema
- Cards com estatísticas
- Guia de primeiros passos
- Verificação de saúde da API

### 2. Banco de Dados (`/database`)
- Configuração de conexão SQL Server
- Toggle entre autenticação Windows/SQL
- Criar/inicializar tabelas
- Feedback em tempo real

### 3. Gerar Dados (`/generate`)
- Parâmetros para geração sintética
- Configuração de período, buchas, frequência
- Taxa de degradação (baixa/média/alta)
- Salvar no banco opcionalmente
- Exibição de resultados

### 4. Otimizar (`/optimize`)
- Seleção de equipamentos
- Parâmetros NSGA-II
- Execução de otimização
- Tabela com top 10 resultados
- Resumo de estatísticas

### 5. Calendário (`/calendar`)
- Lista de manutenções programadas
- Ordenadas por prioridade
- Badges de urgência (urgente/proxima/programada/atrasado)
- Detalhes completos de cada manutenção
- Atualização em tempo real

### 6. Visualizar Dados (`/data`)
- Abas para diferentes tipos de dados
- Dados de Sensores (tabela com 50 registros)
- Ordens de Serviço (lista completa)
- Fronteira de Pareto (busca por equipamento)
- Scroll horizontal para tabelas grandes

### 7. Configurações (`/settings`)
- Informações do sistema
- Características principais
- Documentação de variáveis de ambiente
- Licença e links úteis

## 🎯 Recursos Principais

### Interface
- **Header** com status da API (verde/vermelho)
- **Sidebar** navegável com menu
- **Layout responsivo** (mobile, tablet, desktop)
- **Dark mode pronto** (não ativado por padrão)
- **Animações suaves** com Tailwind

### Funcionalidades
- Integração completa com API backend
- Validação de formulários com feedback visual
- Carregamento assíncrono com loading states
- Tratamento de erros com alertas
- Dados em tempo real
- Tabelas com scroll horizontal
- Cards com badges de status

### Componentes UI
- Botões com variantes (primary, secondary, destructive, outline, ghost)
- Cards com header/title/description/content/footer
- Inputs com validação
- Labels acessíveis
- Alerts com variantes (default, destructive, success)
- Badges para status
- Checkboxes
- Selects customizados
- Tabelas responsivas

## 🚀 Como Usar

### Instalação

```bash
cd frontend-shadcn
cp .env.local.example .env.local
npm install
```

### Desenvolvimento

```bash
npm run dev
```

Acesse: `http://localhost:3000`

### Build

```bash
npm run build
npm start
```

### Lint

```bash
npm run lint
```

## 🔌 Integração com Backend

O frontend integra-se perfeitamente com a API em `http://localhost:8000/api`:

```typescript
// lib/api.ts contém todas as funções:
- checkAPIHealth()
- configureDatabaseConnection()
- generateSyntheticData()
- runOptimization()
- loadEquipmentList()
- loadMaintenanceCalendar()
- getSensorData()
- getMaintenanceOrders()
- getParetoFront()
```

## 📊 Componentes Customizados

Além dos componentes shadcn/ui base, o projeto inclui:

- **Header** - com status da API
- **Sidebar** - navegação com ícones (lucide-react)
- **Páginas completas** - com lógica de negócio

## 🎨 Estilo e Tema

- **Tailwind CSS** para toda estilização
- **CSS Variables** para tema customizável
- **Cores**: Primary (azul), Secondary (azul claro), Destructive (vermelho)
- **Espaçamento**: Baseado em escala de 4px
- **Typography**: Roboto via Google Fonts

## 🔒 Segurança

- TypeScript para type-safety
- Validação de formulários
- Nenhum secret armazenado no cliente
- CORS configurável no backend
- Inputs sanitizados

## 📱 Responsividade

Breakpoints Tailwind:
- `sm`: 640px
- `md`: 768px (transição desktop/mobile)
- `lg`: 1024px
- `xl`: 1280px

Todas as páginas são mobile-first e responsivas.

## 🌟 Diferenciais

✨ Moderno e profissional
✨ Componentes reutilizáveis
✨ Type-safe com TypeScript
✨ Acessível (shadcn/ui + Radix)
✨ Performance otimizada (Next.js)
✨ Fácil de manter e estender
✨ Dark mode preparado
✨ Documentação completa

## 📚 Documentação Incluída

- `README.md` - Documentação completa
- `INSTALACAO.md` - Guia passo-a-passo
- Comments no código
- Type definitions via TypeScript

## 🔄 Próximos Passos (Opcionais)

1. Implementar autenticação/login
2. Adicionar gráficos (Recharts)
3. Implementar dark mode toggle
4. Adicionar temas customizáveis
5. Implementar PWA (Progressive Web App)
6. Adicionar notificações em tempo real (WebSocket)
7. Exportar dados (CSV, PDF)
8. Integração com analytics

## 📞 Estrutura de Pastas Alternativa

Caso preferisse uma estrutura diferente:
- `pages/` em vez de `app/` (Pages Router)
- `public/` para assets estáticos
- `styles/` separado
- `contexts/` para state management global
- `hooks/` para custom hooks

## ✅ Checklist de Conclusão

- ✅ Estrutura Next.js 14 com App Router
- ✅ Componentes shadcn/ui configurados
- ✅ 7 páginas completas implementadas
- ✅ Integração com API
- ✅ Responsividade total
- ✅ TypeScript em todo projeto
- ✅ Documentação completa
- ✅ Arquivo .env.local.example
- ✅ README.md e INSTALACAO.md
- ✅ ESLint configurado
- ✅ Tailwind CSS customizado

## 🎓 Tecnologias Utilizadas

- **Next.js 14** - Framework React
- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem
- **Tailwind CSS** - Estilos
- **shadcn/ui** - Design System
- **Radix UI** - Primitivos acessíveis
- **Axios** - HTTP client
- **React Hook Form** - Formulários
- **Zod** - Validação
- **Lucide React** - Ícones
- **Class Variance Authority** - Variantes CSS
- **clsx/tailwind-merge** - Utilitários CSS

---

**Projeto**: Sistema de Manutenção Preditiva
**Versão**: 2.0.0
**Tecnologia**: Next.js + shadcn/ui
**Data**: 2025
