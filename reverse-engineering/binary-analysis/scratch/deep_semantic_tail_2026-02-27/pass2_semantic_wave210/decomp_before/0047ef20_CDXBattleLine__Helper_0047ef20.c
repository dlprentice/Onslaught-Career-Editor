/* address: 0x0047ef20 */
/* name: CDXBattleLine__Helper_0047ef20 */
/* signature: int * __fastcall CDXBattleLine__Helper_0047ef20(void * param_1) */


int * __fastcall CDXBattleLine__Helper_0047ef20(void *param_1)

{
  int iVar1;
  float *pfVar2;
  int iVar3;

  if (*(int *)((int)param_1 + 0x10) != -0x355db510) {
    return param_1;
  }
  pfVar2 = *(float **)((int)param_1 + 0x20);
  iVar3 = 0;
  *(undefined4 *)param_1 = 100000;
  *(undefined4 *)((int)param_1 + 8) = 0xfffe7960;
  *(undefined4 *)((int)param_1 + 4) = 100000;
  *(undefined4 *)((int)param_1 + 0xc) = 0xfffe7960;
  *(undefined4 *)((int)param_1 + 0x18) = 0xc7c35000;
  *(undefined4 *)((int)param_1 + 0x1c) = 0x47c35000;
  if (0 < *(int *)((int)param_1 + 0x10c0)) {
    do {
      iVar1 = 0;
      if (0 < *(int *)((int)param_1 + 0x10bc)) {
        do {
          if (*pfVar2 < *(float *)((int)param_1 + 0x1034)) {
            if (iVar1 < *(int *)param_1) {
              *(int *)param_1 = iVar1;
            }
            else if (*(int *)((int)param_1 + 8) < iVar1) {
              *(int *)((int)param_1 + 8) = iVar1;
            }
            if (iVar3 < *(int *)((int)param_1 + 4)) {
              *(int *)((int)param_1 + 4) = iVar3;
            }
            else if (*(int *)((int)param_1 + 0xc) < iVar3) {
              *(int *)((int)param_1 + 0xc) = iVar3;
            }
          }
          if (*pfVar2 < *(float *)((int)param_1 + 0x1c)) {
            *(float *)((int)param_1 + 0x1c) = *pfVar2;
          }
          if (*(float *)((int)param_1 + 0x18) < *pfVar2) {
            *(float *)((int)param_1 + 0x18) = *pfVar2;
          }
          pfVar2 = pfVar2 + 6;
          iVar1 = iVar1 + 1;
        } while (iVar1 < *(int *)((int)param_1 + 0x10bc));
      }
      iVar3 = iVar3 + 1;
    } while (iVar3 < *(int *)((int)param_1 + 0x10c0));
  }
  *(undefined4 *)((int)param_1 + 0x14) = *(undefined4 *)((int)param_1 + 0x20);
  *(undefined4 *)((int)param_1 + 0x10) = *(undefined4 *)((int)param_1 + 0x1034);
  return param_1;
}
