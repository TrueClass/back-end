from argon2 import PasswordHasher, Type

password_hasher = PasswordHasher(
    memory_cost=65536,
    time_cost=4,
    parallelism=2,
    hash_len=32,
    type=Type.ID
)

DUMMY_HASH = password_hasher.hash("trueclass-dummy-password")
