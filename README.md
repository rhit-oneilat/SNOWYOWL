## **Current State**
This is a **party management and guest tracking system** designed to streamline check-in, attendance monitoring, and statistical analysis of fraternity events. It uses **SQLite** for persistent data storage and **Streamlit** for an interactive dashboard.

1. **Guest List Management**: CSV files containing guest names (split into on-campus and off-campus) are loaded into an SQLite database. Each guest is associated with a brother (host) and additional attributes like class year, gender, and check-in status.
2. **Check-In System**: A real-time interface allows guests to be checked in or out. Their status updates in the database when a button is clicked.
3. **Dashboard & Analytics**: A separate tab displays real-time statistics and visualizations, including guest distribution by brother, gender ratio, class breakdown, and campus status.
4. **Persistent Storage**: All data is stored in **SQLite**, ensuring that information is retained even after the app is restarted.

- **Core functionality is working**: Guests can be checked in and out, and their statuses update correctly in the database.

## Planned Changes & Improvements

### MVP (Immediate Priorities for Deployment at Next Party)

1. **Deploy to Streamlit Cloud** to provide a public URL for check-in staff.
2. Fix search, issue with case right now (all caps search queries work, nothing else does)
3. Improve check in page UI
4. Ensure guest list updates function properly
5. Fix gender ratio and off campus ratio in logic.py

### Global Improvements (Post-MVP Enhancements)

- **Redesign Guest Management**: Investigate alternative ways to list and manage guests directly within the system while maintaining CSV upload functionality as a fallback. Ideally, guest entry should be fully handled through the app rather than relying on external CSVs.
- **Expand Database Operations**: Implement robust database operations to manage guests and brothers dynamically, allowing for listing, modifying, and deleting entries within the app.
- **Migrate Brothers List to Database**: Store fraternity brother information directly in SQLite instead of a CSV file, enabling real-time updates and reducing reliance on manual file handling.

### Long-Term Goals (Scaling & SaaS Development)

6. **Migrate to Supabase (PostgreSQL) as the backend** for better scalability and real-time updates.
7. **Transition frontend from Streamlit to Next.js** for a more scalable, user-friendly web app.
8. **Implement real-time multi-user functionality** using Supabase subscriptions instead of polling.
9. **Redesign guest management** to allow direct in-app guest entry rather than relying on CSVs.
10. **Enhance authentication with Google Sign-In or fraternity-specific logins.**
11. **Explore Progressive Web App (PWA) or native mobile app development** for features like QR code check-ins.
12. **Investigate monetization strategies**, including insurance partnerships and subscription models.



