### **Current State of SNOWYOWL**  
The **SNOWYOWL** system is a **multi-user guest management and check-in application** designed for fraternity events. It currently runs on **Streamlit Community Cloud**, using **Supabase (PostgreSQL)** for persistent storage. Smooth check-in and check-out updates are now a priority, as the previous **2-second polling mechanism** caused inefficiencies.  
---
#### **Core Features (Working)**  
1. **Guest List Management**:  
   - Supports CSV uploads for guest lists.  
   - Stores guests in Supabase with attributes like host, class year, gender, and check-in status.  

2. **Check-In System**:  
   - Provides a real-time interface for checking guests in/out.  
   - Features **fuzzy name search** and **filters** (check-in status, location).  
   - Ensures **smooth status updates** without lag or refresh delays.  

3. **Dashboard & Analytics**:  
   - Displays live statistics on guest distribution (by brother, gender ratio, class breakdown, campus status).  

4. **Multi-User Support**:  
   - The system is designed to handle **at least 3 simultaneous check-in staff** with **real-time updates**.  
   - Moving away from **polling** to a more efficient **real-time subscription model** for smooth synchronization across devices.  

5. **Authentication**:  
   - A **simple password-based login** restricts access.  

6. **Memory Optimization**:  
   - The app currently uses **~194 MB of memory**, which remains manageable within Streamlit’s 1 GB limit.  

---

### **Planned Improvements & Enhancements**  

#### **Immediate Fixes & Optimizations (Next Deployment)**  

- **Implement Real-Time Updates via Supabase**: Replace inefficient polling with **Supabase's real-time subscriptions**, ensuring instant synchronization across all devices.  
- **Enhance Supabase Query Performance**:  
    - Optimize indexing for fast lookups.  
    - Use **incremental updates** instead of full table refreshes.  
- **Improve Search Functionality**: Fix case-sensitivity issues and enhance search speed.  
- **Refine Check-In Page UI**: Enhance usability for faster guest processing.  
- **Ensure Guest List Updates Work Seamlessly**: Resolve any CSV upload issues to maintain data integrity.  

---

#### **Mid-Term Improvements (Post-MVP Enhancements)**  
- **Transition Frontend to Next.js** for a more user-friendly, scalable interface.  
- **Move Brother Data to the Database** for dynamic updates rather than relying on CSVs.  
- **Enhance Authentication** with Google Sign-In or fraternity-specific logins.  
- **Investigate Progressive Web App (PWA) or Mobile App Support** for easier check-ins via QR codes.  

