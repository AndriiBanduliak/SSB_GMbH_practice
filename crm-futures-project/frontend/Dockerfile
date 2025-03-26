# --- Stage 1: Build React App ---
FROM node:18-alpine as builder

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код приложения
COPY . .

# Собираем продакшен-билд
RUN npm run build

# --- Stage 2: Serve with Nginx ---
FROM nginx:1.21-alpine

# Копируем кастомную конфигурацию Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранные статические файлы из стадии builder
COPY --from=builder /app/build /usr/share/nginx/html

# Открываем порт 80
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
