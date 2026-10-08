# MovieBookingSystem
Production-grade movie ticket booking system with role-based access (User, Theatre Admin, Root Admin), city-wise movie and theatre discovery, show scheduling, NumPy-backed seat grid with locking, simulated payments, e-tickets and revenue dashboards. Built with FastAPI, Streamlit and SQL.

# 🎬 Movie Ticket Booking System

A production-grade movie ticket booking platform where users can discover movies by city, pick a theatre and show, choose seats from a visual grid, pay, and download their tickets. Theatre admins run their own theatres and schedules, while a root admin governs cities, theatres and the movie catalog.

**Project 4 · Group G4 · Domain: Entertainment**

---

## ✨ Features

### For Users
- **Signup and Login** with email and password, JWT-based sessions, account lockout after repeated failed attempts, and 30-minute inactivity timeout
- **City selection**, with the last chosen city remembered
- **Movie browsing** with search and filters (genre, language, format, rating)
- **Theatre and show selection** for the chosen movie and city
- **Visual seat grid** with seat categories, seat locking and lock expiry to prevent double booking
- **Simulated payment** that confirms and reserves seats
- **E-ticket download** in multiple formats
- **Booking history** with full booking details

### For Theatre Admins
- Manage their own theatre details, screens and seat layouts
- Schedule, edit and cancel shows, with conflict detection and refund handling
- Set pricing per seat category
- Block seats for maintenance or reserved use
- View bookings, live occupancy and a cancellation impact preview
- **Dashboard** with revenue trends, occupancy, top movies and peak hours

### For Root Admins
- Add, edit and deactivate cities
- Approve, reject, add and remove theatres, and assign theatre admins
- Manage the movie, genre and language catalog
- Block and unblock users
- Platform-wide dashboard and read-only audit log

---

## 🧱 Modules

| Module | Description |
|---|---|
| Authentication and Role Management | JWT auth with User, Theatre Admin and Root Admin roles (built by the whole team) |
| Catalog Management | CRUD for Movies, Genres, Theatres and Screens, with NumPy-backed seat layouts |
| Show Scheduling | Showtimes, overlap checks, pricing, cancellations |
| Seat Booking Workflow | Booking state machine, seat locking, NumPy boolean seat grid per show |
| Payment and E-Ticket | Payment simulation and ticket generation |
| Reporting and Dashboard | Occupancy, revenue and trend analytics |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | Streamlit |
| Database | SQL |
| Seat engine | NumPy |
| Analytics | matplotlib |
| Auth | JWT |





## 👥 Team (Group G4)

| Member | Module |
|---|---|
| Surabhi Nare | Catalog Management (Movies, Genres, Theatres, Screens) |
| Pranav Marekar | Show and Showtime Scheduling |
| Nischay Sharma | Seat Booking Workflow |
| Yashraj Singh Thakur | Payment Simulation and E-Ticket Generation |
| Shashwat Irali | Reporting and Dashboard |

---


This project was built for academic purposes.
