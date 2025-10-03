FROM node:20 AS build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install

COPY frontend ./
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
RUN apk add --no-cache gettext
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf.template /etc/nginx/templates/default.conf.template

ENV PORT=8080
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
