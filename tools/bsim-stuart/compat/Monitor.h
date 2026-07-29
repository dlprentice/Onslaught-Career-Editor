#ifndef BEA_BSIM_COMPAT_MONITOR_H
#define BEA_BSIM_COMPAT_MONITOR_H

class CGenericActiveReader;

class CMonitor {
public:
    void AddDeletionEvent(CGenericActiveReader *reader);
    void RemoveDeletionEvent(CGenericActiveReader *reader);
};

#endif
