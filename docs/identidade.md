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

### Cores de Fundo (Degradê)

| Nome | HEX | Uso |
|------|-----|-----|
| **Preto Base** | `#030712` | Ponto final do degradê (gray-950) |
| **Cinza Escuro** | `#111827` | Ponto inicial do degradê (gray-900) |
| **Cinza Médio** | `#1F2937` | Cards, superfícies elevadas (gray-800) |

**Degradê Principal do Fundo:**
```css
background: linear-gradient(to bottom, #111827, #030712);
/* ou em Tailwind: bg-gradient-to-b from-gray-900 to-gray-950 */
```

### Cores Douradas (Vibrantes)

| Nome | HEX | RGB | Uso |
|------|-----|-----|-----|
| **Dourado Brilhante** | `#FBBF24` | rgb(251, 191, 36) | Botões principais, CTAs (amber-400) |
| **Dourado Hover** | `#FCD34D` | rgb(252, 211, 77) | Estados hover (amber-300) |
| **Dourado Suave** | `#F59E0B` | rgb(245, 158, 11) | Acentos, bordas (amber-500) |
| **Dourado Texto** | `#D97706` | rgb(217, 119, 6) | Links, textos dourados (amber-600) |

### Cores de Texto

| Nome | HEX | Tailwind | Uso |
|------|-----|----------|-----|
| **Branco** | `#FFFFFF` | white | Títulos, textos principais |
| **Cinza Claro** | `#F3F4F6` | gray-100 | Labels, textos importantes |
| **Cinza Médio** | `#9CA3AF` | gray-400 | Textos secundários |
| **Cinza Escuro** | `#6B7280` | gray-500 | Placeholders, textos mutados |

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

---

## 🎯 Variáveis CSS

```css
:root {
  /* Backgrounds - Degradê */
  --bg-base: #030712;      /* gray-950 */
  --bg-surface: #111827;   /* gray-900 */
  --bg-card: #1F2937;      /* gray-800 */
  --bg-input: rgba(255, 255, 255, 0.05); /* white/5 */
  
  /* Gold - Vibrante */
  --gold-bright: #FBBF24;  /* amber-400 */
  --gold-hover: #FCD34D;   /* amber-300 */
  --gold-accent: #F59E0B;  /* amber-500 */
  
  /* Text */
  --text-primary: #FFFFFF;
  --text-secondary: #9CA3AF; /* gray-400 */
  --text-muted: #6B7280;     /* gray-500 */
  
  /* Borders */
  --border-subtle: rgba(255, 255, 255, 0.1);
  --border-gold: #F59E0B;
  
  /* States */
  --success: #22C55E;  /* green-500 */
  --warning: #EAB308;  /* yellow-500 */
  --error: #EF4444;    /* red-500 */
  --info: #3B82F6;     /* blue-500 */
}
```

---

## 🏷️ Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        // Cores do Tailwind usadas: gray-800/900/950, amber-300/400/500
      },
      fontFamily: {
        display: ['Playfair Display', 'serif'],
        heading: ['Montserrat', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'primor-gradient': 'linear-gradient(to bottom, #111827, #030712)',
      },
    },
  },
}
```

---

## 🧩 Componentes

### Botões

```html
<!-- Botão Primário (Dourado) -->
<button class="w-full rounded-md bg-amber-400 px-4 py-2 text-sm font-semibold text-gray-900 
               hover:bg-amber-300 focus:outline-2 focus:outline-offset-2 focus:outline-amber-400 
               transition-colors">
  Entrar
</button>

<!-- Botão Secundário (Ghost/Glass) -->
<button class="w-full rounded-md bg-white/10 px-4 py-2 text-sm font-semibold text-white 
               border border-white/20 hover:bg-white/20 transition-colors">
  Cancelar
</button>

<!-- Botão Link -->
<button class="text-sm font-semibold text-amber-400 hover:text-amber-300 transition-colors">
  Saiba mais
</button>
```

### Inputs

```html
<input 
  type="email" 
  class="block w-full rounded-md bg-white/5 px-3 py-2 text-white 
         outline-1 -outline-offset-1 outline-white/10 
         placeholder:text-gray-500 
         focus:outline-2 focus:-outline-offset-2 focus:outline-amber-400"
  placeholder="seu@email.com"
/>
```

### Cards

```html
<div class="bg-gray-800/50 backdrop-blur-sm border border-white/10 rounded-xl p-6">
  <!-- Conteúdo -->
</div>
```

---

*Documento criado em: Janeiro/2026*  
*Baseado na identidade visual da logo Primor Garçons*
