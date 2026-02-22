import { SessionProvider } from "@/context/session-context";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SessionProvider>
      <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
        {children}
      </div>
    </SessionProvider>
  );
}
