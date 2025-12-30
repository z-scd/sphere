import { SignInButton, UserButton } from "@clerk/nextjs";
import React from "react";
import { ThemeToggle } from "@/components/ui/ThemeToggle";

export default function HomePage() {
  return (
    <div>
      <SignInButton />
      <UserButton />
      <ThemeToggle />
    </div>
  );
}
