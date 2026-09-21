#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

static char child_stack[1024 * 1024];

static int child_fn(void *none) {
  // Disable stdout buffering so prints show up immediately
  setvbuf(stdout, NULL, _IONBF, 0);

  sleep(1);
  system("ip addr add 10.0.0.4/24 dev veth1");
  system("ip link set veth1 up");
  system("ip link set lo up");

  puts("========= child network interfaces ========");
  system("ip addr");
  puts("===========================================");

  sleep(1);
  system("ping -c 3 10.0.0.3");
  return 0;
}

int main() {
  // Disable stdout buffering in the parent as well
  setvbuf(stdout, NULL, _IONBF, 0);

  char buf[255];

  pid_t pid =
      clone(child_fn, child_stack + 1024 * 1024, CLONE_NEWNET | SIGCHLD, NULL);
  if (pid == -1) {
    perror("clone");
    return 1;
  }

  sprintf(buf, "ip link add name veth0 type veth peer name veth1 netns %d",
          pid);
  system(buf);

  system("ip addr add 10.0.0.3/24 dev veth0");
  system("ip link set veth0 up");

  waitpid(pid, NULL, 0);
  return 0;
}
