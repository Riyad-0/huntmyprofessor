import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const apiPort = 8000;

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: `http://localhost:${apiPort}`,
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
