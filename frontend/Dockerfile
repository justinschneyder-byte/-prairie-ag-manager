FROM node:20-slim AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Vite bakes VITE_* vars into the compiled bundle at build time, not runtime —
# Railway passes service Variables matching this ARG name through automatically.
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

FROM node:20-slim
WORKDIR /app
RUN npm install -g serve@14

COPY --from=build /app/dist ./dist

CMD ["sh", "-c", "serve -s dist -l ${PORT:-3000}"]
