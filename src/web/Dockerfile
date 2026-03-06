ARG NODE_VERSION=22
ARG APP_PORT=3000

FROM oven/bun:1 AS deps
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

FROM node:${NODE_VERSION}-slim AS builder
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1


COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Ensure a clean build directory and build with Turbopack (no standalone output folder produced)
RUN rm -rf .next && npx next build --turbopack

FROM node:${NODE_VERSION}-slim AS runner
ARG APP_PORT=3000
WORKDIR /app
ENV NODE_ENV=production \
    PORT=${APP_PORT} \
    NEXT_TELEMETRY_DISABLED=1

RUN groupadd -r nextjs && useradd -r -g nextjs nextjs

RUN mkdir -p /app/.next/cache && chown -R nextjs:nextjs /app/.next


#############################################
########## Turbopack build output ###########
#############################################

COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=deps /app/node_modules ./node_modules


EXPOSE ${APP_PORT}
USER nextjs


CMD ["node", "node_modules/next/dist/bin/next", "start"]