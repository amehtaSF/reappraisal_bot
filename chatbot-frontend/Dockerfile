# Stage 1: Build React app
FROM node:20.17-alpine as build

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the source code and build the app
COPY . ./
RUN npm run build

# Stage 2: Serve the app with Nginx
FROM nginx:alpine

# Copy custom Nginx config if you have one (optional)
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the React build from the previous stage to the Nginx html directory
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]