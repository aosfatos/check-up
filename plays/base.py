class BasePlay:
    def __init__(self, url, session_dir, wait_time=3, headless=True):
        self.url = url
        self.session_dir = session_dir
        self.wait_time = wait_time
        self.headless = headless

    def pre_run(self):
        raise NotImplementedError()

    def post_run(self, output):
        return output

    def run(self):
        raise NotImplementedError()

    def execute(self):
        self.pre_run()
        output = self.run()
        output = self.post_run(output)
        return output
