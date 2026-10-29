FROM node:20-alpine

WORKDIR /app

# Enable corepack for pnpm support
RUN corepack enable && corepack prepare pnpm@latest --activate

# Install dependencies
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install

# Copy frontend source
COPY . .

# Build arguments for Next.js public env vars
ARG NEXT_PUBLIC_BACKEND_URL=http://localhost:3038
ARG INTERNAL_BACKEND_URL=http://backend:3038
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}
ENV INTERNAL_BACKEND_URL=${INTERNAL_BACKEND_URL}

# Build Next.js production bundle
RUN pnpm run build

EXPOSE 8086

CMD ["pnpm", "start", "-p", "8086", "-H", "0.0.0.0"]

