# SmartHand Reports - Guia de Deploy no Railway

## Visao Geral

Este guia cobre o deploy completo do SmartHand Reports no Railway:
- Backend (FastAPI + Python)
- Banco de Dados (PostgreSQL)
- Frontend (pode ser deployado no Railway ou Vercel)

---

## 1. Pre-requisitos

1. Conta no [Railway](https://railway.app)
2. Repositorio GitHub conectado ao Railway
3. (Opcional) Conta no Cloudflare R2 para armazenamento de fotos

---

## 2. Deploy no Railway

### 2.1 Criar Novo Projeto

1. Acesse [Railway Dashboard](https://railway.app/dashboard)
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha o repositorio `smarthand-reports` (ou `relatorios`)
5. Railway vai detectar automaticamente o projeto

### 2.2 Adicionar PostgreSQL

1. No projeto Railway, clique em **"+ New"**
2. Selecione **"Database"** > **"Add PostgreSQL"**
3. Aguarde o provisionamento (1-2 minutos)
4. Railway automaticamente cria a variavel `DATABASE_URL`

### 2.3 Configurar o Servico Backend

1. Clique no servico do backend (detectado do GitHub)
2. Va em **Settings** > **Root Directory**
3. Configure: `backend`
4. Va em **Settings** > **Build**
5. Verifique que o comando de build e: `pip install -r requirements.txt`

### 2.4 Configurar Variaveis de Ambiente

Va em **Variables** no servico backend e adicione:

```bash
# OBRIGATORIAS
JWT_SECRET_KEY=<gere com: openssl rand -hex 32>
CORS_ORIGINS=["https://seu-frontend.vercel.app","http://localhost:5173"]

# OPCIONAIS (para Cloudflare R2)
R2_ENDPOINT_URL=https://ACCOUNT_ID.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=seu_access_key
R2_SECRET_ACCESS_KEY=seu_secret_key
R2_BUCKET_NAME=smarthand-photos

# Automaticas (Railway configura)
# DATABASE_URL - ja configurado pelo PostgreSQL
# PORT - ja configurado pelo Railway
```

**Para gerar JWT_SECRET_KEY:**
```bash
openssl rand -hex 32
```

### 2.5 Rodar Migrations

Apos o deploy inicial, rode as migrations:

**Opcao A - Via Railway CLI:**
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Conectar ao projeto
railway link

# Rodar migrations
railway run --service=backend alembic upgrade head
```

**Opcao B - Via Railway Dashboard:**
1. Va no servico backend
2. Clique em **"Settings"** > **"Deploy"**
3. Em **"Custom Deploy Command"**, adicione temporariamente:
   ```
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
   ```
4. Faca redeploy
5. Apos as migrations rodarem, remova o `alembic upgrade head &&`

### 2.6 Criar Usuario Admin Inicial

Apos as migrations, crie o primeiro usuario:

```bash
railway run --service=backend python scripts/create_admin.py
```

Se o script nao existir, crie manualmente via API ou banco.

---

## 3. Deploy do Frontend

### Opcao A: Deploy no Vercel (Recomendado)

1. Acesse [Vercel](https://vercel.com)
2. Importe o repositorio
3. Configure:
   - **Root Directory:** `frontend`
   - **Framework:** Vite
4. Adicione variavel de ambiente:
   ```
   VITE_API_URL=https://seu-backend.up.railway.app
   ```
5. Deploy

### Opcao B: Deploy no Railway

1. No projeto Railway, clique em **"+ New"** > **"GitHub Repo"**
2. Selecione o mesmo repositorio
3. Configure **Root Directory:** `frontend`
4. Adicione variavel: `VITE_API_URL=https://seu-backend.up.railway.app`
5. Configure o build:
   - Build Command: `npm run build`
   - Start Command: `npx serve dist -s -l ${PORT:-3000}`

---

## 4. Variaveis de Ambiente - Resumo

### Backend (Railway)
| Variavel | Obrigatoria | Descricao |
|----------|-------------|-----------|
| `DATABASE_URL` | Sim | Auto-configurado pelo PostgreSQL |
| `JWT_SECRET_KEY` | Sim | Chave secreta para JWT (min 32 chars) |
| `CORS_ORIGINS` | Sim | URLs permitidas (JSON array) |
| `R2_ENDPOINT_URL` | Nao | Cloudflare R2 endpoint |
| `R2_ACCESS_KEY_ID` | Nao | Cloudflare R2 access key |
| `R2_SECRET_ACCESS_KEY` | Nao | Cloudflare R2 secret |
| `R2_BUCKET_NAME` | Nao | Nome do bucket R2 |
| `DEBUG` | Nao | `true` para desenvolvimento |

### Frontend (Vercel/Railway)
| Variavel | Obrigatoria | Descricao |
|----------|-------------|-----------|
| `VITE_API_URL` | Sim | URL do backend Railway |

---

## 5. Verificacao do Deploy

### Health Check do Backend
```bash
curl https://seu-backend.up.railway.app/api/v1/health
```
Resposta esperada:
```json
{"status": "healthy", "version": "0.1.0"}
```

### Teste de Login
```bash
curl -X POST https://seu-backend.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=sua_senha"
```

### Frontend
Acesse a URL do frontend e verifique:
1. Pagina de login carrega
2. Console do navegador sem erros de CORS
3. Login funciona

---

## 6. Troubleshooting

### Erro: "relation does not exist"
- Migrations nao foram rodadas
- Solucao: `railway run alembic upgrade head`

### Erro de CORS
- CORS_ORIGINS nao inclui o dominio do frontend
- Solucao: Atualize CORS_ORIGINS com a URL correta

### Erro: "JWT_SECRET_KEY required"
- Variavel nao configurada
- Solucao: Adicione JWT_SECRET_KEY nas variaveis do Railway

### Build falha com erro de dependencia
- Pode ser versao do Python
- Solucao: Adicione `runtime.txt` no backend com: `python-3.11`

### Health check falha
- Aplicacao nao iniciou corretamente
- Solucao: Verifique os logs no Railway Dashboard

---

## 7. Atualizacoes Futuras

Para atualizar a aplicacao:

1. Faca push para o repositorio GitHub
2. Railway detecta automaticamente e faz redeploy
3. Se houver novas migrations:
   ```bash
   railway run alembic upgrade head
   ```

---

## 8. Custos Estimados

Railway oferece tier gratuito com:
- $5 de credito mensal
- Suficiente para projetos pequenos

Para producao, considere:
- **Hobby Plan:** ~$5/mes por servico
- **PostgreSQL:** ~$5-20/mes dependendo do uso
- **Total estimado:** $15-30/mes para setup basico

---

*Ultima atualizacao: 2026-02-02*
