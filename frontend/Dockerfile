# Frontend React - INAOE RAG Assistant
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY react-app/package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY react-app/ ./

# Build de producción
RUN npm run build

# --- Etapa de producción con Nginx ---
FROM nginx:alpine

# Copiar build de React
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración de Nginx para SPA
RUN echo 'server { \
    listen 80; \
    location / { \
    root /usr/share/nginx/html; \
    try_files $uri $uri/ /index.html; \
    } \
    location /api { \
    proxy_pass http://backend:8000; \
    proxy_set_header Host $host; \
    proxy_set_header X-Real-IP $remote_addr; \
    } \
    }' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
