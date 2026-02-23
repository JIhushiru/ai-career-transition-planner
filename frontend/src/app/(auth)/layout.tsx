import { SessionProvider } from "@/context/session-context";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SessionProvider>
      <div className="flex min-h-screen items-center justify-center bg-linear-to-br from-background via-background to-primary/5 p-4">
        {children}
      </div>
    </SessionProvider>
  );
}
