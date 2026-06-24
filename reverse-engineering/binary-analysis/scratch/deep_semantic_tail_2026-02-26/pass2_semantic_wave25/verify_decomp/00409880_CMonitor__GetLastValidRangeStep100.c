/* address: 0x00409880 */
/* name: CMonitor__GetLastValidRangeStep100 */
/* signature: int __fastcall CMonitor__GetLastValidRangeStep100(int param_1) */


int __fastcall CMonitor__GetLastValidRangeStep100(int param_1)

{
  int iVar1;
  int *piVar2;
  int iVar3;

  iVar1 = 0;
  iVar3 = 0;
  piVar2 = (int *)(*(int *)(param_1 + 0xa4) + 0xc);
  do {
    if (*piVar2 != -1) {
      iVar1 = iVar3;
    }
    iVar3 = iVar3 + 100;
    piVar2 = piVar2 + 1;
  } while (iVar3 < 500);
  return iVar1;
}
