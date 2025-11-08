#!/bin/bash

# Quick start script for local development

set -e

echo "🚀 Starting System Architect Generator..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
    echo "   Required: GOOGLE_API_KEY"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
echo ""
echo "🏥 Checking service health..."
docker-compose ps

echo ""
echo "✅ Application started successfully!"
echo ""
echo "📍 Access the application at: http://localhost"
echo "🏥 Health check: http://localhost/health"
echo ""
echo "📊 To view logs: make logs"
echo "🛑 To stop: make down"
echo ""
