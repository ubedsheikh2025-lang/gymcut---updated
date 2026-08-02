import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gym Video AI Editor — Auto-Edit Your Workouts",
  description:
    "Upload your gym videos and let AI automatically find the best moments, stitch them together with music and transitions. No editing skills needed.",
  keywords: [
    "gym video editor",
    "AI video editor",
    "workout video",
    "auto edit gym",
    "fitness video maker",
  ],
  openGraph: {
    title: "Gym Video AI Editor",
    description: "Auto-edit your gym workout videos with AI",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-black text-white antialiased">
        {children}
      </body>
    </html>
  );
}
