import { redirect } from "next/navigation";

export default function Home() {
  // Redirect to signin page by default
  // Once auth is implemented, this will check auth state
  redirect("/signin");
}
