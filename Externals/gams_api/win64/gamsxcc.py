# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.2
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.


from sys import version_info

if version_info >= (2, 6, 0):

    def swig_import_helper():
        from os.path import dirname
        import imp

        fp = None
        try:
            fp, pathname, description = imp.find_module("_gamsxcc", [dirname(__file__)])
        except ImportError:
            import _gamsxcc

            return _gamsxcc
        if fp is not None:
            try:
                _mod = imp.load_module("_gamsxcc", fp, pathname, description)
            finally:
                fp.close()
            return _mod

    _gamsxcc = swig_import_helper()
    del swig_import_helper
else:
    import _gamsxcc
del version_info
try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if name == "thisown":
        return self.this.own(value)
    if name == "this":
        if type(value).__name__ == "SwigPyObject":
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if not static:
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if name == "thisown":
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError(name)


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis)


try:
    _object = object
    _newclass = 1
except AttributeError:

    class _object:
        pass

    _newclass = 0


class intArray(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, intArray, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, intArray, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _gamsxcc.new_intArray(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _gamsxcc.delete_intArray
    __del__ = lambda self: None

    def __getitem__(self, *args):
        return _gamsxcc.intArray___getitem__(self, *args)

    def __setitem__(self, *args):
        return _gamsxcc.intArray___setitem__(self, *args)

    def cast(self):
        return _gamsxcc.intArray_cast(self)

    __swig_getmethods__["frompointer"] = lambda x: _gamsxcc.intArray_frompointer
    if _newclass:
        frompointer = staticmethod(_gamsxcc.intArray_frompointer)


intArray_swigregister = _gamsxcc.intArray_swigregister
intArray_swigregister(intArray)


def intArray_frompointer(*args):
    return _gamsxcc.intArray_frompointer(*args)


intArray_frompointer = _gamsxcc.intArray_frompointer


class doubleArray(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, doubleArray, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, doubleArray, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _gamsxcc.new_doubleArray(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _gamsxcc.delete_doubleArray
    __del__ = lambda self: None

    def __getitem__(self, *args):
        return _gamsxcc.doubleArray___getitem__(self, *args)

    def __setitem__(self, *args):
        return _gamsxcc.doubleArray___setitem__(self, *args)

    def cast(self):
        return _gamsxcc.doubleArray_cast(self)

    __swig_getmethods__["frompointer"] = lambda x: _gamsxcc.doubleArray_frompointer
    if _newclass:
        frompointer = staticmethod(_gamsxcc.doubleArray_frompointer)


doubleArray_swigregister = _gamsxcc.doubleArray_swigregister
doubleArray_swigregister(doubleArray)


def doubleArray_frompointer(*args):
    return _gamsxcc.doubleArray_frompointer(*args)


doubleArray_frompointer = _gamsxcc.doubleArray_frompointer


def new_intp():
    return _gamsxcc.new_intp()


new_intp = _gamsxcc.new_intp


def copy_intp(*args):
    return _gamsxcc.copy_intp(*args)


copy_intp = _gamsxcc.copy_intp


def delete_intp(*args):
    return _gamsxcc.delete_intp(*args)


delete_intp = _gamsxcc.delete_intp


def intp_assign(*args):
    return _gamsxcc.intp_assign(*args)


intp_assign = _gamsxcc.intp_assign


def intp_value(*args):
    return _gamsxcc.intp_value(*args)


intp_value = _gamsxcc.intp_value


def new_doublep():
    return _gamsxcc.new_doublep()


new_doublep = _gamsxcc.new_doublep


def copy_doublep(*args):
    return _gamsxcc.copy_doublep(*args)


copy_doublep = _gamsxcc.copy_doublep


def delete_doublep(*args):
    return _gamsxcc.delete_doublep(*args)


delete_doublep = _gamsxcc.delete_doublep


def doublep_assign(*args):
    return _gamsxcc.doublep_assign(*args)


doublep_assign = _gamsxcc.doublep_assign


def doublep_value(*args):
    return _gamsxcc.doublep_value(*args)


doublep_value = _gamsxcc.doublep_value


def new_gamsxHandle_tp():
    return _gamsxcc.new_gamsxHandle_tp()


new_gamsxHandle_tp = _gamsxcc.new_gamsxHandle_tp


def copy_gamsxHandle_tp(*args):
    return _gamsxcc.copy_gamsxHandle_tp(*args)


copy_gamsxHandle_tp = _gamsxcc.copy_gamsxHandle_tp


def delete_gamsxHandle_tp(*args):
    return _gamsxcc.delete_gamsxHandle_tp(*args)


delete_gamsxHandle_tp = _gamsxcc.delete_gamsxHandle_tp


def gamsxHandle_tp_assign(*args):
    return _gamsxcc.gamsxHandle_tp_assign(*args)


gamsxHandle_tp_assign = _gamsxcc.gamsxHandle_tp_assign


def gamsxHandle_tp_value(*args):
    return _gamsxcc.gamsxHandle_tp_value(*args)


gamsxHandle_tp_value = _gamsxcc.gamsxHandle_tp_value


def new_TBrkPCallBack1_tp():
    return _gamsxcc.new_TBrkPCallBack1_tp()


new_TBrkPCallBack1_tp = _gamsxcc.new_TBrkPCallBack1_tp


def copy_TBrkPCallBack1_tp(*args):
    return _gamsxcc.copy_TBrkPCallBack1_tp(*args)


copy_TBrkPCallBack1_tp = _gamsxcc.copy_TBrkPCallBack1_tp


def delete_TBrkPCallBack1_tp(*args):
    return _gamsxcc.delete_TBrkPCallBack1_tp(*args)


delete_TBrkPCallBack1_tp = _gamsxcc.delete_TBrkPCallBack1_tp


def TBrkPCallBack1_tp_assign(*args):
    return _gamsxcc.TBrkPCallBack1_tp_assign(*args)


TBrkPCallBack1_tp_assign = _gamsxcc.TBrkPCallBack1_tp_assign


def TBrkPCallBack1_tp_value(*args):
    return _gamsxcc.TBrkPCallBack1_tp_value(*args)


TBrkPCallBack1_tp_value = _gamsxcc.TBrkPCallBack1_tp_value


def new_TBrkPCallBack2_tp():
    return _gamsxcc.new_TBrkPCallBack2_tp()


new_TBrkPCallBack2_tp = _gamsxcc.new_TBrkPCallBack2_tp


def copy_TBrkPCallBack2_tp(*args):
    return _gamsxcc.copy_TBrkPCallBack2_tp(*args)


copy_TBrkPCallBack2_tp = _gamsxcc.copy_TBrkPCallBack2_tp


def delete_TBrkPCallBack2_tp(*args):
    return _gamsxcc.delete_TBrkPCallBack2_tp(*args)


delete_TBrkPCallBack2_tp = _gamsxcc.delete_TBrkPCallBack2_tp


def TBrkPCallBack2_tp_assign(*args):
    return _gamsxcc.TBrkPCallBack2_tp_assign(*args)


TBrkPCallBack2_tp_assign = _gamsxcc.TBrkPCallBack2_tp_assign


def TBrkPCallBack2_tp_value(*args):
    return _gamsxcc.TBrkPCallBack2_tp_value(*args)


TBrkPCallBack2_tp_value = _gamsxcc.TBrkPCallBack2_tp_value


def gamsxHandleToPtr(*args):
    """gamsxHandleToPtr(pgamsx) -> void *"""
    return _gamsxcc.gamsxHandleToPtr(*args)


def ptrTogamsxHandle(*args):
    """ptrTogamsxHandle(vptr) -> gamsxHandle_t"""
    return _gamsxcc.ptrTogamsxHandle(*args)


def gamsxGetReady(*args):
    """gamsxGetReady(msgBufSize) -> int"""
    return _gamsxcc.gamsxGetReady(*args)


def gamsxGetReadyD(*args):
    """gamsxGetReadyD(dirName, msgBufSize) -> int"""
    return _gamsxcc.gamsxGetReadyD(*args)


def gamsxGetReadyL(*args):
    """gamsxGetReadyL(libName, msgBufSize) -> int"""
    return _gamsxcc.gamsxGetReadyL(*args)


def gamsxCreate(*args):
    """gamsxCreate(pgamsx, msgBufSize) -> int"""
    return _gamsxcc.gamsxCreate(*args)


def gamsxCreateD(*args):
    """gamsxCreateD(pgamsx, dirName, msgBufSize) -> int"""
    return _gamsxcc.gamsxCreateD(*args)


def gamsxCreateL(*args):
    """gamsxCreateL(pgamsx, libName, msgBufSize) -> int"""
    return _gamsxcc.gamsxCreateL(*args)


def gamsxFree(*args):
    """gamsxFree(pgamsx) -> int"""
    return _gamsxcc.gamsxFree(*args)


def gamsxLibraryLoaded():
    """gamsxLibraryLoaded() -> int"""
    return _gamsxcc.gamsxLibraryLoaded()


def gamsxLibraryUnload():
    """gamsxLibraryUnload() -> int"""
    return _gamsxcc.gamsxLibraryUnload()


def gamsxGetScreenIndicator():
    """gamsxGetScreenIndicator() -> int"""
    return _gamsxcc.gamsxGetScreenIndicator()


def gamsxSetScreenIndicator(*args):
    """gamsxSetScreenIndicator(scrind)"""
    return _gamsxcc.gamsxSetScreenIndicator(*args)


def gamsxGetExceptionIndicator():
    """gamsxGetExceptionIndicator() -> int"""
    return _gamsxcc.gamsxGetExceptionIndicator()


def gamsxSetExceptionIndicator(*args):
    """gamsxSetExceptionIndicator(excind)"""
    return _gamsxcc.gamsxSetExceptionIndicator(*args)


def gamsxGetExitIndicator():
    """gamsxGetExitIndicator() -> int"""
    return _gamsxcc.gamsxGetExitIndicator()


def gamsxSetExitIndicator(*args):
    """gamsxSetExitIndicator(extind)"""
    return _gamsxcc.gamsxSetExitIndicator(*args)


def gamsxGetErrorCallback():
    """gamsxGetErrorCallback() -> gamsxErrorCallback_t"""
    return _gamsxcc.gamsxGetErrorCallback()


def gamsxSetErrorCallback(*args):
    """gamsxSetErrorCallback(func)"""
    return _gamsxcc.gamsxSetErrorCallback(*args)


def gamsxGetAPIErrorCount():
    """gamsxGetAPIErrorCount() -> int"""
    return _gamsxcc.gamsxGetAPIErrorCount()


def gamsxSetAPIErrorCount(*args):
    """gamsxSetAPIErrorCount(ecnt)"""
    return _gamsxcc.gamsxSetAPIErrorCount(*args)


def gamsxErrorHandling(*args):
    """gamsxErrorHandling(msg)"""
    return _gamsxcc.gamsxErrorHandling(*args)


def gamsxRunExecDLL(*args):
    """gamsxRunExecDLL(pgamsx, optPtr, sysDir, AVerbose) -> int"""
    return _gamsxcc.gamsxRunExecDLL(*args)


def gamsxShowError(*args):
    """gamsxShowError(pgamsx, fNameLog) -> int"""
    return _gamsxcc.gamsxShowError(*args)


def gamsxAddBreakPoint(*args):
    """gamsxAddBreakPoint(pgamsx, fn, lineNr)"""
    return _gamsxcc.gamsxAddBreakPoint(*args)


def gamsxClearBreakPoints(*args):
    """gamsxClearBreakPoints(pgamsx)"""
    return _gamsxcc.gamsxClearBreakPoints(*args)


def gamsxSystemInfo(*args):
    """gamsxSystemInfo(pgamsx, INOUT, INOUT) -> int"""
    return _gamsxcc.gamsxSystemInfo(*args)


def gamsxSymbolInfo(*args):
    """gamsxSymbolInfo(pgamsx, SyNr, INOUT, INOUT, INOUT, INOUT) -> int"""
    return _gamsxcc.gamsxSymbolInfo(*args)


def gamsxUelName(*args):
    """gamsxUelName(pgamsx, uel) -> char *"""
    return _gamsxcc.gamsxUelName(*args)


def gamsxFindSymbol(*args):
    """gamsxFindSymbol(pgamsx, SyName) -> int"""
    return _gamsxcc.gamsxFindSymbol(*args)


def gamsxDataReadRawStart(*args):
    """gamsxDataReadRawStart(pgamsx, SyNr, INOUT) -> int"""
    return _gamsxcc.gamsxDataReadRawStart(*args)


def gamsxDataReadRaw(*args):
    """gamsxDataReadRaw(pgamsx, INOUT) -> int"""
    return _gamsxcc.gamsxDataReadRaw(*args)


def gamsxDataReadDone(*args):
    """gamsxDataReadDone(pgamsx) -> int"""
    return _gamsxcc.gamsxDataReadDone(*args)


def gamsxDataWriteRawStart(*args):
    """gamsxDataWriteRawStart(pgamsx, SyNr, DoMerge) -> int"""
    return _gamsxcc.gamsxDataWriteRawStart(*args)


def gamsxDataWriteRaw(*args):
    """gamsxDataWriteRaw(pgamsx, Elements, Vals) -> int"""
    return _gamsxcc.gamsxDataWriteRaw(*args)


def gamsxDataWriteDone(*args):
    """gamsxDataWriteDone(pgamsx) -> int"""
    return _gamsxcc.gamsxDataWriteDone(*args)


def gamsxRegisterCB1(*args):
    """gamsxRegisterCB1(pgamsx, CB1, userMem)"""
    return _gamsxcc.gamsxRegisterCB1(*args)


def gamsxRegisterCB2(*args):
    """gamsxRegisterCB2(pgamsx, CB2, userMem1, userMem2)"""
    return _gamsxcc.gamsxRegisterCB2(*args)


def gamsxGetCB1(*args):
    """gamsxGetCB1(pgamsx) -> TBrkPCallBack1_t"""
    return _gamsxcc.gamsxGetCB1(*args)


def gamsxGetCB2(*args):
    """gamsxGetCB2(pgamsx) -> TBrkPCallBack2_t"""
    return _gamsxcc.gamsxGetCB2(*args)


def gamsxGetCB1UM(*args):
    """gamsxGetCB1UM(pgamsx) -> void *"""
    return _gamsxcc.gamsxGetCB1UM(*args)


def gamsxGetCB2UM1(*args):
    """gamsxGetCB2UM1(pgamsx) -> void *"""
    return _gamsxcc.gamsxGetCB2UM1(*args)


def gamsxGetCB2UM2(*args):
    """gamsxGetCB2UM2(pgamsx) -> void *"""
    return _gamsxcc.gamsxGetCB2UM2(*args)


def gamsxSWSet(*args):
    """gamsxSWSet(pgamsx, x)"""
    return _gamsxcc.gamsxSWSet(*args)


def gamsxStepThrough(*args):
    """gamsxStepThrough(pgamsx) -> int"""
    return _gamsxcc.gamsxStepThrough(*args)


def gamsxStepThroughSet(*args):
    """gamsxStepThroughSet(pgamsx, x)"""
    return _gamsxcc.gamsxStepThroughSet(*args)


def gamsxRunToEnd(*args):
    """gamsxRunToEnd(pgamsx) -> int"""
    return _gamsxcc.gamsxRunToEnd(*args)


def gamsxRunToEndSet(*args):
    """gamsxRunToEndSet(pgamsx, x)"""
    return _gamsxcc.gamsxRunToEndSet(*args)


def gamsxCB1Defined(*args):
    """gamsxCB1Defined(pgamsx) -> int"""
    return _gamsxcc.gamsxCB1Defined(*args)


def gamsxCB2Defined(*args):
    """gamsxCB2Defined(pgamsx) -> int"""
    return _gamsxcc.gamsxCB2Defined(*args)


GLOBAL_MAX_INDEX_DIM = _gamsxcc.GLOBAL_MAX_INDEX_DIM
GLOBAL_UEL_IDENT_SIZE = _gamsxcc.GLOBAL_UEL_IDENT_SIZE
ITERLIM_INFINITY = _gamsxcc.ITERLIM_INFINITY
GMS_MAX_INDEX_DIM = _gamsxcc.GMS_MAX_INDEX_DIM
GMS_UEL_IDENT_SIZE = _gamsxcc.GMS_UEL_IDENT_SIZE
GMS_SSSIZE = _gamsxcc.GMS_SSSIZE
GMS_VARTYPE_UNKNOWN = _gamsxcc.GMS_VARTYPE_UNKNOWN
GMS_VARTYPE_BINARY = _gamsxcc.GMS_VARTYPE_BINARY
GMS_VARTYPE_INTEGER = _gamsxcc.GMS_VARTYPE_INTEGER
GMS_VARTYPE_POSITIVE = _gamsxcc.GMS_VARTYPE_POSITIVE
GMS_VARTYPE_NEGATIVE = _gamsxcc.GMS_VARTYPE_NEGATIVE
GMS_VARTYPE_FREE = _gamsxcc.GMS_VARTYPE_FREE
GMS_VARTYPE_SOS1 = _gamsxcc.GMS_VARTYPE_SOS1
GMS_VARTYPE_SOS2 = _gamsxcc.GMS_VARTYPE_SOS2
GMS_VARTYPE_SEMICONT = _gamsxcc.GMS_VARTYPE_SEMICONT
GMS_VARTYPE_SEMIINT = _gamsxcc.GMS_VARTYPE_SEMIINT
GMS_VARTYPE_MAX = _gamsxcc.GMS_VARTYPE_MAX
GMS_EQUTYPE_E = _gamsxcc.GMS_EQUTYPE_E
GMS_EQUTYPE_G = _gamsxcc.GMS_EQUTYPE_G
GMS_EQUTYPE_L = _gamsxcc.GMS_EQUTYPE_L
GMS_EQUTYPE_N = _gamsxcc.GMS_EQUTYPE_N
GMS_EQUTYPE_X = _gamsxcc.GMS_EQUTYPE_X
GMS_EQUTYPE_C = _gamsxcc.GMS_EQUTYPE_C
GMS_EQUTYPE_MAX = _gamsxcc.GMS_EQUTYPE_MAX
GMS_VAL_LEVEL = _gamsxcc.GMS_VAL_LEVEL
GMS_VAL_MARGINAL = _gamsxcc.GMS_VAL_MARGINAL
GMS_VAL_LOWER = _gamsxcc.GMS_VAL_LOWER
GMS_VAL_UPPER = _gamsxcc.GMS_VAL_UPPER
GMS_VAL_SCALE = _gamsxcc.GMS_VAL_SCALE
GMS_VAL_MAX = _gamsxcc.GMS_VAL_MAX
sv_valund = _gamsxcc.sv_valund
sv_valna = _gamsxcc.sv_valna
sv_valpin = _gamsxcc.sv_valpin
sv_valmin = _gamsxcc.sv_valmin
sv_valeps = _gamsxcc.sv_valeps
sv_normal = _gamsxcc.sv_normal
sv_acronym = _gamsxcc.sv_acronym
GMS_SVIDX_UNDEF = _gamsxcc.GMS_SVIDX_UNDEF
GMS_SVIDX_NA = _gamsxcc.GMS_SVIDX_NA
GMS_SVIDX_PINF = _gamsxcc.GMS_SVIDX_PINF
GMS_SVIDX_MINF = _gamsxcc.GMS_SVIDX_MINF
GMS_SVIDX_EPS = _gamsxcc.GMS_SVIDX_EPS
GMS_SVIDX_NORMAL = _gamsxcc.GMS_SVIDX_NORMAL
GMS_SVIDX_ACR = _gamsxcc.GMS_SVIDX_ACR
GMS_SVIDX_MAX = _gamsxcc.GMS_SVIDX_MAX
dt_set = _gamsxcc.dt_set
dt_par = _gamsxcc.dt_par
dt_var = _gamsxcc.dt_var
dt_equ = _gamsxcc.dt_equ
dt_alias = _gamsxcc.dt_alias
GMS_DT_SET = _gamsxcc.GMS_DT_SET
GMS_DT_PAR = _gamsxcc.GMS_DT_PAR
GMS_DT_VAR = _gamsxcc.GMS_DT_VAR
GMS_DT_EQU = _gamsxcc.GMS_DT_EQU
GMS_DT_ALIAS = _gamsxcc.GMS_DT_ALIAS
GMS_DT_MAX = _gamsxcc.GMS_DT_MAX
GMS_SV_UNDEF = _gamsxcc.GMS_SV_UNDEF
GMS_SV_NA = _gamsxcc.GMS_SV_NA
GMS_SV_PINF = _gamsxcc.GMS_SV_PINF
GMS_SV_MINF = _gamsxcc.GMS_SV_MINF
GMS_SV_EPS = _gamsxcc.GMS_SV_EPS
GMS_SV_ACR = _gamsxcc.GMS_SV_ACR
GMS_SV_NAINT = _gamsxcc.GMS_SV_NAINT
# This file is compatible with both classic and new-style classes.
