# 👥 User Journey


## 🛡️ User Roles & Access Control
- **Business User (Бизнес)** – Submit requests and track status.
- **Executor (Изпълнител)** – View and handle assigned requests, generate annexes.
- **Supervisor (Ръководител)** – Assign requests to executors, manage users, view all productivity data.
- **Director (admin)** – Full access to all data, users, logs, and configurations.

Access is managed via custom middleware and group-based permissions, enforced both in views and templates.

---

## 📄 Example Workflow
1. **Business User** creates an annex request for a specific contract.

2. **Manager** assigns the request to an **Executor**.

3. **Executor** completes specific fields and generates the annex.

4. All signed annexes go into the **Archive/ Register**, where they are filterable and exportable.

5. Annex is **sent to mock API for signing** – only once if successful.

6. **System Logs** track every action.

7. **Productivity Reports** summarize request/annex volume per executor.
