FROM node:24-alpine

WORKDIR /app

# Copy package.json and package-lock.json first
# to leverage Docker's layer caching.
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of frontend source code
COPY . .

# Build the application
RUN npm run build

# Use nginx to serve the built files
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
EXPOSE 80