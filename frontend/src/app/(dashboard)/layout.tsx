import { DashboardShell } from "@/components/layout/dashboard-shell";
import { SessionProvider } from "@/context/session-context";
import { AuthGuard } from "@/components/auth/auth-guard";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SessionProvider>
      <AuthGuard>
        <DashboardShell>{children}</DashboardShell>
      </AuthGuard>
    </SessionProvider>
  );
}
