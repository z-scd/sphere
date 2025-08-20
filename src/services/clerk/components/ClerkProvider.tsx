import { ReactNode } from "react";
import { ClerkProvider as OriginalClerkProvider } from "@clerk/nextjs";

export default function ClerkProvider({ children }: { children: ReactNode }) {
  return <OriginalClerkProvider>{children}</OriginalClerkProvider>;
}
