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
            fp, pathname, description = imp.find_module("_gmdcc", [dirname(__file__)])
        except ImportError:
            import _gmdcc

            return _gmdcc
        if fp is not None:
            try:
                _mod = imp.load_module("_gmdcc", fp, pathname, description)
            finally:
                fp.close()
            return _mod

    _gmdcc = swig_import_helper()
    del swig_import_helper
else:
    import _gmdcc
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


GMD_PARAM = _gmdcc.GMD_PARAM
GMD_UPPER = _gmdcc.GMD_UPPER
GMD_LOWER = _gmdcc.GMD_LOWER
GMD_FIXED = _gmdcc.GMD_FIXED
GMD_PRIMAL = _gmdcc.GMD_PRIMAL
GMD_DUAL = _gmdcc.GMD_DUAL
GMD_DEFAULT = _gmdcc.GMD_DEFAULT
GMD_BASECASE = _gmdcc.GMD_BASECASE
GMD_ACCUMULATE = _gmdcc.GMD_ACCUMULATE
GMD_NRSYMBOLS = _gmdcc.GMD_NRSYMBOLS
GMD_NRUELS = _gmdcc.GMD_NRUELS
GMD_NAME = _gmdcc.GMD_NAME
GMD_DIM = _gmdcc.GMD_DIM
GMD_TYPE = _gmdcc.GMD_TYPE
GMD_NRRECORDS = _gmdcc.GMD_NRRECORDS
GMD_USERINFO = _gmdcc.GMD_USERINFO
GMD_EXPLTEXT = _gmdcc.GMD_EXPLTEXT


class intArray(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, intArray, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, intArray, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _gmdcc.new_intArray(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _gmdcc.delete_intArray
    __del__ = lambda self: None

    def __getitem__(self, *args):
        return _gmdcc.intArray___getitem__(self, *args)

    def __setitem__(self, *args):
        return _gmdcc.intArray___setitem__(self, *args)

    def cast(self):
        return _gmdcc.intArray_cast(self)

    __swig_getmethods__["frompointer"] = lambda x: _gmdcc.intArray_frompointer
    if _newclass:
        frompointer = staticmethod(_gmdcc.intArray_frompointer)


intArray_swigregister = _gmdcc.intArray_swigregister
intArray_swigregister(intArray)


def intArray_frompointer(*args):
    return _gmdcc.intArray_frompointer(*args)


intArray_frompointer = _gmdcc.intArray_frompointer


class doubleArray(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, doubleArray, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, doubleArray, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _gmdcc.new_doubleArray(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _gmdcc.delete_doubleArray
    __del__ = lambda self: None

    def __getitem__(self, *args):
        return _gmdcc.doubleArray___getitem__(self, *args)

    def __setitem__(self, *args):
        return _gmdcc.doubleArray___setitem__(self, *args)

    def cast(self):
        return _gmdcc.doubleArray_cast(self)

    __swig_getmethods__["frompointer"] = lambda x: _gmdcc.doubleArray_frompointer
    if _newclass:
        frompointer = staticmethod(_gmdcc.doubleArray_frompointer)


doubleArray_swigregister = _gmdcc.doubleArray_swigregister
doubleArray_swigregister(doubleArray)


def doubleArray_frompointer(*args):
    return _gmdcc.doubleArray_frompointer(*args)


doubleArray_frompointer = _gmdcc.doubleArray_frompointer


def new_intp():
    return _gmdcc.new_intp()


new_intp = _gmdcc.new_intp


def copy_intp(*args):
    return _gmdcc.copy_intp(*args)


copy_intp = _gmdcc.copy_intp


def delete_intp(*args):
    return _gmdcc.delete_intp(*args)


delete_intp = _gmdcc.delete_intp


def intp_assign(*args):
    return _gmdcc.intp_assign(*args)


intp_assign = _gmdcc.intp_assign


def intp_value(*args):
    return _gmdcc.intp_value(*args)


intp_value = _gmdcc.intp_value


def new_doublep():
    return _gmdcc.new_doublep()


new_doublep = _gmdcc.new_doublep


def copy_doublep(*args):
    return _gmdcc.copy_doublep(*args)


copy_doublep = _gmdcc.copy_doublep


def delete_doublep(*args):
    return _gmdcc.delete_doublep(*args)


delete_doublep = _gmdcc.delete_doublep


def doublep_assign(*args):
    return _gmdcc.doublep_assign(*args)


doublep_assign = _gmdcc.doublep_assign


def doublep_value(*args):
    return _gmdcc.doublep_value(*args)


doublep_value = _gmdcc.doublep_value


def new_gmdHandle_tp():
    return _gmdcc.new_gmdHandle_tp()


new_gmdHandle_tp = _gmdcc.new_gmdHandle_tp


def copy_gmdHandle_tp(*args):
    return _gmdcc.copy_gmdHandle_tp(*args)


copy_gmdHandle_tp = _gmdcc.copy_gmdHandle_tp


def delete_gmdHandle_tp(*args):
    return _gmdcc.delete_gmdHandle_tp(*args)


delete_gmdHandle_tp = _gmdcc.delete_gmdHandle_tp


def gmdHandle_tp_assign(*args):
    return _gmdcc.gmdHandle_tp_assign(*args)


gmdHandle_tp_assign = _gmdcc.gmdHandle_tp_assign


def gmdHandle_tp_value(*args):
    return _gmdcc.gmdHandle_tp_value(*args)


gmdHandle_tp_value = _gmdcc.gmdHandle_tp_value


def gmdHandleToPtr(*args):
    """gmdHandleToPtr(pgmd) -> void *"""
    return _gmdcc.gmdHandleToPtr(*args)


def ptrTogmdHandle(*args):
    """ptrTogmdHandle(vptr) -> gmdHandle_t"""
    return _gmdcc.ptrTogmdHandle(*args)


def gmdGetReady(*args):
    """gmdGetReady(msgBufSize) -> int"""
    return _gmdcc.gmdGetReady(*args)


def gmdGetReadyD(*args):
    """gmdGetReadyD(dirName, msgBufSize) -> int"""
    return _gmdcc.gmdGetReadyD(*args)


def gmdGetReadyL(*args):
    """gmdGetReadyL(libName, msgBufSize) -> int"""
    return _gmdcc.gmdGetReadyL(*args)


def gmdCreate(*args):
    """gmdCreate(pgmd, msgBufSize) -> int"""
    return _gmdcc.gmdCreate(*args)


def gmdCreateD(*args):
    """gmdCreateD(pgmd, dirName, msgBufSize) -> int"""
    return _gmdcc.gmdCreateD(*args)


def gmdCreateDD(*args):
    """gmdCreateDD(pgmd, dirName, msgBufSize) -> int"""
    return _gmdcc.gmdCreateDD(*args)


def gmdCreateL(*args):
    """gmdCreateL(pgmd, libName, msgBufSize) -> int"""
    return _gmdcc.gmdCreateL(*args)


def gmdFree(*args):
    """gmdFree(pgmd) -> int"""
    return _gmdcc.gmdFree(*args)


def gmdLibraryLoaded():
    """gmdLibraryLoaded() -> int"""
    return _gmdcc.gmdLibraryLoaded()


def gmdLibraryUnload():
    """gmdLibraryUnload() -> int"""
    return _gmdcc.gmdLibraryUnload()


def gmdGetScreenIndicator():
    """gmdGetScreenIndicator() -> int"""
    return _gmdcc.gmdGetScreenIndicator()


def gmdSetScreenIndicator(*args):
    """gmdSetScreenIndicator(scrind)"""
    return _gmdcc.gmdSetScreenIndicator(*args)


def gmdGetExceptionIndicator():
    """gmdGetExceptionIndicator() -> int"""
    return _gmdcc.gmdGetExceptionIndicator()


def gmdSetExceptionIndicator(*args):
    """gmdSetExceptionIndicator(excind)"""
    return _gmdcc.gmdSetExceptionIndicator(*args)


def gmdGetExitIndicator():
    """gmdGetExitIndicator() -> int"""
    return _gmdcc.gmdGetExitIndicator()


def gmdSetExitIndicator(*args):
    """gmdSetExitIndicator(extind)"""
    return _gmdcc.gmdSetExitIndicator(*args)


def gmdGetErrorCallback():
    """gmdGetErrorCallback() -> gmdErrorCallback_t"""
    return _gmdcc.gmdGetErrorCallback()


def gmdSetErrorCallback(*args):
    """gmdSetErrorCallback(func)"""
    return _gmdcc.gmdSetErrorCallback(*args)


def gmdGetAPIErrorCount():
    """gmdGetAPIErrorCount() -> int"""
    return _gmdcc.gmdGetAPIErrorCount()


def gmdSetAPIErrorCount(*args):
    """gmdSetAPIErrorCount(ecnt)"""
    return _gmdcc.gmdSetAPIErrorCount(*args)


def gmdErrorHandling(*args):
    """gmdErrorHandling(msg)"""
    return _gmdcc.gmdErrorHandling(*args)


def gmdInitFromGDX(*args):
    """gmdInitFromGDX(pgmd, fileName) -> int"""
    return _gmdcc.gmdInitFromGDX(*args)


def gmdInitFromDict(*args):
    """gmdInitFromDict(pgmd, gmoPtr) -> int"""
    return _gmdcc.gmdInitFromDict(*args)


def gmdInitFromDB(*args):
    """gmdInitFromDB(pgmd, gmdSrcPtr) -> int"""
    return _gmdcc.gmdInitFromDB(*args)


def gmdRegisterGMO(*args):
    """gmdRegisterGMO(pgmd, gmoPtr) -> int"""
    return _gmdcc.gmdRegisterGMO(*args)


def gmdCloseGDX(*args):
    """gmdCloseGDX(pgmd, loadRemain) -> int"""
    return _gmdcc.gmdCloseGDX(*args)


def gmdAddSymbolXPy(*args):
    """gmdAddSymbolXPy(pgmd, symName, aDim, stype, userInfo, explText, vDomPtrIn, keyStr_in, status) -> void *"""
    return _gmdcc.gmdAddSymbolXPy(*args)


def gmdAddSymbolPy(*args):
    """gmdAddSymbolPy(pgmd, symName, aDim, stype, userInfo, explText, status) -> void *"""
    return _gmdcc.gmdAddSymbolPy(*args)


def gmdFindSymbolPy(*args):
    """gmdFindSymbolPy(pgmd, symName, status) -> void *"""
    return _gmdcc.gmdFindSymbolPy(*args)


def gmdGetSymbolByIndexPy(*args):
    """gmdGetSymbolByIndexPy(pgmd, idx, status) -> void *"""
    return _gmdcc.gmdGetSymbolByIndexPy(*args)


def gmdClearSymbol(*args):
    """gmdClearSymbol(pgmd, symPtr) -> int"""
    return _gmdcc.gmdClearSymbol(*args)


def gmdCopySymbol(*args):
    """gmdCopySymbol(pgmd, tarSymPtr, srcSymPtr) -> int"""
    return _gmdcc.gmdCopySymbol(*args)


def gmdFindRecordPy(*args):
    """gmdFindRecordPy(pgmd, symPtr, keyStr_in, status) -> void *"""
    return _gmdcc.gmdFindRecordPy(*args)


def gmdFindFirstRecordPy(*args):
    """gmdFindFirstRecordPy(pgmd, symPtr, status) -> void *"""
    return _gmdcc.gmdFindFirstRecordPy(*args)


def gmdFindFirstRecordSlicePy(*args):
    """gmdFindFirstRecordSlicePy(pgmd, symPtr, keyStr_in, status) -> void *"""
    return _gmdcc.gmdFindFirstRecordSlicePy(*args)


def gmdFindLastRecordPy(*args):
    """gmdFindLastRecordPy(pgmd, symPtr, status) -> void *"""
    return _gmdcc.gmdFindLastRecordPy(*args)


def gmdFindLastRecordSlicePy(*args):
    """gmdFindLastRecordSlicePy(pgmd, symPtr, keyStr_in, status) -> void *"""
    return _gmdcc.gmdFindLastRecordSlicePy(*args)


def gmdRecordMoveNext(*args):
    """gmdRecordMoveNext(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdRecordMoveNext(*args)


def gmdRecordHasNext(*args):
    """gmdRecordHasNext(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdRecordHasNext(*args)


def gmdRecordMovePrev(*args):
    """gmdRecordMovePrev(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdRecordMovePrev(*args)


def gmdSameRecord(*args):
    """gmdSameRecord(pgmd, symIterPtrSrc, symIterPtrtar) -> int"""
    return _gmdcc.gmdSameRecord(*args)


def gmdRecordHasPrev(*args):
    """gmdRecordHasPrev(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdRecordHasPrev(*args)


def gmdGetElemText(*args):
    """gmdGetElemText(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdGetElemText(*args)


def gmdGetLevel(*args):
    """gmdGetLevel(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdGetLevel(*args)


def gmdGetLower(*args):
    """gmdGetLower(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdGetLower(*args)


def gmdGetUpper(*args):
    """gmdGetUpper(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdGetUpper(*args)


def gmdGetMarginal(*args):
    """gmdGetMarginal(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdGetMarginal(*args)


def gmdGetScale(*args):
    """gmdGetScale(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdGetScale(*args)


def gmdSetElemText(*args):
    """gmdSetElemText(pgmd, symIterPtr, txt) -> int"""
    return _gmdcc.gmdSetElemText(*args)


def gmdSetLevel(*args):
    """gmdSetLevel(pgmd, symIterPtr, value) -> int"""
    return _gmdcc.gmdSetLevel(*args)


def gmdSetLower(*args):
    """gmdSetLower(pgmd, symIterPtr, value) -> int"""
    return _gmdcc.gmdSetLower(*args)


def gmdSetUpper(*args):
    """gmdSetUpper(pgmd, symIterPtr, value) -> int"""
    return _gmdcc.gmdSetUpper(*args)


def gmdSetMarginal(*args):
    """gmdSetMarginal(pgmd, symIterPtr, value) -> int"""
    return _gmdcc.gmdSetMarginal(*args)


def gmdSetScale(*args):
    """gmdSetScale(pgmd, symIterPtr, value) -> int"""
    return _gmdcc.gmdSetScale(*args)


def gmdSetUserInfo(*args):
    """gmdSetUserInfo(pgmd, symPtr, value) -> int"""
    return _gmdcc.gmdSetUserInfo(*args)


def gmdAddRecordPy(*args):
    """gmdAddRecordPy(pgmd, symPtr, keyStr_in, status) -> void *"""
    return _gmdcc.gmdAddRecordPy(*args)


def gmdDeleteRecord(*args):
    """gmdDeleteRecord(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdDeleteRecord(*args)


def gmdGetKeys(*args):
    """gmdGetKeys(pgmd, symIterPtr, aDim) -> int"""
    return _gmdcc.gmdGetKeys(*args)


def gmdGetKey(*args):
    """gmdGetKey(pgmd, symIterPtr, idx) -> int"""
    return _gmdcc.gmdGetKey(*args)


def gmdGetDomain(*args):
    """gmdGetDomain(pgmd, symPtr, aDim) -> int"""
    return _gmdcc.gmdGetDomain(*args)


def gmdCopySymbolIteratorPy(*args):
    """gmdCopySymbolIteratorPy(pgmd, symIterPtrSrc, status) -> void *"""
    return _gmdcc.gmdCopySymbolIteratorPy(*args)


def gmdFreeSymbolIterator(*args):
    """gmdFreeSymbolIterator(pgmd, symIterPtr) -> int"""
    return _gmdcc.gmdFreeSymbolIterator(*args)


def gmdMergeUel(*args):
    """gmdMergeUel(pgmd, uel) -> int"""
    return _gmdcc.gmdMergeUel(*args)


def gmdInfo(*args):
    """gmdInfo(pgmd, infoKey) -> int"""
    return _gmdcc.gmdInfo(*args)


def gmdSymbolInfo(*args):
    """gmdSymbolInfo(pgmd, symPtr, infoKey) -> int"""
    return _gmdcc.gmdSymbolInfo(*args)


def gmdSymbolDim(*args):
    """gmdSymbolDim(pgmd, symPtr) -> int"""
    return _gmdcc.gmdSymbolDim(*args)


def gmdSymbolType(*args):
    """gmdSymbolType(pgmd, symPtr) -> int"""
    return _gmdcc.gmdSymbolType(*args)


def gmdWriteGDX(*args):
    """gmdWriteGDX(pgmd, fileName, noDomChk) -> int"""
    return _gmdcc.gmdWriteGDX(*args)


def gmdSetSpecialValues(*args):
    """gmdSetSpecialValues(pgmd, specVal) -> int"""
    return _gmdcc.gmdSetSpecialValues(*args)


def gmdSetDebug(*args):
    """gmdSetDebug(pgmd, debugLevel) -> int"""
    return _gmdcc.gmdSetDebug(*args)


def gmdGetLastError(*args):
    """gmdGetLastError(pgmd) -> int"""
    return _gmdcc.gmdGetLastError(*args)


def gmdCheckDBDV(*args):
    """gmdCheckDBDV(pgmd, dv) -> int"""
    return _gmdcc.gmdCheckDBDV(*args)


def gmdCheckSymbolDV(*args):
    """gmdCheckSymbolDV(pgmd, symPtr, dv) -> int"""
    return _gmdcc.gmdCheckSymbolDV(*args)


def gmdGetFirstDBDVPy(*args):
    """gmdGetFirstDBDVPy(pgmd, status) -> void *"""
    return _gmdcc.gmdGetFirstDBDVPy(*args)


def gmdGetFirstDVInSymbolPy(*args):
    """gmdGetFirstDVInSymbolPy(pgmd, symPtr, status) -> void *"""
    return _gmdcc.gmdGetFirstDVInSymbolPy(*args)


def gmdDomainCheckDone(*args):
    """gmdDomainCheckDone(pgmd) -> int"""
    return _gmdcc.gmdDomainCheckDone(*args)


def gmdGetFirstDVInNextSymbol(*args):
    """gmdGetFirstDVInNextSymbol(pgmd, dvHandle, nextavail) -> int"""
    return _gmdcc.gmdGetFirstDVInNextSymbol(*args)


def gmdMoveNextDVInSymbol(*args):
    """gmdMoveNextDVInSymbol(pgmd, dvHandle, nextavail) -> int"""
    return _gmdcc.gmdMoveNextDVInSymbol(*args)


def gmdFreeDVHandle(*args):
    """gmdFreeDVHandle(pgmd, dvHandle) -> int"""
    return _gmdcc.gmdFreeDVHandle(*args)


def gmdGetDVSymbolPy(*args):
    """gmdGetDVSymbolPy(pgmd, dvHandle, status) -> void *"""
    return _gmdcc.gmdGetDVSymbolPy(*args)


def gmdGetDVSymbolRecordPy(*args):
    """gmdGetDVSymbolRecordPy(pgmd, dvHandle, status) -> void *"""
    return _gmdcc.gmdGetDVSymbolRecordPy(*args)


def gmdGetDVIndicator(*args):
    """gmdGetDVIndicator(pgmd, dvHandle, viol) -> int"""
    return _gmdcc.gmdGetDVIndicator(*args)


def gmdInitUpdate(*args):
    """gmdInitUpdate(pgmd, gmoPtr) -> int"""
    return _gmdcc.gmdInitUpdate(*args)


def gmdUpdateModelSymbol(*args):
    """gmdUpdateModelSymbol(pgmd, gamsSymPtr, actionType, dataSymPtr, updateType, INOUT) -> int"""
    return _gmdcc.gmdUpdateModelSymbol(*args)


def gmdCallSolver(*args):
    """gmdCallSolver(pgmd, solvername) -> int"""
    return _gmdcc.gmdCallSolver(*args)


def gmdDenseSymbolToDenseArray(*args):
    """gmdDenseSymbolToDenseArray(pgmd, cube, vDim, symPtr, field) -> int"""
    return _gmdcc.gmdDenseSymbolToDenseArray(*args)


def gmdSparseSymbolToDenseArray(*args):
    """gmdSparseSymbolToDenseArray(pgmd, cube, vDim, symPtr, vDomPtr, field) -> int"""
    return _gmdcc.gmdSparseSymbolToDenseArray(*args)


def gmdSparseSymbolToSqzdArray(*args):
    """gmdSparseSymbolToSqzdArray(pgmd, cube, vDim, symPtr, vDomSqueezePtr, vDomPtr, field) -> int"""
    return _gmdcc.gmdSparseSymbolToSqzdArray(*args)


def gmdDenseArrayToSymbol(*args):
    """gmdDenseArrayToSymbol(pgmd, symPtr, vDomPtr, cube, vDim) -> int"""
    return _gmdcc.gmdDenseArrayToSymbol(*args)


def gmdDenseArraySlicesToSymbol(*args):
    """gmdDenseArraySlicesToSymbol(pgmd, symPtr, vDomSlicePtr, vDomPtr, cube, vDim) -> int"""
    return _gmdcc.gmdDenseArraySlicesToSymbol(*args)


GLOBAL_MAX_INDEX_DIM = _gmdcc.GLOBAL_MAX_INDEX_DIM
GLOBAL_UEL_IDENT_SIZE = _gmdcc.GLOBAL_UEL_IDENT_SIZE
ITERLIM_INFINITY = _gmdcc.ITERLIM_INFINITY
GMS_MAX_INDEX_DIM = _gmdcc.GMS_MAX_INDEX_DIM
GMS_UEL_IDENT_SIZE = _gmdcc.GMS_UEL_IDENT_SIZE
GMS_SSSIZE = _gmdcc.GMS_SSSIZE
GMS_VARTYPE_UNKNOWN = _gmdcc.GMS_VARTYPE_UNKNOWN
GMS_VARTYPE_BINARY = _gmdcc.GMS_VARTYPE_BINARY
GMS_VARTYPE_INTEGER = _gmdcc.GMS_VARTYPE_INTEGER
GMS_VARTYPE_POSITIVE = _gmdcc.GMS_VARTYPE_POSITIVE
GMS_VARTYPE_NEGATIVE = _gmdcc.GMS_VARTYPE_NEGATIVE
GMS_VARTYPE_FREE = _gmdcc.GMS_VARTYPE_FREE
GMS_VARTYPE_SOS1 = _gmdcc.GMS_VARTYPE_SOS1
GMS_VARTYPE_SOS2 = _gmdcc.GMS_VARTYPE_SOS2
GMS_VARTYPE_SEMICONT = _gmdcc.GMS_VARTYPE_SEMICONT
GMS_VARTYPE_SEMIINT = _gmdcc.GMS_VARTYPE_SEMIINT
GMS_VARTYPE_MAX = _gmdcc.GMS_VARTYPE_MAX
GMS_EQUTYPE_E = _gmdcc.GMS_EQUTYPE_E
GMS_EQUTYPE_G = _gmdcc.GMS_EQUTYPE_G
GMS_EQUTYPE_L = _gmdcc.GMS_EQUTYPE_L
GMS_EQUTYPE_N = _gmdcc.GMS_EQUTYPE_N
GMS_EQUTYPE_X = _gmdcc.GMS_EQUTYPE_X
GMS_EQUTYPE_C = _gmdcc.GMS_EQUTYPE_C
GMS_EQUTYPE_MAX = _gmdcc.GMS_EQUTYPE_MAX
GMS_VAL_LEVEL = _gmdcc.GMS_VAL_LEVEL
GMS_VAL_MARGINAL = _gmdcc.GMS_VAL_MARGINAL
GMS_VAL_LOWER = _gmdcc.GMS_VAL_LOWER
GMS_VAL_UPPER = _gmdcc.GMS_VAL_UPPER
GMS_VAL_SCALE = _gmdcc.GMS_VAL_SCALE
GMS_VAL_MAX = _gmdcc.GMS_VAL_MAX
sv_valund = _gmdcc.sv_valund
sv_valna = _gmdcc.sv_valna
sv_valpin = _gmdcc.sv_valpin
sv_valmin = _gmdcc.sv_valmin
sv_valeps = _gmdcc.sv_valeps
sv_normal = _gmdcc.sv_normal
sv_acronym = _gmdcc.sv_acronym
GMS_SVIDX_UNDEF = _gmdcc.GMS_SVIDX_UNDEF
GMS_SVIDX_NA = _gmdcc.GMS_SVIDX_NA
GMS_SVIDX_PINF = _gmdcc.GMS_SVIDX_PINF
GMS_SVIDX_MINF = _gmdcc.GMS_SVIDX_MINF
GMS_SVIDX_EPS = _gmdcc.GMS_SVIDX_EPS
GMS_SVIDX_NORMAL = _gmdcc.GMS_SVIDX_NORMAL
GMS_SVIDX_ACR = _gmdcc.GMS_SVIDX_ACR
GMS_SVIDX_MAX = _gmdcc.GMS_SVIDX_MAX
dt_set = _gmdcc.dt_set
dt_par = _gmdcc.dt_par
dt_var = _gmdcc.dt_var
dt_equ = _gmdcc.dt_equ
dt_alias = _gmdcc.dt_alias
GMS_DT_SET = _gmdcc.GMS_DT_SET
GMS_DT_PAR = _gmdcc.GMS_DT_PAR
GMS_DT_VAR = _gmdcc.GMS_DT_VAR
GMS_DT_EQU = _gmdcc.GMS_DT_EQU
GMS_DT_ALIAS = _gmdcc.GMS_DT_ALIAS
GMS_DT_MAX = _gmdcc.GMS_DT_MAX
GMS_SV_UNDEF = _gmdcc.GMS_SV_UNDEF
GMS_SV_NA = _gmdcc.GMS_SV_NA
GMS_SV_PINF = _gmdcc.GMS_SV_PINF
GMS_SV_MINF = _gmdcc.GMS_SV_MINF
GMS_SV_EPS = _gmdcc.GMS_SV_EPS
GMS_SV_ACR = _gmdcc.GMS_SV_ACR
GMS_SV_NAINT = _gmdcc.GMS_SV_NAINT
# This file is compatible with both classic and new-style classes.
