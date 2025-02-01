from fastapi import status


class BaseApplicationError(Exception):
    message: str = ""
    context_message: str = ""
    data: dict | None = None

    def __init__(
        self,
        message: str | None = None,
        fields: list | None = None,
        context_message: str | None = None,
        data: dict | None = None,
    ) -> None:
        self.fields = fields
        if message:
            self.message = message
        if context_message:
            self.context_message = context_message
        if data:
            self.data = data


class ApplicationError(BaseApplicationError):
    def __init__(
        self,
        fields: list[str] | None = None,
        context_message: str | None = None,
        message: str | dict | None = None,
        data: dict | None = None,
    ) -> None:
        super().__init__(
            fields=fields,
            context_message=context_message or self.context_message,
            message=message or self.message,
            data=data or self.data,
        )

    @property
    def context(self) -> str:
        if not self.fields and not self.data:
            return ""

        if self.data and self.fields:
            return ""

        field_format = ""

        if self.data:
            field_format = ", ".join([f"{field}={value}" for field, value in self.data.items()])

        if self.fields:
            field_format = ", ".join(self.fields)

        return self.context_message.format(field=field_format)


class StatusError400(ApplicationError):
    status = status.HTTP_400_BAD_REQUEST


class StatusError403(ApplicationError):
    status = status.HTTP_403_FORBIDDEN


class StatusError404(ApplicationError):
    status = status.HTTP_404_NOT_FOUND


class StatusError409(ApplicationError):
    status = status.HTTP_409_CONFLICT


class StatusError500(ApplicationError):
    status = status.HTTP_500_INTERNAL_SERVER_ERROR


class RequestDataError(StatusError400):
    message = "The data was transmitted incorrectly"
    context_message = "One of these fields {field} must be filled in"


class ObjectNotFoundError(StatusError404):
    message = "The object was not found"
    context_message = "An object with such a {field} was not found"


class DBConflictError(StatusError409):
    message = "Conflict when working with the database"
