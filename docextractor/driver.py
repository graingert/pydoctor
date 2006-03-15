from docextractor import model
import sys, os

def error(msg, *args):
    if args:
        msg = msg%args
    print >> sys.stderr, msg
    sys.exit(1)

def main(args):
    from optparse import OptionParser
    import cPickle
    parser = OptionParser()
##     parser.add_option('-c', '--config', dest='configfile',
##                       help="Use config from this file (any command line"
##                            "options override settings from the file).")
    parser.add_option('-p', '--input-pickle', dest='inputpickle',
                      help="Load the system from this pickle file (default: "
                      "none, a blank system is created).")
    parser.add_option('-o', '--output-pickle', dest='outputpickle',
                      help="Save the system to this pickle file (default: "
                      "none, the system is not saved by default).")
    parser.add_option('--system-class', dest='systemclass',
                      help="a dotted name of the class to use to make a system")
    parser.add_option('--testing', dest='testing', action='store_true',
                      help="don't complain if the run doesn't have any effects")
    parser.add_option('--target-state', dest='targetstate',
                      default='finalized',
                      choices=model.states,
                      help="the state to move the system to (default: %default).")
    parser.add_option('--make-html',
                      action='store_true', dest='makehtml',
                      help="")
    parser.add_option('--html-subject', dest='htmlsubject',
                      help="fullName of object to generate API docs for"
                      " (default: everything).")
    parser.add_option('--html-output', dest='htmloutput',
                      help="Directory to save HTML files to "
                           "(default 'apidocs')")
    parser.add_option('--html-writer', dest='htmlwriter',
                      help="dotted name of html writer class to use"
                           "(default 'XXX')")
    parser.add_option('--add-package',
                      action='append', dest='packages', metavar='PACKAGEDIR',
                      help='Add a package to the system.  Can be repeated '
                           'to add more than one package.')
    parser.add_option('--no-find-import-star',
                      action='store_false', dest='findimportstar',
                      default=True,
                      help="Don't preprocess the modules to resolve import *s."
                           " It's a significant speed saving if you don't need"
                           " it.")
    parser.add_option('-v', '--verbose', action='count', dest='verbosity',
                      help="Be noisier.  Can be repeated for more noise.")
    options, args = parser.parse_args(args)

    print options.__dict__.keys()

    # step 1: make/find the system
    if options.systemclass:
        if '.' not in options.systemclass:
            error("--system-class takes a dotted name")
        parts = options.systemclass.rsplit('.', 1)
        try:
            mod = __import__(parts[0], globals(), locals(), parts[1])
        except ImportError:
            error("could not import module %s", parts[0])
        try:
            systemclass = getattr(mod, parts[1])
        except AttributeError:
            error("did not find %s in module %s", parts[1], parts[0])
        if not issubclass(systemclass, model.System):
            msg = "%s is not a subclass of model.System"
            error(msg, systemclass)
    else:
        systemclass = model.System

    if options.inputpickle:
        system = cPickle.load(open(options.inputpickle, 'rb'))
        if options.systemclass:
            if type(system) is not systemclass:
                msg = ("loaded pickle has class %s.%s, differing "
                       "from explicitly requested %s")
                error(msg, cls.__module__, cls.__name__, options.systemclass)
    else:
        system = systemclass()

    system.verbosity = options.verbosity

    # step 1.5: check that we're actually going to accomplish something here

    if not options.outputpickle and not options.makehtml \
           and not options.testing:
        msg = ("this invocation isn't going to do anything\n"
               "maybe supply --make-html and/or --output-pickle?")
        error(msg)

    # step 2: add any packages

    if options.packages:
        if system.state not in ['blank', 'preparse']:
            msg = 'system is in state %r, which is too late to add new code'
            error(msg, system.state)
        for path in options.packages:
            path = os.path.normpath(path)
            print 'adding directory', path
            model.preprocessDirectory(system, path)

    # step 3: move the system to the desired state

    curstateindex = model.states.index(system.state)
    finalstateindex = model.states.index(options.targetstate)

    if finalstateindex < curstateindex:
        msg = 'cannot reverse system from %r to %r'
        error(msg, system.state, options.targetstate)

    if finalstateindex > 0 and curstateindex == 0:
        msg = 'cannot advance totally blank system to %r'
        error(msg, options.targetstate)

    funcs = [None,
             model.findImportStars,
             model.extractDocstrings,
             model.finalStateComputations]

    for i in range(curstateindex, finalstateindex):
        f = funcs[i]
        if not (f == model.findImportStars and not options.findimportstar):
            print f.__name__
            f(system)

    if system.state != options.targetstate:
        msg = "failed to advance state to %r (this is a bug)"
        error(msg, options.targetstate)

    # step 4: save the system, if desired

    if options.outputpickle:
        f = open(options.outputpickle, 'wb')
        cPickle.dump(system, f)
        f.close()

    # step 5: make html, if desired

    if options.makehtml:
        print 'we should be making HTML now'

if __name__ == '__main__':
    main(sys.argv[1:])
from docextractor import model
import sys, os

def error(msg, *args):
    if args:
        msg = msg%args
    print >> sys.stderr, msg
    sys.exit(1)

def main(args):
    from optparse import OptionParser
    import cPickle
    parser = OptionParser()
##     parser.add_option('-c', '--config', dest='configfile',
##                       help="Use config from this file (any command line"
##                            "options override settings from the file).")
    parser.add_option('-p', '--input-pickle', dest='inputpickle',
                      help="Load the system from this pickle file (default: "
                      "none, a blank system is created).")
    parser.add_option('-o', '--output-pickle', dest='outputpickle',
                      help="Save the system to this pickle file (default: "
                      "none, the system is not saved by default).")
    parser.add_option('--system-class', dest='systemclass',
                      help="a dotted name of the class to use to make a system")
    parser.add_option('--testing', dest='testing', action='store_true',
                      help="don't complain if the run doesn't have any effects")
    parser.add_option('--target-state', dest='targetstate',
                      default='finalized',
                      choices=model.states,
                      help="the state to move the system to (default: %default).")
    parser.add_option('--make-html',
                      action='store_true', dest='makehtml',
                      help="")
    parser.add_option('--html-subject', dest='htmlsubject',
                      help="fullName of object to generate API docs for"
                      " (default: everything).")
    parser.add_option('--html-output', dest='htmloutput',
                      help="Directory to save HTML files to "
                           "(default 'apidocs')")
    parser.add_option('--html-writer', dest='htmlwriter',
                      help="dotted name of html writer class to use"
                           "(default 'XXX')")
    parser.add_option('--add-package',
                      action='append', dest='packages', metavar='PACKAGEDIR',
                      help='Add a package to the system.  Can be repeated '
                           'to add more than one package.')
    parser.add_option('--no-find-import-star',
                      action='store_false', dest='findimportstar',
                      default=True,
                      help="Don't preprocess the modules to resolve import *s."
                           " It's a significant speed saving if you don't need"
                           " it.")
    parser.add_option('-v', '--verbose', action='count', dest='verbosity',
                      help="Be noisier.  Can be repeated for more noise.")
    options, args = parser.parse_args(args)

    print options.__dict__.keys()

    # step 1: make/find the system
    if options.systemclass:
        if '.' not in options.systemclass:
            error("--system-class takes a dotted name")
        parts = options.systemclass.rsplit('.', 1)
        try:
            mod = __import__(parts[0], globals(), locals(), parts[1])
        except ImportError:
            error("could not import module %s", parts[0])
        try:
            systemclass = getattr(mod, parts[1])
        except AttributeError:
            error("did not find %s in module %s", parts[1], parts[0])
        if not issubclass(systemclass, model.System):
            msg = "%s is not a subclass of model.System"
            error(msg, systemclass)
    else:
        systemclass = model.System

    if options.inputpickle:
        system = cPickle.load(open(options.inputpickle, 'rb'))
        if options.systemclass:
            if type(system) is not systemclass:
                msg = ("loaded pickle has class %s.%s, differing "
                       "from explicitly requested %s")
                error(msg, cls.__module__, cls.__name__, options.systemclass)
    else:
        system = systemclass()

    system.verbosity = options.verbosity

    # step 1.5: check that we're actually going to accomplish something here

    if not options.outputpickle and not options.makehtml \
           and not options.testing:
        msg = ("this invocation isn't going to do anything\n"
               "maybe supply --make-html and/or --output-pickle?")
        error(msg)

    # step 2: add any packages

    if options.packages:
        if system.state not in ['blank', 'preparse']:
            msg = 'system is in state %r, which is too late to add new code'
            error(msg, system.state)
        for path in options.packages:
            path = os.path.normpath(path)
            print 'adding directory', path
            model.preprocessDirectory(system, path)

    # step 3: move the system to the desired state

    curstateindex = model.states.index(system.state)
    finalstateindex = model.states.index(options.targetstate)

    if finalstateindex < curstateindex:
        msg = 'cannot reverse system from %r to %r'
        error(msg, system.state, options.targetstate)

    if finalstateindex > 0 and curstateindex == 0:
        msg = 'cannot advance totally blank system to %r'
        error(msg, options.targetstate)

    funcs = [None,
             model.findImportStars,
             model.extractDocstrings,
             model.finalStateComputations]

    for i in range(curstateindex, finalstateindex):
        f = funcs[i]
        if not (f == model.findImportStars and not options.findimportstar):
            print f.__name__
            f(system)

    if system.state != options.targetstate:
        msg = "failed to advance state to %r (this is a bug)"
        error(msg, options.targetstate)

    # step 4: save the system, if desired

    if options.outputpickle:
        f = open(options.outputpickle, 'wb')
        cPickle.dump(system, f)
        f.close()

    # step 5: make html, if desired

    if options.makehtml:
        print 'we should be making HTML now'

if __name__ == '__main__':
    main(sys.argv[1:])
