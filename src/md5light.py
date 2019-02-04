import cmd2
import argparse
import uuid
import getpass
import smtplib

import solver_tasks
import simple_server


SERVER_PORT = 8000


class MD5Light(cmd2.Cmd):
    prompt = '(MD5Light) '
    intro = 'Welcome to the MD5Light. Type help or ? to list commands.\n'

    solver_tasks = solver_tasks.SolverTasks()
    server = simple_server.SimpleServer()
    SMTP = None
    sender = None

    def shutdown_server(self):
        answer = self.server.shutdown()
        self.poutput(answer)

    def is_SMTP_connected(self):
        if self.SMTP is None:
            return False
        try:
            status = self.SMTP.noop()[0]
        except:
            status = -1
        return True if status == 250 else False

    def quit_SMTP(self):
        self.poutput("Quiting from SMTP session...")
        self.SMTP.quit()

        self.SMTP = None
        self.solver_tasks.set_SMTP_and_sender(None, None)

        self.poutput("Done.")

    def do_startSMTP(self, args):
        """Start SMTP session."""

        if self.is_SMTP_connected():
            self.quit_SMTP()

        self.poutput("Print Start SMTP sessionfollowing:")
        host = input("SMTP server host: ")
        username = input('Username: ')
        password = getpass.getpass()
        self.sender = input('Your email: ')

        try:
            self.SMTP = smtplib.SMTP(host, 587)
            self.SMTP.starttls()
            answer = self.SMTP.login(username, password)

            self.solver_tasks.set_SMTP_and_sender(self.SMTP, self.sender)
            self.poutput(answer)

        except Exception as e:
            self.poutput(e)

    add_parser = argparse.ArgumentParser()
    add_parser.add_argument('url', type=str, help='url of file')
    add_parser.add_argument('-e', '--email', type=str, help='email to send')

    @cmd2.with_argparser(add_parser)
    def do_add(self, args):
        """Add a new task."""
        answer = self.solver_tasks.add_task(args.url, args.email)
        self.poutput(answer)

    get_parser = argparse.ArgumentParser()
    get_parser.add_argument('task_id', type=str, help='get status of task')

    @cmd2.with_argparser(get_parser)
    def do_get(self, args):
        """Get status of task."""
        content = self.solver_tasks.get_task(args.task_id)
        self.poutput(content)

    def do_getall(self, args):
        """Get ids of all tasks."""
        tasks_id = self.solver_tasks.get_all_ids()
        self.poutput(tasks_id)

    def do_run(self, args):
        """Run a server."""
        answer = self.server.run(self.solver_tasks)
        self.poutput(answer)

    def do_shutdown(self, args):
        """Shut down the server."""
        self.shutdown_server()

    def do_stopSMTP(self, args):
        if self.is_SMTP_connected():
            self.quit_SMTP()
        else:
            self.poutput("SMTP session is not active.")

    def do_quit(self, args):
        if self.server.get_is_serving():
            self.poutput("Shutdowning the server...")
            self.shutdown_server()

        if self.is_SMTP_connected():
            self.quit_SMTP()

        return True

    do_q = do_quit


if __name__ == '__main__':
    app = MD5Light()

    app.cmdloop()
