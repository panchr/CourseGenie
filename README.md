# CourseGenie

## Team Information
### Project Leader
Kathy Fan (zyfan@princeton.edu) - Backend

### Team Members
- Rushy Panchal (rpanchal@princeton.edu) - Frontend, Infrastructure
- Fiona Maciontosh (fgm@princeton.edu) - Frontend, UI Design
- Anya Hargil (ahargil@princeton.edu) - Backend, API
- Simisola Olofinboba (simisola@princeton.edu) – Backend

### Project Manager
Christopher Moretti

## Design Document
Our design document is located [here](https://docs.google.com/a/princeton.edu/document/d/1KuW7e6nxcN4gpxhSCqNdtfDCPzYpbqxFUk7qM4q_pas/edit?usp=sharing).

## Timeline
#### Initial Planning. 3/19/17
- *Backend Team.* Plan data format for data collection.
- *Frontend Team.* Make final draft of user interface.

#### Preliminary Steps. 3/26/17 (Over Spring Break)
- Formulate elevator pitch.
- Enter data about majors (BSE only, 6) and certificates (all, 53).
- Git Tutorial.
- *Backend Team.*
	* Django Tutorial, transcript parser and CAS integration.
	* Plan database schema for major/certificate requirements and user profile.
- *Frontend Team.*
	* Create welcome/about/FAQ/contact pages
	* React Tutorial

#### Preliminary Feature: Transcript Upload & Data Storage. 3/30/17
- Determine API endpoints and how frontend interacts with backend.
- *Backend Team.*
	* Encode major/certifcate requirements into Django models.
	* Come up with data models to store transcript information taken from Django
	file uploads and store information for each student account.
- *Frontend Team.*
	* Design page for uploading transcript/entering student information

#### Primary Feature: basic course recommendations according to major requirements. 4/6/17
- *Backend Team.*
	* Determine and implement algorithm for recommend courses from major requirements and student's past courses.
	* Determine how to show/represent student's satisfied requirements.
	* Ensure feature can be tested independently of frontend progress.
- *Frontend Team.*
	* Design user's home page: semester-view scroll-through calendar and suggestions section.

#### Primary Feature: basic course recommendations based on certificate requirements. 4/12/17
- *Backend Team.*
	* Adapt algorithm to include certificate requirements.
- *Frontend Team.*
	* Continue with design of user's home page.
	* Requirements and sandbox tabs
	* Ability to add new schedules
	* Magic lamp and corresponding options

#### Secondary Features (3). 4/19/17
- *Backend Team.* Adapt algorithm to allow filtering of courses user explicitly
	wants to ignore, give higher weight to courses user explicitly wants to take,
	and support multiple majors/saving multiple calendars.
- *Frontend Team.* Refine visual appearance and styling of website. Add more
	comprehensive tutorial to welcome site and link to homepage.

#### Secondary Features (2). 4/26/17
- Support for other components of degree (B.S.E. core requirements, humanities requirements)
- Integrate feedback from Alpha tests

#### Secondary Features (1). 5/7/17
- "I'm feeling lucky"
- Integrate feedback from Beta tests

#### Submission. 5/14/17

## Elevator Pitch
Not fully completed.
