#ifndef BEA_BSIM_COMPAT_COMMON_H
#define BEA_BSIM_COMPAT_COMMON_H

#ifndef _SIZE_T_DEFINED
#define _SIZE_T_DEFINED
typedef unsigned int size_t;
#endif

typedef int BOOL;

#ifndef NULL
#define NULL 0
#endif
#ifndef TRUE
#define TRUE 1
#endif
#ifndef FALSE
#define FALSE 0
#endif

class CMemoryManagerCompat {
public:
    void DoesExist(void *pointer);
};

class CDebugLogCompat {
public:
    void AddMessage(const char *message);
};

extern CMemoryManagerCompat MEM_MANAGER;
extern CDebugLogCompat LOG;

void AssertCompat(int condition, const char *file, int line);

#define ASSERT(expression) \
    ((expression) ? (void)0 : AssertCompat(0, __FILE__, __LINE__))

#ifndef MEMTYPE_SPTRSET
#define MEMTYPE_SPTRSET 1
#endif

void *__cdecl operator new(size_t size, int memory_type);
void *__cdecl operator new[](size_t size, int memory_type);
void __cdecl operator delete(void *pointer, int memory_type);
void __cdecl operator delete[](void *pointer, int memory_type);

#endif
