def get_query(date_one, date_two, template_date_column):
    """
    creates query required to check the account accessed with in duration
    param: data_one - dates higher limit
    param: date_two - dates lower limit
    param: date column associated to the template
    """
    return (
        "SELECT auth.user.username FROM auth.user where (auth.user.last_login_date is null AND "
        f"auth.user.account_creation_date between '{date_one}' AND '{date_two}' AND "
        f"auth.user.{template_date_column} is null) OR (auth.user.last_login_date is not null AND "
        f"auth.user.last_login_date between '{date_one}' AND '{date_two}' AND "
        f"auth.user.{template_date_column} is null) "
    )


class AuthDueDeletionSchedulerError(Exception):
    def __init__(self, description=None, error=None, **kwargs):
        self.description = description
        self.error = error
        for k, v in kwargs.items():
            self.__dict__[k] = v
