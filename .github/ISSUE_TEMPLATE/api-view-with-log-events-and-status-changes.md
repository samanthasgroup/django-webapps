---
name: API View with log events and status changes
about: Issue template for creating an API View that includes creation of log events
  and status changes
title: 'API view: '
labels: API views, enhancement
assignees: Roxe322

---

When ____:

## Create/change objects
- 

## Create log events

Types of `LogEvent`s to be created:

- coordinator(s): `TYPE`
- group: `TYPE`
- students: `TYPE`
- teacher(s): `TYPE`

## Set statuses
- group: `WORKING`
- Its coordinators' statuses change depending on the number of groups each of them has:
  - if ...: `STATUS`
  - if ...: `STATUS`
- students: `STUDYING`
- teachers' statuses depend on...:
  - if... :  `STATUS`
  - else: `STATUS`

Remember to update `status_since` to current time in UTC in objects (where applicable).
