import { SignIn, SignInButton, UserButton } from "@clerk/nextjs";
import React from "react";

export default function HomePage() {
  return (
    <div>
      <SignInButton />
      <UserButton />
    </div>
  );
}
