
import { useEffect, useState } from "react";
import Auth from "./Auth";
import ContribMateApp from "./ContribMateApp";

function App() {
  const [user, setUser] = useState(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    async function checkSession() {
      try {
        const response = await fetch("/api/auth/me", {
          credentials: "include",
        });

        if (response.ok) {
          const data = await response.json();
          setUser(data.user);
        }
      } catch (error) {
        console.error("Session check failed:", error);
      } finally {
        setCheckingAuth(false);
      }
    }

    checkSession();
  }, []);

  async function handleLogout() {
    try {
      const response = await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Logout failed.");
      }

      setUser(null);
    } catch {
      alert("Unable to log out. Please try again.");
    }
  }

  if (checkingAuth) {
    return <p style={{ textAlign: "center", padding: 40 }}>
      Checking login...
    </p>;
  }

  if (!user) {
    return <Auth onLogin={setUser} />;
  }

  return (
    <>
      <div style={{
        display: "flex",
        justifyContent: "flex-end",
        alignItems: "center",
        gap: 12,
        padding: "12px 24px",
      }}>
        <span>Welcome, {user.name}</span>
        <button type="button" onClick={handleLogout}>
          Logout
        </button>
      </div>

      <ContribMateApp />
    </>
  );
}

export default App;
