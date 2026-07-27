# RetainIQ — Project Handoff Guide (Teammate)

Prepared for the presenting team member. Covers project purpose, current
capabilities, deliberate omissions, and what remains for future weeks.

---

## 1. What RetainIQ Is

RetainIQ is a decision support web application built for a University of the
People MSIT capstone project. It helps lecturers identify students who are at
risk of dropping out, based on early term engagement and performance data
such as attendance, assignment submission timing, and grades.

The core idea is that a lecturer logs in and sees a ranked list of their
students, color coded by risk level. Clicking into a flagged student would
eventually reveal why they were flagged, so the lecturer, not the system,
makes the final decision on whether to intervene. This is an important
design principle: the system is explicitly a decision support tool, not an
autonomous one. It surfaces information. It does not take action on its own.

Target users are university lecturers and instructors who want an early
warning signal for struggling students, without needing to manually track
spreadsheets of attendance and grades themselves.

---

## 2. Where the Project Stands Right Now

The project has gone through three stages so far. It is currently in the
third stage.

### Stage 1: Architecture and Design (Complete)

A full System Architecture Blueprint was written before any code existed. It
defines nine cooperating modules, twelve functional requirements, six non
functional requirement categories including a fairness and ethics
requirement, and documented reasoning for each major technology choice.

The nine modules are:

- Data Ingestion Module, a Python ETL process scheduled to run periodically
- Feature Engineering Module, which turns raw records into signals such as
  an attendance proxy, submission lateness pattern, and grade trajectory
- Model Training Module, a Logistic Regression baseline plus a stronger
  Random Forest or XGBoost model
- Model Inference Module, which scores each student and assigns a risk tier
- Authentication Module, JWT based login with bcrypt password hashing
- Risk List and Student Detail API Module, the FastAPI routes that serve
  data to the frontend
- Scheduler and Automation Module, which triggers ETL and re scoring on a
  recurring basis
- Lecturer Dashboard Module, the React frontend
- Engineering and DevOps Module, testing, CI, and deployment

Why this matters for the presenter: every piece of code built so far exists
because this document said it should. If asked why a decision was made a
certain way, the honest answer is almost always: it follows the architecture
blueprint that was written and approved before implementation began.

### Stage 2: Repository Scaffolding (Complete)

The GitHub repository was structured to mirror the nine modules, using a two
branch model. The main branch is reserved for stable, milestone ready states.
The development branch is where in progress work happens. Feature branches
are created off development for individual pieces of work, then merged back
through a pull request.

This branching approach was documented in a standalone version control
overview as part of satisfying the project's maintainability and traceability
requirement.

### Stage 3: Barebones MVP, Current Week (In Progress)

This week's task was to move from design into a first working version,
focused narrowly on two things: the API layer and the UI layer. Everything
else was deliberately deferred. The next two sections explain exactly what
was built, and just as importantly, what was left out and why.

---

## 3. What Has Been Built

### Backend: Mock Risk List API

A single FastAPI application was written containing one endpoint,
`GET /api/risk-list`. Instead of querying a real database or running a real
machine learning model, this endpoint returns hardcoded JSON data
representing five fake students, each with a name, a risk level of High,
Medium, or Low, and an engagement score.

Why this approach: It proves the API layer works end to end, meaning the
backend can serve structured data over HTTP in the exact shape the frontend
expects, without requiring the database or the model to exist yet. This
isolates and de-risks the frontend and backend integration before the harder
data and modeling work begins.

This directly corresponds to the Risk List and Student Detail API Module in
the architecture blueprint, though only the list portion, not yet the
individual student detail portion.

### Frontend: Lecturer Dashboard

A React application was built using Vite. It contains a single component,
the Lecturer Dashboard, which fetches data from the mock API endpoint and
renders it as a table with three columns: Name, Risk Level, and Engagement
Score.

On top of the basic table, the following presentation features were added:

- Rows are color coded by risk level. High risk rows use a red tint, Medium
  uses yellow, Low uses green, so a lecturer can visually scan urgency at a
  glance
- Students are sorted High risk first by default, since the entire purpose
  of the dashboard is to surface the most urgent cases first
- Clicking the Risk Level column header toggles the sort direction between
  High to Low and Low to High
- Hovering over a row slightly deepens its background tint, giving the table
  a more interactive, polished feel
- A loading state is shown briefly while data is being fetched, simulating
  what a real network request would feel like
- Rows fade in gently when the table first renders, rather than appearing
  instantly
- The browser tab title was set to RetainIQ instead of the default Vite
  placeholder

Why this approach: This fulfills the UI layout requirement from the
assignment and demonstrates the Lecturer Dashboard Module from the
architecture. The sorting and hover behavior are not just cosmetic. They
reflect the actual design intent of the module, which is to help a lecturer
quickly identify who needs attention first.

---

## 4. What Was Deliberately Left Out, and Why

Every omission below was a conscious scoping decision, not an oversight.
Building any of these now would either misrepresent how far the project has
actually progressed, or would consume time that belongs to a later week in
the capstone schedule.

| Left out | Why it was left out |
|---|---|
| Real database (PostgreSQL) | No student data is being stored or queried yet. All data is hardcoded directly in the API response. Setting up a real database now would front load work from a later capstone week without a data pipeline in place to actually populate it. |
| Machine learning model | Risk levels are hand assigned in the mock data, not predicted. Training a real model requires clean engineered features, which requires the ingestion and feature engineering modules, neither of which exist yet. |
| Data ingestion and ETL pipeline | There is no real attendance, submission, or grade data being pulled from anywhere. This depends on data sources and infrastructure not yet built. |
| Authentication and login | The architecture blueprint defines this as its own module with its own security requirements, JWT issuing, and password hashing. Building a fake or partial login now would either be non functional and misleading in a demo, or would require doing a later week's work early, leaving nothing left to build when that week arrives. |
| Multiple pages or tabs | The current scope is one dashboard view. Adding tabs implies additional views that do not yet exist behind them. |
| Student detail drill down | Clicking a flagged student to see why they were flagged is part of the design, but it depends on explanation data that does not exist until the model and feature engineering modules are built. |

The guiding principle behind all of these decisions: build only what can be
honestly demonstrated as real and working, and defer anything that would need
to be faked or rebuilt later.

---

## 5. What Remains, In Rough Order

The order below follows the dependency chain in the architecture. Later
modules generally depend on earlier ones being in place first.

### Near term: data and model foundation

- **Data Ingestion Module:** real Python ETL that loads attendance,
  submission, and grade records into PostgreSQL
- **Feature Engineering Module:** turning raw records into the attendance
  proxy, submission lateness pattern, and grade trajectory features
- **Model Training Module:** training and validating the Logistic Regression
  baseline and the stronger Random Forest or XGBoost model, including proper
  evaluation metrics

### Mid term: serving layer

- **Model Inference Module:** loading the trained model to generate real per
  student risk scores, plus explanations for why a student was flagged
- **Authentication Module:** real JWT login and protected routes
- **Risk List and Student Detail API Module:** replacing the hardcoded mock
  data with real database backed responses, and adding the student detail
  endpoint

### Later stages: frontend and automation

- **Full Lecturer Dashboard:** login screen, real data instead of mock data,
  student drill down view, and cohort level charts
- **Scheduler and Automation Module:** automatic recurring ETL and re
  scoring runs

### Ongoing throughout

- **Engineering and DevOps Module:** real automated test suites, GitHub
  Actions CI running on every push, Docker Compose so all services run
  together consistently, and eventual deployment

---

## 6. Version Control Notes

The repository uses a two branch model. Main is reserved for stable, demo
ready milestones. Development holds in progress work. This week's work was
built on a feature branch created off development, then merged back through a
pull request rather than committed directly.

If the presenter needs to check what changed and why at any point, the pull
request history and commit messages on GitHub are the source of truth. Commit
messages follow a consistent pattern describing what was added and which
module it corresponds to, so the history itself is a useful reference, not
just a formality.

---

## 7. Key Talking Points for the Presentation

If explaining this project out loud, these are the points most worth making
clearly:

- The system is a decision support tool for lecturers, not an automated
  decision maker. The lecturer always makes the final call.
- Design and architecture were fully completed and documented before any
  code was written.
- This week's build deliberately isolates the API and UI layers to prove
  they work together, while the database, model, and pipeline are
  intentionally mocked.
- Every omission is a scoping decision tied to the capstone's weekly
  structure, not a gap in understanding of what the finished system needs.
- The sort-by-risk and color coding in the dashboard are not just visual
  polish. They reflect the actual purpose of the module, which is to help a
  lecturer see who needs attention first.
