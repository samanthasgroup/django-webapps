# Архитектура статусов и автоматизация

## Домены статусов

### Project-статусы

**Группа** (`GroupProjectStatus`)

- pending (Набирается)
- awaiting_start (Собрана, ожидается начало)
- working (Занимается)
- aborted (Занималась < 4 мес.)
- finished (Завершила занятия)

**Учитель** (`TeacherProjectStatus`)

- no_group_yet (Не преподает, ждет группу)
- working (Преподает)
- on_leave, left_prematurely, finished_left, finished_stays, banned, removed

**Ученик** (`StudentProjectStatus`)

- needs_interview_to_determine_level
- no_group_yet (Ждет группу)
- study (Учится в группе)
- on_leave, left_prematurely, finished, banned

**Координатор** (`CoordinatorProjectStatus`)

- pending
- working_below_threshold / working_ok / working_limit_reached
- on_leave, left_prematurely, finished_stays, finished_left, removed, banned

### Situational-статусы

**Группа** (`GroupSituationalStatus`)

- attention
- holiday

**Учитель** (`TeacherSituationalStatus`)

- group_offered
- awaiting_start
- holiday (новый)
- needs_substitution
- no_response

**Ученик** (`StudentSituationalStatus`)

- group_offered
- awaiting_start
- holiday (новый)
- not_attending
- needs_transfer
- no_response

**Координатор** (`CoordinatorSituationalStatus`)

- onboarding
- onboarding_stale
- no_response

## Где и как выставляются статусы

### Основной поток (процессоры групп)

- Create (PENDING):
  - Группа -> project = pending
  - Учитель: situational пересчитывается (обычно group_offered)
  - Ученик: group_offered выставляется вручную, автоматом не ставится
  - Координатор: пересчет active-групп

- Confirm ready to start (AWAITING_START):
  - Группа -> project = awaiting_start
  - Учитель/Ученик: situational = awaiting_start (по пересчету)
  - Координатор: пересчет active-групп

- Start (WORKING):
  - Группа -> project = working
  - Учитель -> project = working
  - Ученик -> project = study
  - situational пересчитывается (обычно очищается)
  - Координатор: пересчет active-групп

- Finish (FINISHED):
  - Группа -> project = finished
  - Учитель/Ученик: project пересчитывается по наличию других групп
  - situational пересчитывается
  - Координатор: пересчет active-групп

- Abort (ABORTED):
  - Группа -> project = aborted
  - Учитель/Ученик: project пересчитывается по наличию других групп
  - situational пересчитывается
  - Координатор: пересчет active-групп

- Discard (удаление группы):
  - Перед удалением фиксируется список учителей/учеников/координаторов
  - После удаления: пересчет coordinators + пересчет situational для affected людей

### Редактирование группы в админке

- При сохранении группы или изменении M2M (учителя/студенты/координаторы):
  - Пересчет статусов координаторов
  - Пересчет situational у учителей/учеников группы

## Вариант A: автоматизация на основе групп

### Active group (для координатора)

Активной считается группа со статусом:

- pending / awaiting_start / working / holiday

### Логика project-статусов для учителя/ученика

- Если есть хотя бы одна working-группа -> project = working / study.
- Иначе project-статусы не меняются автоматически (только вручную).

### Логика situational-статусов (учитель/ученик)

Пересчет по всем связанным группам. Приоритеты:

1) needs_substitution / needs_transfer
2) no_response / not_attending
3) holiday
4) awaiting_start
5) group_offered (только для учителя автоматически)
6) пусто

Правило для ученика:

- group_offered выставляется вручную и сохраняется. Автоустановка не применяется.

## Краткая привязка к бизнес-сценариям

[Группа: Набирается]

- Учитель: situational = group_offered
- Ученик: situational = group_offered (вручную)
- Координатор: активная группа

[Группа: Собрана, ожидается начало]

- Учитель: situational = awaiting_start
- Ученик: situational = awaiting_start
- Координатор: активная группа

[Группа: Занимается]

- Учитель: project = working, situational = пусто
- Ученик: project = study, situational = пусто
- Координатор: активная группа

[Группа: Занималась < 4 мес.]

- Учитель/Ученик: project зависит от наличия других групп
- Координатор: группа не активная

[Группа: Завершила занятия]

- Учитель/Ученик: project зависит от наличия других групп
- Координатор: группа не активная

[Группа: Каникулы]

- Учитель: situational = holiday
- Ученик: situational = holiday
- Координатор: активная группа

## Manual QA checklist (admin)
1) Holiday propagation
- Open group: Admin -> Api -> Groups -> <group>
- Set situational status = Holiday, save.
- Check related teachers/students: situational status becomes Holiday.
- Remove Holiday and save: situational recalculates (awaiting_start / group_offered / empty).

2) Pending -> Awaiting start
- Set project status = Pending, save.
- Teacher situational becomes group_offered (unless higher priority exists).
- Student group_offered is manual (no auto change).
- Set project status = Awaiting start, save.
- Teacher/Student situational becomes awaiting_start.

3) Working
- Set project status = Working, save.
- Teacher project = working, student project = study.
- Situational clears (unless higher priority exists).

4) Abort/Finish
- Set project status = Aborted or Finished.
- If teacher/student has other groups: project stays working/study.
- If no other groups: project becomes no_group_yet.

5) M2M changes
- Add/remove teacher or student in group, save.
- Check that situational is recalculated for affected people.
