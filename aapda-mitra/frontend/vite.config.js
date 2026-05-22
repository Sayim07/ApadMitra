import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'AapdaMitra - Disaster Alert Platform',
        short_name: 'AapdaMitra',
        description: 'Real-time disaster alerts and community resilience',
        theme_color: '#1f2937',
        background_color: '#ffffff',
        start_url: '/',
        scope: '/',
        display: 'standalone'
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/tile\.openstreetmap\.org\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'map-tiles',
              expiration: { maxEntries: 50, maxAgeSeconds: 86400 }
            }
          }
        ]
      },
      devOptions: { enabled: process.env.SW_DEV === 'true' }
    })
  ],
  server: { port: 3000 }
})
