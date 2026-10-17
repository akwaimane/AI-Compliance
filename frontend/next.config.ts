import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Every page is static: the export is served by the FastAPI backend so the
  // whole platform deploys as a single service.
  output: "export",
  trailingSlash: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
