
FROM node:24-alpine

WORKDIR /app

# Copy package.json and package-lock.json first
# to leverage Docker's layer caching.
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your frontend source code
COPY . .

# Expose the port Vite runs on
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]