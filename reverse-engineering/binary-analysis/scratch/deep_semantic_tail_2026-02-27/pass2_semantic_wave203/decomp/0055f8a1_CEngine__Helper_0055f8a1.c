/* address: 0x0055f8a1 */
/* name: CEngine__Helper_0055f8a1 */
/* signature: int __cdecl CEngine__Helper_0055f8a1(void * param_1, void * param_2) */


int __cdecl CEngine__Helper_0055f8a1(void *param_1,void *param_2)

{
  int iVar1;
  uint uVar2;
  byte *pbVar3;
  ushort uVar4;
  char *pcVar5;
  ushort uVar6;
  uint uVar7;
  byte local_8;
  byte local_7;

  if (DAT_009d33bc == 0) {
    iVar1 = stricmp(param_1,param_2);
  }
  else {
    CRT__LockByIndex(0x19);
    do {
      uVar7 = (uint)*(byte *)param_1;
      pbVar3 = (byte *)((int)param_1 + 1);
      if ((*(byte *)((int)&DAT_009d34c0 + uVar7 + 1) & 4) == 0) {
        param_1 = pbVar3;
        if ((*(byte *)((int)&DAT_009d34c0 + uVar7 + 1) & 0x10) == 0x10) {
          uVar7 = (uint)(byte)(&DAT_009d33c0)[uVar7];
        }
      }
      else if (*pbVar3 == 0) {
        uVar7 = 0;
        param_1 = pbVar3;
      }
      else {
        iVar1 = CRT__LCMapStringA_Compat();
        if (iVar1 == 1) {
          uVar7 = (uint)local_8;
        }
        else {
          if (iVar1 != 2) goto LAB_0055fa05;
          uVar7 = (uint)local_8 * 0x100 + (uint)local_7;
        }
        param_1 = (byte *)((int)param_1 + 2);
      }
      uVar2 = (uint)*(byte *)param_2;
      uVar4 = (ushort)*(byte *)param_2;
      pcVar5 = (char *)((int)param_2 + 1);
      if ((*(byte *)((int)&DAT_009d34c0 + uVar2 + 1) & 4) == 0) {
        param_2 = pcVar5;
        if ((*(byte *)((int)&DAT_009d34c0 + uVar2 + 1) & 0x10) == 0x10) {
          uVar4 = (ushort)(byte)(&DAT_009d33c0)[uVar2];
        }
      }
      else if (*pcVar5 == '\0') {
        uVar4 = 0;
        param_2 = pcVar5;
      }
      else {
        iVar1 = CRT__LCMapStringA_Compat();
        if (iVar1 == 1) {
          uVar4 = (ushort)local_8;
        }
        else {
          if (iVar1 != 2) {
LAB_0055fa05:
            CRT__UnlockByIndex(0x19);
            return 0x7fffffff;
          }
          uVar4 = (ushort)local_8 * 0x100 + (ushort)local_7;
        }
        param_2 = (void *)((int)param_2 + 2);
      }
      uVar6 = (ushort)uVar7;
      if (uVar6 != uVar4) {
        CRT__UnlockByIndex(0x19);
        return (-(uint)(uVar4 < uVar6) & 2) - 1;
      }
    } while (uVar6 != 0);
    CRT__UnlockByIndex(0x19);
    iVar1 = 0;
  }
  return iVar1;
}
