import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { Fraunces, Manrope, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-fraunces',
  display: 'swap',
})

const manrope = Manrope({
  subsets: ['latin'],
  variable: '--font-manrope',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Lesedi Lens',
  description:
    'Lesedi Lens is a calm, caregiver-friendly Q-CHAT-10 screening experience for early childhood development conversations in Lesotho.',
  keywords: ['Lesedi Lens', 'autism screening', 'early childhood', 'Lesotho', 'Q-CHAT-10'],
  alternates: {
    canonical: 'https://lesedi-lens.vercel.app',
  },
  openGraph: {
    title: 'Lesedi Lens',
    description:
      'A calm, caregiver-friendly Q-CHAT-10 screening experience for early childhood development conversations in Lesotho.',
    url: 'https://lesedi-lens.vercel.app',
    siteName: 'Lesedi Lens',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Lesedi Lens',
    description:
      'A calm, caregiver-friendly Q-CHAT-10 screening experience for early childhood development conversations in Lesotho.',
  },
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  colorScheme: 'dark',
  themeColor: '#0f3145',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      className={`dark bg-background ${fraunces.variable} ${manrope.variable} ${jetbrainsMono.variable}`}
    >
      <body className="antialiased">
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
