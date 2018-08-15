'''
Qoma Utilities for FAME HLI
'''
import platform
import re
import sys

import numpy as np
import pandas as pd
import pkg_resources
import pyhli


def open_hli():
    '''
    open the FAME host language interface
    '''
    status = [-1]
    pyhli.cfmini(status)
    if status[0] != pyhli.HSUCC:
        if status[0] == pyhli.HBPROD:
            print("\n\nObtain or update QOMA_PIN" +
                  " environment variable:\n\t{0:s}\n\n".format(
                      pyhli.get_support_url()))
        print("cfmini() {0}".format(status[0]))
        return status[0]

    ver = [-1.0]
    pyhli.cfmver(status, ver)
    if status[0] != pyhli.HSUCC:
        print("cfmver() {0}".format(status[0]))
        return status[0]

    print_stack(ver)
    return status[0]


def close_hli():
    '''
    close the FAME host language interface
    '''
    status = [-1]
    pyhli.cfmfin(status)
    if status[0] != pyhli.HSUCC:
        print("cfmfin() {0}".format(status[0]))
    return status[0]


def print_file(filename):
    '''
    print a file
    '''
    with open(filename) as file:
        for line in file:
            sys.stdout.write(line)
    file.close()
    sys.stdout.flush()


def print_stack(ver):
    '''
    print the package versions in the analytic ecosystem
    '''
    print("\n{0} {1} ({2}) {3}".format(platform.system(), platform.release(),
                                     platform.version(), platform.machine()))
    print("Python {0}".format(sys.version))
    print("NumPy {0:s} Pandas {1:s} FAME HLI {2:.5f} pyhli {3:s}".format(
        pkg_resources.get_distribution("numpy").version,
        pkg_resources.get_distribution("pandas").version, ver[0],
        pkg_resources.get_distribution("pyhli").version))


def print_catalog(famedata):
    '''
    print a meta data catalog
    '''
    for key in famedata:
        print(meta_to_string(famedata, key))


def get(db_dict, key):
    '''
    get data for <key> from <db_dict>
    '''
    entry = db_dict.get(key, None)
    if entry is None:
        return None

    data = entry.get('data', None)
    if data is None:
        return None

    fameinfo = entry.get('fame', None)
    if fameinfo is None:
        return None

    if fameinfo.get('class') == pyhli.HSERIE:
        frng =  entry.get('fame').get('range')
        print(frng)
        idx = to_pandas_range( frng )
        print(idx)
        return pd.Series(data=entry.get('data'),index=idx,name=key)

    return entry.get('data')


def put(db_dict,
        key,
        data,
        desc=None,
        docu=None,
        otype=pyhli.HPRECN,
        basis=pyhli.HBSBUS,
        obse=pyhli.HOBEND):
    '''
    put <data> for <key> in <db_dict>
    '''
    entry = dict()
    entry['data'] = data
    fameinfo = dict()

    if not desc is None and desc:
        fameinfo['desc'] = desc

    if not docu is None and docu:
        fameinfo['docu'] = docu

    if isinstance(data, pd.Series):
        fameinfo['range'] = to_fame_range(data.index)
        fameinfo['class'] = pyhli.HSERIE
        fameinfo['type'] = otype
        fameinfo['basis'] = basis
        fameinfo['observ'] = obse
    else:
        fameinfo['class'] = pyhli.HSCALA
        fameinfo['type'] = otype
    entry['fame'] = fameinfo
    db_dict[key] = entry


def meta_to_string(container, key):
    '''
    format meta data as a string for <key> from <container>
    '''
    meta = None
    entry = container.get(key, None)
    if not entry is None:
        fameinfo = entry.get('fame', None)
        if not fameinfo is None:
            fametype = fameinfo.get('type', None)
            if not fametype is None:
                fame_type_string = type_to_string(fametype)
                fameclass = fameinfo.get('class')
                if fameclass == pyhli.HSCALA:
                    meta = "SCALAR {0} : {1}".format(key, fame_type_string)
                elif fameclass == pyhli.HSERIE:
                    rng = fameinfo.get('range', None)
                    if not rng is None:
                        freq_code = rng[0]
                    if freq_code == pyhli.HCASEX:
                        rng_string = "{0} to {1}".format(rng[1], rng[2])
                    else:
                        start_str = [
                            "{0:{width}s}".format(
                                "", width=80)
                        ]
                        end_str = [
                            "{0:{width}s}".format(
                                "", width=80)
                        ]
                        outlen = [-1]
                        pyhli.fame_date_to_literal(
                            freq_code, rng[1], start_str, pyhli.HDEC,
                            pyhli.HFYAUT, 80, outlen)
                        pyhli.fame_date_to_literal(
                            freq_code, rng[2], end_str, pyhli.HDEC,
                            pyhli.HFYAUT, 80, outlen)
                        rng_string = "{0} to {1}".format(
                            start_str[0], end_str[0])
                    fame_index_string = "CASE" if freq_code == pyhli.HCASEX else type_to_string(freq_code)
                    meta = "SERIES {0} : {1} BY {2} {3}".format(
                        key, fame_type_string, fame_index_string,
                        rng_string)
            famedesc = fameinfo.get('desc', None)
            if not famedesc is None and famedesc:
                meta = "{0} -- {1}".format(meta, famedesc)
            famedocu = fameinfo.get('docu', None)
            if not famedocu is None and famedocu:
                meta = "{0}\n{1}\n".format(meta, famedocu)
            else:
                meta = "{0}\n".format(meta)
    return meta


FAME_CLASS = {
    pyhli.HSERIE: "SERIES",
    pyhli.HSCALA: "SCALAR",
    pyhli.HFRMLA: "FORMULA",
    pyhli.HGLNAM: "GLNAME",
    pyhli.HGLFOR: "GLFORMULA"
}

PANDAS_FREQ = {
    pyhli.HANDEC: 'A',
    pyhli.HQTDEC: 'Q',
    pyhli.HMONTH: 'M',
    pyhli.HWKFRI: 'W-FRI',
    pyhli.HBUSNS: 'B',
    pyhli.HDAILY: 'D',
    pyhli.HHOUR: 'H',
    pyhli.HMIN: 'T',
    pyhli.HSEC: 'S',
    pyhli.HMSEC: 'L'
}

FAME_FREQ = {'W': pyhli.HWKFRI}
for freq in PANDAS_FREQ:
    FAME_FREQ[PANDAS_FREQ[freq]] = freq
del FAME_FREQ['W-FRI']


def class_to_string(class_code):
    '''
    obtain a string FAME class description
    '''
    return FAME_CLASS[class_code]


def type_to_string(type_code):
    '''
    obtain a string FAME type description
    '''
    inlen = 80
    outlen = [-1]
    type_string = ["{0:{width}s}".format("", width=inlen)]
    pyhli.fame_type_to_string(type_code, type_string, inlen, outlen)

    is_date_data = type_code >= pyhli.HDATE

    fame_type_string = "{0}{1}{2}".format("DATE(" if is_date_data else "",
                                          type_string[0], ")"
                                          if is_date_data else "")

    return fame_type_string


def to_fame_range(pandas_range):
    '''
    convert a Pandas date range to a FAME date range
    '''
    dt0 = pandas_range[0]
    dt1 = pandas_range[-1]
    if not pandas_range.dtype == 'datetime64[ns]':
        return [pyhli.HCASEX, dt0, dt1]

    fame_freq = FAME_FREQ[(pandas_range.freq)._prefix]  # pylint: disable=W0212

    frng = [fame_freq, -1, -1]
    output = [-1]

    pyhli.fame_time_to_index(fame_freq, output, dt0.year, dt0.month, dt0.day,
                             dt0.hour, dt0.minute, dt0.second,
                             dt0.microsecond / 1000, pyhli.HCONT)
    frng[1] = output[0]

    pyhli.fame_time_to_index(fame_freq, output, dt1.year, dt1.month, dt1.day,
                             dt1.hour, dt1.minute, dt1.second,
                             dt1.microsecond / 1000, pyhli.HCONT)
    frng[2] = output[0]

    return frng


def to_pandas_range(fame_range):
    '''
    convert a FAME date range to a Pandas date range
    '''
    if fame_range[0] == pyhli.HCASEX:
        return np.arange(fame_range[1], fame_range[2] + 1, 1, dtype=np.int)
    pfrq = PANDAS_FREQ.get(fame_range[0], None)
    if pfrq is None:
        print("{0} frequency not implemented".format(
            type_to_string(fame_range[0])))
        return None
    return pd.date_range(
        start=_to_pandas_datetime(fame_range[0], fame_range[1]),
        end=_to_pandas_datetime(fame_range[0], fame_range[2]),
        freq=pfrq)


def _to_pandas_datetime(fame_freq, date):
    '''convert FAME frequency and date to Pandas datetime'''
    status = [-1]
    year = [-1]
    month = [-1]
    day = [-1]
    tgt_date = [-1]
    pyhli.cfmchfr(status, fame_freq, date, pyhli.HEND, pyhli.HDAILY, tgt_date, pyhli.HCONT)
    print("cfmchfr() status={0}\n".format(status[0]))
    pyhli.cfmdatd(status, pyhli.HDAILY, tgt_date[0], year, month, day)
    print("cfmdatd() status={0}\n".format(status[0]))

    return pd.to_datetime({
        'year': [year[0]],
        'month': [month[0]],
        'day': [day[0]]
        })[0]


def read_fame(dbname, wilnam="?", fame_range=None):
    '''
    read the contents of a FAME database into nested dictionaries

    outer dictionary: object name maps to a dictionary

    object dictionary: entries 'data' and 'fame'

    object's 'fame' dictionary:
        'desc' 'docu' 'range' 'class' 'type' 'basis' 'observ' 'cdate' 'mdate'
    '''
    status = [-1]
    dbkey = [-1]
    pyhli.cfmopdb(status, dbkey, [dbname], pyhli.HRMODE)
    pyhli.cfminwc(status, dbkey[0], [wilnam])

    _class = [-1]
    _type = [-1]
    _freq = [-1]
    findex = [-1]
    lindex = [-1]

    database = dict()
    outlen = [-1]
    while status[0] == pyhli.HSUCC:
        objnam = ["{0:{width}s}".format("", width=80)]
        pyhli.cfmnxwc(status, dbkey[0], objnam, _class, _type, _freq)
        if status[0] == pyhli.HSUCC:
            object_dict = dict()
            meta_dict = dict()

            basis = [-1]
            observ = [-1]
            cdate = [-1]
            mdate = [-1]
            desc = ["{0:{width}s}".format("", width=1024)]
            outdesclen = [-1]
            doc = ["{0:{width}s}".format("", width=1024)]
            outdoclen = [-1]
            status[0] = pyhli.fame_info(dbkey[0], objnam, _class, _type, _freq, findex,
                            lindex, basis, observ, cdate, mdate, desc,
                            1024, outdesclen, doc,
                            1024, outdoclen)

            meta_dict['desc'] = desc[0]
            meta_dict['docu'] = doc[0]
            if _class[0] == pyhli.HSERIE:
                rng = [_freq[0], findex[0],
                       lindex[0]] if fame_range is None else fame_range
                if _freq[0] != rng[0]:
                    continue
            else:
                if not fame_range is None:  # fame_range doesnt match scalar
                    continue
                rng = [0, 0, 0]

            numobs = rng[2] - rng[1] + 1

            if _type[0] == pyhli.HPRECN:
                valary = [0.0] * numobs
                pyhli.cfmrrng_double(status, dbkey[0], objnam, rng, valary,
                                     pyhli.HTMIS, [np.nan, np.nan, np.nan])
            elif _type[0] == pyhli.HNUMRC:
                valary = [0.0] * numobs
                pyhli.cfmrrng_float(status, dbkey[0], objnam, rng, valary,
                                    pyhli.HTMIS, [np.nan, np.nan, np.nan])
            elif _type[0] == pyhli.HSTRNG:
                valary = ["   "] * numobs
                misary = [0] * numobs
                inlen = [0] * numobs
                outlen = [0] * numobs
                pyhli.cfmgtsts(status, dbkey[0], objnam, rng, valary, misary, inlen, outlen)
                for i in range(numobs):
                    inlen[i] = outlen[i]
                    valary[i] = "".ljust(inlen[i])
                pyhli.cfmgtsts(status, dbkey[0], objnam, rng, valary, misary, inlen, outlen)
                for i in range(numobs):
                    valary[i] = None if misary[i] != pyhli.HNMVAL else valary[i]
            else:
                status = [-1]
                inlen = 10
                outlen = [0]
                valary = ["".ljust(inlen)]
                pyhli.cfmgtnl(status, dbkey[0], objnam, pyhli.HNLALL, valary,
                              inlen, outlen)
                
                if status[0] == pyhli.HTRUNC:
                    # allocate more space, try again
                    inlen = outlen[0]
                    valary = ["".ljust(inlen)]
                    pyhli.cfmgtnl(status, dbkey[0], objnam, pyhli.HNLALL,
                                  valary, inlen, outlen)

            if _class[0] == pyhli.HSCALA:
                object_dict['data'] = valary[0]
            else:
                object_dict['data'] = valary
                meta_dict['range'] = rng

            meta_dict['class'] = _class[0]
            meta_dict['type'] = _type[0]
            meta_dict['basis'] = basis[0]
            meta_dict['observ'] = observ[0]
            meta_dict['cdate'] = cdate[0]
            meta_dict['mdate'] = mdate[0]
            object_dict['fame'] = meta_dict
            database[objnam[0]] = object_dict

    pyhli.cfmcldb(status, dbkey[0])
    return database


def write_fame(dbname, container):
    '''
    write the contents of a python nested dictionary to FAME

    outer dictionary: object name maps to a dictionary

    object dictionary: entries 'data' and 'fame'

    object's 'fame' dictionary:
        'desc' 'docu' 'range' 'class' 'type' 'basis' 'observ' 'cdate' 'mdate'
    '''
    _status = [-1]
    _dbkey = [-1]
    pyhli.cfmopdb(_status, _dbkey, [dbname], pyhli.HUMODE)
    if _status[0] == pyhli.HRNEXI:
        pyhli.cfmopdb(_status, _dbkey, [dbname], pyhli.HCMODE)

    for key in container:
        entry = container[key]
        data = entry['data']
        meta = entry['fame']

        _objnam = [key]
        _class = meta['class']
        _range = meta['range'] if _class == pyhli.HSERIE else [0, 0, 0]
        _freq = _range[0] if _class == pyhli.HSERIE else pyhli.HUNDFX
        _type = meta['type']
        _basis = meta[
            'basis'] if _class == pyhli.HSERIE and _freq != pyhli.HCASEX else pyhli.HUNDFX
        _observ = meta[
            'observ'] if _class == pyhli.HSERIE and _freq != pyhli.HCASEX else pyhli.HOBUND
        _numobs = _range[2] - _range[1] + 1
        _numchr = 0
        if _type == pyhli.HSTRNG and _class == pyhli.HSERIE:
            _numchr = sum(len(s) for s in data)
        elif _type == pyhli.HSTRNG:
            _numchr = len(data)
        elif _type == pyhli.HNAMEL:
            _namelist = re.split('[, ]+', re.sub('[{}]', '', data))
            _numobs = len(_namelist)
            _numchr = sum(len(s) for s in _namelist)
        _growth = 0.0
        pyhli.cfmalob(_status, _dbkey[0], _objnam, _class, _freq, _type,
                      _basis, _observ, _numobs, _numchr, _growth)

        famedesc = meta.get('desc', None)
        if not famedesc is None and famedesc:
            pyhli.cfmsdes(_status, _dbkey[0], _objnam, [famedesc])

        famedocu = meta.get('docu', None)
        if not famedocu is None and famedocu:
            pyhli.cfmsdoc(_status, _dbkey[0], _objnam, [famedocu])

        if _type == pyhli.HPRECN:
            pyhli.cfmwrng_double(_status, _dbkey[0], _objnam, _range, data,
                                 pyhli.HTMIS, [np.nan, np.nan, np.nan])
        elif _type == pyhli.HNUMRC:
            pyhli.cfmwrng_float(_status, _dbkey[0], _objnam, _range, data,
                                pyhli.HTMIS, [np.nan, np.nan, np.nan])
        elif _type == pyhli.HSTRNG:
            _status[0] = pyhli.fame_write_strings(_dbkey[0], _objnam, _range,
                                                  data)
        else:
            for i in range(0, _numobs):
                pyhli.cfmwtnl(_status, _dbkey[0], _objnam, i + 1,
                              [_namelist[i]])

    pyhli.cfmcldb(_status, _dbkey[0])
