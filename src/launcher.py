
import argparse
# from pathlib import Path
import traceback, sys






if __name__ == '__main__':
    # run as a program
    import report_create as report_html_create
elif '.' in __name__:
    # package
    from . import report_create as report_html_create
else:
    # included with no parent package
    import report_create as report_html_create







def call_report_html_program(*argcs,**kwargs):
    return report_html_create.entry_point({'arglist_strict':False})

def call_templatetest_program(*argcs,**kwargs):
    # return report_html_create.print_test()
    pass

def call_test_program(*argcs,**kwargs):
    msg = '''
hello, world!
    '''
    print(msg)
    return True




run_programs = {
    'report': call_report_html_program,
    'report_html': call_report_html_program,
    'test': call_test_program,
    'templatetest': call_templatetest_program,
}



def main():
    try:
        parser = argparse.ArgumentParser(
            description="Universal caller of mdmtoolsap-py utilities"
        )
        parser.add_argument(
            #'-1',
            '--program',
            choices=dict.keys(run_programs),
            type=str,
            required=True
        )
        args, args_rest = parser.parse_known_args()
        if args.program:
            program = '{arg}'.format(arg=args.program)
            if program in run_programs:
                run_programs[program](args_rest)
            else:
                raise AttributeError('program to run not recognized: {program}'.format(program=args.program))
        else:
            print('program to run not specified')
            raise AttributeError('program to run not specified')
    except Exception as e:
        # the program is designed to be user-friendly
        # that's why we reformat error messages a little bit
        # stack trace is still printed (I even made it longer to 20 steps!)
        # but the error message itself is separated and printed as the last message again

        # for example, I don't write "print('File Not Found!');exit(1);", I just write "raise FileNotFoundErro()"
        print('',file=sys.stderr)
        print('Stack trace:',file=sys.stderr)
        print('',file=sys.stderr)
        traceback.print_exception(e,limit=20)
        print('',file=sys.stderr)
        print('',file=sys.stderr)
        print('',file=sys.stderr)
        print('Error:',file=sys.stderr)
        print('',file=sys.stderr)
        print('{e}'.format(e=e),file=sys.stderr)
        print('',file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()
