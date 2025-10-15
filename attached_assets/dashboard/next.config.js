/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  ...(process.env.NODE_ENV === "production"
    ? { output: "export", trailingSlash: true }
    : {}),
  // TODO: Removing this currently breaks the export with Next 15.2.4.
  // Revisit when Next.js fixes ESM externals handling for static export.
  experimental: {
    esmExternals: false,
  },
}

module.exports = nextConfig
