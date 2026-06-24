/* address: 0x0056202e */
/* name: CDXTexture__Helper_0056202e */
/* signature: int __cdecl CDXTexture__Helper_0056202e(void * param_1, uint param_2) */


int __cdecl CDXTexture__Helper_0056202e(void *param_1,uint param_2)

{
  void *pvVar1;
  int iVar2;
  uint uVar3;
  LPVOID pvVar4;
  byte *pbVar5;
  int local_3c;
  uint local_38;
  byte *local_34;
  void *local_30;
  void *local_2c;
  byte *local_28;
  void *local_24;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &DAT_005e5ca8;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  pbVar5 = (byte *)0x0;
  if (param_1 == (void *)0x0) {
    ExceptionList = &local_14;
    pvVar1 = _malloc(param_2);
  }
  else {
    if (param_2 == 0) {
      ExceptionList = &local_14;
      CRT__FreeBase((int)param_1);
    }
    else {
      ExceptionList = &local_14;
      if (DAT_009d35e8 == 3) {
        do {
          local_28 = (byte *)0x0;
          if (param_2 < (void *)0xffffffe1) {
            CDXTexture__Helper_00561179(9);
            local_8 = 0;
            local_2c = (void *)CRT__FindSmallBlockHeapEntryForPtr((int)param_1);
            if (local_2c != (void *)0x0) {
              if (param_2 <= DAT_009d35e0) {
                iVar2 = CDXTexture__Helper_00566b42(local_2c,(int)param_1,param_2);
                if (iVar2 == 0) {
                  local_28 = (byte *)CRT__SbHeapAllocBlock((void *)param_2);
                  if (local_28 != (byte *)0x0) {
                    local_24 = (void *)(*(int *)((int)param_1 + -4) - 1);
                    pvVar1 = local_24;
                    if (param_2 <= local_24) {
                      pvVar1 = (void *)param_2;
                    }
                    CTexture__Helper_00567700(local_28,param_1,(uint)pvVar1);
                    local_2c = (void *)CRT__FindSmallBlockHeapEntryForPtr((int)param_1);
                    CDXTexture__Helper_00566364(local_2c,(int)param_1);
                  }
                }
                else {
                  local_28 = param_1;
                }
              }
              if (local_28 == (byte *)0x0) {
                if ((void *)param_2 == (void *)0x0) {
                  param_2 = 1;
                }
                param_2 = param_2 + 0xf & 0xfffffff0;
                local_28 = HeapAlloc(DAT_009d35e4,0,param_2);
                if (local_28 != (byte *)0x0) {
                  local_24 = (void *)(*(int *)((int)param_1 + -4) - 1);
                  pvVar1 = local_24;
                  if (param_2 <= local_24) {
                    pvVar1 = (void *)param_2;
                  }
                  CTexture__Helper_00567700(local_28,param_1,(uint)pvVar1);
                  CDXTexture__Helper_00566364(local_2c,(int)param_1);
                }
              }
            }
            local_8 = 0xffffffff;
            CTexture__Helper_005621b9();
            if (local_2c == (void *)0x0) {
              if ((void *)param_2 == (void *)0x0) {
                param_2 = 1;
              }
              param_2 = param_2 + 0xf & 0xfffffff0;
              local_28 = HeapReAlloc(DAT_009d35e4,0,param_1,param_2);
            }
          }
          if (local_28 != (byte *)0x0) {
            ExceptionList = local_14;
            return (int)(int *)local_28;
          }
          if (DAT_009d09b4 == (byte *)0x0) {
            ExceptionList = local_14;
            return 0;
          }
          iVar2 = CDXTexture__Helper_00566104(param_2);
        } while (iVar2 != 0);
      }
      else {
        ExceptionList = &local_14;
        if (DAT_009d35e8 == 2) {
          ExceptionList = &local_14;
          if (param_2 < 0xffffffe1) {
            if (param_2 == 0) {
              param_2 = 0x10;
              ExceptionList = &local_14;
            }
            else {
              param_2 = param_2 + 0xf & 0xfffffff0;
              ExceptionList = &local_14;
            }
          }
          do {
            local_28 = pbVar5;
            if (param_2 < 0xffffffe1) {
              CDXTexture__Helper_00561179(9);
              local_8 = 1;
              pbVar5 = (byte *)CDXTexture__Helper_00567094(param_1,&local_3c,&local_30);
              local_34 = pbVar5;
              if (pbVar5 == (byte *)0x0) {
                local_28 = HeapReAlloc(DAT_009d35e4,0,param_1,param_2);
              }
              else {
                if (param_2 < DAT_00655da4) {
                  iVar2 = CTexture__Helper_0056745c(local_3c,local_30,pbVar5,param_2 >> 4);
                  if (iVar2 == 0) {
                    local_28 = (byte *)CRT__SbHeapAllocDeferredBlock(param_2 >> 4);
                    if (local_28 != (byte *)0x0) {
                      local_38 = (uint)*pbVar5 << 4;
                      uVar3 = local_38;
                      if (param_2 <= local_38) {
                        uVar3 = param_2;
                      }
                      CTexture__Helper_00567700(local_28,param_1,uVar3);
                      CRT__SbHeapReleasePageBlock(local_3c,(int)local_30,pbVar5);
                    }
                  }
                  else {
                    local_28 = param_1;
                  }
                }
                if ((local_28 == (byte *)0x0) &&
                   (local_28 = HeapAlloc(DAT_009d35e4,0,param_2), local_28 != (byte *)0x0)) {
                  local_38 = (uint)*pbVar5 << 4;
                  uVar3 = local_38;
                  if (param_2 <= local_38) {
                    uVar3 = param_2;
                  }
                  CTexture__Helper_00567700(local_28,param_1,uVar3);
                  CRT__SbHeapReleasePageBlock(local_3c,(int)local_30,pbVar5);
                }
              }
              local_8 = 0xffffffff;
              CTexture__Helper_00562307();
            }
            if (local_28 != pbVar5) {
              ExceptionList = local_14;
              return (int)local_28;
            }
            if (DAT_009d09b4 == pbVar5) {
              ExceptionList = local_14;
              return (int)local_28;
            }
            iVar2 = CDXTexture__Helper_00566104(param_2);
          } while (iVar2 != 0);
        }
        else {
          do {
            pvVar4 = (LPVOID)0x0;
            if (param_2 < 0xffffffe1) {
              if (param_2 == 0) {
                param_2 = 1;
              }
              param_2 = param_2 + 0xf & 0xfffffff0;
              pvVar4 = HeapReAlloc(DAT_009d35e4,0,param_1,param_2);
            }
            if (pvVar4 != (LPVOID)0x0) {
              ExceptionList = local_14;
              return (int)pvVar4;
            }
            if (DAT_009d09b4 == (byte *)0x0) {
              ExceptionList = local_14;
              return 0;
            }
            iVar2 = CDXTexture__Helper_00566104(param_2);
          } while (iVar2 != 0);
        }
      }
    }
    pvVar1 = (void *)0x0;
  }
  ExceptionList = local_14;
  return (int)pvVar1;
}
