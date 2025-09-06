// This file exports utility functions that can be reused throughout the application.

function formatDate(date) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString(undefined, options);
}

function generateUniqueId() {
    return 'id-' + Math.random().toString(36).substr(2, 16);
}

function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

export { formatDate, generateUniqueId, deepClone };