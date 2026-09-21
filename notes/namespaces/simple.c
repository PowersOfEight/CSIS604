#define _GNU_SOURCE
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

static char child_stack[5000];

void grchild(int num) {
  printf("child(%d) in ns my PID: %d Parent ID=%d\n", num, getpid(), getppid());
  sleep(5);
  puts("end child");
}

int child_fn(void *arg) {
  int ppid = (int)(long)arg;
  int i;
  printf("PID: %ld Parent:%ld\n", (long)getpid(), (long)getppid());

  pid_t first_child_pid = -1;

  for (i = 0; i < 3; i++) {
    pid_t cp = fork();
    if (cp == 0) {
      grchild(i + 1);
      exit(0);
    }
    if (i == 0) {
      first_child_pid = cp; // Capture the actual PID instead of guessing '2'
    }
  }

  // This has no effect because ppid is outside the namespace
  kill(ppid, SIGKILL);

  sleep(2);

  // Safely kill the first child using its actual tracked PID
  if (first_child_pid > 0) {
    kill(first_child_pid, SIGKILL);
  }

  sleep(10);
  return 0;
}

int main() {
  // Pass getpid() safely through the void* argument parameter of clone
  pid_t pid = clone(child_fn, child_stack + 5000, CLONE_NEWPID | SIGCHLD,
                    (void *)(long)getpid());
  if (pid == -1) {
    perror("clone");
    return 1;
  }
  printf("clone() = %d\n", pid);

  waitpid(pid, NULL, 0);
  return 0;
}
