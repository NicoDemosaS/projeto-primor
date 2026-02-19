# Primor Garçons - Identidade Visual

## 🎨 Análise da Logo

A logo da **Primor Garçons** transmite:
- **Elegância** e **sofisticação**
- **Luxo** e **premium**
- **Profissionalismo** no segmento de eventos

### Elementos da Logo
- Tipografia serifada clássica em "Primor"
- Tipografia em caixa alta espaçada em "GARÇONS"
- Diamante decorativo sobre o "i"
- Linha ornamental dourada
- Gradiente dourado (do claro ao profundo)

---

## 🎨 Paleta de Cores

### Cores Primárias

| Nome | HEX | RGB | Uso |
|------|-----|-----|-----|
| **Preto Primor** | `#0D0D0D` | rgb(13, 13, 13) | Fundos principais, textos |
| **Dourado Claro** | `#E8C872` | rgb(232, 200, 114) | Destaques, hover states |
| **Dourado Principal** | `#C9A227` | rgb(201, 162, 39) | Botões, ícones, acentos |
| **Dourado Profundo** | `#A67C00` | rgb(166, 124, 0) | Bordas, elementos secundários |

### Cores Secundárias

| Nome | HEX | RGB | Uso |
|------|-----|-----|-----|
| **Cinza Escuro** | `#1A1A1A` | rgb(26, 26, 26) | Cards, sidebars |
| **Cinza Médio** | `#2D2D2D` | rgb(45, 45, 45) | Inputs, bordas |
| **Cinza Claro** | `#4A4A4A` | rgb(74, 74, 74) | Textos secundários |
| **Off-White** | `#F5F5F0` | rgb(245, 245, 240) | Textos sobre fundo escuro |

### Cores de Estado

| Nome | HEX | RGB | Uso |
|------|-----|-----|-----|
| **Sucesso** | `#4CAF50` | rgb(76, 175, 80) | Confirmado, sucesso |
| **Alerta** | `#FFC107` | rgb(255, 193, 7) | Pendente, atenção |
| **Erro** | `#F44336` | rgb(244, 67, 54) | Recusado, erro |
| **Info** | `#2196F3` | rgb(33, 150, 243) | Informações |

---

## 🔤 Tipografia

### Fontes Sugeridas (Google Fonts)

| Uso | Fonte | Alternativa | Peso |
|-----|-------|-------------|------|
| **Logo/Títulos** | Playfair Display | Cormorant Garamond | 400, 600, 700 |
| **Subtítulos** | Montserrat | Poppins | 500, 600 |
| **Corpo** | Inter | Open Sans | 400, 500, 600 |
| **Mono/Dados** | JetBrains Mono | Fira Code | 400 |

### Hierarquia de Texto

```css
/* Títulos */
h1 { font-family: 'Playfair Display'; font-size: 2.5rem; font-weight: 700; }
h2 { font-family: 'Playfair Display'; font-size: 2rem; font-weight: 600; }
h3 { font-family: 'Montserrat'; font-size: 1.5rem; font-weight: 600; }
h4 { font-family: 'Montserrat'; font-size: 1.25rem; font-weight: 500; }

/* Corpo */
body { font-family: 'Inter'; font-size: 1rem; font-weight: 400; }
.small { font-size: 0.875rem; }
.caption { font-size: 0.75rem; }
```

---

## 🎯 Aplicação no UI

### Tema Escuro (Principal)

```css
:root {
  /* Backgrounds */
  --bg-primary: #0D0D0D;
  --bg-secondary: #1A1A1A;
  --bg-tertiary: #2D2D2D;
  
  /* Gold */
  --gold-light: #E8C872;
  --gold-main: #C9A227;
  --gold-deep: #A67C00;
  
  /* Text */
  --text-primary: #F5F5F0;
  --text-secondary: #B0B0B0;
  --text-muted: #6B6B6B;
  
  /* Borders */
  --border-color: #2D2D2D;
  --border-gold: #A67C00;
}
```

### Componentes

#### Botões

| Tipo | Background | Texto | Borda |
|------|------------|-------|-------|
| **Primário** | Gradiente dourado | Preto | - |
| **Secundário** | Transparente | Dourado | Dourado |
| **Ghost** | Transparente | Off-white | - |
| **Danger** | Vermelho | Branco | - |

```css
/* Botão Primário */
.btn-primary {
  background: linear-gradient(135deg, #E8C872 0%, #C9A227 50%, #A67C00 100%);
  color: #0D0D0D;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #F0D080 0%, #D4AF37 50%, #B8860B 100%);
  box-shadow: 0 4px 20px rgba(201, 162, 39, 0.3);
}

/* Botão Secundário */
.btn-secondary {
  background: transparent;
  color: #C9A227;
  border: 1px solid #C9A227;
  border-radius: 8px;
  padding: 12px 24px;
}

.btn-secondary:hover {
  background: rgba(201, 162, 39, 0.1);
}
```

#### Cards

```css
.card {
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 12px;
  padding: 24px;
}

.card:hover {
  border-color: #A67C00;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
}

.card-header {
  border-bottom: 1px solid #2D2D2D;
  padding-bottom: 16px;
  margin-bottom: 16px;
}
```

#### Inputs

```css
.input {
  background: #2D2D2D;
  border: 1px solid #4A4A4A;
  border-radius: 8px;
  color: #F5F5F0;
  padding: 12px 16px;
}

.input:focus {
  border-color: #C9A227;
  outline: none;
  box-shadow: 0 0 0 3px rgba(201, 162, 39, 0.2);
}

.input::placeholder {
  color: #6B6B6B;
}
```

#### Sidebar/Menu

```css
.sidebar {
  background: #0D0D0D;
  border-right: 1px solid #2D2D2D;
}

.nav-item {
  color: #B0B0B0;
  padding: 12px 20px;
  border-radius: 8px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #1A1A1A;
  color: #F5F5F0;
}

.nav-item.active {
  background: rgba(201, 162, 39, 0.1);
  color: #C9A227;
  border-left: 3px solid #C9A227;
}
```

---

## 📱 Responsividade

| Breakpoint | Tamanho | Uso |
|------------|---------|-----|
| **Mobile** | < 640px | Smartphones |
| **Tablet** | 640px - 1024px | Tablets |
| **Desktop** | > 1024px | Computadores |

---

## ✨ Efeitos e Animações

### Gradiente Dourado Animado
```css
.gold-shimmer {
  background: linear-gradient(
    90deg,
    #A67C00 0%,
    #E8C872 25%,
    #C9A227 50%,
    #E8C872 75%,
    #A67C00 100%
  );
  background-size: 200% auto;
  animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
  to { background-position: 200% center; }
}
```

### Hover Sutil
```css
.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}
```

### Glow Dourado
```css
.gold-glow {
  box-shadow: 0 0 20px rgba(201, 162, 39, 0.3);
}
```

---

## 🖼️ Ícones

### Estilo Recomendado
- **Biblioteca:** Lucide Icons ou Phosphor Icons
- **Stroke:** 1.5px - 2px
- **Cor padrão:** Off-white (#F5F5F0)
- **Cor destaque:** Dourado (#C9A227)

### Ícones do Sistema
| Função | Ícone Sugerido |
|--------|----------------|
| Dashboard | LayoutDashboard |
| Garçons | Users |
| Eventos | Calendar |
| Relatórios | BarChart3 |
| Configurações | Settings |
| Notificações | Bell |
| Confirmado | CheckCircle |
| Pendente | Clock |
| Recusado | XCircle |
| WhatsApp | MessageCircle |

---

## 📐 Espaçamento

### Sistema de Spacing (8px base)

| Token | Valor | Uso |
|-------|-------|-----|
| `xs` | 4px | Ícones inline |
| `sm` | 8px | Gaps pequenos |
| `md` | 16px | Padding padrão |
| `lg` | 24px | Seções |
| `xl` | 32px | Entre componentes |
| `2xl` | 48px | Entre seções |
| `3xl` | 64px | Hero/headers |

---

## 🎭 Aplicação por Tela

### Login
- Fundo: Preto sólido com textura sutil
- Card central com borda dourada sutil
- Logo centralizada no topo
- Inputs com foco dourado

### Dashboard
- Sidebar escura com menu
- Cards com métricas em fundo cinza
- Números em dourado
- Gráficos com acentos dourados

### Listagens (Garçons/Eventos)
- Tabelas com hover em cinza escuro
- Badges coloridos para status
- Ações com ícones dourados

### Formulários
- Labels em off-white
- Inputs escuros com borda
- Botão primário dourado
- Validações com cores de estado

---

## 🏷️ Tailwind Config (Sugestão)

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primor: {
          black: '#0D0D0D',
          dark: '#1A1A1A',
          gray: '#2D2D2D',
        },
        gold: {
          light: '#E8C872',
          DEFAULT: '#C9A227',
          deep: '#A67C00',
        },
      },
      fontFamily: {
        display: ['Playfair Display', 'serif'],
        heading: ['Montserrat', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'gold-gradient': 'linear-gradient(135deg, #E8C872 0%, #C9A227 50%, #A67C00 100%)',
      },
    },
  },
}
```

---

## ✅ Checklist de Implementação

- [ ] Configurar paleta de cores no Tailwind/CSS
- [ ] Importar fontes do Google Fonts
- [ ] Criar componentes base (Button, Card, Input)
- [ ] Implementar tema escuro
- [ ] Adicionar logo nos assets
- [ ] Configurar favicon dourado
- [ ] Testar contraste de acessibilidade (WCAG)

---

*Documento criado em: Janeiro/2026*  
*Baseado na identidade visual da logo Primor Garçons*
