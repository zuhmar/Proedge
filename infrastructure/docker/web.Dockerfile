FROM node:22-alpine
WORKDIR /app
COPY --chown=node:node package.json package-lock.json ./
COPY --chown=node:node apps/web/package.json apps/web/package.json
COPY --chown=node:node packages/shared-types/package.json packages/shared-types/package.json
RUN --mount=type=secret,id=ca_bundle,target=/tmp/ca-bundle \
    if [ -s /tmp/ca-bundle ]; then export NODE_EXTRA_CA_CERTS=/tmp/ca-bundle; fi; \
    npm ci --no-audit --no-fund
COPY --chown=node:node apps/web apps/web
COPY --chown=node:node packages/shared-types packages/shared-types
ENV NEXT_TELEMETRY_DISABLED=1
ENV API_INTERNAL_URL=http://api:8000
RUN npm run build
RUN chown -R node:node /app/apps/web/.next
USER node
EXPOSE 3000
CMD ["npm", "run", "start", "-w", "apps/web"]
