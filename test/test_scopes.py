import logging


def test_proc_factory_function(process_factory):
    logging.info("here we run a process")
    p=process_factory("/usr/bin/true")
    p.run_bg()

def test_proc_factory_function_2(process_factory):
    logging.info("here we run a process 2")
    p=process_factory("/usr/bin/true")
    p.run_bg()

