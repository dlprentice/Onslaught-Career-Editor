/* address: 0x0055f807 */
/* name: CRT__MbsNcpy_LocaleLock */
/* signature: int __cdecl CRT__MbsNcpy_LocaleLock(void * param_1, void * param_2, uint param_3) */


int __cdecl CRT__MbsNcpy_LocaleLock(void *param_1,void *param_2,uint param_3)

{
  byte bVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;
  byte *pbVar5;
  byte *pbVar6;

  if (DAT_009d33bc == 0) {
    param_1 = _strncpy(param_1,param_2,param_3);
  }
  else {
    CRT__LockByIndex(0x19);
    uVar4 = 0;
    pbVar6 = param_1;
    pbVar5 = param_1;
    if (param_3 != 0) {
      do {
        bVar1 = *(byte *)param_2;
        uVar4 = param_3 - 1;
        bVar2 = *(byte *)((int)&DAT_009d34c0 + bVar1 + 1);
        *pbVar5 = bVar1;
        if ((bVar2 & 4) == 0) {
          pbVar6 = pbVar5 + 1;
          param_2 = (void *)((int)param_2 + 1);
          if (bVar1 == 0) goto LAB_0055f878;
        }
        else {
          pbVar6 = pbVar5 + 1;
          if (uVar4 == 0) {
            *pbVar5 = 0;
            goto LAB_0055f878;
          }
          bVar1 = *(byte *)((int)param_2 + 1);
          uVar4 = param_3 - 2;
          *pbVar6 = bVar1;
          pbVar6 = pbVar5 + 2;
          param_2 = (void *)((int)param_2 + 2);
          if (bVar1 == 0) {
            *pbVar5 = 0;
            goto LAB_0055f878;
          }
        }
        param_3 = uVar4;
        pbVar5 = pbVar6;
      } while (uVar4 != 0);
      uVar4 = 0;
    }
LAB_0055f878:
    if (uVar4 != 0) {
      for (uVar3 = uVar4 >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
        pbVar6[0] = 0;
        pbVar6[1] = 0;
        pbVar6[2] = 0;
        pbVar6[3] = 0;
        pbVar6 = pbVar6 + 4;
      }
      for (uVar4 = uVar4 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
        *pbVar6 = 0;
        pbVar6 = pbVar6 + 1;
      }
    }
    CRT__UnlockByIndex(0x19);
  }
  return (int)param_1;
}
