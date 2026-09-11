import enum


class Environment(enum.StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class SSLMode(enum.StrEnum):
    DISABLE = "disable"
    ALLOW = "allow"
    PREFER = "prefer"
    REQUIRE = "require"
    VERIFY_CA = "verify-ca"
    VERIFY_FULL = "verify-full"
