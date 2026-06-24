/* address: 0x005689b8 */
/* name: CTexture__Helper_005689b8 */
/* signature: int * __cdecl CTexture__Helper_005689b8(int param_1, int param_2) */


int * __cdecl CTexture__Helper_005689b8(int param_1,int param_2)

{
  int iVar1;
  void *pvVar2;
  void *pvVar3;
  void *_Size;
  int *local_24;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e5e88;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  pvVar2 = (void *)(param_1 * param_2);
  pvVar3 = pvVar2;
  ExceptionList = &local_14;
  if (pvVar2 < (void *)0xffffffe1) {
    if (pvVar2 == (void *)0x0) {
      pvVar3 = (void *)0x1;
    }
    pvVar3 = (void *)((int)pvVar3 + 0xfU & 0xfffffff0);
    ExceptionList = &local_14;
  }
  do {
    local_24 = (int *)0x0;
    if (pvVar3 < (void *)0xffffffe1) {
      if (DAT_009d35e8 == 3) {
        if (pvVar2 <= DAT_009d35e0) {
          CRT__LockByIndex(9);
          local_8 = 0;
          local_24 = CRT__SbHeapAllocBlock(pvVar2);
          local_8 = 0xffffffff;
          CRT__UnlockHeap9_SbAllocPath();
          _Size = pvVar2;
          if (local_24 == (int *)0x0) goto LAB_00568aa5;
LAB_00568a94:
          _memset(local_24,0,(size_t)_Size);
        }
LAB_00568aa0:
        if (local_24 != (int *)0x0) {
          ExceptionList = local_14;
          return local_24;
        }
      }
      else {
        if ((DAT_009d35e8 != 2) || (DAT_00655da4 < pvVar3)) goto LAB_00568aa0;
        CRT__LockByIndex(9);
        local_8 = 1;
        local_24 = CRT__SbHeapAllocDeferredBlock((uint)pvVar3 >> 4);
        local_8 = 0xffffffff;
        CRT__UnlockHeap9_DeferredAllocPath();
        _Size = pvVar3;
        if (local_24 != (int *)0x0) goto LAB_00568a94;
      }
LAB_00568aa5:
      local_24 = HeapAlloc(DAT_009d35e4,8,(SIZE_T)pvVar3);
    }
    if (local_24 != (int *)0x0) {
      ExceptionList = local_14;
      return local_24;
    }
    if (DAT_009d09b4 == 0) {
      ExceptionList = local_14;
      return (int *)0x0;
    }
    iVar1 = CRT__InvokeLocaleValidationCallback((int)pvVar3);
    if (iVar1 == 0) {
      ExceptionList = local_14;
      return (int *)0x0;
    }
  } while( true );
}
