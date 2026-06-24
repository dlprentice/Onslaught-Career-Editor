/* address: 0x00490780 */
/* name: CMonitor__Unk_00490780 */
/* signature: void __thiscall CMonitor__Unk_00490780(void * this, int param_1, int param_2) */


void __thiscall CMonitor__Unk_00490780(void *this,int param_1,int param_2)

{
  bool bVar1;
  int iVar2;
  int *piVar3;

  DAT_009c6904 = 1;
  piVar3 = (int *)((int)this + 0x1cc);
  iVar2 = 1;
  DAT_009c68a0 = param_1 != 0;
  do {
    if (*piVar3 != 0) {
      (&DAT_009c68a0)[iVar2] = param_1 != 0;
      (&DAT_009c6904)[iVar2] = 1;
    }
    piVar3 = piVar3 + 0x1d;
    bVar1 = iVar2 < 8;
    iVar2 = iVar2 + 1;
  } while (bVar1);
  return;
}
