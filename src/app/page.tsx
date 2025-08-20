import { SignIn, UserButton } from "@clerk/nextjs";
import React from "react";

export default function HomePage() {
  return (
    <div>
      <SignIn />
      <UserButton />
    </div>
  );
}
