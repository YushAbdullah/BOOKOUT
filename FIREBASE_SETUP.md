# Switching on multiplayer (Firebase, free)

BOOKOUT plays solo until a Firebase project is connected. Setup takes about 5 minutes and stays on the free Spark plan.

1. Go to https://console.firebase.google.com, click **Create a project**, name it `bookout`, and skip Google Analytics.
2. **Build → Authentication → Get started.** Enable **Google** (choose your support email) and **Email/Password**.
3. **Authentication → Settings → Authorized domains → Add domain:** `yushabdullah.github.io`.
4. **Build → Realtime Database → Create database.** Pick the region closest to you (Singapore, `asia-southeast1`) and start in **locked mode**.
5. **Realtime Database → Rules:** paste the contents of `database.rules.json` from this repo and click **Publish**.
6. **Project settings (gear icon) → Your apps → Web (`</>`)**: register an app called `bookout`. Hosting is not needed. Copy the `firebaseConfig` object it shows.
7. Paste that object into `index.html` in place of `const FIREBASE_CONFIG = null;`, or send it to Claude to do.

The web config is not a secret. It is meant to be public, and access is controlled by the database rules.

## Admin

The admin page (More → Admin) appears for the email listed in `ADMIN_EMAILS` in `index.html`, and in the `users` read rule in `database.rules.json`. Sign in with that Google account. To add another admin, add their email in both places.

## Testing locally without Firebase

Open two tabs in the same browser:

- `index.html?mp=local&slot=a`
- `index.html?mp=local&slot=b`

Sign in with any email in each tab. The two players will see each other.
