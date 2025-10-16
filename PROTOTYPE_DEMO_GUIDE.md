# 🎯 EdPrep AI Mentorship Platform - Prototype Demo Guide

## 🚀 **Complete Step-by-Step Demo Script**

This guide will walk you through demonstrating the mentorship social platform as a complete prototype.

---

## 📋 **Pre-Demo Setup**

### **1. Access the Application**
- **Frontend**: http://localhost:3000 (or 3001/3002 if ports are busy)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### **2. Available Test Accounts**

| Role | Username | Email | Password | Specialization |
|------|----------|-------|----------|----------------|
| **Student** | admin1 | admin1@edprep.ai | admin123 | - |
| **Mentor** | admin2 | admin2@edprep.ai | admin123 | Writing Task 2, Speaking |
| **Tutor** | admin3 | admin3@edprep.ai | admin123 | Reading, Listening |
| **Mentor** | admin4 | admin4@edprep.ai | admin123 | All Skills, Band 7+ |
| **Tutor** | admin5 | admin5@edprep.ai | admin123 | Writing, Speaking, Grammar |

---

## 🎬 **Demo Script: Complete Mentor-Mentee Flow**

### **Step 1: Student Perspective - Finding Mentors**

1. **Login as Student**
   - Go to http://localhost:3000
   - Click "Sign In"
   - Use: `admin1@edprep.ai` / `admin123`
   - You'll be redirected to the dashboard

2. **Navigate to Mentorship**
   - Click "Mentorship" in the header navigation
   - Or click the "Mentorship" quick action card on dashboard

3. **Browse Available Mentors**
   - You'll see 4 available mentors/tutors
   - Each has detailed profiles with:
     - Bio and teaching experience
     - Specializations (Writing, Speaking, Reading, etc.)
     - Certifications
     - Availability (days and hours)
     - Timezone information

4. **Filter Mentors** (Optional)
   - Use the search filters:
     - Specializations: "Writing Task 2"
     - Target Band Score: 7.5
     - Timezone: "UTC+8"

### **Step 2: Student Perspective - Requesting Mentorship**

1. **Select a Mentor**
   - Click on "admin2" (Writing Task 2 specialist)
   - Review their detailed profile

2. **Send Connection Request**
   - Fill in the connection request form:
     - **Message**: "Hi! I'm preparing for IELTS and need help with Writing Task 2. I'm aiming for band 7.5."
     - **Goals**: "Improve essay structure, develop arguments, enhance vocabulary"
     - **Target Band Score**: 7.5
     - **Focus Areas**: "Writing Task 2, Academic Writing"
   - Click "Send Connection Request"

3. **View Your Connections**
   - Switch to "My Connections" tab
   - You'll see the pending request with status "pending"

### **Step 3: Mentor Perspective - Managing Requests**

1. **Login as Mentor**
   - Open a new browser tab/incognito window
   - Go to http://localhost:3000
   - Login with: `admin2@edprep.ai` / `admin123`

2. **Check Connection Requests**
   - Navigate to Mentorship
   - **Note**: As a mentor, you'll automatically see "My Mentees" tab (not "Find Mentors")
   - You'll see the pending request from admin1
   - Review the mentee's message and goals

3. **Accept the Request**
   - Click "Accept" on the connection request
   - Add a response message: "Hello! I'd be happy to help you with Writing Task 2. Let's schedule our first session."

4. **View Active Connection**
   - The status changes to "active"
   - You can now see the connection details

### **Step 4: Communication - Messaging System**

1. **From Student Side**
   - Go back to admin1's browser tab
   - In "My Connections", click "View Details" on the active connection
   - Send a message: "Thank you for accepting! When would be a good time for our first session?"

2. **From Mentor Side**
   - Go back to admin2's browser tab
   - In "My Connections", click "View Details"
   - Reply: "How about this Friday at 2 PM UTC+8? We can start with a diagnostic essay."

### **Step 5: Session Management**

1. **Schedule a Session (Mentor)**
   - In the connection details, scroll to "Scheduled Sessions"
   - Click "Schedule New Session"
   - Fill in:
     - **Title**: "Writing Task 2 Diagnostic Session"
     - **Description**: "Initial assessment and goal setting"
     - **Session Type**: "general"
     - **Scheduled At**: Choose a future date/time
     - **Duration**: 60 minutes
     - **Agenda**: "1. Diagnostic essay, 2. Feedback discussion, 3. Study plan creation"
   - Click "Create Session"

2. **View Scheduled Session (Student)**
   - Go back to admin1's browser tab
   - In connection details, you'll see the scheduled session
   - The session appears in "Scheduled Sessions" section

### **Step 6: Profile Management**

1. **Update Mentor Profile**
   - As admin2, go to "My Profile" tab
   - Update bio: "Now accepting new mentees for Writing Task 2 preparation!"
   - Change availability: Add "Sunday" to available days
   - Click "Update Profile"

2. **View Updated Profile**
   - As admin1, refresh the mentors list
   - You'll see the updated profile information

### **Step 7: Multiple Connections Demo**

1. **Request Another Mentor**
   - As admin1, go to "Find Mentors"
   - Send a request to admin3 (Reading specialist)
   - Message: "I also need help with Reading strategies for band 7+"

2. **Manage Multiple Connections**
   - As admin3, login and accept the request
   - Now admin1 has 2 active mentorship connections
   - Each can be managed independently

### **Step 8: Rating and Feedback**

1. **Complete a Session**
   - As admin2, go to the session details
   - Click "Complete Session"
   - Add notes: "Great progress on essay structure. Next focus: argument development."
   - Rate the session: 4.5/5

2. **Rate the Mentorship**
   - As admin1, in connection details
   - Click "Rate Mentorship"
   - Give rating: 5/5
   - Add feedback: "Excellent feedback and very helpful strategies!"

---

## 🎯 **Key Features to Highlight**

### **🔍 Smart Matching System**
- Mentors are filtered by specializations, availability, and experience
- Students can find mentors matching their specific needs
- **Role-based Interface**: Students see "Find Mentors", Mentors see "My Mentees"

### **💬 Real-time Communication**
- Built-in messaging system for mentor-mentee communication
- File sharing capabilities for essays and feedback

### **📅 Session Management**
- Schedule and manage mentorship sessions
- Track session history and progress notes

### **⭐ Rating & Review System**
- Rate mentorship experiences
- Build mentor reputation and credibility

### **👥 Multi-User Support**
- Handle multiple mentorship relationships
- Different user roles (student, mentor, tutor, admin)

### **📊 Progress Tracking**
- Track mentorship progress and goals
- Monitor session completion and feedback

---

## 🚀 **Advanced Demo Scenarios**

### **Scenario 1: Group Mentorship**
- Show how a mentor can handle multiple mentees
- Demonstrate session scheduling for different students

### **Scenario 2: Specialized Tutoring**
- Use admin3 (Reading specialist) to show subject-specific mentoring
- Highlight different teaching approaches

### **Scenario 3: Admin Management**
- Login as admin1 and show the platform from an admin perspective
- Demonstrate user management capabilities

---

## 🎉 **Demo Conclusion Points**

1. **Complete Social Platform**: "This is a fully functional mentor-mentee social platform integrated with our IELTS preparation system."

2. **Real User Interactions**: "Students can find, connect with, and learn from real mentors and tutors."

3. **Professional Features**: "Includes session scheduling, messaging, rating systems, and progress tracking."

4. **Scalable Architecture**: "Built to handle multiple users, connections, and mentorship relationships."

5. **Production Ready**: "All features are working with real database storage and API endpoints."

---

## 🔧 **Troubleshooting**

### **If mentors don't show up:**
```bash
cd /Users/shan/Desktop/Work/Projects/EdPrep\ AI/ielts-master-platform/backend
python setup_mentor_profiles.py
```

### **If API errors occur:**
- Check backend is running: http://localhost:8000/health
- Check API docs: http://localhost:8000/docs

### **If frontend issues:**
- Check frontend is running: http://localhost:3000
- Try different ports: 3001, 3002

---

## 📱 **Mobile Responsiveness**

The platform is fully responsive and works on:
- Desktop browsers
- Tablet devices
- Mobile phones

Test the mobile experience by resizing your browser window or using browser dev tools.

---

**🎯 This prototype demonstrates a complete, production-ready mentorship social platform that can be presented to investors, users, or stakeholders as a fully functional system!**
