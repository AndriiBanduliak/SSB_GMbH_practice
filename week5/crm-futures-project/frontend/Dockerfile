# --- Stage 1: Build React App ---
    FROM node:18-alpine as builder

    WORKDIR /app
    
    COPY package*.json ./
    # Если используете yarn:
    # COPY yarn.lock ./
    
    # Используем npm install вместо npm ci
    RUN npm install # <--- ЗАМЕНИЛИ ЗДЕСЬ
    
    COPY . .
    RUN npm run build
    
    # --- Stage 2: Serve with Nginx ---
    FROM nginx:1.21-alpine
    
    COPY nginx.conf /etc/nginx/conf.d/default.conf
    COPY --from=builder /app/build /usr/share/nginx/html
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]