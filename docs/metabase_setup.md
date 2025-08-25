# Metabase Setup

1. Add the following variables to `backend/.env`:

   ```
   MB_SITE_URL=http://localhost:3000
   MB_ENCRYPTION_SECRET=change_me
   ```

2. Start the services:

   ```
   cd backend
   docker compose up
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser to complete Metabase's initial setup.

4. When prompted to add your database, use these values:

   - **Database type:** Postgres
   - **Host:** db
   - **Port:** 5432
   - **Database name:** mega_x
   - **Username:** postgres
   - **Password:** password

