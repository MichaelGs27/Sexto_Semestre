require('dotenv').config();
const express = require('express');
const userRoutes = require('./routes/user.routes');
const authRoutes = require('./routes/auth.routes');

// Initialize express app
const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
    next();
});

// CORS middleware
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
    if (req.method === 'OPTIONS') {
        res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH');
        return res.status(200).json({});
    }
    next();
});

// Health check route
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'OK', timestamp: new Date() });
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);

// Handle undefined routes - FIXED: Using correct Express syntax
app.use((req, res) => {
    res.status(404).json({ 
        message: `No se puede encontrar ${req.originalUrl} en este servidor!` 
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    const statusCode = err.statusCode || 500;
    res.status(statusCode).json({
        status: 'error',
        message: err.message || 'Error interno del servidor'
    });
});

// Server configuration
const PORT = process.env.PORT || 3000;

// Start server
const server = app.listen(PORT, () => {
    console.log('=================================');
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV}`);
    console.log('=================================');
    console.log('Available routes:');
    console.log('AUTH ROUTES:');
    console.log('POST /api/auth/register - Register new user');
    console.log('POST /api/auth/login - Login user');
    console.log('\nUSER ROUTES:');
    console.log('GET /api/users/profile - Get user profile (protected)');
    console.log('PUT /api/users/update - Update user profile (protected)');
    console.log('DELETE /api/users/delete - Delete user (protected)');
    console.log('GET /api/users/dashboard - Get user dashboard (protected)');
    console.log('=================================');
});

module.exports = app;