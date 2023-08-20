class _TaskConstType(enum.EnumType):
    # def __init_subclass__(cls, /, category: str = None, **kwargs):
    #     if category is None:
    #         logging.getLogger('meta').warning(f'Instantiating constant class {cls.__name__} without category.')
    #     super().__init_subclass__(**kwargs)
    #     cls.category = category
    ...


class _ConstReader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        log = logging.getLogger('meta')
        log.info(f"Initializing constants reader.")
        self._loaded = False
        self.constants = {}
        try:
            with open(PATH.CONSTANTS, mode='rb') as constants:
                constants = json.load(constants)
            self._validate_constants(constants)
        except:
            log.warning(f"Couldn't load constants file \"{PATH.CONSTANTS}\".",
                        exc_info=sys.exc_info())
        else:
            self.constants = constants
            self._loaded = True

    @staticmethod
    def _validate_constants(constants):
        log = logging.getLogger('meta')
        if not isinstance(constants, dict):
            raise ValueError(
                f"Constants json must be an object (dict),"
                f" got {constants.__class__.__name__} \"{str(constants)[:100]}\".")
        if 'step' not in constants:
            log.warning(f"Step ordering is missing from constants file.")
        else:
            steps = constants['step']

            # Validate steps ordering.
            if isinstance(steps, list):
                steps = dict(enumerate(steps))
            elif isinstance(steps, dict):
                pass
            else:
                log.error(f"Constants category \"step\" must be an array (list) or object (dict), removing,"
                          f" got {steps.__class__.__name__} \"{str(steps)[:100]}\".")
                steps = {}
            constants['step'] = steps

            # Validate categories.
            for cat, v in tuple(constants.items()):
                if cat != 'step':
                    if isinstance(v, list):  # Category is a list ordering
                        non_string, names = {}, set()
                        for n, name in enumerate(v):
                            if isinstance(name, str):
                                names.add(name)
                            else:
                                non_string[n] = name
                        if non_string:
                            log.error(f"Constants in list ordering for category {cat} must be strings, ")
                        constants[cat] = {name: n for n, name in enumerate(v) if name in names.keys()}
                    elif isinstance(v, dict):
                        for step in v.keys():
                            if step not in steps:
                                log.warning(
                                    f"Couldn't find ordering for step \"{step}\" in constants file, appending.")
                                steps.append(step)
                    else:
                        log.error(f"Constants category \"{cat}\" must be an object (dict), removing")

    def index(self, category: str, name: str):
        log = logging.getLogger('meta')
        if self._loaded and category not in self.constants:
            log.warning(f"Couldn't find constants category {category}, falling back to auto-ordering.")
        constants = self.constants.setdefault(category, [])

        if isinstance(constants, dict):
            steps = self.constants.setdefault('step', [])

            i = 0
            for k, v in sorted(constants.items(), key=lambda e: steps.index(e[0])):
                for const in v:
                    if const == name:
                        return i
                    else:
                        i += 1
            else:
                if self._loaded:
                    log.warning(f"Couldn't find index for ")
