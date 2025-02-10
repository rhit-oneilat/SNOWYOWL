### **Current State of SNOWYOWL**  
The **SNOWYOWL** system is a **multi-user guest management and check-in application** designed for fraternity events. It currently runs on **Streamlit Community Cloud**, using **SQLite** for persistent storage and a **2-second polling mechanism** for real-time updates.  

#### **Core Features (Working)**
1. **Guest List Management**:  
   - Supports CSV uploads for guest lists.  
   - Stores guests in an SQLite database with attributes like host, class year, gender, and check-in status.  

2. **Check-In System**:  
   - Provides a real-time interface for checking guests in/out.  
   - Features **fuzzy name search** and **filters** (check-in status, location).  

3. **Dashboard & Analytics**:  
   - Displays live statistics on guest distribution (by brother, gender ratio, class breakdown, campus status).  

4. **Multi-User Support**:  
   - The system is designed to handle **at least 3 simultaneous check-in staff** with **live updates**.  
   - Uses a **polling mechanism** (refreshing every 2 seconds) for real-time sync across devices.  

5. **Authentication**:  
   - A **simple password-based login** restricts access.  

6. **Memory Optimization**:  
   - The app currently uses **~194 MB of memory**, which remains manageable within Streamlit’s 1 GB limit.  

---


### **Planned Improvements & Enhancements**

#### **Immediate Fixes & Optimizations (Next Deployment)**

- **Optimize Polling for Efficiency**: Implement **adaptive polling**, reducing frequency when fewer users are online to minimize redundant queries.
- **Enhance SQLite Performance & Stability**:
    - Move database storage to `/mount/` for persistent access.
    - Use **streaming queries** to load only necessary data rather than keeping entire guest lists in memory.
    - Implement **`st.cache_data(ttl=30)`** to reduce redundant database queries.
    - Ensure proper write-locking mechanisms to support simultaneous updates without conflicts.
- **Improve Search Functionality**: Fix current case-sensitivity issue (currently only works with all-caps queries).
- **Refine Check-In Page UI**: Enhance usability for faster guest processing.
- **Ensure Guest List Updates Work Seamlessly**: Resolve any CSV upload issues to maintain data integrity.

---

#### **Mid-Term Improvements (Post-MVP Enhancements)**
- **Migrate to Supabase (PostgreSQL)** for better scalability and **real-time updates without polling**.  
- **Transition Frontend to Next.js** for a more user-friendly, scalable interface.  
- **Move Brother Data to the Database** for dynamic updates rather than relying on CSVs.  
- **Enhance Authentication** with Google Sign-In or fraternity-specific logins.  
- **Investigate Progressive Web App (PWA) or Mobile App Support** for easier check-ins via QR codes.  
 

---




