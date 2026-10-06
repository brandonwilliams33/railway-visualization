import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({base:'./',plugins:[react(),tailwindcss()],build:{rollupOptions:{output:{manualChunks(id){if(id.includes('/src/data/network.json'))return 'rail-data';if(id.includes('/src/data/geography.json'))return 'geography';if(id.includes('node_modules/leaflet')||id.includes('node_modules/react-leaflet')||id.includes('node_modules/@react-leaflet'))return 'map-vendor'}}}}});
