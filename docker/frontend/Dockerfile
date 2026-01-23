# Frontend Dockerfile for Todo Chatbot - Phase IV
# Multi-stage build for Next.js application with node:20-alpine
# Health check endpoint: /health (expected to be served by Next.js)

# ================================
# Stage 1: Dependencies Installation
# ================================
FROM node:20-alpine AS deps

# Install dependencies only when needed
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies using npm ci for reproducible builds
RUN npm ci

# ================================
# Stage 2: Build Stage
# ================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source code
COPY . ./

# Build Next.js application
# This generates optimized production build in .next directory
RUN npm run build

# ================================
# Stage 3: Production Runtime
# ================================
FROM node:20-alpine AS runner

WORKDIR /app

# Set NODE_ENV to production
ENV NODE_ENV=production

# Create non-root user for security (using node user from base image)
# node user has UID 1000 in node:20-alpine
USER node

# Copy built application
COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next ./.next
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/package.json ./package.json

# Expose port 3000
EXPOSE 3000

# Set environment variables
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check (Next.js should serve this endpoint at /api/health or /health)
# Using wget as it's available in alpine by default
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start Next.js production server
CMD ["npm", "start"]
