/* address: 0x0056ce8a */
/* name: CRT__IsInDst */
/* signature: bool __cdecl CRT__IsInDst(void * param_1) */


bool __cdecl CRT__IsInDst(void *param_1)

{
  int iVar1;
  int iVar2;

  if (DAT_0065698c != 0) {
    if ((*(int *)((int)param_1 + 0x14) != DAT_00656a20) ||
       (*(int *)((int)param_1 + 0x14) != DAT_00656a30)) {
      if (DAT_009d0b40 == 0) {
        CRT__ComputeDstTransitionDayMillis();
        CRT__ComputeDstTransitionDayMillis();
      }
      else {
        CRT__ComputeDstTransitionDayMillis();
        CRT__ComputeDstTransitionDayMillis();
      }
    }
    iVar1 = *(int *)((int)param_1 + 0x1c);
    if (DAT_00656a24 < DAT_00656a34) {
      if ((DAT_00656a24 <= iVar1) && (iVar1 <= DAT_00656a34)) {
        if ((DAT_00656a24 < iVar1) && (iVar1 < DAT_00656a34)) {
          return true;
        }
LAB_0056d002:
        iVar2 = ((*(int *)((int)param_1 + 8) * 0x3c + *(int *)((int)param_1 + 4)) * 0x3c +
                *(int *)param_1) * 1000;
        if (iVar1 == DAT_00656a24) {
          return DAT_00656a28 <= iVar2;
        }
        return iVar2 < DAT_00656a38;
      }
    }
    else {
      if (iVar1 < DAT_00656a34) {
        return true;
      }
      if (DAT_00656a24 < iVar1) {
        return true;
      }
      if ((iVar1 <= DAT_00656a34) || (DAT_00656a24 <= iVar1)) goto LAB_0056d002;
    }
  }
  return false;
}
