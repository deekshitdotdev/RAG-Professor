import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The Python/Node backend that serves /api/* (upload, ask, models, status,
// history) is expected to run separately. During development, proxy API
// calls to it so the Vite dev server and backend can run on different ports.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
