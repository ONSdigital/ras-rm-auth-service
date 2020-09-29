ALTER TABLE auth.user
ADD due_deletion_first_notification_date TIMESTAMP without time zone,
    due_deletion_second_notification_date TIMESTAMP without time zone,
    due_deletion_third_notification_date TIMESTAMP without time zone;
