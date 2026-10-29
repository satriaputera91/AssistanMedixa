/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const backendUrl =
      process.env.INTERNAL_BACKEND_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'http://localhost:3038';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
