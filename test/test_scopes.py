import logging

# TODO Fix disabled test cases: one of them makes the plugin leak
#       processes or disturbs the execution order


def test_proc_factory_module_first(process_factory):
    logging.info(
        "That one runs without the module fixture (no module fixture requested yet)"
    )
    proc = process_factory("/usr/bin/true")
    proc.run_bg()


def test_proc_factory_module(process_factory_module):
    logging.info("here we create the fixture")
    proc = process_factory_module("/usr/bin/true")
    proc.run_bg()


def test_proc_factory_module_2(process_factory_module):
    logging.info("here we create the fixture 2")
    proc = process_factory_module("/usr/bin/true")
    proc.run_bg()


def test_proc_factory_function(process_factory):
    logging.info("here we run a process")
    proc = process_factory("/usr/bin/true")
    proc.run_bg()


def test_proc_factory_function_2(process_factory):
    logging.info("here we run a process 2")
    proc = process_factory("/usr/bin/true")
    proc.run_bg()


def dis_test_proc_factory_session(process_factory_session):
    """TODO Disabled: stdout of pytest appears in the logged stdout ???
    Do we have a os.fork going wild?
    """
    logging.info("here we run a session fixture")
    proc = process_factory_session("/usr/bin/true")
    proc.run_bg()


def dis_test_proc_factory_function_2(process_factory_session):
    logging.info("here we run a session fixture 2")
    proc = process_factory_session("/usr/bin/true")
    proc.run_bg()
