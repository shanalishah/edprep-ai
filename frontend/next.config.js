/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'vercel.app', '*.vercel.app'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  },
  // Optimize for Vercel deployment
  output: 'standalone',
  experimental: {
    // Enable modern bundling
    esmExternals: true,
  },
  // Handle API routes properly - proxy to Railway backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://web-production-4d7f.up.railway.app/api/:path*',
      },
    ]
  },
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
