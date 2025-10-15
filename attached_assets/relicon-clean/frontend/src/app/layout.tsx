import './globals.css'

export const metadata = {
  title: 'Relicon Clean System',
  description: 'AI-Powered Video Generation - Clean Architecture',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}