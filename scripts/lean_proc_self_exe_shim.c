#define _GNU_SOURCE

#include <dlfcn.h>
#include <errno.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

typedef ssize_t (*readlink_fn)(const char *, char *, size_t);

static int is_proc_exe_path(const char *path) {
    const char *last_slash;

    if (path == NULL || strncmp(path, "/proc/", 6) != 0) {
        return 0;
    }
    last_slash = strrchr(path, '/');
    return last_slash != NULL && strcmp(last_slash, "/exe") == 0;
}

ssize_t readlink(const char *path, char *buffer, size_t buffer_size) {
    static readlink_fn next_readlink = NULL;
    const char *override = getenv("LEAN_PROC_SELF_EXE");

    if (override != NULL && is_proc_exe_path(path)) {
        size_t length = strlen(override);
        if (length > buffer_size) {
            length = buffer_size;
        }
        memcpy(buffer, override, length);
        return (ssize_t)length;
    }

    if (next_readlink == NULL) {
        next_readlink = (readlink_fn)dlsym(RTLD_NEXT, "readlink");
    }
    if (next_readlink == NULL) {
        errno = ENOSYS;
        return -1;
    }
    return next_readlink(path, buffer, buffer_size);
}
