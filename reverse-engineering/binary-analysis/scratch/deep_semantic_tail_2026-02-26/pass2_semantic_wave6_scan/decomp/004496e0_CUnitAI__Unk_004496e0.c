/* address: 0x004496e0 */
/* name: CUnitAI__Unk_004496e0 */
/* signature: int __fastcall CUnitAI__Unk_004496e0(int param_1) */


int __fastcall CUnitAI__Unk_004496e0(int param_1)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  int *piVar4;
  int iVar5;

  iVar3 = 1;
  bVar2 = false;
  piVar4 = (int *)(param_1 + 0x4d0);
  iVar5 = 10;
  do {
    iVar1 = *piVar4;
    if (((iVar1 == 1) || (iVar1 == 2)) && (bVar2 = true, iVar1 == 2)) {
      iVar3 = 0;
    }
    piVar4 = piVar4 + 2;
    iVar5 = iVar5 + -1;
  } while (iVar5 != 0);
  if (!bVar2) {
    CConsole__Printf(&DAT_0066f580,s_ERROR__No_secondary_objectives_i_00628ad8);
    iVar3 = 0;
  }
  return iVar3;
}
