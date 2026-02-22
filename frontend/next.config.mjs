/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Custom port configuration
  devServer: {
    port: 3007,
  },
}

export default nextConfig
