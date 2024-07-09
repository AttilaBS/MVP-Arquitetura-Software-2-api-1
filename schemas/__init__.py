'''Module responsible for importing schemas into the application'''
from schemas.reminder import ReminderSchema, ReminderUpdateSchema, \
                            ReminderSearchSchema, ReminderDeleteSchema, \
                            ReminderViewSchema, RemindersListSchema, \
                            ReminderSearchByNameSchema, \
                            show_reminder, show_reminders, RemindersSearchSchema, \
                            ReminderCreateOrUpdateSchema
from schemas.user import UserSchema, UserViewSchema, UserWithIdViewSchema, \
                            UserSearchSchema
from schemas.send_email import SendEmailSchema
from schemas.error import ErrorSchema
