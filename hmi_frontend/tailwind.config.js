/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Engineering Application Palette
        workbench: {
          bg: '#f3f4f6', // Light gray background
          surface: '#ffffff',
          border: '#e5e7eb',
          panelBg: '#f9fafb',
          text: '#111827',
          textMuted: '#6b7280',
          accent: '#0066cc', // Polarion/Enterprise blue
          accentHover: '#0052a3',
          danger: '#dc2626',
          warning: '#d97706',
          success: '#16a34a',
          sidebarBg: '#0f4a66',
          sidebarHover: '#165a78',
          sidebarActive: '#135471',
          sidebarText: '#e2e8f0',
          headerBg: '#0b3d54',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'Menlo', 'monospace'],
      }
    },
  },
  plugins: [],
}
