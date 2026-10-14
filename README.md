# SmartCampusDevOps – Smart Campus Complaint and Maintenance System

## 1. Project Overview

SmartCampusDevOps is a web-based campus complaint and maintenance management system developed to simplify the process of reporting, tracking, and resolving maintenance issues within a college campus.

Students and staff can report issues such as damaged classroom equipment, water leakage, electrical problems, and Wi-Fi connectivity failures. Administrators can view complaints and update their status.

This project integrates DevOps tools to automate application building, testing, containerization, and deployment.

## 2. Objectives

- To develop a centralized campus complaint management system.
- To simplify the reporting and tracking of maintenance issues.
- To manage complaint records using an SQLite database.
- To maintain source code and version history using Git and GitHub.
- To automate application build and testing using Jenkins.
- To package the application using Docker.
- To automate deployment using Ansible.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| Flask | Web application framework |
| HTML, CSS | User interface |
| JavaScript | Client-side interactions |
| SQLite | Database management |
| Git | Version control |
| GitHub | Source code hosting |
| Jenkins | CI/CD pipeline automation |
| Docker | Application containerization |
| Ansible | Deployment automation |
| WSL Ubuntu | Linux environment for Ansible |

## 4. System Features

- Submit campus maintenance complaints.
- View registered complaints.
- Search and filter complaint records.
- Track complaint status.
- Update complaint status.
- Store complaint details in a database.
- Build and package the application using Docker.
- Automate deployment through Ansible.
- Automate development and deployment workflows through Jenkins.

*Note: The features available in the running application depend on the implemented code.*

## 5. System Architecture

```text
        Developer
            |
            v
       Git / GitHub
            |
            v
          Jenkins
            |
            v
    Automated Testing
            |
            v
      Docker Image
            |
            v
          Ansible
            |
            v
   Docker Application
            |
            v
     Flask Web App
            |
            v
      SQLite Database
```

## 6. Project Structure

```text
SmartCampusDevOps/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
├── campus.db
│
├── ansible/
│   ├── inventory
│   └── deploy.yml
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── tests/
│   └── test_app.py
│
└── README.md
```

*The structure above is illustrative. Keep only the files and folders that exist in your repository.*

## 7. Installation and Execution

### Prerequisites

Install or configure the following:

- Python
- Git
- Docker Desktop
- Jenkins
- WSL 2 with Ubuntu
- Ansible in the configured Linux environment

### Step 1: Clone the Repository

```bash
git clone https://github.com/DEIVAPRIYA1001/SmartCampusDevOps.git
cd SmartCampusDevOps
```

### Step 2: Install Dependencies

On Windows Command Prompt:

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
python app.py
```

Open the application in your browser:

http://localhost:5000

### Step 4: Build the Docker Image

Make sure Docker Desktop is running.

```bash
docker build -t smart-campus .
```

### Step 5: Run the Docker Container

```bash
docker run -d --name smart-campus-app -p 5000:5000 smart-campus
```

Check running containers:

```bash
docker ps
```

View Docker images:

```bash
docker images
```

View application logs:

```bash
docker logs smart-campus-app
```

If the container name is already in use, remove the existing container before creating another one:

```bash
docker rm -f smart-campus-app
```

### Step 6: Deploy Using Ansible

Run the following command in Ubuntu WSL from the directory containing the Ansible files:

```bash
ansible-playbook -i inventory deploy.yml
```

A successful deployment should show a play recap with `failed=0`.

### Step 7: Execute the Jenkins Pipeline

1. Start Jenkins.
2. Open http://localhost:8080.
3. Open the SmartCampusDevOps job.
4. Click **Build Now**.
5. Open the latest build's **Console Output**.
6. Verify that the configured pipeline stages complete successfully.

## 8. Database

The application uses SQLite to store campus complaint information.

The database file is:

```text
campus.db
```

Depending on the database schema, complaint records can contain fields such as:

- Complaint ID
- Requester name
- Requester email
- Complaint title
- Category
- Priority
- Location
- Description
- Status
- Created date

Example SQL query:

```sql
SELECT * FROM complaints;
```

## 9. DevOps Workflow

1. The developer creates or modifies the application code.
2. Git tracks the source code changes.
3. GitHub hosts the project repository.
4. Jenkins executes the configured pipeline.
5. Automated tests check application behavior.
6. Docker builds an image containing the application.
7. Ansible automates the configured deployment tasks.
8. The application runs in a Docker container.
9. SQLite stores the application data.

## 10. Testing and Verification

The following checks can be used to verify the project:

- Run the application and open it in a browser.
- Submit a complaint and verify the displayed record.
- Execute automated tests through Jenkins.
- Run `docker images` to verify the image.
- Run `docker ps` to verify the running container.
- Execute the Ansible playbook and inspect its final recap.
- Inspect the SQLite database to verify stored records.

## 11. Advantages

- Reduces manual deployment effort.
- Provides centralized complaint management.
- Supports version tracking and collaboration.
- Improves consistency through containerization.
- Automates repetitive deployment tasks.
- Makes application testing and maintenance easier.

## 12. Future Enhancements

- User authentication and role-based access control.
- Email or SMS notifications for complaint updates.
- Complaint priority and deadline management.
- Dashboard analytics and complaint reports.
- Automated security scanning in the CI/CD pipeline.
- Cloud deployment and monitoring.
- Database backup and recovery.

## 13. Conclusion

SmartCampusDevOps demonstrates how a campus complaint management application can be integrated with DevOps practices. Git and GitHub support version control, Jenkins automates the configured CI/CD workflow, Docker packages the application, Ansible automates deployment, and SQLite stores application records.

The project provides practical experience in application development, testing, containerization, and deployment automation.

## Author

**Project:** SmartCampusDevOps – Smart Campus Complaint and Maintenance System

**Repository:** https://github.com/DEIVAPRIYA1001/SmartCampusDevOps
