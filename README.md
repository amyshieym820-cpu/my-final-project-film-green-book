# Film Green Book · Art Department Carbon Calculator

A browser-based carbon footprint calculator for film and theatre art departments to compare material sourcing, purchasing methods, and delivery routes.

## GitHub Pages Deployment

1. Create a new repository on GitHub (e.g., `film-green-book`).
2. Upload `index.html` (and optionally this `README.md`) to the root directory of the repository.
3. Go to **Settings → Pages**.
4. Under **Build and deployment → Source**, select **Deploy from a branch**.
5. Select the `main` branch and `/ (root)` folder, then click **Save**.
6. Your web app will be live at `https://<your-username>.github.io/<repo-name>/` within 1–2 minutes.

## Optional: Kakao Maps API Setup

- The app works out of the box using OpenStreetMap and Daum Postcode search.
- For more accurate Korean address search, obtain a **JavaScript Key** from [Kakao Developers](https://developers.kakao.com/), register your GitHub Pages URL (`https://<your-username>.github.io`) under **Platform → Web**, and either paste it in the app's **Address search settings** or set `const KAKAO_JS_KEY = 'YOUR_KEY';` inside `index.html`.
