/* address: 0x00472670 */
/* name: CGame__Unk_00472670 */
/* signature: int __fastcall CGame__Unk_00472670(int param_1) */


int __fastcall CGame__Unk_00472670(int param_1)

{
  int iVar1;
  int *piVar2;
  int iVar3;

  iVar1 = 0;
  piVar2 = (int *)(param_1 + 0x4c);
  iVar3 = 10;
  do {
    if (*piVar2 != 0) {
      iVar1 = iVar1 + 1;
    }
    piVar2 = piVar2 + 2;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  return iVar1;
}
